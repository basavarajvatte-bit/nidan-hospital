-- =========================================================
-- VATTE HOSPITAL OS — PHASE 7 (AI Agent Engine)
-- Every agent has a fixed list of ACTIONS. Each action has a risk level:
--   low        -> runs at once (read-only checks / reports)
--   controlled -> waits for doctor/admin approval, then runs (changes a record)
--   high       -> waits for the DOCTOR's approval, then runs
-- Agents only touch their own allowed tables, every step is logged (agent_logs, tamper-proof),
-- the Boss agent runs all checks and reports to the doctor. Scheduled by pg_cron.
-- Agents never diagnose or prescribe. Run after phase1-6.
-- =========================================================

create extension if not exists pg_cron;

-- ---------- registry additions ----------
alter table public.agents add column if not exists icon text;
alter table public.agents add column if not exists last_run_at timestamptz;
alter table public.agents add column if not exists last_summary text;

create table if not exists public.agent_actions (
  id text primary key,                         -- e.g. 'nurse.overdue_vitals'
  agent_id text not null references public.agents(id),
  title text not null,                         -- shown on the button (Hinglish)
  description text not null,
  kind text not null check (kind in ('check','act')),
  risk text not null check (risk in ('low','controlled','high')),
  requester_roles text[] not null,             -- who may ask the agent to do it
  approver_roles text[] not null default '{}', -- who may approve (controlled / high)
  tables text[] not null,                      -- tables the action reads / writes
  ord int not null default 0
);
alter table public.agent_actions enable row level security;
drop policy if exists p_read on public.agent_actions;
create policy p_read on public.agent_actions for select to authenticated using (true);
revoke all on public.agent_actions from anon;
revoke insert, update, delete on public.agent_actions from authenticated;
grant select on public.agent_actions to authenticated;

alter table public.agent_tasks add column if not exists action text references public.agent_actions(id);
alter table public.agent_tasks add column if not exists decision_note text;
alter table public.agent_tasks add column if not exists decided_at timestamptz;
alter table public.agent_tasks add column if not exists summary text;
create index if not exists agent_tasks_agent_idx on public.agent_tasks(hospital_id, agent_id, created_at desc);

-- tasks are created only through agent_submit() (checks role + risk); no direct inserts from the app
drop policy if exists p_insert on public.agent_tasks;
revoke insert on public.agent_tasks from authenticated;
-- approvers must see what is waiting for them
drop policy if exists p_read on public.agent_tasks;
create policy p_read on public.agent_tasks for select to authenticated
  using (hospital_id = public.my_hospital()
         and (requested_by = auth.uid() or public.has_role('{doctor,admin}')));

update public.agents set icon = x.icon from (values
  ('boss','🤖'),('nurse','🩺'),('appointment','📅'),('reception','🧾'),('accountant','💰'),('pharmacy','💊'),
  ('lab','🧪'),('followup','📞'),('hr','👥'),('operations','🛏️'),('procurement','📦'),('records','🗂️'),('quality','✅')
) as x(id, icon) where agents.id = x.id;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord) values
 ('nurse.overdue_vitals','nurse','Kis patient ke vitals baaki hain?','Admit patients jinke vitals pichhle 6 ghante mein nahi liye gaye','check','low','{doctor,admin,nurse}','{}','{admissions,vitals,patients,beds}',1),
 ('reception.today','reception','Aaj ka reception hisaab','Aaj naye patient, OPD khule case, IPD admit','check','low','{doctor,admin,receptionist}','{}','{patients,encounters,admissions}',2),
 ('appointment.today','appointment','Aaj ki appointments','Aaj ki appointments status ke hisaab se','check','low','{doctor,admin,receptionist}','{}','{appointments}',3),
 ('operations.beds','operations','Bed ki sthiti','Kitne bed khali / bhare / safai / band','check','low','{doctor,admin,nurse,receptionist}','{}','{beds,rooms}',4),
 ('pharmacy.stock','pharmacy','Expiry aur kam stock','60 din mein expire hone wale batch aur reorder level se kam dawaiyan','check','low','{doctor,admin,pharmacist}','{}','{medicines,medicine_batches}',5),
 ('lab.pending','lab','Lab ke baaki kaam','24 ghante se purane bina report ke test, aur critical report','check','low','{doctor,admin,lab}','{}','{lab_orders,lab_tests,patients}',6),
 ('accountant.dues','accountant','Baaki paisa (unpaid bills)','Unpaid / partial bills ki ginti aur rakam','check','low','{doctor,admin,accountant}','{}','{invoices}',7),
 ('followup.due','followup','Aaj ke follow-up','Aaj ya pehle ke baaki follow-up','check','low','{doctor,admin,receptionist,nurse}','{}','{follow_ups,patients}',8),
 ('boss.daily_report','boss','Poore hospital ki report','Boss AI sab agents se check karwata hai aur doctor ko report deta hai','check','low','{doctor,admin}','{}','{agent_tasks,agent_logs,notifications}',0),
 ('followup.schedule','followup','Follow-up date lagao','Patient ka follow-up record banana (approval ke baad)','act','controlled','{doctor,admin,receptionist,nurse}','{doctor,admin}','{follow_ups}',20),
 ('operations.bed_status','operations','Bed ko safai / band / khali karo','Bed ka status badalna (bhare bed ko nahi) — approval ke baad','act','controlled','{doctor,admin,nurse,receptionist}','{doctor,admin}','{beds}',21),
 ('pharmacy.writeoff_expired','pharmacy','Expired batch ko zero karo','Expire ho chuke batch ka stock 0 karna (sirf doctor ki approval se)','act','high','{doctor,admin,pharmacist}','{doctor}','{medicine_batches}',22)
on conflict (id) do update set agent_id=excluded.agent_id, title=excluded.title, description=excluded.description, kind=excluded.kind,
  risk=excluded.risk, requester_roles=excluded.requester_roles, approver_roles=excluded.approver_roles, tables=excluded.tables, ord=excluded.ord;

-- every action may only use tables its agent is allowed to (boss uses the task tables)
update public.agents set allowed_tables = allowed_tables || '{beds,rooms}' where id='operations' and not ('rooms' = any(allowed_tables));
update public.agents set allowed_tables = allowed_tables || '{admissions,beds,patients}' where id='nurse' and not ('beds' = any(allowed_tables));
update public.agents set allowed_tables = allowed_tables || '{lab_tests,patients}' where id='lab' and not ('patients' = any(allowed_tables));
do $$
declare bad text;
begin
  select string_agg(a.id, ', ') into bad from public.agent_actions a join public.agents g on g.id = a.agent_id
   where not (a.tables <@ g.allowed_tables);
  if bad is not null then raise exception 'Agent action uses a table its agent may not touch: %', bad; end if;
end $$;
update public.agents set status = 'active' where id in (select distinct agent_id from public.agent_actions);

-- ---------- helpers ----------
create or replace function public.agent_log(h uuid, t uuid, a text, lvl text, msg text) returns void
language sql security definer set search_path = public as $$
  insert into public.agent_logs(hospital_id, task_id, agent_id, level, message) values (h, t, a, lvl, msg);
$$;

-- notification without spamming: same title from same agent not repeated within 6 hours
create or replace function public.agent_notify(h uuid, role text, lvl text, ttl text, bdy text, src text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if exists (select 1 from public.notifications where hospital_id = h and source = src and title = ttl
             and coalesce(target_role,'') = coalesce(role,'') and created_at > now() - interval '6 hours') then return; end if;
  insert into public.notifications(hospital_id, target_role, level, title, body, source) values (h, role, lvl, ttl, bdy, src);
end $$;

-- ---------- CHECK handlers (read-only; return {summary, items, alert}) ----------
create or replace function public.agent_h_overdue_vitals(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare hrs int := coalesce((inp->>'hours')::int, 6); items jsonb; n int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('patient', p.full_name, 'uhid', p.uhid, 'bed', b.label,
           'last', to_char(lv.at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM')) order by lv.at nulls first), '[]'), count(*)
    into items, n
    from public.admissions a join public.patients p on p.id = a.patient_id
    left join public.beds b on b.id = a.bed_id
    left join lateral (select max(v.recorded_at) at from public.vitals v where v.patient_id = a.patient_id) lv on true
   where a.hospital_id = h and a.status = 'admitted' and (lv.at is null or lv.at < now() - make_interval(hours => hrs));
  return jsonb_build_object('summary', case when n = 0 then 'Sab admit patients ke vitals time par hain ✓'
                                            else n || ' patient ke vitals ' || hrs || ' ghante se nahi liye' end,
                            'items', items, 'alert', n > 0, 'alert_role', 'nurse');
end $$;

create or replace function public.agent_h_reception_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; np int; opd int; ipd int;
begin
  select count(*) into np from public.patients where hospital_id = h and (created_at at time zone 'Asia/Kolkata')::date = d;
  select count(*) into opd from public.encounters where hospital_id = h and kind = 'opd' and status = 'open';
  select count(*) into ipd from public.admissions where hospital_id = h and status = 'admitted';
  return jsonb_build_object('summary', 'Aaj ' || np || ' naye patient · OPD khule ' || opd || ' · IPD admit ' || ipd,
                            'items', jsonb_build_array(jsonb_build_object('new_patients', np, 'opd_open', opd, 'ipd_admitted', ipd)), 'alert', false);
end $$;

create or replace function public.agent_h_appointments_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; items jsonb; n int;
begin
  select coalesce(jsonb_object_agg(status, c), '{}'), coalesce(sum(c), 0) into items, n from (
    select status, count(*) c from public.appointments
     where hospital_id = h and (starts_at at time zone 'Asia/Kolkata')::date = d group by status) s;
  return jsonb_build_object('summary', 'Aaj ' || n || ' appointments', 'items', jsonb_build_array(items), 'alert', false);
end $$;

create or replace function public.agent_h_beds(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; total int; free int;
begin
  select coalesce(jsonb_object_agg(status, c), '{}'), coalesce(sum(c), 0), coalesce(sum(c) filter (where status = 'available'), 0)
    into items, total, free from (select status, count(*) c from public.beds where hospital_id = h group by status) s;
  return jsonb_build_object('summary', case when total = 0 then 'Abhi koi bed nahi bana (Reception → Rooms & Beds)'
                                            else free || ' / ' || total || ' bed khali' end,
                            'items', jsonb_build_array(items), 'alert', total > 0 and free = 0, 'alert_role', 'doctor');
end $$;

create or replace function public.agent_h_pharmacy_stock(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare days int := coalesce((inp->>'days')::int, 60); exp jsonb; low jsonb; ne int; nl int; nx int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('medicine', m.name, 'batch', b.batch_no, 'expiry', b.expiry_date, 'qty', b.quantity,
           'expired', b.expiry_date < current_date, 'batch_id', b.id) order by b.expiry_date), '[]'), count(*),
         count(*) filter (where b.expiry_date < current_date)
    into exp, ne, nx
    from public.medicine_batches b join public.medicines m on m.id = b.medicine_id
   where b.hospital_id = h and b.quantity > 0 and b.expiry_date <= current_date + days;
  select coalesce(jsonb_agg(jsonb_build_object('medicine', name, 'stock', stock, 'reorder_level', reorder_level) order by name), '[]'), count(*)
    into low, nl
    from (select m.name, m.reorder_level, coalesce(sum(b.quantity) filter (where b.expiry_date >= current_date), 0) stock
            from public.medicines m left join public.medicine_batches b on b.medicine_id = m.id
           where m.hospital_id = h and coalesce(m.active, true) and coalesce(m.reorder_level, 0) > 0 group by m.id) s
   where stock < reorder_level;
  return jsonb_build_object('summary', ne || ' batch ' || days || ' din mein expire (' || nx || ' expire ho chuke) · ' || nl || ' dawa kam stock',
                            'items', jsonb_build_object('expiring', exp, 'low_stock', low), 'alert', nx > 0 or nl > 0, 'alert_role', 'pharmacist');
end $$;

create or replace function public.agent_h_lab_pending(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; n int; crit int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('patient', p.full_name, 'test', t.name, 'status', o.status,
           'ordered', to_char(o.ordered_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM')) order by o.ordered_at), '[]'), count(*)
    into items, n
    from public.lab_orders o join public.patients p on p.id = o.patient_id join public.lab_tests t on t.id = o.test_id
   where o.hospital_id = h and o.status in ('ordered','sample_collected','processing') and o.ordered_at < now() - interval '24 hours';
  select count(*) into crit from public.lab_orders where hospital_id = h and is_critical and reported_at > now() - interval '24 hours';
  return jsonb_build_object('summary', n || ' test 24 ghante se baaki · ' || crit || ' critical report (24 ghante)',
                            'items', items, 'alert', n > 0 or crit > 0, 'alert_role', 'lab');
end $$;

create or replace function public.agent_h_dues(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare n int; amt numeric;
begin
  select count(*), coalesce(sum(total - discount), 0) into n, amt from public.invoices
   where hospital_id = h and status in ('unpaid','partial');
  return jsonb_build_object('summary', n || ' bill baaki · kul ₹' || to_char(amt, 'FM99,99,99,990') || ' (partial bill ki poori rakam shaamil)',
                            'items', jsonb_build_array(jsonb_build_object('bills', n, 'amount', amt)), 'alert', false);
end $$;

create or replace function public.agent_h_followups(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; items jsonb; n int; late int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('patient', p.full_name, 'uhid', p.uhid, 'phone', p.phone, 'due_on', f.due_on, 'reason', f.reason)
           order by f.due_on), '[]'), count(*), count(*) filter (where f.due_on < d)
    into items, n, late
    from public.follow_ups f join public.patients p on p.id = f.patient_id
   where f.hospital_id = h and f.status = 'pending' and f.due_on <= d;
  return jsonb_build_object('summary', n || ' follow-up aaj tak baaki (' || late || ' late)', 'items', items,
                            'alert', late > 0, 'alert_role', 'receptionist');
end $$;

-- ---------- ACT handlers (change records; only run after approval) ----------
create or replace function public.agent_h_followup_schedule(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare pid uuid := (inp->>'patient_id')::uuid; due date := (inp->>'due_on')::date; fid uuid; pname text;
begin
  select full_name into pname from public.patients where id = pid and hospital_id = h;
  if pname is null then raise exception 'Patient nahi mila'; end if;
  if due is null or due < current_date then raise exception 'Follow-up ki date aaj ya aage ki honi chahiye'; end if;
  insert into public.follow_ups(hospital_id, patient_id, due_on, reason, created_by)
  values (h, pid, due, nullif(inp->>'reason',''), coalesce(req, auth.uid())) returning id into fid;
  return jsonb_build_object('summary', pname || ' ka follow-up ' || to_char(due, 'DD Mon YYYY') || ' ko laga diya ✓',
                            'items', jsonb_build_array(jsonb_build_object('follow_up_id', fid)), 'alert', false);
end $$;

create or replace function public.agent_h_bed_status(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare bid uuid := (inp->>'bed_id')::uuid; st text := inp->>'status'; cur text; lbl text;
begin
  if st not in ('available','cleaning','blocked') then raise exception 'Status sirf available / cleaning / blocked ho sakta hai'; end if;
  select status, label into cur, lbl from public.beds where id = bid and hospital_id = h for update;
  if cur is null then raise exception 'Bed nahi mila'; end if;
  if cur = 'occupied' or exists (select 1 from public.admissions where bed_id = bid and status = 'admitted') then
    raise exception 'Bed % par patient admit hai — pehle discharge / transfer karein', lbl; end if;
  update public.beds set status = st where id = bid;
  return jsonb_build_object('summary', 'Bed ' || lbl || ': ' || cur || ' → ' || st || ' ✓', 'items', '[]'::jsonb, 'alert', false);
end $$;

create or replace function public.agent_h_writeoff_expired(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare bid uuid := (inp->>'batch_id')::uuid; ex date; q int; nm text; bn text;
begin
  select b.expiry_date, b.quantity, m.name, b.batch_no into ex, q, nm, bn
    from public.medicine_batches b join public.medicines m on m.id = b.medicine_id where b.id = bid and b.hospital_id = h for update;
  if ex is null then raise exception 'Batch nahi mila'; end if;
  if ex >= current_date then raise exception 'Ye batch abhi expire nahi hua (expiry %)', ex; end if;
  update public.medicine_batches set quantity = 0 where id = bid;
  return jsonb_build_object('summary', nm || ' batch ' || bn || ': ' || q || ' expired stock zero kiya ✓', 'items', '[]'::jsonb, 'alert', false);
end $$;

-- ---------- engine: run one task ----------
create or replace function public.agent_exec(p_task uuid) returns public.agent_tasks
language plpgsql security definer set search_path = public as $$
declare t public.agent_tasks; act public.agent_actions; res jsonb; sub jsonb := '[]'; a record; st public.agent_tasks; nalerts int := 0;
begin
  select * into t from public.agent_tasks where id = p_task for update;
  if t.status not in ('queued','approved') then return t; end if;
  select * into act from public.agent_actions where id = t.action;
  update public.agent_tasks set status = 'running', attempts = attempts + 1, updated_at = now() where id = t.id;
  perform public.agent_log(t.hospital_id, t.id, t.agent_id, 'info', 'Shuru: ' || act.title);
  begin
    res := case t.action
      when 'nurse.overdue_vitals'      then public.agent_h_overdue_vitals(t.hospital_id, t.input)
      when 'reception.today'           then public.agent_h_reception_today(t.hospital_id, t.input)
      when 'appointment.today'         then public.agent_h_appointments_today(t.hospital_id, t.input)
      when 'operations.beds'           then public.agent_h_beds(t.hospital_id, t.input)
      when 'pharmacy.stock'            then public.agent_h_pharmacy_stock(t.hospital_id, t.input)
      when 'lab.pending'               then public.agent_h_lab_pending(t.hospital_id, t.input)
      when 'accountant.dues'           then public.agent_h_dues(t.hospital_id, t.input)
      when 'followup.due'              then public.agent_h_followups(t.hospital_id, t.input)
      when 'followup.schedule'         then public.agent_h_followup_schedule(t.hospital_id, t.input, t.requested_by)
      when 'operations.bed_status'     then public.agent_h_bed_status(t.hospital_id, t.input, t.requested_by)
      when 'pharmacy.writeoff_expired' then public.agent_h_writeoff_expired(t.hospital_id, t.input, t.requested_by)
      else null end;

    if t.action = 'boss.daily_report' then
      -- Boss asks every department agent to run its check, as sub-tasks
      for a in select * from public.agent_actions where kind = 'check' and agent_id <> 'boss' order by ord loop
        insert into public.agent_tasks(hospital_id, agent_id, action, requested_by, parent_task_id, input, risk, status)
        values (t.hospital_id, a.agent_id, a.id, t.requested_by, t.id, '{}', 'low', 'queued') returning * into st;
        st := public.agent_exec(st.id);
        sub := sub || jsonb_build_object('agent', a.agent_id, 'title', a.title, 'status', st.status,
                                         'summary', coalesce(st.summary, st.error), 'alert', coalesce((st.result->>'alert')::boolean, false));
        if coalesce((st.result->>'alert')::boolean, false) or st.status = 'failed' then nalerts := nalerts + 1; end if;
      end loop;
      res := jsonb_build_object('summary', case when nalerts = 0 then 'Sab theek ✓ — ' || jsonb_array_length(sub) || ' agents ne check kiya'
                                                else nalerts || ' jagah dhyan dena hai — ' || jsonb_array_length(sub) || ' agents ne check kiya' end,
                                'items', sub, 'alert', nalerts > 0, 'alert_role', 'doctor');
      perform public.agent_notify(t.hospital_id, 'doctor', case when nalerts > 0 then 'warning' else 'info' end,
        '🤖 Boss AI report: ' || (res->>'summary'),
        (select string_agg(case when (x->>'alert')::boolean then '⚠️ ' else '✓ ' end || (x->>'title') || ': ' || (x->>'summary'), E'\n')
           from jsonb_array_elements(sub) x),
        'agent:boss:' || to_char(now() at time zone 'Asia/Kolkata', 'YYYYMMDDHH24MI'));
    end if;

    if res is null then raise exception 'Is action ka handler nahi bana: %', t.action; end if;
    if coalesce((res->>'alert')::boolean, false) and t.agent_id <> 'boss' and t.parent_task_id is null then
      perform public.agent_notify(t.hospital_id, res->>'alert_role', 'warning', act.title || ': ' || (res->>'summary'), null, 'agent:' || t.agent_id);
    end if;
    update public.agent_tasks set status = 'done', result = res, summary = res->>'summary', error = null, updated_at = now()
     where id = t.id returning * into t;
    update public.agents set last_run_at = now(), last_summary = res->>'summary', status = 'active' where id = t.agent_id;
    perform public.agent_log(t.hospital_id, t.id, t.agent_id, case when (res->>'alert')::boolean then 'warning' else 'info' end, 'Ho gaya: ' || (res->>'summary'));
  exception when others then
    update public.agent_tasks set status = 'failed', error = sqlerrm, summary = null, updated_at = now() where id = p_task returning * into t;
    perform public.agent_log(t.hospital_id, t.id, t.agent_id, 'error', 'Fail: ' || sqlerrm);
  end;
  return t;
end $$;
revoke all on function public.agent_exec(uuid) from public, anon, authenticated;

-- ---------- app entry points ----------
create or replace function public.agent_submit(p_action text, p_input jsonb default '{}') returns public.agent_tasks
language plpgsql security definer set search_path = public as $$
declare act public.agent_actions; t public.agent_tasks; h uuid := public.my_hospital(); r text;
begin
  select * into act from public.agent_actions where id = p_action;
  if act.id is null then raise exception 'Ye kaam kisi agent ke paas nahi hai: %', p_action; end if;
  if h is null or not public.has_role(act.requester_roles) then
    raise exception 'Aapka role is kaam ko chalane ki permission nahi rakhta'; end if;
  if (select status from public.agents where id = act.agent_id) = 'paused' then raise exception 'Ye agent abhi band (paused) hai'; end if;
  insert into public.agent_tasks(hospital_id, agent_id, action, requested_by, input, risk, status)
  values (h, act.agent_id, act.id, auth.uid(), coalesce(p_input, '{}'), act.risk,
          case when act.risk = 'low' then 'queued' else 'waiting_approval' end) returning * into t;
  perform public.agent_log(h, t.id, t.agent_id, 'info', 'Kaam mila: ' || act.title ||
    case when act.risk <> 'low' then ' (approval ka intezaar — ' || act.risk || ')' else '' end);
  if act.risk = 'low' then
    return public.agent_exec(t.id);
  end if;
  for r in select unnest(act.approver_roles) loop
    perform public.agent_notify(h, r, 'warning', '✋ Approval chahiye: ' || act.title,
      'AI Agents → Approval mein dekhein. Maanga: ' || coalesce((select full_name from public.profiles where id = auth.uid()), 'staff'),
      'agent:approval:' || t.id);
  end loop;
  return t;
end $$;
revoke all on function public.agent_submit(text, jsonb) from public, anon;
grant execute on function public.agent_submit(text, jsonb) to authenticated;

create or replace function public.agent_decide(p_task uuid, p_approve boolean, p_note text default null) returns public.agent_tasks
language plpgsql security definer set search_path = public as $$
declare t public.agent_tasks; act public.agent_actions;
begin
  select * into t from public.agent_tasks where id = p_task and hospital_id = public.my_hospital() for update;
  if t.id is null then raise exception 'Task nahi mila'; end if;
  if t.status <> 'waiting_approval' then raise exception 'Is task par pehle hi faisla ho chuka hai (%)', t.status; end if;
  select * into act from public.agent_actions where id = t.action;
  if not public.has_role(act.approver_roles) then raise exception 'Is kaam ko sirf % approve kar sakte hain', array_to_string(act.approver_roles, ' / '); end if;
  if not p_approve and coalesce(trim(p_note), '') = '' then raise exception 'Mana karne ka kaaran likhein'; end if;
  update public.agent_tasks set status = case when p_approve then 'approved' else 'rejected' end, approved_by = auth.uid(),
         decided_at = now(), decision_note = nullif(trim(p_note), ''), updated_at = now() where id = t.id returning * into t;
  perform public.agent_log(t.hospital_id, t.id, t.agent_id, 'info',
    case when p_approve then 'Approve kiya' else 'Mana kiya: ' || p_note end || ' — ' ||
    coalesce((select full_name from public.profiles where id = auth.uid()), ''));
  if p_approve then t := public.agent_exec(t.id); end if;
  if t.requested_by is not null and t.requested_by <> auth.uid() then
    insert into public.notifications(hospital_id, target_user, level, title, body, source)
    values (t.hospital_id, t.requested_by, case when t.status = 'done' then 'info' else 'warning' end,
            act.title || ': ' || case t.status when 'done' then 'ho gaya ✓' when 'rejected' then 'mana kiya gaya' else t.status end,
            coalesce(t.summary, t.error, t.decision_note), 'agent:' || t.agent_id);
  end if;
  return t;
end $$;
revoke all on function public.agent_decide(uuid, boolean, text) from public, anon;
grant execute on function public.agent_decide(uuid, boolean, text) to authenticated;

-- retry a failed check (requester or doctor/admin)
create or replace function public.agent_retry(p_task uuid) returns public.agent_tasks
language plpgsql security definer set search_path = public as $$
declare t public.agent_tasks;
begin
  select * into t from public.agent_tasks where id = p_task and hospital_id = public.my_hospital();
  if t.id is null or t.status <> 'failed' then raise exception 'Sirf fail hua task dobara chala sakte hain'; end if;
  if not (t.requested_by = auth.uid() or public.has_role('{doctor,admin}')) then raise exception 'Permission nahi'; end if;
  if t.risk <> 'low' and t.approved_by is null then raise exception 'Is task ko approval chahiye'; end if;
  update public.agent_tasks set status = case when t.risk = 'low' then 'queued' else 'approved' end where id = t.id;
  return public.agent_exec(t.id);
end $$;
revoke all on function public.agent_retry(uuid) from public, anon;
grant execute on function public.agent_retry(uuid) to authenticated;

-- doctor can pause / resume an agent
create or replace function public.agent_set_status(p_agent text, p_status text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.has_role('{doctor}') then raise exception 'Sirf doctor agent ko band / chalu kar sakte hain'; end if;
  if p_status not in ('active','paused') then raise exception 'Status active ya paused'; end if;
  update public.agents set status = p_status where id = p_agent;
  insert into public.agent_logs(hospital_id, agent_id, level, message)
  values (public.my_hospital(), p_agent, 'warning', 'Doctor ne agent ' || case when p_status = 'paused' then 'band kiya' else 'chalu kiya' end);
end $$;
revoke all on function public.agent_set_status(text, text) from public, anon;
grant execute on function public.agent_set_status(text, text) to authenticated;

-- logs readable by doctor/admin (already) — also let requester read logs of own tasks
drop policy if exists p_read on public.agent_logs;
create policy p_read on public.agent_logs for select to authenticated
  using (hospital_id = public.my_hospital() and (public.has_role('{doctor,admin}')
         or exists (select 1 from public.agent_tasks t where t.id = agent_logs.task_id and t.requested_by = auth.uid())));

-- ---------- schedules (server runs these even when nobody has the app open) ----------
create or replace function public.agent_cron(p_action text) returns int
language plpgsql security definer set search_path = public as $$
declare h uuid; t public.agent_tasks; n int := 0; act public.agent_actions;
begin
  select * into act from public.agent_actions where id = p_action and risk = 'low';
  if act.id is null then raise exception 'Schedule sirf low-risk check ke liye'; end if;
  if (select status from public.agents where id = act.agent_id) = 'paused' then return 0; end if;
  for h in select id from public.hospitals loop
    insert into public.agent_tasks(hospital_id, agent_id, action, requested_by, input, risk, status)
    values (h, act.agent_id, act.id, null, '{}', 'low', 'queued') returning * into t;
    perform public.agent_log(h, t.id, t.agent_id, 'info', 'Schedule se kaam: ' || act.title);
    perform public.agent_exec(t.id);
    n := n + 1;
  end loop;
  return n;
end $$;
revoke all on function public.agent_cron(text) from public, anon, authenticated;

do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname in ('vatte_boss_morning','vatte_boss_evening','vatte_nurse_vitals');
  perform cron.schedule('vatte_boss_morning', '0 3 * * *',  $c$select public.agent_cron('boss.daily_report')$c$);   -- 8:30 AM IST
  perform cron.schedule('vatte_boss_evening', '30 14 * * *', $c$select public.agent_cron('boss.daily_report')$c$);  -- 8:00 PM IST
  perform cron.schedule('vatte_nurse_vitals', '15 * * * *', $c$select public.agent_cron('nurse.overdue_vitals')$c$); -- every hour
end $$;

-- internal agent functions must never be called directly from the app (only through agent_submit / agent_decide)
do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and (p.proname like 'agent\_h\_%' or p.proname in ('agent_log','agent_notify','agent_exec','agent_cron'))
  loop
    execute format('revoke all on function %s from public, anon, authenticated', f);
  end loop;
end $$;
