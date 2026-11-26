-- =========================================================
-- VATTE HOSPITAL OS — PHASE 14 (Medical Records + Follow-up + Quality AI)
-- Records: doctor visit note (complaints, examination, diagnosis, advice) + prescription in one save, allergy check by the server,
--          printable Rx; discharge summary (versioned); documents / reports upload (private storage, per hospital)
--          Notes are never edited — a change is a new version that points to the old one.
-- Follow-up: call / WhatsApp list, came / not came / move date; a visit within ±3 days closes the follow-up by itself
-- Quality: incident reporting (any staff, can hide own name), daily checklists, monthly quality numbers
-- AI: records pending, today's quality, quality numbers (read-only)
-- =========================================================

-- ---------- visit notes ----------
create table if not exists public.clinical_notes (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  complaints text,
  history text,
  examination text,
  provisional_dx text,
  final_dx text,
  advice text,
  vitals_snapshot jsonb,
  prescription_id uuid references public.prescriptions(id),
  follow_up_on date,
  supersedes_id uuid references public.clinical_notes(id),
  amend_reason text,
  allergy_override text,
  written_by uuid not null references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists clinical_notes_patient_idx on public.clinical_notes(patient_id, created_at desc);
create index if not exists clinical_notes_enc_idx on public.clinical_notes(encounter_id);
alter table public.clinical_notes enable row level security;
drop policy if exists p_read on public.clinical_notes;
create policy p_read on public.clinical_notes for select to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse}'));
revoke all on public.clinical_notes from anon;
revoke insert, update, delete on public.clinical_notes from authenticated;
grant select on public.clinical_notes to authenticated;
drop trigger if exists no_change on public.clinical_notes;
create trigger no_change before update or delete on public.clinical_notes for each row execute function public.block_change();
drop trigger if exists audit on public.clinical_notes;
create trigger audit after insert on public.clinical_notes for each row execute function public.audit_row();

-- prescriptions: only through rec_save_visit from now on
drop policy if exists p_insert on public.prescriptions;
revoke insert on public.prescriptions from authenticated;
alter table public.prescriptions add column if not exists note_id uuid;

-- allergy words in patient's allergy text that appear in a medicine name / generic name
create or replace function public.rx_allergy_hits(p_patient uuid, p_items jsonb) returns text
language plpgsql stable security definer set search_path = public as $$
declare al text; w text; x jsonb; hits text[] := '{}'; nm text; gen text;
begin
  select lower(coalesce(allergies, '')) into al from public.patients where id = p_patient;
  if al = '' or al ~ '^\s*(nil|none|no|nahi|nkda|no known.*)\s*\.?$' then return null; end if;
  for x in select * from jsonb_array_elements(coalesce(p_items, '[]')) loop
    nm := lower(coalesce(x->>'medicine', ''));
    select lower(coalesce(generic_name, '')) into gen from public.medicines where id = nullif(x->>'medicine_id', '')::uuid;
    for w in select unnest(regexp_split_to_array(al, '[^a-z0-9]+')) loop
      continue when length(w) < 4 or w in ('allergy','allergic','tablet','tablets','drug','drugs','medicine','reaction','rash','food','with','from','some');
      if position(w in nm) > 0 or position(w in coalesce(gen, '')) > 0
         or (w like 'penicil%' and (nm ~ '(amoxi|ampi|penicil|cloxa|piperacil)' or gen ~ '(amoxi|ampi|penicil|cloxa|piperacil)'))
         or (w like 'sulf%' and (nm ~ '(sulfa|sulpha|cotrimox|septran|bactrim)' or gen ~ '(sulfa|sulpha|trimethoprim)'))
         or (w in ('nsaid','nsaids','painkiller') and (nm ~ '(diclo|ibupro|aceclo|naprox|aspirin|ketorol|mefen)' or gen ~ '(diclo|ibupro|aceclo|naprox|aspirin|ketorol|mefen)')) then
        hits := hits || (x->>'medicine'); exit;
      end if;
    end loop;
  end loop;
  return nullif(array_to_string(array(select distinct unnest(hits)), ', '), '');
end $$;
revoke all on function public.rx_allergy_hits(uuid, jsonb) from public, anon;
grant execute on function public.rx_allergy_hits(uuid, jsonb) to authenticated;

-- one save = note + prescription + follow-up
-- p_rx: [{ "medicine": "Paracetamol 500 mg", "medicine_id": "...", "dose": "1 tab", "frequency": "1-0-1", "days": 5, "instructions": "khane ke baad" }]
create or replace function public.rec_save_visit(p_encounter uuid, p_note jsonb, p_rx jsonb, p_follow_up date default null,
  p_allergy_override text default null, p_supersedes uuid default null, p_amend_reason text default null) returns public.clinical_notes
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); e public.encounters; n public.clinical_notes; rx public.prescriptions; hits text; x jsonb; v jsonb; old public.clinical_notes;
begin
  if not public.has_role('{doctor}') then raise exception 'Visit note aur parchi sirf Doctor likh sakte hain'; end if;
  select * into e from public.encounters where id = p_encounter and hospital_id = h;
  if e.id is null then raise exception 'Visit nahi mila'; end if;
  if e.status = 'cancelled' then raise exception 'Ye visit cancel hai'; end if;
  if p_supersedes is not null then
    select * into old from public.clinical_notes where id = p_supersedes and encounter_id = e.id;
    if old.id is null then raise exception 'Purana note nahi mila'; end if;
    if exists (select 1 from public.clinical_notes where supersedes_id = old.id) then raise exception 'Is note ka naya version pehle se hai — sabse naya kholein'; end if;
    if coalesce(trim(p_amend_reason), '') = '' then raise exception 'Note badalne ka kaaran likhein'; end if;
  elsif exists (select 1 from public.clinical_notes where encounter_id = e.id) then
    raise exception 'Is visit ka note pehle se hai — "Badlo" se naya version banayein';
  end if;
  if coalesce(trim(p_note->>'complaints'), '') = '' and coalesce(trim(p_note->>'provisional_dx'), '') = '' and coalesce(trim(p_note->>'final_dx'), '') = '' then
    raise exception 'Kam se kam shikayat ya diagnosis likhein'; end if;
  if jsonb_typeof(coalesce(p_rx, '[]')) <> 'array' or jsonb_array_length(coalesce(p_rx, '[]')) > 30 then raise exception 'Parchi mein 30 dawa tak'; end if;
  for x in select * from jsonb_array_elements(coalesce(p_rx, '[]')) loop
    if coalesce(trim(x->>'medicine'), '') = '' then raise exception 'Har dawa ka naam likhein'; end if;
    if coalesce(trim(x->>'frequency'), '') = '' then raise exception '%: kitni baar (jaise 1-0-1) likhein', x->>'medicine'; end if;
    if nullif(x->>'days', '') is not null and ((x->>'days')::int <= 0 or (x->>'days')::int > 365) then raise exception '%: din galat', x->>'medicine'; end if;
  end loop;
  if p_follow_up is not null and (p_follow_up <= (now() at time zone 'Asia/Kolkata')::date or p_follow_up > (now() at time zone 'Asia/Kolkata')::date + 365) then
    raise exception 'Follow-up ki date kal se 1 saal ke andar'; end if;
  hits := public.rx_allergy_hits(e.patient_id, p_rx);
  if hits is not null and coalesce(trim(p_allergy_override), '') = '' then
    raise exception 'ALLERGY: patient ko "%" se allergy likhi hai — parchi mein: %. Phir bhi deni hai to kaaran likhein.',
      (select allergies from public.patients where id = e.patient_id), hits; end if;
  select to_jsonb(vv) into v from (
    select bp_systolic, bp_diastolic, pulse, temperature_f, spo2, resp_rate, recorded_at from public.vitals where patient_id = e.patient_id
     order by recorded_at desc limit 1) vv;
  if jsonb_array_length(coalesce(p_rx, '[]')) > 0 then
    insert into public.prescriptions(hospital_id, patient_id, encounter_id, items, advice, prescribed_by)
    values (h, e.patient_id, e.id, (select jsonb_agg(jsonb_build_object('medicine', trim(i->>'medicine'), 'medicine_id', nullif(i->>'medicine_id', ''),
                                      'dose', nullif(trim(i->>'dose'), ''), 'frequency', trim(i->>'frequency'), 'days', nullif(i->>'days', '')::int,
                                      'instructions', nullif(trim(i->>'instructions'), ''))) from jsonb_array_elements(p_rx) i),
            nullif(trim(p_note->>'advice'), ''), auth.uid()) returning * into rx;
  end if;
  insert into public.clinical_notes(hospital_id, patient_id, encounter_id, complaints, history, examination, provisional_dx, final_dx, advice,
    vitals_snapshot, prescription_id, follow_up_on, supersedes_id, amend_reason, allergy_override, written_by)
  values (h, e.patient_id, e.id, nullif(trim(p_note->>'complaints'), ''), nullif(trim(p_note->>'history'), ''), nullif(trim(p_note->>'examination'), ''),
    nullif(trim(p_note->>'provisional_dx'), ''), nullif(trim(p_note->>'final_dx'), ''), nullif(trim(p_note->>'advice'), ''), v, rx.id, p_follow_up,
    p_supersedes, nullif(trim(p_amend_reason), ''), case when hits is not null then trim(p_allergy_override) || ' [' || hits || ']' end, auth.uid())
  returning * into n;
  if p_follow_up is not null and not exists (select 1 from public.follow_ups where patient_id = e.patient_id and status = 'pending' and due_on = p_follow_up) then
    insert into public.follow_ups(hospital_id, patient_id, due_on, reason, created_by)
    values (h, e.patient_id, p_follow_up, coalesce(nullif(trim(p_note->>'final_dx'), ''), nullif(trim(p_note->>'provisional_dx'), ''), 'Follow-up'), auth.uid());
  end if;
  if e.doctor_id is null then update public.encounters set doctor_id = auth.uid() where id = e.id; end if;
  if hits is not null then
    perform public.agent_notify(h, 'doctor', 'warning', '⚠️ Allergy ke bawajood dawa likhi gayi', hits || ' — kaaran: ' || trim(p_allergy_override), 'agent:records:allergy:' || n.id);
  end if;
  return n;
end $$;
revoke all on function public.rec_save_visit(uuid, jsonb, jsonb, date, text, uuid, text) from public, anon;
grant execute on function public.rec_save_visit(uuid, jsonb, jsonb, date, text, uuid, text) to authenticated;

-- ---------- discharge summary (versioned) ----------
create table if not exists public.discharge_summaries (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  admission_id uuid not null references public.admissions(id),
  patient_id uuid not null references public.patients(id),
  diagnosis text not null,
  course text,
  procedures text,
  investigations text,
  condition_at_discharge text,
  medicines jsonb not null default '[]',
  advice text,
  follow_up_on date,
  supersedes_id uuid references public.discharge_summaries(id),
  amend_reason text,
  written_by uuid not null references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists ds_adm_idx on public.discharge_summaries(admission_id, created_at desc);
alter table public.discharge_summaries enable row level security;
drop policy if exists p_read on public.discharge_summaries;
create policy p_read on public.discharge_summaries for select to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse,receptionist}'));
revoke all on public.discharge_summaries from anon;
revoke insert, update, delete on public.discharge_summaries from authenticated;
grant select on public.discharge_summaries to authenticated;
drop trigger if exists no_change on public.discharge_summaries;
create trigger no_change before update or delete on public.discharge_summaries for each row execute function public.block_change();
drop trigger if exists audit on public.discharge_summaries;
create trigger audit after insert on public.discharge_summaries for each row execute function public.audit_row();

create or replace function public.rec_save_discharge(p_admission uuid, p_data jsonb, p_supersedes uuid default null, p_amend_reason text default null)
returns public.discharge_summaries
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); a public.admissions; d public.discharge_summaries; fu date := nullif(p_data->>'follow_up_on', '')::date; hits text;
begin
  if not public.has_role('{doctor}') then raise exception 'Discharge summary sirf Doctor likh sakte hain'; end if;
  select * into a from public.admissions where id = p_admission and hospital_id = h;
  if a.id is null then raise exception 'Admission nahi mila'; end if;
  if coalesce(trim(p_data->>'diagnosis'), '') = '' then raise exception 'Diagnosis likhna zaroori hai'; end if;
  if p_supersedes is not null then
    if not exists (select 1 from public.discharge_summaries where id = p_supersedes and admission_id = a.id) then raise exception 'Purani summary nahi mili'; end if;
    if exists (select 1 from public.discharge_summaries where supersedes_id = p_supersedes) then raise exception 'Naya version pehle se hai'; end if;
    if coalesce(trim(p_amend_reason), '') = '' then raise exception 'Badalne ka kaaran likhein'; end if;
  elsif exists (select 1 from public.discharge_summaries where admission_id = a.id) then
    raise exception 'Summary pehle se hai — "Badlo" se naya version banayein';
  end if;
  hits := public.rx_allergy_hits(a.patient_id, coalesce(p_data->'medicines', '[]'));
  if hits is not null and coalesce(trim(p_data->>'allergy_override'), '') = '' then
    raise exception 'ALLERGY: discharge dawa mein % — patient ki allergy: %. Phir bhi deni hai to kaaran likhein.', hits, (select allergies from public.patients where id = a.patient_id); end if;
  insert into public.discharge_summaries(hospital_id, admission_id, patient_id, diagnosis, course, procedures, investigations, condition_at_discharge,
    medicines, advice, follow_up_on, supersedes_id, amend_reason, written_by)
  values (h, a.id, a.patient_id, trim(p_data->>'diagnosis'), nullif(trim(p_data->>'course'), ''), nullif(trim(p_data->>'procedures'), ''),
    nullif(trim(p_data->>'investigations'), ''), nullif(trim(p_data->>'condition_at_discharge'), ''), coalesce(p_data->'medicines', '[]'),
    nullif(trim(p_data->>'advice'), '') || case when hits is not null then E'\n[Allergy override: ' || trim(p_data->>'allergy_override') || ']' else '' end,
    fu, p_supersedes, nullif(trim(p_amend_reason), ''), auth.uid()) returning * into d;
  update public.admissions set discharge_summary = left(d.diagnosis || coalesce(' · ' || d.condition_at_discharge, ''), 500) where id = a.id;
  if fu is not null and fu > current_date and not exists (select 1 from public.follow_ups where patient_id = a.patient_id and status = 'pending' and due_on = fu) then
    insert into public.follow_ups(hospital_id, patient_id, due_on, reason, created_by) values (h, a.patient_id, fu, 'Discharge ke baad: ' || d.diagnosis, auth.uid());
  end if;
  return d;
end $$;
revoke all on function public.rec_save_discharge(uuid, jsonb, uuid, text) from public, anon;
grant execute on function public.rec_save_discharge(uuid, jsonb, uuid, text) to authenticated;

-- ---------- documents (private storage bucket, folder = hospital id) — storage part applied as migration "phase14b_docs_storage" ----------
insert into storage.buckets(id, name, public, file_size_limit, allowed_mime_types)
values ('medical-docs', 'medical-docs', false, 10485760, array['image/jpeg','image/png','image/webp','application/pdf'])
on conflict (id) do update set public = false, file_size_limit = 10485760, allowed_mime_types = excluded.allowed_mime_types;
drop policy if exists "vatte docs read" on storage.objects;
create policy "vatte docs read" on storage.objects for select to authenticated
  using (bucket_id = 'medical-docs' and (storage.foldername(name))[1] = public.my_hospital()::text and public.has_role('{doctor,admin,nurse,lab}'));
drop policy if exists "vatte docs upload" on storage.objects;
create policy "vatte docs upload" on storage.objects for insert to authenticated
  with check (bucket_id = 'medical-docs' and (storage.foldername(name))[1] = public.my_hospital()::text and public.has_role('{doctor,admin,nurse,lab}'));
alter table public.medical_documents add column if not exists mime text;
alter table public.medical_documents add column if not exists size_bytes int;
drop policy if exists p_read on public.medical_documents;
create policy p_read on public.medical_documents for select to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse,lab}'));
drop policy if exists p_insert on public.medical_documents;
create policy p_insert on public.medical_documents for insert to authenticated
  with check (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse,lab}') and storage_path like public.my_hospital()::text || '/%'
              and exists (select 1 from public.patients p where p.id = patient_id and p.hospital_id = public.my_hospital()));
grant insert on public.medical_documents to authenticated;

-- ---------- follow-up ----------
create or replace function public.fu_update(p_id uuid, p_status text, p_feedback text default null, p_new_due date default null) returns public.follow_ups
language plpgsql security definer set search_path = public as $$
declare f public.follow_ups;
begin
  if not public.has_role('{doctor,admin,receptionist,nurse}') then raise exception 'Permission nahi'; end if;
  if p_status not in ('done','missed','cancelled','moved','called') then raise exception 'Status galat'; end if;
  select * into f from public.follow_ups where id = p_id and hospital_id = public.my_hospital() for update;
  if f.id is null or f.status <> 'pending' then raise exception 'Khula follow-up nahi mila'; end if;
  if p_status = 'moved' then
    if p_new_due is null or p_new_due < (now() at time zone 'Asia/Kolkata')::date then raise exception 'Nayi date aaj ya aage ki'; end if;
    update public.follow_ups set due_on = p_new_due, feedback = concat_ws(' · ', feedback, to_char(now() at time zone 'Asia/Kolkata', 'DD Mon') || ': date badli → ' || to_char(p_new_due, 'DD Mon') || coalesce(' (' || nullif(trim(p_feedback), '') || ')', ''))
     where id = f.id returning * into f;
  elsif p_status = 'called' then
    if coalesce(trim(p_feedback), '') = '' then raise exception 'Call par kya baat hui, likhein'; end if;
    update public.follow_ups set feedback = concat_ws(' · ', feedback, to_char(now() at time zone 'Asia/Kolkata', 'DD Mon HH24:MI') || ' 📞 ' || trim(p_feedback))
     where id = f.id returning * into f;
  else
    update public.follow_ups set status = p_status, feedback = concat_ws(' · ', feedback, nullif(trim(p_feedback), '')) where id = f.id returning * into f;
  end if;
  return f;
end $$;
revoke all on function public.fu_update(uuid, text, text, date) from public, anon;
grant execute on function public.fu_update(uuid, text, text, date) to authenticated;

-- a visit within 3 days of the follow-up date closes it
create or replace function public.fu_close_on_visit() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  update public.follow_ups set status = 'done', feedback = concat_ws(' · ', feedback, 'Patient aaya ' || to_char(new.started_at at time zone 'Asia/Kolkata', 'DD Mon'))
   where patient_id = new.patient_id and status = 'pending' and due_on between (new.started_at at time zone 'Asia/Kolkata')::date - 3 and (new.started_at at time zone 'Asia/Kolkata')::date + 3;
  return new;
end $$;
revoke all on function public.fu_close_on_visit() from public, anon, authenticated;
drop trigger if exists fu_close on public.encounters;
create trigger fu_close after insert on public.encounters for each row execute function public.fu_close_on_visit();

-- ---------- quality: incidents ----------
create table if not exists public.incidents (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  incident_no int not null,
  kind text not null check (kind in ('fall','medication_error','needle_stick','near_miss','equipment','infection','complaint','violence','other')),
  severity text not null check (severity in ('no_harm','minor','moderate','severe','death')),
  happened_at timestamptz not null,
  location text,
  patient_id uuid references public.patients(id),
  description text not null,
  immediate_action text,
  anonymous boolean not null default false,
  reported_by uuid not null references auth.users(id),
  status text not null default 'open' check (status in ('open','reviewed','closed')),
  root_cause text,
  corrective_action text,
  reviewed_by uuid references auth.users(id),
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);
alter table public.incidents enable row level security;
drop policy if exists p_read on public.incidents;
create policy p_read on public.incidents for select to authenticated
  using (hospital_id = public.my_hospital() and (public.has_role('{doctor,admin}') or reported_by = auth.uid()));
revoke all on public.incidents from anon;
revoke insert, update, delete on public.incidents from authenticated;
grant select on public.incidents to authenticated;
drop trigger if exists no_delete on public.incidents;
create trigger no_delete before delete on public.incidents for each row execute function public.block_delete();

-- the doctor sees "anonymous" reports without the reporter's name (view runs as owner and applies the same rule as p_read)
drop view if exists public.incidents_view;
create view public.incidents_view as
  select id, hospital_id, incident_no, kind, severity, happened_at, location, patient_id, description, immediate_action, anonymous,
         case when anonymous and reported_by <> auth.uid() then null else reported_by end as reported_by,
         status, root_cause, corrective_action, reviewed_by, reviewed_at, created_at
    from public.incidents
   where hospital_id = public.my_hospital() and (public.has_role('{doctor,admin}') or reported_by = auth.uid());
revoke all on public.incidents_view from anon;
grant select on public.incidents_view to authenticated;
revoke select on public.incidents from authenticated;

create or replace function public.q_report_incident(p_kind text, p_severity text, p_when timestamptz, p_location text, p_patient uuid,
  p_description text, p_action text, p_anonymous boolean default false) returns int
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); n int;
begin
  if h is null or public.my_role() = 'pending' then raise exception 'Permission nahi'; end if;
  if length(coalesce(trim(p_description), '')) < 10 then raise exception 'Kya hua, thoda detail mein likhein'; end if;
  if p_when is null or p_when > now() + interval '5 minutes' or p_when < now() - interval '30 days' then raise exception 'Kab hua — pichhle 30 din mein'; end if;
  if p_patient is not null and not exists (select 1 from public.patients where id = p_patient and hospital_id = h) then raise exception 'Patient nahi mila'; end if;
  n := public.next_number(h, 'incident');
  insert into public.incidents(hospital_id, incident_no, kind, severity, happened_at, location, patient_id, description, immediate_action, anonymous, reported_by)
  values (h, n, p_kind, p_severity, p_when, nullif(trim(p_location), ''), p_patient, trim(p_description), nullif(trim(p_action), ''), coalesce(p_anonymous, false), auth.uid());
  perform public.agent_notify(h, 'doctor', case when p_severity in ('severe','death','moderate') then 'critical' else 'warning' end,
    '⚠️ Ghatna #' || n || ': ' || replace(p_kind, '_', ' ') || ' (' || replace(p_severity, '_', ' ') || ')', left(trim(p_description), 200), 'agent:quality:inc:' || n);
  return n;
end $$;
revoke all on function public.q_report_incident(text, text, timestamptz, text, uuid, text, text, boolean) from public, anon;
grant execute on function public.q_report_incident(text, text, timestamptz, text, uuid, text, text, boolean) to authenticated;

create or replace function public.q_review_incident(p_id uuid, p_root text, p_action text, p_close boolean) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.has_role('{doctor,admin}') then raise exception 'Review sirf Doctor / Admin'; end if;
  if coalesce(trim(p_action), '') = '' then raise exception 'Aage se rokne ke liye kya karenge, likhein'; end if;
  update public.incidents set root_cause = nullif(trim(p_root), ''), corrective_action = trim(p_action), reviewed_by = auth.uid(), reviewed_at = now(),
         status = case when p_close then 'closed' else 'reviewed' end
   where id = p_id and hospital_id = public.my_hospital() and status <> 'closed';
  if not found then raise exception 'Khuli ghatna nahi mili'; end if;
end $$;
revoke all on function public.q_review_incident(uuid, text, text, boolean) from public, anon;
grant execute on function public.q_review_incident(uuid, text, text, boolean) to authenticated;

-- ---------- quality: daily checklists ----------
create table if not exists public.quality_templates (
  id text primary key,
  name text not null,
  items text[] not null,
  roles text[] not null,
  per_shift boolean not null default false,
  ord int not null default 0
);
alter table public.quality_templates enable row level security;
drop policy if exists p_read on public.quality_templates;
create policy p_read on public.quality_templates for select to authenticated using (true);
revoke all on public.quality_templates from anon;
revoke insert, update, delete on public.quality_templates from authenticated;
grant select on public.quality_templates to authenticated;
insert into public.quality_templates(id, name, items, roles, per_shift, ord) values
 ('hand_hygiene','🧼 Haath safai (hand hygiene)', array['Har bed ke paas sanitizer bhara hai','Wash basin par sabun / paani hai','Staff ne patient chhoone se pehle haath saaf kiye (5 log dekhe)','Gloves badal kar pehne gaye'], '{doctor,admin,nurse}', true, 1),
 ('bmw','🗑️ Biomedical waste (BMW) alag-alag', array['Peela dabba: khoon / pattiyan / body waste','Laal dabba: plastic tube, IV set, gloves','Safed dabba: suiyaan / blade (puncture-proof)','Neela dabba: kaanch / sheeshi','Dabbe 3/4 se zyada nahi bhare','BMW gaadi ne aaj kachra uthaya'], '{doctor,admin,nurse}', false, 2),
 ('crash_cart','🚑 Emergency trolley (crash cart)', array['Adrenaline, atropine, hydrocortisone maujood (expiry theek)','Ambu bag + mask (bade / bachche)','Oxygen cylinder bhara hai, key saath hai','Suction machine chalu','Laryngoscope bulb jal raha hai','IV cannula, fluids maujood'], '{doctor,admin,nurse}', false, 3),
 ('fridge','❄️ Dawa / vaccine fridge', array['Taapmaan 2°C se 8°C ke beech','Fridge mein khana nahi rakha','Expired vial / vaccine nahi'], '{doctor,admin,nurse,pharmacist}', true, 4),
 ('cleaning','🧹 Ward / OT safai', array['Farsh pocha (disinfectant) hua','Bed rail / table saaf','Bathroom saaf, sukha','Bedsheet badli (gandi / discharge ke baad)'], '{doctor,admin,nurse,hr}', true, 5),
 ('fire','🧯 Aag se suraksha', array['Fire extinguisher apni jagah, gauge hara','Emergency exit ka raasta khula','Bijli ke taar khule / jale nahi'], '{doctor,admin,hr}', false, 6)
on conflict (id) do update set name = excluded.name, items = excluded.items, roles = excluded.roles, per_shift = excluded.per_shift, ord = excluded.ord;

create table if not exists public.quality_checks (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  template_id text not null references public.quality_templates(id),
  day date not null,
  shift text not null default 'day' check (shift in ('day','morning','evening','night')),
  answers jsonb not null,
  failed int not null default 0,
  remarks text,
  checked_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  unique (hospital_id, template_id, day, shift)
);
alter table public.quality_checks enable row level security;
drop policy if exists p_read on public.quality_checks;
create policy p_read on public.quality_checks for select to authenticated using (hospital_id = public.my_hospital() and public.my_role() <> 'pending');
revoke all on public.quality_checks from anon;
revoke insert, update, delete on public.quality_checks from authenticated;
grant select on public.quality_checks to authenticated;
drop trigger if exists no_change on public.quality_checks;
create trigger no_change before update or delete on public.quality_checks for each row execute function public.block_change();

-- p_answers: { "item text": true / false }
create or replace function public.q_save_check(p_template text, p_shift text, p_answers jsonb, p_remarks text) returns public.quality_checks
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); t public.quality_templates; c public.quality_checks; nf int := 0; it text;
begin
  select * into t from public.quality_templates where id = p_template;
  if t.id is null then raise exception 'Checklist nahi mili'; end if;
  if not public.has_role(t.roles) then raise exception 'Aapka role ye checklist nahi bhar sakta'; end if;
  if not t.per_shift then p_shift := 'day'; elsif p_shift not in ('morning','evening','night') then raise exception 'Shift chunein'; end if;
  foreach it in array t.items loop
    if not (p_answers ? it) then raise exception 'Har line ka jawab dein: %', it; end if;
    if (p_answers->>it)::boolean is not true then nf := nf + 1; end if;
  end loop;
  if nf > 0 and coalesce(trim(p_remarks), '') = '' then raise exception '% line "nahi" hain — kya kiya / kya karna hai, likhein', nf; end if;
  insert into public.quality_checks(hospital_id, template_id, day, shift, answers, failed, remarks, checked_by)
  values (h, t.id, (now() at time zone 'Asia/Kolkata')::date, p_shift, p_answers, nf, nullif(trim(p_remarks), ''), auth.uid()) returning * into c;
  if nf > 0 and t.id in ('crash_cart','fridge','fire') then
    perform public.agent_notify(h, 'doctor', 'warning', '✅ Checklist: ' || t.name || ' — ' || nf || ' kami', trim(p_remarks), 'agent:quality:check:' || c.id);
  end if;
  return c;
exception when unique_violation then raise exception 'Ye checklist aaj (is shift) pehle hi bhari ja chuki hai';
end $$;
revoke all on function public.q_save_check(text, text, jsonb, text) from public, anon;
grant execute on function public.q_save_check(text, text, jsonb, text) to authenticated;

-- ---------- quality numbers ----------
create or replace function public.quality_numbers(h uuid, p_from date, p_to date) returns jsonb
language sql stable security definer set search_path = public as $$
  select jsonb_build_object(
    'from', p_from, 'to', p_to,
    'opd_visits', (select count(*) from public.encounters where hospital_id = h and kind in ('opd','emergency') and (started_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'avg_opd_wait_min', (select round(avg(extract(epoch from started_at - created_at) / 60)) from public.opd_queue where hospital_id = h and day between p_from and p_to and started_at is not null),
    'visit_notes_pct', (select round(100.0 * count(*) filter (where exists (select 1 from public.clinical_notes n where n.encounter_id = e.id)) / nullif(count(*), 0))
                          from public.encounters e where e.hospital_id = h and e.status <> 'cancelled' and (e.started_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'admissions', (select count(*) from public.admissions where hospital_id = h and (admitted_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'avg_stay_days', (select round(avg(extract(epoch from discharged_at - admitted_at) / 86400)::numeric, 1) from public.admissions where hospital_id = h and discharged_at is not null and (discharged_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'discharge_summary_pct', (select round(100.0 * count(*) filter (where exists (select 1 from public.discharge_summaries d where d.admission_id = a.id)) / nullif(count(*), 0))
                          from public.admissions a where a.hospital_id = h and a.discharged_at is not null and (a.discharged_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'readmit_30d', (select count(*) from public.admissions a where a.hospital_id = h and (a.admitted_at at time zone 'Asia/Kolkata')::date between p_from and p_to
                      and exists (select 1 from public.admissions b where b.patient_id = a.patient_id and b.id <> a.id and b.discharged_at between a.admitted_at - interval '30 days' and a.admitted_at)),
    'deaths', (select count(*) from public.admissions where hospital_id = h and status = 'expired' and (discharged_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'lama', (select count(*) from public.admissions where hospital_id = h and status = 'lama' and (discharged_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'lab_avg_tat_min', (select round(avg(extract(epoch from reported_at - ordered_at) / 60)) from public.lab_orders where hospital_id = h and status = 'reported' and (reported_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'critical_ack_avg_min', (select round(avg(extract(epoch from critical_ack_at - reported_at) / 60)) from public.lab_orders where hospital_id = h and is_critical and critical_ack_at is not null and (reported_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'critical_not_ack', (select count(*) from public.lab_orders where hospital_id = h and is_critical and critical_ack_at is null and status = 'reported' and (reported_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'followup_done_pct', (select round(100.0 * count(*) filter (where status = 'done') / nullif(count(*) filter (where status <> 'cancelled'), 0)) from public.follow_ups where hospital_id = h and due_on between p_from and least(p_to, current_date - 1)),
    'incidents', (select count(*) from public.incidents where hospital_id = h and (happened_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'incidents_serious', (select count(*) from public.incidents where hospital_id = h and severity in ('moderate','severe','death') and (happened_at at time zone 'Asia/Kolkata')::date between p_from and p_to),
    'incidents_open', (select count(*) from public.incidents where hospital_id = h and status = 'open'),
    'checklists_done', (select count(*) from public.quality_checks where hospital_id = h and day between p_from and p_to),
    'checklist_fail_lines', (select coalesce(sum(failed), 0) from public.quality_checks where hospital_id = h and day between p_from and p_to),
    'allergy_overrides', (select count(*) from public.clinical_notes where hospital_id = h and allergy_override is not null and (created_at at time zone 'Asia/Kolkata')::date between p_from and p_to)
  )
$$;
revoke all on function public.quality_numbers(uuid, date, date) from public, anon, authenticated;
create or replace function public.q_numbers(p_from date, p_to date) returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not public.has_role('{doctor,admin}') then raise exception 'Quality numbers sirf Doctor / Admin'; end if;
  if p_to < p_from or p_to - p_from > 366 then raise exception 'Date range galat (1 saal tak)'; end if;
  return public.quality_numbers(public.my_hospital(), p_from, p_to);
end $$;
revoke all on function public.q_numbers(date, date) from public, anon;
grant execute on function public.q_numbers(date, date) to authenticated;

-- ---------- AI handlers (read-only) ----------
create or replace function public.agent_h_records_pending(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare nv int; nd int; items jsonb;
begin
  select count(*) into nv from public.encounters e where e.hospital_id = h and e.status <> 'cancelled' and e.kind in ('opd','emergency')
     and e.started_at < now() - interval '4 hours' and e.started_at > now() - interval '7 days'
     and not exists (select 1 from public.clinical_notes n where n.encounter_id = e.id);
  select count(*) into nd from public.admissions a where a.hospital_id = h and a.discharged_at is not null and a.discharged_at > now() - interval '30 days'
     and not exists (select 1 from public.discharge_summaries d where d.admission_id = a.id);
  select coalesce(jsonb_agg(x), '[]') into items from (
    select jsonb_build_object('patient', p.full_name, 'uhid', p.uhid, 'kya', 'Visit note baaki', 'kab', to_char(e.started_at at time zone 'Asia/Kolkata', 'DD Mon')) x
      from public.encounters e join public.patients p on p.id = e.patient_id
     where e.hospital_id = h and e.status <> 'cancelled' and e.kind in ('opd','emergency') and e.started_at < now() - interval '4 hours' and e.started_at > now() - interval '7 days'
       and not exists (select 1 from public.clinical_notes n where n.encounter_id = e.id)
    union all
    select jsonb_build_object('patient', p.full_name, 'uhid', p.uhid, 'kya', 'Discharge summary baaki', 'kab', to_char(a.discharged_at at time zone 'Asia/Kolkata', 'DD Mon'))
      from public.admissions a join public.patients p on p.id = a.patient_id
     where a.hospital_id = h and a.discharged_at is not null and a.discharged_at > now() - interval '30 days'
       and not exists (select 1 from public.discharge_summaries d where d.admission_id = a.id)
    limit 30) s;
  return jsonb_build_object('summary', nv || ' visit ka note baaki (7 din) · ' || nd || ' discharge summary baaki', 'items', items, 'alert', nd > 0, 'alert_role', 'doctor');
end $$;

create or replace function public.agent_h_quality_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; missing text; fails int; openi int; serious int;
begin
  select string_agg(t.name, ', ' order by t.ord) into missing from public.quality_templates t
   where not exists (select 1 from public.quality_checks c where c.hospital_id = h and c.template_id = t.id and c.day = d);
  select coalesce(sum(failed), 0) into fails from public.quality_checks where hospital_id = h and day = d;
  select count(*), count(*) filter (where severity in ('moderate','severe','death')) into openi, serious from public.incidents where hospital_id = h and status = 'open';
  return jsonb_build_object('summary', coalesce('Aaj baaki checklist: ' || missing, 'Aaj ki saari checklist bhari ✓') || ' · ' || fails || ' kami mili · ' || openi || ' ghatna review baaki',
    'items', jsonb_build_array(jsonb_build_object('checklist_baaki', missing, 'kami', fails, 'ghatna_khuli', openi, 'gambhir_ghatna', serious)),
    'alert', serious > 0, 'alert_role', 'doctor');
end $$;

create or replace function public.agent_h_quality_numbers(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare f date := coalesce(nullif(inp->>'from','')::date, date_trunc('month', now() at time zone 'Asia/Kolkata')::date);
        t date := coalesce(nullif(inp->>'to','')::date, (now() at time zone 'Asia/Kolkata')::date); q jsonb;
begin
  q := public.quality_numbers(h, f, t);
  return jsonb_build_object('summary', to_char(f, 'DD Mon') || '–' || to_char(t, 'DD Mon') || ': ' || (q->>'opd_visits') || ' OPD · note ' || coalesce(q->>'visit_notes_pct', '—') || '% · lab TAT '
           || coalesce(q->>'lab_avg_tat_min', '—') || ' min · follow-up ' || coalesce(q->>'followup_done_pct', '—') || '% · ' || (q->>'incidents') || ' ghatna',
    'items', jsonb_build_array(q), 'alert', false);
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('records.pending','records','Records baaki','Jin visit ka doctor note nahi likha (7 din), aur discharge summary baaki','check','low','{doctor,admin,nurse}','{}','{encounters,clinical_notes,admissions,discharge_summaries}',17,'agent_h_records_pending', null),
 ('quality.today','quality','Aaj ki quality','Aaj kaun si checklist baaki, kitni kami mili, review baaki ghatna','check','low','{doctor,admin,nurse}','{}','{quality_checks,incidents}',18,'agent_h_quality_today', null),
 ('quality.numbers','quality','Quality numbers','Is mahine (ya chuni dates) ke quality aankde: OPD intezaar, note %, lab TAT, critical, follow-up %, ghatna, readmission','check','low','{doctor,admin}','{}','{encounters,opd_queue,lab_orders,follow_ups,incidents,admissions}',19,'agent_h_quality_numbers',
   '{"type":"object","properties":{"from":{"type":"string","description":"YYYY-MM-DD"},"to":{"type":"string","description":"YYYY-MM-DD"}}}')
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{clinical_notes,discharge_summaries,prescriptions,encounters,admissions}')) where id = 'records';
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{incidents,quality_checks,quality_templates,lab_orders,opd_queue,follow_ups}')) where id = 'quality';
insert into public.ai_chat_agents(agent_id, title, roles, tools) values
 ('records','Records AI','{doctor,admin,nurse}','{find_patient,records.pending,lab.patient_reports,followup.due}'),
 ('quality','Quality AI','{doctor,admin}','{quality.today,quality.numbers,records.pending}')
on conflict (agent_id) do update set title=excluded.title, roles=excluded.roles, tools=excluded.tools;
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{records.pending,quality.today}')) where agent_id = 'boss';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{quality.today}')) where agent_id = 'nurse';

-- 6:00 PM IST: checklists not filled → Sister reminder
create or replace function public.quality_evening_job() returns void
language plpgsql security definer set search_path = public as $$
declare h uuid; d date := (now() at time zone 'Asia/Kolkata')::date; m text;
begin
  for h in select id from public.hospitals loop
    select string_agg(t.name, ', ' order by t.ord) into m from public.quality_templates t
     where 'nurse' = any(t.roles) and not exists (select 1 from public.quality_checks c where c.hospital_id = h and c.template_id = t.id and c.day = d);
    if m is not null then perform public.agent_notify(h, 'nurse', 'warning', '✅ Aaj ki checklist baaki', m, 'agent:quality:evening:' || d); end if;
  end loop;
end $$;
revoke all on function public.quality_evening_job() from public, anon, authenticated;
do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname = 'vatte_quality_evening';
  perform cron.schedule('vatte_quality_evening', '30 12 * * *', $c$select public.quality_evening_job()$c$);
end $$;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;
