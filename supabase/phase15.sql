-- =========================================================
-- VATTE HOSPITAL OS — PHASE 15 (Boss AI)
-- • Priorities: one list of everything that needs the Doctor now (approvals, critical labs, serious incidents, leave, purchases,
--   missing records, stock, dues, repairs, missed checklists…) — red first, each with the module to open
-- • Daily numbers saved every night (boss_snapshots) → today vs yesterday vs 7-day average, month so far vs target, 30-day trend
-- • Monthly targets set by the Doctor
-- • Weekly report every Monday 8:30 AM (this week vs last week) + the morning / evening Boss report (phase 7) now include priorities
-- • Boss AI chat gets "priorities" and "numbers" tools; it only reads — every change still goes through approval
-- =========================================================

-- ---------- one day's numbers ----------
create or replace function public.boss_day_metrics(h uuid, d date) returns jsonb
language sql stable security definer set search_path = public as $$
  with r as (select (d::timestamp at time zone 'Asia/Kolkata') s, ((d + 1)::timestamp at time zone 'Asia/Kolkata') e)
  select jsonb_build_object(
    'opd', (select count(*) from public.encounters, r where hospital_id = h and kind in ('opd','emergency') and status <> 'cancelled' and started_at >= r.s and started_at < r.e),
    'new_patients', (select count(*) from public.patients, r where hospital_id = h and created_at >= r.s and created_at < r.e),
    'admissions', (select count(*) from public.admissions, r where hospital_id = h and admitted_at >= r.s and admitted_at < r.e),
    'discharges', (select count(*) from public.admissions, r where hospital_id = h and discharged_at >= r.s and discharged_at < r.e),
    'ipd_end', (select count(*) from public.admissions, r where hospital_id = h and admitted_at < r.e and (discharged_at is null or discharged_at >= r.e)),
    'collection', (select coalesce(sum(amount), 0) from public.payments, r where hospital_id = h and created_at >= r.s and created_at < r.e),
    'expenses', (select coalesce(sum(amount), 0) from public.expenses where hospital_id = h and spent_on = d),
    'billed', (select coalesce(sum(total - discount), 0) from public.invoices, r where hospital_id = h and status <> 'cancelled' and created_at >= r.s and created_at < r.e),
    'pharmacy_sale', (select coalesce(sum(total - discount), 0) from public.invoices, r where hospital_id = h and category = 'pharmacy' and status <> 'cancelled' and created_at >= r.s and created_at < r.e),
    'lab_tests', (select count(*) from public.lab_orders, r where hospital_id = h and status <> 'cancelled' and ordered_at >= r.s and ordered_at < r.e),
    'lab_critical', (select count(*) from public.lab_orders, r where hospital_id = h and is_critical and reported_at >= r.s and reported_at < r.e),
    'avg_wait_min', (select round(avg(extract(epoch from started_at - created_at) / 60)) from public.opd_queue where hospital_id = h and day = d and started_at is not null),
    'incidents', (select count(*) from public.incidents, r where hospital_id = h and happened_at >= r.s and happened_at < r.e),
    'staff_present', (select count(*) from public.attendance where hospital_id = h and day = d and status in ('present','half_day')),
    'staff_absent', (select count(*) from public.attendance where hospital_id = h and day = d and status = 'absent'),
    'followups_done', (select count(*) from public.follow_ups where hospital_id = h and due_on = d and status = 'done'),
    'followups_due', (select count(*) from public.follow_ups where hospital_id = h and due_on = d and status <> 'cancelled')
  )
$$;
revoke all on function public.boss_day_metrics(uuid, date) from public, anon, authenticated;

create table if not exists public.boss_snapshots (
  hospital_id uuid not null references public.hospitals(id),
  day date not null,
  metrics jsonb not null,
  saved_at timestamptz not null default now(),
  primary key (hospital_id, day)
);
alter table public.boss_snapshots enable row level security;
drop policy if exists p_read on public.boss_snapshots;
create policy p_read on public.boss_snapshots for select to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin}'));
revoke all on public.boss_snapshots from anon;
revoke insert, update, delete on public.boss_snapshots from authenticated;
grant select on public.boss_snapshots to authenticated;

create or replace function public.boss_snapshot_job(p_day date default null) returns void
language plpgsql security definer set search_path = public as $$
declare h uuid; d date := coalesce(p_day, (now() at time zone 'Asia/Kolkata')::date);
begin
  for h in select id from public.hospitals loop
    insert into public.boss_snapshots(hospital_id, day, metrics) values (h, d, public.boss_day_metrics(h, d))
    on conflict (hospital_id, day) do update set metrics = excluded.metrics, saved_at = now();
  end loop;
end $$;
revoke all on function public.boss_snapshot_job(date) from public, anon, authenticated;
-- fill the last 60 days once
do $$ declare i int; begin for i in 1..60 loop perform public.boss_snapshot_job((now() at time zone 'Asia/Kolkata')::date - i); end loop; end $$;

-- ---------- monthly targets ----------
create table if not exists public.boss_targets (
  hospital_id uuid not null references public.hospitals(id),
  metric text not null check (metric in ('opd','new_patients','admissions','collection','pharmacy_sale','lab_tests','expenses_max','avg_wait_max')),
  value numeric not null check (value >= 0),
  set_by uuid references auth.users(id),
  set_at timestamptz not null default now(),
  primary key (hospital_id, metric)
);
alter table public.boss_targets enable row level security;
drop policy if exists p_read on public.boss_targets;
create policy p_read on public.boss_targets for select to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin}'));
revoke all on public.boss_targets from anon;
revoke insert, update, delete on public.boss_targets from authenticated;
grant select on public.boss_targets to authenticated;
drop trigger if exists audit on public.boss_targets;
create trigger audit after insert or update on public.boss_targets for each row execute function public.audit_row();

create or replace function public.boss_set_target(p_metric text, p_value numeric) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.has_role('{doctor}') then raise exception 'Target sirf Doctor rakh sakte hain'; end if;
  if p_value is null then
    delete from public.boss_targets where hospital_id = public.my_hospital() and metric = p_metric; return;
  end if;
  if p_value < 0 or p_value > 1000000000 then raise exception 'Target galat'; end if;
  insert into public.boss_targets(hospital_id, metric, value, set_by) values (public.my_hospital(), p_metric, p_value, auth.uid())
  on conflict (hospital_id, metric) do update set value = excluded.value, set_by = auth.uid(), set_at = now();
end $$;
revoke all on function public.boss_set_target(text, numeric) from public, anon;
grant execute on function public.boss_set_target(text, numeric) to authenticated;

-- ---------- priorities (what needs the Doctor now) ----------
-- level: 1 = red (now), 2 = amber (today), 3 = info
create or replace function public.boss_priorities_rows(h uuid) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; out jsonb := '[]'; n int; amt numeric; t text;
begin
  -- 1. critical lab not seen
  select count(*), string_agg(p.full_name || ' — ' || lt.name, ', ') into n, t from public.lab_orders l join public.patients p on p.id = l.patient_id join public.lab_tests lt on lt.id = l.test_id
   where l.hospital_id = h and l.is_critical and l.critical_ack_at is null and l.status = 'reported';
  if n > 0 then out := out || jsonb_build_object('level', 1, 'area', 'Lab', 'title', n || ' CRITICAL lab report kisi ne nahi dekhi', 'detail', left(t, 200), 'module', 'lab'); end if;
  -- 2. serious incidents open
  select count(*) into n from public.incidents where hospital_id = h and status = 'open' and severity in ('moderate','severe','death');
  if n > 0 then out := out || jsonb_build_object('level', 1, 'area', 'Quality', 'title', n || ' gambhir ghatna review baaki', 'module', 'quality'); end if;
  -- 3. urgent repairs
  select count(*), string_agg(title, ', ') into n, t from public.ops_tickets where hospital_id = h and status in ('open','in_progress') and priority = 'urgent';
  if n > 0 then out := out || jsonb_build_object('level', 1, 'area', 'Operations', 'title', n || ' URGENT repair khula', 'detail', left(t, 200), 'module', 'ops'); end if;
  -- 4. expired stock still on shelf
  select count(*) into n from public.medicine_batches where hospital_id = h and quantity > 0 and expiry_date < current_date;
  if n > 0 then out := out || jsonb_build_object('level', 1, 'area', 'Pharmacy', 'title', n || ' expired batch abhi stock mein (bikta nahi, par hatana hai)', 'module', 'pharmacy'); end if;
  -- 5. approvals waiting
  select count(*), string_agg(distinct a.title, ', ') into n, t from public.agent_tasks k join public.agent_actions a on a.id = k.action
   where k.hospital_id = h and k.status = 'waiting_approval';
  if n > 0 then out := out || jsonb_build_object('level', 2, 'area', 'AI Agents', 'title', n || ' AI kaam aapki approval ka intezaar', 'detail', t, 'module', 'agents'); end if;
  select count(*), coalesce(sum(total), 0) into n, amt from public.purchases where hospital_id = h and purpose = 'general' and status = 'pending_approval';
  if n > 0 then out := out || jsonb_build_object('level', 2, 'area', 'Kharid', 'title', n || ' kharid manzoori baaki (₹' || to_char(amt, 'FM99,99,990') || ')', 'module', 'ops'); end if;
  select count(*) into n from public.leave_requests where hospital_id = h and status = 'pending';
  if n > 0 then out := out || jsonb_build_object('level', 2, 'area', 'HR', 'title', n || ' chhutti ki arzi baaki', 'module', 'hr'); end if;
  -- 6. records
  select count(*) into n from public.admissions a where a.hospital_id = h and a.discharged_at is not null and a.discharged_at > now() - interval '30 days'
     and not exists (select 1 from public.discharge_summaries s where s.admission_id = a.id);
  if n > 0 then out := out || jsonb_build_object('level', 2, 'area', 'Records', 'title', n || ' discharge summary baaki', 'module', 'records'); end if;
  select count(*) into n from public.encounters e where e.hospital_id = h and e.status <> 'cancelled' and e.kind in ('opd','emergency')
     and e.started_at < now() - interval '4 hours' and e.started_at > now() - interval '7 days' and not exists (select 1 from public.clinical_notes c where c.encounter_id = e.id);
  if n > 0 then out := out || jsonb_build_object('level', 3, 'area', 'Records', 'title', n || ' visit ka doctor note nahi likha (7 din)', 'module', 'records'); end if;
  -- 7. lab late
  select count(*) into n from public.lab_orders o join public.lab_tests t2 on t2.id = o.test_id
   where o.hospital_id = h and o.status in ('ordered','sample_collected','processing') and o.ordered_at < now() - make_interval(hours => t2.tat_hours);
  if n > 0 then out := out || jsonb_build_object('level', 2, 'area', 'Lab', 'title', n || ' test samay se late', 'module', 'lab'); end if;
  -- 8. money
  if exists (select 1 from public.payments where hospital_id = h and (created_at at time zone 'Asia/Kolkata')::date = d - 1)
     and not exists (select 1 from public.cash_closings where hospital_id = h and day = d - 1) then
    out := out || jsonb_build_object('level', 2, 'area', 'Accounts', 'title', 'Kal ka cash close nahi hua', 'module', 'accounts'); end if;
  select count(*), coalesce(sum(i.total - i.discount - public.invoice_paid(i.id)), 0) into n, amt from public.invoices i
   where i.hospital_id = h and i.status in ('unpaid','partial') and i.created_at < now() - interval '7 days';
  if n > 0 then out := out || jsonb_build_object('level', 3, 'area', 'Accounts', 'title', n || ' bill 7 din se zyada baaki (₹' || to_char(amt, 'FM99,99,990') || ')', 'module', 'accounts'); end if;
  -- 9. pharmacy low stock
  select count(*) into n from public.pharmacy_reorder_rows(h);
  if n > 0 then out := out || jsonb_build_object('level', 3, 'area', 'Pharmacy', 'title', n || ' dawa ka stock kam', 'module', 'pharmacy'); end if;
  -- 10. follow-ups late
  select count(*) into n from public.follow_ups where hospital_id = h and status = 'pending' and due_on < d;
  if n > 0 then out := out || jsonb_build_object('level', 3, 'area', 'Follow-up', 'title', n || ' follow-up late (patient nahi aaya / call nahi hua)', 'module', 'records'); end if;
  -- 11. yesterday's checklists
  select count(*) into n from public.quality_templates qt where not exists (select 1 from public.quality_checks c where c.hospital_id = h and c.template_id = qt.id and c.day = d - 1);
  if n > 0 then out := out || jsonb_build_object('level', 3, 'area', 'Quality', 'title', 'Kal ki ' || n || ' checklist nahi bhari', 'module', 'quality'); end if;
  -- 12. allergy overrides (24 h)
  select count(*) into n from public.clinical_notes where hospital_id = h and allergy_override is not null and created_at > now() - interval '24 hours';
  if n > 0 then out := out || jsonb_build_object('level', 2, 'area', 'Records', 'title', n || ' parchi allergy ke bawajood likhi gayi (24 ghante)', 'module', 'records'); end if;
  -- 13. beds full
  if (select count(*) from public.beds where hospital_id = h) > 0 and not exists (select 1 from public.beds where hospital_id = h and status = 'available') then
    out := out || jsonb_build_object('level', 2, 'area', 'Beds', 'title', 'Koi bed khali nahi', 'module', 'reception'); end if;
  -- 14. OPD line long
  select count(*) into n from public.opd_queue where hospital_id = h and day = d and status = 'waiting';
  if n >= 15 then out := out || jsonb_build_object('level', 2, 'area', 'OPD', 'title', n || ' patient OPD line mein', 'module', 'appointments'); end if;
  return coalesce((select jsonb_agg(x order by (x->>'level')::int) from jsonb_array_elements(out) x), '[]');
end $$;
revoke all on function public.boss_priorities_rows(uuid) from public, anon, authenticated;

-- ---------- one call for the Boss screen ----------
create or replace function public.boss_overview() returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare h uuid := public.my_hospital(); d date := (now() at time zone 'Asia/Kolkata')::date; m0 date := date_trunc('month', now() at time zone 'Asia/Kolkata')::date;
        today jsonb; mtd jsonb; avg7 jsonb; series jsonb; tg jsonb;
begin
  if not public.has_role('{doctor,admin}') then raise exception 'Boss screen sirf Doctor / Admin ke liye'; end if;
  today := public.boss_day_metrics(h, d);
  select coalesce(jsonb_object_agg(k, s), '{}') into mtd from (
    select k, sum((metrics->>k)::numeric) s from public.boss_snapshots, jsonb_object_keys(metrics) k
     where hospital_id = h and day >= m0 and day < d and k not in ('avg_wait_min','ipd_end') group by k) x;
  select coalesce(jsonb_object_agg(k, round(a, 1)), '{}') into avg7 from (
    select k, avg(nullif(metrics->>k, '')::numeric) a from public.boss_snapshots, jsonb_object_keys(metrics) k
     where hospital_id = h and day between d - 7 and d - 1 group by k) x;
  select coalesce(jsonb_agg(jsonb_build_object('day', day, 'm', metrics) order by day), '[]') into series
    from public.boss_snapshots where hospital_id = h and day between d - 30 and d - 1;
  select coalesce(jsonb_object_agg(metric, value), '{}') into tg from public.boss_targets where hospital_id = h;
  return jsonb_build_object('today', today,
    'yesterday', (select metrics from public.boss_snapshots where hospital_id = h and day = d - 1),
    'avg7', avg7, 'mtd', mtd, 'targets', tg, 'series', series, 'priorities', public.boss_priorities_rows(h),
    'month_days', extract(day from (m0 + interval '1 month - 1 day'))::int, 'day_of_month', extract(day from d)::int,
    'ipd_now', (select count(*) from public.admissions where hospital_id = h and status = 'admitted'),
    'beds_free', (select count(*) from public.beds where hospital_id = h and status = 'available'),
    'beds_total', (select count(*) from public.beds where hospital_id = h));
end $$;
revoke all on function public.boss_overview() from public, anon;
grant execute on function public.boss_overview() to authenticated;

-- ---------- AI handlers ----------
create or replace function public.agent_h_boss_priorities(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare p jsonb := public.boss_priorities_rows(h); nr int; na int;
begin
  select count(*) filter (where (x->>'level')::int = 1), count(*) filter (where (x->>'level')::int = 2) into nr, na from jsonb_array_elements(p) x;
  return jsonb_build_object('summary', case when jsonb_array_length(p) = 0 then 'Abhi koi zaroori kaam nahi ✓'
                                            else nr || ' turant (laal) · ' || na || ' aaj (peela) · ' || (jsonb_array_length(p) - nr - na) || ' dhyan mein rakhein' end,
                            'items', p, 'alert', nr > 0, 'alert_role', 'doctor');
end $$;

create or replace function public.agent_h_boss_numbers(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := coalesce(nullif(inp->>'day','')::date, (now() at time zone 'Asia/Kolkata')::date); m jsonb; y jsonb; m0 date := date_trunc('month', d)::date; mtd jsonb;
begin
  m := public.boss_day_metrics(h, d);
  y := public.boss_day_metrics(h, d - 1);
  select coalesce(jsonb_object_agg(k, s), '{}') into mtd from (
    select k, sum((metrics->>k)::numeric) s from public.boss_snapshots, jsonb_object_keys(metrics) k
     where hospital_id = h and day >= m0 and day < d and k not in ('avg_wait_min','ipd_end') group by k) x;
  return jsonb_build_object('summary', to_char(d, 'DD Mon') || ': ' || (m->>'opd') || ' OPD (kal ' || (y->>'opd') || ') · ₹' || to_char((m->>'collection')::numeric, 'FM99,99,990')
           || ' aaya (kal ₹' || to_char((y->>'collection')::numeric, 'FM99,99,990') || ') · ' || (m->>'admissions') || ' admit',
    'items', jsonb_build_object('din', m, 'kal', y, 'mahine_mein_ab_tak_kal_tak', mtd,
                                'targets', (select coalesce(jsonb_object_agg(metric, value), '{}') from public.boss_targets where hospital_id = h)), 'alert', false);
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('boss.priorities','boss','Abhi kya zaroori hai?','Poore hospital mein jo Doctor ka dhyan maangta hai — laal (turant), peela (aaj), baaki','check','low','{doctor,admin}','{}','{lab_orders,incidents,ops_tickets,agent_tasks,purchases,leave_requests,admissions,invoices,follow_ups,quality_checks}',0,'agent_h_boss_priorities', null),
 ('boss.numbers','boss','Hospital ke aankde','Kisi din ke OPD, admit, paisa, kharcha, pharmacy, lab — kal se tulna aur mahine mein ab tak','check','low','{doctor,admin}','{}','{encounters,admissions,payments,expenses,invoices,lab_orders}',0,'agent_h_boss_numbers',
   '{"type":"object","properties":{"day":{"type":"string","description":"YYYY-MM-DD (khaali = aaj)"}}}')
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{boss.priorities,boss.numbers,hr.salary_due,quality.numbers,lab.patient_reports,accountant.patient_balance}')) where agent_id = 'boss';
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{boss_snapshots,boss_targets}')) where id = 'boss';

-- ---------- Boss report: add priorities on top (morning / evening notification) ----------
create or replace function public.boss_after_report() returns trigger
language plpgsql security definer set search_path = public as $$
declare p jsonb; txt text;
begin
  if new.action = 'boss.daily_report' and new.status = 'done' and old.status is distinct from 'done' then
    p := public.boss_priorities_rows(new.hospital_id);
    if jsonb_array_length(p) > 0 then
      select string_agg(case (x->>'level')::int when 1 then '🔴 ' when 2 then '🟡 ' else '⚪ ' end || (x->>'title'), E'\n') into txt
        from (select x from jsonb_array_elements(p) x limit 8) s;
      perform public.agent_notify(new.hospital_id, 'doctor', case when exists (select 1 from jsonb_array_elements(p) x where (x->>'level')::int = 1) then 'critical' else 'warning' end,
        '🎯 Aaj ki zaroori baatein (' || jsonb_array_length(p) || ')', txt, 'agent:boss:prio:' || to_char(now() at time zone 'Asia/Kolkata', 'YYYYMMDDHH24'));
    end if;
  end if;
  return new;
end $$;
revoke all on function public.boss_after_report() from public, anon, authenticated;
drop trigger if exists boss_after_report on public.agent_tasks;
create trigger boss_after_report after update on public.agent_tasks for each row execute function public.boss_after_report();

-- ---------- weekly report (Monday) ----------
create or replace function public.boss_weekly_job() returns void
language plpgsql security definer set search_path = public as $$
declare h uuid; d date := (now() at time zone 'Asia/Kolkata')::date; tw jsonb; lw jsonb; txt text; k text;
  labels jsonb := '{"opd":"OPD","new_patients":"Naye patient","admissions":"Admit","collection":"Paisa aaya ₹","expenses":"Kharcha ₹","pharmacy_sale":"Pharmacy ₹","lab_tests":"Lab test","incidents":"Ghatna"}';
begin
  for h in select id from public.hospitals loop
    select coalesce(jsonb_object_agg(k2, s), '{}') into tw from (select k2, sum((metrics->>k2)::numeric) s from public.boss_snapshots, jsonb_object_keys(metrics) k2
      where hospital_id = h and day between d - 7 and d - 1 group by k2) a;
    select coalesce(jsonb_object_agg(k2, s), '{}') into lw from (select k2, sum((metrics->>k2)::numeric) s from public.boss_snapshots, jsonb_object_keys(metrics) k2
      where hospital_id = h and day between d - 14 and d - 8 group by k2) a;
    txt := '';
    for k in select jsonb_object_keys(labels) loop
      txt := txt || (labels->>k) || ': ' || to_char(coalesce((tw->>k)::numeric, 0), 'FM99,99,99,990') || ' (pichhla hafta ' || to_char(coalesce((lw->>k)::numeric, 0), 'FM99,99,99,990')
             || case when coalesce((lw->>k)::numeric, 0) > 0 then ', ' || case when (tw->>k)::numeric >= (lw->>k)::numeric then '▲' else '▼' end
                      || abs(round(100 * (coalesce((tw->>k)::numeric, 0) - (lw->>k)::numeric) / (lw->>k)::numeric)) || '%' else '' end || ')' || E'\n';
    end loop;
    perform public.agent_notify(h, 'doctor', 'info', '📊 Hafte ki report (' || to_char(d - 7, 'DD Mon') || ' – ' || to_char(d - 1, 'DD Mon') || ')', txt, 'agent:boss:week:' || d);
  end loop;
end $$;
revoke all on function public.boss_weekly_job() from public, anon, authenticated;

do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname in ('vatte_boss_snapshot','vatte_boss_weekly');
  perform cron.schedule('vatte_boss_snapshot', '20 18 * * *', $c$select public.boss_snapshot_job()$c$);   -- 11:50 PM IST
  perform cron.schedule('vatte_boss_weekly', '0 3 * * 1', $c$select public.boss_weekly_job()$c$);        -- Monday 8:30 AM IST
end $$;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;
