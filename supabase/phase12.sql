-- =========================================================
-- VATTE HOSPITAL OS — PHASE 12 (Lab AI)
-- • Test list with parameters (CBC, LFT, KFT…), units, normal ranges (male / female), critical limits
-- • Doctor / Sister write tests → sample collected (sample no.) → result entry → final report
-- • Server marks every value High / Low / CRITICAL itself; results are append-only (a change after the report needs a reason and is marked "amended")
-- • Critical value → Doctor + Sister notified at once; repeats every 30 min until someone acknowledges
-- • Lab orders change only through server functions; billing picks up lab tests automatically (Accounts → suggest_bill)
-- • Lab AI: today's lab work, a patient's recent reports, pending tests (read-only; it never orders tests or writes results)
-- =========================================================

-- ---------- test list ----------
alter table public.lab_tests add column if not exists category text not null default 'Other';
alter table public.lab_tests add column if not exists sample_type text not null default 'Blood';
alter table public.lab_tests add column if not exists tat_hours int not null default 24 check (tat_hours between 1 and 240);
alter table public.lab_tests add column if not exists ord int not null default 100;

create table if not exists public.lab_test_params (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  test_id uuid not null references public.lab_tests(id) on delete cascade,
  name text not null,
  unit text,
  kind text not null default 'number' check (kind in ('number','choice','text')),
  ref_low numeric, ref_high numeric,          -- male / everyone
  ref_low_f numeric, ref_high_f numeric,      -- female (if different)
  crit_low numeric, crit_high numeric,
  choices text[],                             -- for kind = choice
  abnormal_choices text[],                    -- choices that are abnormal (e.g. Positive)
  ref_text text,                              -- shown on report when no numbers
  ord int not null default 0,
  active boolean not null default true,
  unique (test_id, name)
);
alter table public.lab_test_params enable row level security;
drop policy if exists p_read on public.lab_test_params;
create policy p_read on public.lab_test_params for select to authenticated using (hospital_id = public.my_hospital() and public.my_role() <> 'pending');
revoke all on public.lab_test_params from anon;
revoke insert, update, delete on public.lab_test_params from authenticated;
grant select on public.lab_test_params to authenticated;

-- ---------- orders: extra fields; no direct writes from the app ----------
alter table public.lab_orders add column if not exists urgent boolean not null default false;
alter table public.lab_orders add column if not exists note text;
alter table public.lab_orders add column if not exists sample_no text;
alter table public.lab_orders add column if not exists collected_by uuid references auth.users(id);
alter table public.lab_orders add column if not exists amended_at timestamptz;
alter table public.lab_orders add column if not exists cancel_reason text;
alter table public.lab_orders add column if not exists critical_ack_at timestamptz;
alter table public.lab_orders add column if not exists critical_ack_by uuid references auth.users(id);
create index if not exists lab_orders_patient_idx on public.lab_orders(patient_id, ordered_at desc);
drop policy if exists p_insert on public.lab_orders; drop policy if exists p_update on public.lab_orders;
revoke insert, update, delete on public.lab_orders from authenticated;
drop policy if exists p_insert on public.lab_tests; drop policy if exists p_update on public.lab_tests;
revoke insert, update, delete on public.lab_tests from authenticated;

-- ---------- results (append-only; latest row per parameter is the current value) ----------
create table if not exists public.lab_results (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  order_id uuid not null references public.lab_orders(id),
  param_id uuid not null references public.lab_test_params(id),
  value_text text not null,
  value_num numeric,
  flag text not null check (flag in ('normal','low','high','crit_low','crit_high','abnormal','text')),
  reason text,                                  -- needed when changed after the report
  entered_by uuid not null references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists lab_results_order_idx on public.lab_results(order_id, param_id, created_at desc);
alter table public.lab_results enable row level security;
drop policy if exists p_read on public.lab_results;
create policy p_read on public.lab_results for select to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse,lab}'));
revoke all on public.lab_results from anon;
revoke insert, update, delete on public.lab_results from authenticated;
grant select on public.lab_results to authenticated;
drop trigger if exists no_change on public.lab_results;
create trigger no_change before update or delete on public.lab_results for each row execute function public.block_change();
drop trigger if exists audit on public.lab_results;
create trigger audit after insert on public.lab_results for each row execute function public.audit_row();

-- current value of every parameter of an order
create or replace view public.lab_current as
  select distinct on (r.order_id, r.param_id) r.*
    from public.lab_results r order by r.order_id, r.param_id, r.created_at desc;
alter view public.lab_current set (security_invoker = true);
grant select on public.lab_current to authenticated;

-- ---------- flag a value (server decides High / Low / Critical) ----------
create or replace function public.lab_flag(p public.lab_test_params, g text, v text, out num numeric, out flag text)
language plpgsql immutable set search_path = public as $$
declare lo numeric; hi numeric;
begin
  num := null;
  if p.kind = 'text' then flag := 'text'; return; end if;
  if p.kind = 'choice' then
    if not (v = any(coalesce(p.choices, '{}'))) then raise exception '%: in mein se chunein — %', p.name, array_to_string(p.choices, ' / '); end if;
    flag := case when v = any(coalesce(p.abnormal_choices, '{}')) then 'abnormal' else 'normal' end; return;
  end if;
  begin num := replace(trim(v), ',', '')::numeric; exception when others then raise exception '%: sirf number likhein (mila: %)', p.name, v; end;
  if num < 0 or num > 10000000 then raise exception '%: number galat lagta hai (%)', p.name, v; end if;
  lo := case when g = 'female' and p.ref_low_f is not null then p.ref_low_f else p.ref_low end;
  hi := case when g = 'female' and p.ref_high_f is not null then p.ref_high_f else p.ref_high end;
  flag := case when p.crit_low is not null and num < p.crit_low then 'crit_low'
               when p.crit_high is not null and num > p.crit_high then 'crit_high'
               when lo is not null and num < lo then 'low'
               when hi is not null and num > hi then 'high' else 'normal' end;
end $$;
revoke all on function public.lab_flag(public.lab_test_params, text, text) from public, anon;
grant execute on function public.lab_flag(public.lab_test_params, text, text) to authenticated;

-- ---------- write tests (order) ----------
create or replace function public.lab_order_tests(p_patient uuid, p_tests uuid[], p_urgent boolean default false, p_note text default null)
returns setof public.lab_orders
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); enc uuid; t uuid; o public.lab_orders; nm text;
begin
  if not public.has_role('{doctor,nurse,lab}') then raise exception 'Test sirf Doctor / Sister / Lab likh sakte hain'; end if;
  if not exists (select 1 from public.patients where id = p_patient and hospital_id = h) then raise exception 'Patient nahi mila'; end if;
  if coalesce(array_length(p_tests, 1), 0) = 0 then raise exception 'Kam se kam ek test chunein'; end if;
  if array_length(p_tests, 1) > 30 then raise exception 'Ek baar mein 30 test tak'; end if;
  select id into enc from public.encounters where patient_id = p_patient and hospital_id = h and status = 'open' order by started_at desc limit 1;
  foreach t in array p_tests loop
    select name into nm from public.lab_tests where id = t and hospital_id = h and active;
    if nm is null then raise exception 'Test list mein nahi / band hai'; end if;
    if exists (select 1 from public.lab_orders where patient_id = p_patient and test_id = t and status in ('ordered','sample_collected','processing')) then
      raise exception '% pehle se likha hua hai (report baaki)', nm; end if;
    insert into public.lab_orders(hospital_id, patient_id, encounter_id, test_id, status, ordered_by, urgent, note)
    values (h, p_patient, enc, t, 'ordered', auth.uid(), coalesce(p_urgent, false), nullif(trim(p_note), '')) returning * into o;
    return next o;
  end loop;
  if p_urgent then
    perform public.agent_notify(h, 'lab', 'warning', '🚨 URGENT test likha gaya', (select full_name from public.patients where id = p_patient) || ': ' || array_length(p_tests, 1) || ' test',
                                'agent:lab:urgent:' || p_patient || ':' || to_char(now(), 'YYYYMMDDHH24MI'));
  end if;
end $$;
revoke all on function public.lab_order_tests(uuid, uuid[], boolean, text) from public, anon;
grant execute on function public.lab_order_tests(uuid, uuid[], boolean, text) to authenticated;

-- ---------- sample collected (one sample no. for all tests taken together) ----------
create or replace function public.lab_collect(p_orders uuid[]) returns text
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); sn text; n int;
begin
  if not public.has_role('{doctor,nurse,lab}') then raise exception 'Permission nahi'; end if;
  if (select count(distinct patient_id) from public.lab_orders where id = any(p_orders) and hospital_id = h) <> 1 then
    raise exception 'Ek baar mein ek hi patient ke test chunein'; end if;
  sn := 'S' || to_char(now() at time zone 'Asia/Kolkata', 'YYMMDD') || '-' || lpad(public.next_number(h, 'sample_' || to_char(now() at time zone 'Asia/Kolkata', 'YYMMDD'))::text, 3, '0');
  update public.lab_orders set status = 'sample_collected', sample_no = sn, sample_collected_at = now(), collected_by = auth.uid()
   where id = any(p_orders) and hospital_id = h and status = 'ordered';
  get diagnostics n = row_count;
  if n = 0 then raise exception 'In test ka sample pehle hi liya ja chuka hai'; end if;
  return sn;
end $$;
revoke all on function public.lab_collect(uuid[]) from public, anon;
grant execute on function public.lab_collect(uuid[]) to authenticated;

-- ---------- enter results (draft or final report) ----------
-- p_results: [{ "param_id": "...", "value": "9.4" }]
create or replace function public.lab_save_results(p_order uuid, p_results jsonb, p_final boolean default false, p_reason text default null)
returns public.lab_orders
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); o public.lab_orders; g text; x jsonb; p public.lab_test_params; f record; cur text;
        was_reported boolean; missing text; summary text; crit boolean; pname text; tname text; nchanged int := 0;
begin
  if not public.has_role('{doctor,lab}') then raise exception 'Result sirf Lab / Doctor bhar sakte hain'; end if;
  select * into o from public.lab_orders where id = p_order and hospital_id = h for update;
  if o.id is null then raise exception 'Test nahi mila'; end if;
  if o.status = 'cancelled' then raise exception 'Ye test cancel hai'; end if;
  if o.status = 'ordered' then raise exception 'Pehle sample lene ka button dabayein'; end if;
  was_reported := o.status = 'reported';
  if was_reported and coalesce(trim(p_reason), '') = '' then raise exception 'Report ho chuki hai — badalne ka kaaran likhna zaroori hai'; end if;
  select gender, full_name into g, pname from public.patients where id = o.patient_id;
  select name into tname from public.lab_tests where id = o.test_id;
  if jsonb_typeof(coalesce(p_results, '[]')) <> 'array' then raise exception 'Result galat format'; end if;
  for x in select * from jsonb_array_elements(coalesce(p_results, '[]')) loop
    continue when coalesce(trim(x->>'value'), '') = '';
    select * into p from public.lab_test_params where id = (x->>'param_id')::uuid and test_id = o.test_id;
    if p.id is null then raise exception 'Ye parameter is test ka nahi hai'; end if;
    if length(x->>'value') > 500 then raise exception '%: bahut lamba', p.name; end if;
    select value_text into cur from public.lab_current where order_id = o.id and param_id = p.id;
    continue when cur is not distinct from trim(x->>'value');
    select * into f from public.lab_flag(p, g, trim(x->>'value'));
    insert into public.lab_results(hospital_id, order_id, param_id, value_text, value_num, flag, reason, entered_by)
    values (h, o.id, p.id, trim(x->>'value'), f.num, f.flag, case when was_reported then trim(p_reason) end, auth.uid());
    nchanged := nchanged + 1;
  end loop;
  if was_reported and nchanged = 0 then raise exception 'Kuch badla nahi'; end if;
  if p_final or was_reported then
    select string_agg(tp.name, ', ' order by tp.ord) into missing from public.lab_test_params tp
     where tp.test_id = o.test_id and tp.active and not exists (select 1 from public.lab_current c where c.order_id = o.id and c.param_id = tp.id);
    if missing is not null then raise exception 'Ye result baaki hain: %', missing; end if;
    select string_agg(tp.name || ' ' || c.value_text || coalesce(' ' || tp.unit, '') ||
             case c.flag when 'low' then ' (L)' when 'high' then ' (H)' when 'crit_low' then ' (CRITICAL L)' when 'crit_high' then ' (CRITICAL H)' when 'abnormal' then ' (!)' else '' end,
             '; ' order by tp.ord),
           bool_or(c.flag in ('crit_low','crit_high'))
      into summary, crit
      from public.lab_current c join public.lab_test_params tp on tp.id = c.param_id where c.order_id = o.id;
    update public.lab_orders set status = 'reported', result = summary, is_critical = crit,
           reported_by = case when was_reported then reported_by else auth.uid() end,
           reported_at = case when was_reported then reported_at else now() end,
           amended_at = case when was_reported then now() else amended_at end,
           critical_ack_at = case when crit and not coalesce(o.is_critical, false) then null else critical_ack_at end
     where id = o.id returning * into o;
    if crit then
      perform public.agent_notify(h, 'doctor', 'critical', '🚨 CRITICAL lab: ' || pname || ' — ' || tname, summary, 'agent:lab:crit:' || o.id || ':0');
      perform public.agent_notify(h, 'nurse', 'critical', '🚨 CRITICAL lab: ' || pname || ' — ' || tname, 'Doctor ko turant batayein. ' || summary, 'agent:lab:crit:' || o.id || ':0');
    end if;
  else
    update public.lab_orders set status = 'processing' where id = o.id and status = 'sample_collected' returning * into o;
    select * into o from public.lab_orders where id = p_order;
  end if;
  return o;
end $$;
revoke all on function public.lab_save_results(uuid, jsonb, boolean, text) from public, anon;
grant execute on function public.lab_save_results(uuid, jsonb, boolean, text) to authenticated;

-- ---------- critical seen by doctor / sister ----------
create or replace function public.lab_ack_critical(p_order uuid) returns public.lab_orders
language plpgsql security definer set search_path = public as $$
declare o public.lab_orders;
begin
  if not public.has_role('{doctor,nurse}') then raise exception 'Critical report Doctor / Sister hi "dekh liya" kar sakte hain'; end if;
  update public.lab_orders set critical_ack_at = now(), critical_ack_by = auth.uid()
   where id = p_order and hospital_id = public.my_hospital() and is_critical and critical_ack_at is null returning * into o;
  if o.id is null then raise exception 'Khula critical report nahi mila'; end if;
  return o;
end $$;
revoke all on function public.lab_ack_critical(uuid) from public, anon;
grant execute on function public.lab_ack_critical(uuid) to authenticated;

-- ---------- cancel a test (before report) ----------
create or replace function public.lab_cancel(p_order uuid, p_reason text) returns public.lab_orders
language plpgsql security definer set search_path = public as $$
declare o public.lab_orders;
begin
  if not public.has_role('{doctor,lab}') then raise exception 'Test cancel sirf Doctor / Lab kar sakte hain'; end if;
  if coalesce(trim(p_reason), '') = '' then raise exception 'Cancel ka kaaran likhein'; end if;
  if exists (select 1 from public.invoice_items ii join public.invoices i on i.id = ii.invoice_id where ii.lab_order_id = p_order and i.status <> 'cancelled') then
    raise exception 'Is test ka bill ban chuka hai — pehle Accounts se bill cancel karwayein'; end if;
  update public.lab_orders set status = 'cancelled', cancel_reason = trim(p_reason)
   where id = p_order and hospital_id = public.my_hospital() and status in ('ordered','sample_collected','processing') returning * into o;
  if o.id is null then raise exception 'Report ho chuka / pehle se cancel test cancel nahi hota'; end if;
  return o;
end $$;
revoke all on function public.lab_cancel(uuid, text) from public, anon;
grant execute on function public.lab_cancel(uuid, text) to authenticated;

-- ---------- test list editing (price, TAT, on/off; new single-value test) ----------
create or replace function public.lab_save_test(p_id uuid, p_name text, p_category text, p_sample text, p_price numeric, p_tat int, p_active boolean,
  p_unit text default null, p_ref_low numeric default null, p_ref_high numeric default null, p_crit_low numeric default null, p_crit_high numeric default null)
returns public.lab_tests
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); t public.lab_tests;
begin
  if not public.has_role('{doctor,admin,lab}') then raise exception 'Test list sirf Doctor / Admin / Lab badal sakte hain'; end if;
  if coalesce(trim(p_name), '') = '' then raise exception 'Test ka naam likhein'; end if;
  if coalesce(p_price, -1) < 0 or p_price > 100000 then raise exception 'Rate galat hai'; end if;
  if p_id is null then
    insert into public.lab_tests(hospital_id, name, price, category, sample_type, tat_hours, active, normal_range)
    values (h, trim(p_name), p_price, coalesce(nullif(trim(p_category), ''), 'Other'), coalesce(nullif(trim(p_sample), ''), 'Blood'), coalesce(p_tat, 24), true,
            case when p_ref_low is not null or p_ref_high is not null then coalesce(p_ref_low::text, '') || ' - ' || coalesce(p_ref_high::text, '') || coalesce(' ' || p_unit, '') end)
    returning * into t;
    insert into public.lab_test_params(hospital_id, test_id, name, unit, kind, ref_low, ref_high, crit_low, crit_high, ord)
    values (h, t.id, trim(p_name), nullif(trim(p_unit), ''), case when p_ref_low is null and p_ref_high is null then 'text' else 'number' end,
            p_ref_low, p_ref_high, p_crit_low, p_crit_high, 1);
  else
    update public.lab_tests set name = trim(p_name), price = p_price, category = coalesce(nullif(trim(p_category), ''), category),
           sample_type = coalesce(nullif(trim(p_sample), ''), sample_type), tat_hours = coalesce(p_tat, tat_hours), active = coalesce(p_active, active)
     where id = p_id and hospital_id = h returning * into t;
    if t.id is null then raise exception 'Test nahi mila'; end if;
  end if;
  return t;
exception when unique_violation then raise exception 'Is naam ka test pehle se hai';
end $$;
revoke all on function public.lab_save_test(uuid, text, text, text, numeric, int, boolean, text, numeric, numeric, numeric, numeric) from public, anon;
grant execute on function public.lab_save_test(uuid, text, text, text, numeric, int, boolean, text, numeric, numeric, numeric, numeric) to authenticated;

-- ---------- critical not acknowledged → remind doctor every 30 min ----------
create or replace function public.lab_critical_job() returns void
language plpgsql security definer set search_path = public as $$
declare o record;
begin
  for o in select l.id, l.hospital_id, l.result, p.full_name, t.name tname, floor(extract(epoch from now() - l.reported_at) / 1800)::int slot
             from public.lab_orders l join public.patients p on p.id = l.patient_id join public.lab_tests t on t.id = l.test_id
            where l.is_critical and l.critical_ack_at is null and l.status = 'reported'
              and l.reported_at < now() - interval '25 minutes' and l.reported_at > now() - interval '2 days' loop
    perform public.agent_notify(o.hospital_id, 'doctor', 'critical', '🚨 Abhi tak kisi ne nahi dekha — CRITICAL: ' || o.full_name || ' — ' || o.tname,
                                o.result, 'agent:lab:crit:' || o.id || ':' || o.slot);
  end loop;
end $$;
revoke all on function public.lab_critical_job() from public, anon, authenticated;
do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname = 'vatte_lab_critical';
  perform cron.schedule('vatte_lab_critical', '*/15 * * * *', $c$select public.lab_critical_job()$c$);
end $$;

-- ---------- Lab AI handlers (read-only) ----------
create or replace function public.agent_h_lab_pending(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; n int; crit int; late int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('patient', p.full_name, 'uhid', p.uhid, 'test', t.name, 'status', o.status, 'urgent', o.urgent,
           'ordered', to_char(o.ordered_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM'),
           'late', o.ordered_at < now() - make_interval(hours => t.tat_hours)) order by o.urgent desc, o.ordered_at), '[]'),
         count(*), count(*) filter (where o.ordered_at < now() - make_interval(hours => t.tat_hours))
    into items, n, late
    from public.lab_orders o join public.patients p on p.id = o.patient_id join public.lab_tests t on t.id = o.test_id
   where o.hospital_id = h and o.status in ('ordered','sample_collected','processing');
  select count(*) into crit from public.lab_orders where hospital_id = h and is_critical and critical_ack_at is null and status = 'reported';
  return jsonb_build_object('summary', n || ' test baaki · ' || late || ' samay se late · ' || crit || ' critical report bina dekhe',
                            'items', items, 'alert', late > 0 or crit > 0, 'alert_role', 'lab');
end $$;

create or replace function public.agent_h_lab_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; tot int; done int; waiting int; crit int; avgm int;
begin
  select count(*), count(*) filter (where status = 'reported'), count(*) filter (where status = 'ordered'),
         count(*) filter (where is_critical), round(avg(extract(epoch from reported_at - ordered_at) / 60) filter (where status = 'reported'))
    into tot, done, waiting, crit, avgm
    from public.lab_orders where hospital_id = h and (ordered_at at time zone 'Asia/Kolkata')::date = d and status <> 'cancelled';
  return jsonb_build_object('summary', 'Aaj ' || tot || ' test · ' || done || ' report ho gaye · ' || waiting || ' ka sample baaki · ' || crit || ' critical'
           || coalesce(' · avg ' || avgm || ' min mein report', ''),
    'items', jsonb_build_array(jsonb_build_object('total', tot, 'reported', done, 'sample_baaki', waiting, 'critical', crit, 'avg_minutes', avgm)), 'alert', false);
end $$;

create or replace function public.agent_h_lab_patient(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare pid uuid := (inp->>'patient_id')::uuid; nm text; items jsonb; n int;
begin
  select full_name into nm from public.patients where id = pid and hospital_id = h;
  if nm is null then raise exception 'Patient nahi mila'; end if;
  select coalesce(jsonb_agg(jsonb_build_object('test', t.name, 'status', o.status, 'date', to_char(coalesce(o.reported_at, o.ordered_at) at time zone 'Asia/Kolkata', 'DD Mon YY'),
           'result', o.result, 'critical', o.is_critical) order by o.ordered_at desc), '[]'), count(*)
    into items, n
    from (select * from public.lab_orders where patient_id = pid and hospital_id = h and status <> 'cancelled' order by ordered_at desc limit 15) o
    join public.lab_tests t on t.id = o.test_id;
  return jsonb_build_object('summary', nm || ': ' || n || ' test (aakhri 15)', 'items', items, 'alert', false);
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('lab.today','lab','Aaj ka lab kaam','Aaj kitne test, kitne report hue, kitne sample baaki, critical, report mein avg samay','check','low','{doctor,admin,lab}','{}','{lab_orders}',9,'agent_h_lab_today', null),
 ('lab.patient_reports','lab','Patient ki lab reports','Ek patient ke aakhri 15 test aur unke result','check','low','{doctor,admin,lab,nurse}','{}','{lab_orders,lab_tests,patients}',10,'agent_h_lab_patient',
   '{"type":"object","properties":{"patient_id":{"type":"string"}},"required":["patient_id"]}')
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;
update public.agent_actions set description = 'Baaki test (urgent pehle), samay (TAT) se late test, aur bina dekhe critical report' where id = 'lab.pending';
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{lab_results,lab_test_params}')) where id = 'lab';
update public.ai_chat_agents set roles = '{doctor,admin,lab}', tools = '{find_patient,lab.pending,lab.today,lab.patient_reports}' where agent_id = 'lab';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{lab.today}')) where agent_id = 'boss';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{lab.patient_reports}')) where agent_id = 'nurse';

-- ---------- starter test list (adult reference ranges; doctor / lab should check against own lab's machine & kit) ----------
do $$
declare h uuid; tid uuid; t record; p record;
begin
  for h in select id from public.hospitals loop
    for t in select * from (values
      ('CBC (Complete Blood Count)','Haematology','Blood (EDTA)',300,4,1),
      ('Haemoglobin (Hb)','Haematology','Blood (EDTA)',100,2,2),
      ('ESR','Haematology','Blood (EDTA)',100,4,3),
      ('Blood Group & Rh','Haematology','Blood (EDTA)',100,2,4),
      ('Blood Sugar Random (RBS)','Biochemistry','Blood (Fluoride)',60,1,10),
      ('Blood Sugar Fasting (FBS)','Biochemistry','Blood (Fluoride)',60,2,11),
      ('HbA1c','Biochemistry','Blood (EDTA)',450,24,12),
      ('Kidney Function (Urea, Creatinine)','Biochemistry','Blood (Plain)',350,6,13),
      ('Serum Electrolytes (Na, K)','Biochemistry','Blood (Plain)',400,6,14),
      ('Liver Function Test (LFT)','Biochemistry','Blood (Plain)',550,6,15),
      ('Lipid Profile','Biochemistry','Blood (Plain)',500,24,16),
      ('TSH','Hormones','Blood (Plain)',350,24,17),
      ('CRP','Serology','Blood (Plain)',350,6,20),
      ('Malaria Antigen (Rapid)','Serology','Blood (EDTA)',250,1,21),
      ('Dengue NS1 Antigen','Serology','Blood (Plain)',600,2,22),
      ('Widal Test','Serology','Blood (Plain)',200,4,23),
      ('HIV I & II (Rapid)','Serology','Blood (Plain)',300,1,24),
      ('HBsAg (Rapid)','Serology','Blood (Plain)',250,1,25),
      ('Urine Routine','Urine','Urine',150,2,30),
      ('Urine Pregnancy Test (UPT)','Urine','Urine',100,1,31)
    ) as x(name, cat, sample, price, tat, ord) loop
      insert into public.lab_tests(hospital_id, name, price, category, sample_type, tat_hours, ord)
      values (h, t.name, t.price, t.cat, t.sample, t.tat, t.ord) on conflict (hospital_id, name) do nothing;
      select id into tid from public.lab_tests where hospital_id = h and name = t.name;
      for p in select * from (values
        -- test, ord, name, unit, kind, lo, hi, lo_f, hi_f, crit_lo, crit_hi, choices, abnormal, ref_text
        ('CBC (Complete Blood Count)',1,'Haemoglobin','g/dL','number',13.0,17.0,12.0,15.5,7.0,20.0,null::text[],null::text[],null),
        ('CBC (Complete Blood Count)',2,'Total WBC count','x10³/µL','number',4.0,11.0,null,null,2.0,30.0,null,null,null),
        ('CBC (Complete Blood Count)',3,'Neutrophils','%','number',40,75,null,null,null,null,null,null,null),
        ('CBC (Complete Blood Count)',4,'Lymphocytes','%','number',20,45,null,null,null,null,null,null,null),
        ('CBC (Complete Blood Count)',5,'Eosinophils','%','number',1,6,null,null,null,null,null,null,null),
        ('CBC (Complete Blood Count)',6,'Platelet count','x10³/µL','number',150,410,null,null,20,1000,null,null,null),
        ('CBC (Complete Blood Count)',7,'RBC count','x10⁶/µL','number',4.5,5.5,3.8,4.8,null,null,null,null,null),
        ('CBC (Complete Blood Count)',8,'PCV / Haematocrit','%','number',40,50,36,46,null,null,null,null,null),
        ('Haemoglobin (Hb)',1,'Haemoglobin','g/dL','number',13.0,17.0,12.0,15.5,7.0,20.0,null,null,null),
        ('ESR',1,'ESR','mm/1st hr','number',0,15,0,20,null,null,null,null,null),
        ('Blood Group & Rh',1,'Blood group',null,'choice',null,null,null,null,null,null,array['A','B','AB','O'],null,null),
        ('Blood Group & Rh',2,'Rh factor',null,'choice',null,null,null,null,null,null,array['Positive','Negative'],null,null),
        ('Blood Sugar Random (RBS)',1,'Glucose (random)','mg/dL','number',70,140,null,null,50,400,null,null,null),
        ('Blood Sugar Fasting (FBS)',1,'Glucose (fasting)','mg/dL','number',70,100,null,null,50,400,null,null,null),
        ('HbA1c',1,'HbA1c','%','number',4.0,5.6,null,null,null,null,null,null,'<5.7 normal · 5.7–6.4 prediabetes · ≥6.5 diabetes'),
        ('Kidney Function (Urea, Creatinine)',1,'Blood urea','mg/dL','number',15,40,null,null,null,null,null,null,null),
        ('Kidney Function (Urea, Creatinine)',2,'Serum creatinine','mg/dL','number',0.7,1.3,0.5,1.1,null,null,null,null,null),
        ('Serum Electrolytes (Na, K)',1,'Sodium (Na)','mmol/L','number',135,145,null,null,120,160,null,null,null),
        ('Serum Electrolytes (Na, K)',2,'Potassium (K)','mmol/L','number',3.5,5.1,null,null,2.8,6.2,null,null,null),
        ('Liver Function Test (LFT)',1,'Bilirubin total','mg/dL','number',0.2,1.2,null,null,null,null,null,null,null),
        ('Liver Function Test (LFT)',2,'Bilirubin direct','mg/dL','number',0.0,0.3,null,null,null,null,null,null,null),
        ('Liver Function Test (LFT)',3,'SGOT (AST)','U/L','number',0,40,null,null,null,null,null,null,null),
        ('Liver Function Test (LFT)',4,'SGPT (ALT)','U/L','number',0,41,null,null,null,null,null,null,null),
        ('Liver Function Test (LFT)',5,'Alkaline phosphatase','U/L','number',40,130,null,null,null,null,null,null,null),
        ('Liver Function Test (LFT)',6,'Total protein','g/dL','number',6.0,8.3,null,null,null,null,null,null,null),
        ('Liver Function Test (LFT)',7,'Albumin','g/dL','number',3.5,5.2,null,null,null,null,null,null,null),
        ('Lipid Profile',1,'Total cholesterol','mg/dL','number',0,200,null,null,null,null,null,null,null),
        ('Lipid Profile',2,'Triglycerides','mg/dL','number',0,150,null,null,null,null,null,null,null),
        ('Lipid Profile',3,'HDL cholesterol','mg/dL','number',40,null,50,null,null,null,null,null,null),
        ('Lipid Profile',4,'LDL cholesterol','mg/dL','number',0,100,null,null,null,null,null,null,null),
        ('TSH',1,'TSH','µIU/mL','number',0.4,4.5,null,null,null,null,null,null,null),
        ('CRP',1,'CRP','mg/L','number',0,6,null,null,null,null,null,null,null),
        ('Malaria Antigen (Rapid)',1,'Malaria (P. vivax / P. falciparum)',null,'choice',null,null,null,null,null,null,array['Negative','P. vivax positive','P. falciparum positive','Mixed positive'],array['P. vivax positive','P. falciparum positive','Mixed positive'],null),
        ('Dengue NS1 Antigen',1,'Dengue NS1',null,'choice',null,null,null,null,null,null,array['Negative','Positive'],array['Positive'],null),
        ('Widal Test',1,'Widal (titres)',null,'text',null,null,null,null,null,null,null,null,'Titre ≥1:160 significant (single test)'),
        ('HIV I & II (Rapid)',1,'HIV I & II',null,'choice',null,null,null,null,null,null,array['Non-reactive','Reactive'],array['Reactive'],null),
        ('HBsAg (Rapid)',1,'HBsAg',null,'choice',null,null,null,null,null,null,array['Non-reactive','Reactive'],array['Reactive'],null),
        ('Urine Routine',1,'Colour / appearance',null,'text',null,null,null,null,null,null,null,null,'Pale yellow, clear'),
        ('Urine Routine',2,'Albumin (protein)',null,'choice',null,null,null,null,null,null,array['Nil','Trace','+','++','+++'],array['+','++','+++'],null),
        ('Urine Routine',3,'Sugar',null,'choice',null,null,null,null,null,null,array['Nil','Trace','+','++','+++'],array['+','++','+++'],null),
        ('Urine Routine',4,'Pus cells','/hpf','text',null,null,null,null,null,null,null,null,'0–5 /hpf'),
        ('Urine Routine',5,'RBCs','/hpf','text',null,null,null,null,null,null,null,null,'Nil'),
        ('Urine Pregnancy Test (UPT)',1,'Urine hCG',null,'choice',null,null,null,null,null,null,array['Negative','Positive'],null,null)
      ) as y(test, ord, name, unit, kind, lo, hi, lo_f, hi_f, clo, chi, ch, ab, rt) where y.test = t.name loop
        insert into public.lab_test_params(hospital_id, test_id, name, unit, kind, ref_low, ref_high, ref_low_f, ref_high_f, crit_low, crit_high, choices, abnormal_choices, ref_text, ord)
        values (h, tid, p.name, p.unit, p.kind, p.lo, p.hi, p.lo_f, p.hi_f, p.clo, p.chi, p.ch, p.ab, p.rt, p.ord) on conflict (test_id, name) do nothing;
      end loop;
    end loop;
  end loop;
end $$;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;

-- (applied as migration "phase12b_lab_result_order") latest value = highest seq, so two changes in the same second stay in order
alter table public.lab_results add column if not exists seq bigint generated always as identity;
create or replace view public.lab_current as
  select distinct on (r.order_id, r.param_id) r.*
    from public.lab_results r order by r.order_id, r.param_id, r.seq desc;
alter view public.lab_current set (security_invoker = true);
grant select on public.lab_current to authenticated;
