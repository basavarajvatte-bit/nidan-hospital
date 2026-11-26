-- =========================================================
-- VATTE HOSPITAL OS — PHASE 15b (Boss AI: patient lists)
-- Doctor asked Boss AI "saare admit patient ki list" and it had no tool. New read-only tools:
--   ipd.admitted        — abhi admit saare patient (bed, kitne din, aakhri vitals, baaki lab, baaki bill)
--   opd.list            — kisi din ke OPD patient (token, shikayat, note likha ya nahi)
--   ipd.movements       — dates ke beech admit / discharge hue patient
--   patient.summary     — ek patient ki poori jhalak (allergy, admit, aakhri diagnosis, vitals, dawa, lab, follow-up, baaki bill)
-- Boss AI now gets EVERY read-only check that a doctor may run, so it should never say "tool nahi hai" for a report.
-- Keys patient / uhid / phone are used so names are hidden from the outside AI (codes P1, U1…) and shown again in the app.
-- =========================================================

create or replace function public.agent_h_ipd_admitted(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; n int;
begin
  select coalesce(jsonb_agg(jsonb_build_object(
           'patient', p.full_name, 'uhid', p.uhid, 'patient_id', p.id, 'umar', p.age_years, 'gender', p.gender,
           'bed', coalesce(r.name || ' ', '') || coalesce(b.label, '—'),
           'admit_date', to_char(a.admitted_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM'),
           'din', greatest(1, ceil(extract(epoch from now() - a.admitted_at) / 86400.0)::int),
           'diagnosis', (select coalesce(c.final_dx, c.provisional_dx) from public.clinical_notes c where c.patient_id = p.id order by c.created_at desc limit 1),
           'allergy', nullif(p.allergies, ''),
           'aakhri_vitals', (select to_char(v.recorded_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM') || ' · BP ' || coalesce(v.bp_systolic::text, '–') || '/' || coalesce(v.bp_diastolic::text, '–')
                                    || ' · P ' || coalesce(v.pulse::text, '–') || ' · SpO2 ' || coalesce(v.spo2::text, '–') || ' · T ' || coalesce(v.temperature_f::text, '–')
                               from public.vitals v where v.patient_id = p.id order by v.recorded_at desc limit 1),
           'lab_baaki', (select count(*) from public.lab_orders l where l.patient_id = p.id and l.status in ('ordered','sample_collected','processing')),
           'critical_lab', (select count(*) from public.lab_orders l where l.patient_id = p.id and l.is_critical and l.critical_ack_at is null and l.status = 'reported'),
           'bill_baaki', (select coalesce(sum(i.total - i.discount - public.invoice_paid(i.id)), 0) from public.invoices i where i.patient_id = p.id and i.status in ('unpaid','partial'))
         ) order by a.admitted_at), '[]'), count(*)
    into items, n
    from public.admissions a join public.patients p on p.id = a.patient_id
    left join public.beds b on b.id = a.bed_id left join public.rooms r on r.id = b.room_id
   where a.hospital_id = h and a.status = 'admitted';
  return jsonb_build_object('summary', case when n = 0 then 'Abhi koi patient admit nahi' else n || ' patient abhi admit hain' end, 'items', items, 'alert', false);
end $$;

create or replace function public.agent_h_opd_list(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := coalesce(nullif(inp->>'day','')::date, (now() at time zone 'Asia/Kolkata')::date); items jsonb; n int; nopen int;
begin
  select coalesce(jsonb_agg(jsonb_build_object(
           'patient', p.full_name, 'uhid', p.uhid, 'patient_id', p.id, 'umar', p.age_years, 'gender', p.gender,
           'samay', to_char(e.started_at at time zone 'Asia/Kolkata', 'HH12:MI AM'), 'kind', e.kind, 'status', e.status,
           'token', (select q.token_no from public.opd_queue q where q.encounter_id = e.id limit 1),
           'shikayat', e.chief_complaint,
           'diagnosis', (select coalesce(c.final_dx, c.provisional_dx) from public.clinical_notes c where c.encounter_id = e.id order by c.created_at desc limit 1),
           'note_likha', exists (select 1 from public.clinical_notes c where c.encounter_id = e.id)
         ) order by e.started_at), '[]'), count(*), count(*) filter (where e.status = 'open')
    into items, n, nopen
    from public.encounters e join public.patients p on p.id = e.patient_id
   where e.hospital_id = h and e.kind in ('opd','emergency') and e.status <> 'cancelled' and (e.started_at at time zone 'Asia/Kolkata')::date = d;
  return jsonb_build_object('summary', to_char(d, 'DD Mon') || ': ' || n || ' OPD patient (' || nopen || ' abhi khule)', 'items', items, 'alert', false);
end $$;

create or replace function public.agent_h_ipd_movements(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare t date := coalesce(nullif(inp->>'to','')::date, (now() at time zone 'Asia/Kolkata')::date);
        f date := coalesce(nullif(inp->>'from','')::date, t - 6); items jsonb; na int; nd int;
begin
  if t - f > 92 then raise exception 'Ek baar mein 3 mahine tak'; end if;
  select coalesce(jsonb_agg(x order by x->>'sort'), '[]'),
         count(*) filter (where x->>'kya' = 'admit'), count(*) filter (where x->>'kya' <> 'admit')
    into items, na, nd
    from (
      select jsonb_build_object('kya', 'admit', 'patient', p.full_name, 'uhid', p.uhid, 'patient_id', p.id,
               'kab', to_char(a.admitted_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM'), 'abhi', a.status, 'sort', a.admitted_at::text) x
        from public.admissions a join public.patients p on p.id = a.patient_id
       where a.hospital_id = h and (a.admitted_at at time zone 'Asia/Kolkata')::date between f and t
      union all
      select jsonb_build_object('kya', case a.status when 'discharged' then 'discharge' else a.status end, 'patient', p.full_name, 'uhid', p.uhid, 'patient_id', p.id,
               'kab', to_char(a.discharged_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM'),
               'ruke_din', greatest(1, ceil(extract(epoch from a.discharged_at - a.admitted_at) / 86400.0)::int),
               'summary_bani', exists (select 1 from public.discharge_summaries s where s.admission_id = a.id), 'sort', a.discharged_at::text)
        from public.admissions a join public.patients p on p.id = a.patient_id
       where a.hospital_id = h and a.discharged_at is not null and (a.discharged_at at time zone 'Asia/Kolkata')::date between f and t
    ) s;
  return jsonb_build_object('summary', to_char(f, 'DD Mon') || ' – ' || to_char(t, 'DD Mon') || ': ' || na || ' admit · ' || nd || ' discharge / chhutti', 'items', items, 'alert', false);
end $$;

create or replace function public.agent_h_patient_summary(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare pid uuid := (inp->>'patient_id')::uuid; p public.patients; a record; o jsonb;
begin
  select * into p from public.patients where id = pid and hospital_id = h;
  if p.id is null then raise exception 'Patient nahi mila'; end if;
  select ad.admitted_at, b.label, r.name room into a from public.admissions ad left join public.beds b on b.id = ad.bed_id left join public.rooms r on r.id = b.room_id
   where ad.patient_id = pid and ad.status = 'admitted' limit 1;
  o := jsonb_build_object(
    'patient', p.full_name, 'uhid', p.uhid, 'phone', p.phone, 'umar', p.age_years, 'gender', p.gender, 'blood_group', p.blood_group,
    'allergy', coalesce(nullif(p.allergies, ''), 'likhi nahi'),
    'abhi_admit', case when a.admitted_at is null then 'nahi' else 'haan — ' || coalesce(a.room || ' ', '') || coalesce(a.label, '') || ' · ' || to_char(a.admitted_at at time zone 'Asia/Kolkata', 'DD Mon') || ' se' end,
    'aakhri_visits', (select coalesce(jsonb_agg(v), '[]') from (select jsonb_build_object('din', to_char(e.started_at at time zone 'Asia/Kolkata', 'DD Mon YY'), 'kind', e.kind,
         'shikayat', coalesce(c.complaints, e.chief_complaint), 'diagnosis', coalesce(c.final_dx, c.provisional_dx), 'salah', c.advice) v
       from public.encounters e left join lateral (select * from public.clinical_notes x where x.encounter_id = e.id order by x.created_at desc limit 1) c on true
      where e.patient_id = pid and e.status <> 'cancelled' order by e.started_at desc limit 3) s),
    'aakhri_vitals', (select jsonb_build_object('kab', to_char(recorded_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM'), 'bp', coalesce(bp_systolic::text, '–') || '/' || coalesce(bp_diastolic::text, '–'),
         'pulse', pulse, 'spo2', spo2, 'temp_f', temperature_f, 'resp', resp_rate) from public.vitals where patient_id = pid order by recorded_at desc limit 1),
    'aakhri_parchi', (select jsonb_build_object('kab', to_char(created_at at time zone 'Asia/Kolkata', 'DD Mon'), 'dawa', items) from public.prescriptions where patient_id = pid order by created_at desc limit 1),
    'lab', (select coalesce(jsonb_agg(l), '[]') from (select jsonb_build_object('test', t.name, 'status', o2.status, 'result', o2.result, 'critical', o2.is_critical,
         'kab', to_char(coalesce(o2.reported_at, o2.ordered_at) at time zone 'Asia/Kolkata', 'DD Mon')) l
       from public.lab_orders o2 join public.lab_tests t on t.id = o2.test_id where o2.patient_id = pid and o2.status <> 'cancelled' order by o2.ordered_at desc limit 8) s),
    'agla_follow_up', (select to_char(due_on, 'DD Mon YYYY') || coalesce(' · ' || reason, '') from public.follow_ups where patient_id = pid and status = 'pending' order by due_on limit 1),
    'bill_baaki', (select coalesce(sum(i.total - i.discount - public.invoice_paid(i.id)), 0) from public.invoices i where i.patient_id = pid and i.status in ('unpaid','partial')));
  return jsonb_build_object('summary', p.full_name || ' (' || p.uhid || ') ki jhalak', 'items', jsonb_build_array(o), 'alert', false);
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('ipd.admitted','reception','Abhi admit patient','Abhi admit saare patient: bed, kitne din se, diagnosis, allergy, aakhri vitals, baaki lab, critical lab, baaki bill','check','low',
   '{doctor,admin,nurse,receptionist}','{}','{admissions,patients,beds,rooms,vitals,lab_orders,invoices,clinical_notes}',3,'agent_h_ipd_admitted', null),
 ('opd.list','reception','OPD patient list','Kisi din (khaali = aaj) ke saare OPD / emergency patient: samay, token, shikayat, diagnosis, note likha ya nahi','check','low',
   '{doctor,admin,nurse,receptionist}','{}','{encounters,patients,opd_queue,clinical_notes}',3,'agent_h_opd_list',
   '{"type":"object","properties":{"day":{"type":"string","description":"YYYY-MM-DD (khaali = aaj)"}}}'),
 ('ipd.movements','reception','Admit / discharge list','Do tareekhon ke beech kaun admit hua aur kaun discharge / LAMA / expired hua (khaali = pichhle 7 din)','check','low',
   '{doctor,admin,nurse,receptionist}','{}','{admissions,patients,discharge_summaries}',3,'agent_h_ipd_movements',
   '{"type":"object","properties":{"from":{"type":"string","description":"YYYY-MM-DD"},"to":{"type":"string","description":"YYYY-MM-DD"}}}'),
 ('patient.summary','records','Patient ki poori jhalak','Ek patient: allergy, abhi admit?, aakhri 3 visit ka diagnosis, aakhri vitals, aakhri parchi, lab, agla follow-up, baaki bill. Pehle find_patient se patient_id lo.','check','low',
   '{doctor,admin,nurse}','{}','{patients,encounters,clinical_notes,vitals,prescriptions,lab_orders,follow_ups,invoices,admissions}',3,'agent_h_patient_summary',
   '{"type":"object","properties":{"patient_id":{"type":"string"}},"required":["patient_id"]}')
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;

-- Boss AI: every read-only check a doctor may run (+ patient search, vitals, beds)
update public.ai_chat_agents set tools = array(select distinct x from unnest(
    array['find_patient','latest_vitals','list_beds'] || array(select id from public.agent_actions where kind = 'check' and 'doctor' = any(requester_roles))) x)
 where agent_id = 'boss';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{ipd.admitted,opd.list,ipd.movements,patient.summary}')) where agent_id in ('nurse','records');
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{ipd.admitted,opd.list,ipd.movements}')) where agent_id = 'reception';

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;

-- ---------- (applied as migration "phase15c_all_patients_list") patients.list: SAARE registered patient ----------
create or replace function public.agent_h_patients_list(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare f date := nullif(inp->>'from','')::date; t date := nullif(inp->>'to','')::date;
        lim int := least(greatest(coalesce(nullif(inp->>'limit','')::int, 100), 1), 300);
        g text := nullif(lower(inp->>'gender'), ''); items jsonb; n int; tot int;
begin
  select count(*) into tot from public.patients where hospital_id = h;
  select count(*) into n from public.patients p where p.hospital_id = h
     and (f is null or (p.created_at at time zone 'Asia/Kolkata')::date >= f) and (t is null or (p.created_at at time zone 'Asia/Kolkata')::date <= t)
     and (g is null or p.gender = g);
  select coalesce(jsonb_agg(x), '[]') into items from (
    select jsonb_build_object('patient', p.full_name, 'uhid', p.uhid, 'patient_id', p.id, 'phone', p.phone, 'umar', p.age_years, 'gender', p.gender,
             'register_hua', to_char(p.created_at at time zone 'Asia/Kolkata', 'DD Mon YY'),
             'aakhri_visit', (select to_char(max(e.started_at) at time zone 'Asia/Kolkata', 'DD Mon YY') from public.encounters e where e.patient_id = p.id and e.status <> 'cancelled'),
             'visits', (select count(*) from public.encounters e where e.patient_id = p.id and e.status <> 'cancelled'),
             'abhi_admit', exists (select 1 from public.admissions a where a.patient_id = p.id and a.status = 'admitted')) x
      from public.patients p where p.hospital_id = h
       and (f is null or (p.created_at at time zone 'Asia/Kolkata')::date >= f) and (t is null or (p.created_at at time zone 'Asia/Kolkata')::date <= t)
       and (g is null or p.gender = g)
     order by p.created_at desc limit lim) s;
  return jsonb_build_object('summary', 'Hospital mein kul ' || tot || ' patient registered' ||
           case when f is not null or t is not null or g is not null then ' · filter se ' || n else '' end ||
           case when n > lim then ' · naye ' || lim || ' dikhaye (aur chahiye to limit badhayein)' else '' end,
    'items', items, 'alert', false);
end $$;
revoke all on function public.agent_h_patients_list(uuid, jsonb) from public, anon, authenticated;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('patients.list','reception','Saare patient ki list','Hospital mein register hue SAARE patient (naye pehle): naam, UHID, phone, umar, kab register, aakhri visit, kitne visit, abhi admit? Date / gender filter ho sakta hai','check','low',
   '{doctor,admin,receptionist,nurse}','{}','{patients,encounters,admissions}',2,'agent_h_patients_list',
   '{"type":"object","properties":{"from":{"type":"string","description":"register hone ki shuru date YYYY-MM-DD (optional)"},"to":{"type":"string","description":"aakhri date YYYY-MM-DD (optional)"},"gender":{"type":"string","enum":["male","female","other"]},"limit":{"type":"integer","description":"kitne (default 100, max 300)"}}}')
on conflict (id) do update set title=excluded.title, description=excluded.description, requester_roles=excluded.requester_roles, tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{patients.list}')) where agent_id in ('boss','reception','nurse','records');
