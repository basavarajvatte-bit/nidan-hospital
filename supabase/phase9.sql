-- =========================================================
-- VATTE HOSPITAL OS — PHASE 9 (Appointment AI + OPD line)
-- • OPD timings per hospital (morning / evening, slot length, weekly off)
-- • Free-slot finder + safe booking / reschedule / cancel (no double booking)
-- • OPD token line: every OPD / emergency visit gets a token automatically; emergency first, then 65+ age, then token order
-- • Agent engine upgrade: each action names its own handler + its input fields, so new actions need no engine change
-- • Night job: today's un-attended appointments → "missed"; old waiting tokens → "left"; tomorrow's list → reception
-- =========================================================

-- ---------- OPD timings ----------
create table if not exists public.opd_settings (
  hospital_id uuid primary key default public.my_hospital() references public.hospitals(id),
  morning_start time not null default '10:00', morning_end time not null default '14:00',
  evening_start time default '17:00', evening_end time default '20:00',
  slot_minutes int not null default 10 check (slot_minutes between 5 and 60),
  weekly_off int[] not null default '{0}',          -- 0 = Sunday … 6 = Saturday
  updated_at timestamptz not null default now(),
  check (morning_end > morning_start),
  check (evening_start is null or (evening_end > evening_start and evening_start >= morning_end))
);
alter table public.opd_settings enable row level security;
drop policy if exists p_read on public.opd_settings;
drop policy if exists p_write on public.opd_settings;
drop policy if exists p_update on public.opd_settings;
create policy p_read on public.opd_settings for select to authenticated using (hospital_id = public.my_hospital());
create policy p_write on public.opd_settings for insert to authenticated with check (hospital_id = public.my_hospital() and public.has_role('{doctor,admin}'));
create policy p_update on public.opd_settings for update to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin}'));
revoke all on public.opd_settings from anon;
grant select, insert, update on public.opd_settings to authenticated;
insert into public.opd_settings(hospital_id) select id from public.hospitals on conflict do nothing;

-- the hospital's main doctor (owner) — default doctor for bookings
create or replace function public.main_doctor(h uuid default public.my_hospital()) returns uuid
language sql stable security definer set search_path = public as $$
  select id from public.profiles where hospital_id = h and role = 'doctor' order by created_at limit 1
$$;
revoke all on function public.main_doctor(uuid) from public, anon;
grant execute on function public.main_doctor(uuid) to authenticated;

-- ---------- free slots ----------
create or replace function public.opd_free_slots(p_day date, p_doctor uuid default null)
returns table (slot_start timestamptz, slot_end timestamptz, label text, free boolean)
language plpgsql stable security invoker set search_path = public as $$
declare s public.opd_settings; d uuid := coalesce(p_doctor, public.main_doctor()); t time; stop time; part int;
begin
  select * into s from public.opd_settings where hospital_id = public.my_hospital();
  if s.hospital_id is null or extract(dow from p_day)::int = any(s.weekly_off) then return; end if;
  for part in 1..2 loop
    if part = 1 then t := s.morning_start; stop := s.morning_end;
    elsif s.evening_start is not null then t := s.evening_start; stop := s.evening_end; else exit; end if;
    while t + make_interval(mins => s.slot_minutes) <= stop loop
      slot_start := (p_day + t) at time zone 'Asia/Kolkata';
      slot_end := slot_start + make_interval(mins => s.slot_minutes);
      label := to_char(p_day + t, 'HH12:MI AM');
      free := slot_start > now() and not exists (
        select 1 from public.appointments a where a.doctor_id = d and a.status in ('booked','checked_in')
           and tstzrange(a.starts_at, a.ends_at) && tstzrange(slot_start, slot_end));
      return next;
      t := t + make_interval(mins => s.slot_minutes);
    end loop;
  end loop;
end $$;
revoke all on function public.opd_free_slots(date, uuid) from public, anon;
grant execute on function public.opd_free_slots(date, uuid) to authenticated;

-- ---------- booking ----------
create or replace function public.book_appointment(p_patient uuid, p_start timestamptz, p_reason text default null, p_doctor uuid default null)
returns public.appointments
language plpgsql security invoker set search_path = public as $$
declare s public.opd_settings; d uuid := coalesce(p_doctor, public.main_doctor()); a public.appointments; lt time; dd date;
begin
  if not public.has_role('{doctor,admin,receptionist}') then raise exception 'Appointment sirf Reception / Doctor / Admin laga sakte hain'; end if;
  select * into s from public.opd_settings where hospital_id = public.my_hospital();
  dd := (p_start at time zone 'Asia/Kolkata')::date; lt := (p_start at time zone 'Asia/Kolkata')::time;
  if p_start < now() then raise exception 'Beete hue samay ki appointment nahi lag sakti'; end if;
  if extract(dow from dd)::int = any(s.weekly_off) then raise exception 'Us din OPD band rehti hai'; end if;
  if not ((lt >= s.morning_start and lt + make_interval(mins => s.slot_minutes) <= s.morning_end)
       or (s.evening_start is not null and lt >= s.evening_start and lt + make_interval(mins => s.slot_minutes) <= s.evening_end)) then
    raise exception '%', 'Ye samay OPD ke time (' || to_char(s.morning_start, 'HH12:MI AM') || ' – ' || to_char(s.morning_end, 'HH12:MI AM')
      || coalesce(', ' || to_char(s.evening_start, 'HH12:MI AM') || ' – ' || to_char(s.evening_end, 'HH12:MI AM'), '') || ') ke bahar hai';
  end if;
  if exists (select 1 from public.appointments where patient_id = p_patient and status = 'booked'
              and (starts_at at time zone 'Asia/Kolkata')::date = dd) then
    raise exception 'Is patient ki us din pehle se appointment hai — use badlo (reschedule)';
  end if;
  begin
    insert into public.appointments(patient_id, doctor_id, starts_at, ends_at, reason)
    values (p_patient, d, p_start, p_start + make_interval(mins => s.slot_minutes), nullif(trim(p_reason), '')) returning * into a;
  exception when exclusion_violation then
    raise exception 'Ye slot pehle se bhara hai — doosra samay chuno';
  end;
  return a;
end $$;
revoke all on function public.book_appointment(uuid, timestamptz, text, uuid) from public, anon;
grant execute on function public.book_appointment(uuid, timestamptz, text, uuid) to authenticated;

create or replace function public.reschedule_appointment(p_id uuid, p_start timestamptz) returns public.appointments
language plpgsql security invoker set search_path = public as $$
declare old public.appointments; a public.appointments;
begin
  select * into old from public.appointments where id = p_id and status = 'booked' for update;
  if old.id is null then raise exception 'Sirf "booked" appointment badal sakte hain'; end if;
  update public.appointments set status = 'cancelled', reason = coalesce(reason, '') || ' [badla: ' || to_char(p_start at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM') || ']'
   where id = p_id;
  a := public.book_appointment(old.patient_id, p_start, old.reason, old.doctor_id);
  return a;
end $$;
revoke all on function public.reschedule_appointment(uuid, timestamptz) from public, anon;
grant execute on function public.reschedule_appointment(uuid, timestamptz) to authenticated;

create or replace function public.cancel_appointment(p_id uuid, p_reason text) returns public.appointments
language plpgsql security invoker set search_path = public as $$
declare a public.appointments;
begin
  if coalesce(trim(p_reason), '') = '' then raise exception 'Cancel karne ka kaaran likhein'; end if;
  update public.appointments set status = 'cancelled', reason = coalesce(reason || ' · ', '') || 'Cancel: ' || trim(p_reason)
   where id = p_id and status = 'booked' returning * into a;
  if a.id is null then raise exception 'Sirf "booked" appointment cancel ho sakti hai'; end if;
  return a;
end $$;
revoke all on function public.cancel_appointment(uuid, text) from public, anon;
grant execute on function public.cancel_appointment(uuid, text) to authenticated;

-- ---------- OPD token line ----------
create table if not exists public.opd_queue (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  day date not null,
  token_no int not null,
  patient_id uuid not null references public.patients(id),
  encounter_id uuid unique references public.encounters(id),
  appointment_id uuid references public.appointments(id),
  priority text not null default 'normal' check (priority in ('emergency','senior','normal')),
  status text not null default 'waiting' check (status in ('waiting','called','in_consult','done','no_show','left')),
  created_at timestamptz not null default now(),
  called_at timestamptz, started_at timestamptz, done_at timestamptz,
  unique (hospital_id, day, token_no)
);
create index if not exists opd_queue_day_idx on public.opd_queue(hospital_id, day, status);
alter table public.opd_queue enable row level security;
drop policy if exists p_read on public.opd_queue;
create policy p_read on public.opd_queue for select to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,receptionist,nurse}'));
revoke all on public.opd_queue from anon;
revoke insert, update, delete on public.opd_queue from authenticated;
grant select on public.opd_queue to authenticated;
drop trigger if exists no_delete on public.opd_queue;
create trigger no_delete before delete on public.opd_queue for each row execute function public.block_delete();

-- every new OPD / emergency visit gets the next token of the day (and checks in today's appointment)
create or replace function public.opd_token_on_visit() returns trigger
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; n int; ap uuid; age int; pr text;
begin
  if new.kind not in ('opd','emergency') then return new; end if;
  perform pg_advisory_xact_lock(hashtext('opd_token:' || new.hospital_id || ':' || d));
  select coalesce(max(token_no), 0) + 1 into n from public.opd_queue where hospital_id = new.hospital_id and day = d;
  select id into ap from public.appointments where patient_id = new.patient_id and status = 'booked'
     and (starts_at at time zone 'Asia/Kolkata')::date = d order by starts_at limit 1;
  if ap is not null then update public.appointments set status = 'checked_in' where id = ap; end if;
  select public.patient_age(p) into age from public.patients p where p.id = new.patient_id;
  pr := case when new.kind = 'emergency' then 'emergency' when coalesce(age, 0) >= 65 then 'senior' else 'normal' end;
  insert into public.opd_queue(hospital_id, day, token_no, patient_id, encounter_id, appointment_id, priority)
  values (new.hospital_id, d, n, new.patient_id, new.id, ap, pr);
  return new;
end $$;
revoke all on function public.opd_token_on_visit() from public, anon, authenticated;
drop trigger if exists opd_token on public.encounters;
create trigger opd_token after insert on public.encounters for each row execute function public.opd_token_on_visit();

-- visit closed at reception → token done, appointment completed
create or replace function public.opd_close_on_visit() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.status <> 'open' and old.status = 'open' then
    update public.opd_queue set status = 'done', done_at = coalesce(done_at, now())
     where encounter_id = new.id and status in ('waiting','called','in_consult');
    update public.appointments set status = 'completed'
     where id = (select appointment_id from public.opd_queue where encounter_id = new.id) and status = 'checked_in';
  end if;
  return new;
end $$;
revoke all on function public.opd_close_on_visit() from public, anon, authenticated;
drop trigger if exists opd_close on public.encounters;
create trigger opd_close after update of status on public.encounters for each row execute function public.opd_close_on_visit();

-- tokens for OPD visits that were already open before this phase
do $$
declare e record; n int; d date := (now() at time zone 'Asia/Kolkata')::date;
begin
  for e in select * from public.encounters where kind in ('opd','emergency') and status = 'open'
             and not exists (select 1 from public.opd_queue q where q.encounter_id = encounters.id) order by started_at loop
    select coalesce(max(token_no), 0) + 1 into n from public.opd_queue where hospital_id = e.hospital_id and day = d;
    insert into public.opd_queue(hospital_id, day, token_no, patient_id, encounter_id, priority, created_at)
    values (e.hospital_id, d, n, e.patient_id, e.id, case when e.kind = 'emergency' then 'emergency' else 'normal' end, e.started_at);
  end loop;
end $$;

-- move a token: called → in_consult → done, or no_show
create or replace function public.queue_set(p_id uuid, p_status text) returns public.opd_queue
language plpgsql security definer set search_path = public as $$
declare q public.opd_queue;
begin
  if not public.has_role('{doctor,admin,receptionist,nurse}') then raise exception 'Permission nahi'; end if;
  if p_status not in ('waiting','called','in_consult','done','no_show') then raise exception 'Galat status'; end if;
  update public.opd_queue set status = p_status,
         called_at = case when p_status = 'called' then now() else called_at end,
         started_at = case when p_status = 'in_consult' then now() else started_at end,
         done_at = case when p_status in ('done','no_show') then now() else done_at end
   where id = p_id and hospital_id = public.my_hospital() returning * into q;
  if q.id is null then raise exception 'Token nahi mila'; end if;
  if p_status in ('done','no_show') then
    update public.encounters set status = case when p_status = 'done' then 'closed' else 'cancelled' end, ended_at = now()
     where id = q.encounter_id and status = 'open';
    if p_status = 'no_show' and q.appointment_id is not null then
      update public.appointments set status = 'missed' where id = q.appointment_id and status in ('booked','checked_in');
    end if;
  end if;
  return q;
end $$;
revoke all on function public.queue_set(uuid, text) from public, anon;
grant execute on function public.queue_set(uuid, text) to authenticated;

-- call the next patient: emergency first, then senior citizens, then token order
create or replace function public.queue_call_next() returns public.opd_queue
language plpgsql security definer set search_path = public as $$
declare q public.opd_queue; d date := (now() at time zone 'Asia/Kolkata')::date;
begin
  if not public.has_role('{doctor,admin,receptionist,nurse}') then raise exception 'Permission nahi'; end if;
  select * into q from public.opd_queue where hospital_id = public.my_hospital() and day = d and status = 'waiting'
   order by case priority when 'emergency' then 0 when 'senior' then 1 else 2 end, token_no limit 1 for update skip locked;
  if q.id is null then raise exception 'Line mein koi patient nahi'; end if;
  return public.queue_set(q.id, 'called');
end $$;
revoke all on function public.queue_call_next() from public, anon;
grant execute on function public.queue_call_next() to authenticated;

-- ---------- agent engine upgrade: handler + input fields per action ----------
alter table public.agent_actions add column if not exists handler text;
alter table public.agent_actions add column if not exists params jsonb;   -- JSON schema of inputs (for the AI chat)
update public.agent_actions set handler = x.h from (values
  ('nurse.overdue_vitals','agent_h_overdue_vitals'), ('reception.today','agent_h_reception_today'), ('appointment.today','agent_h_appointments_today'),
  ('operations.beds','agent_h_beds'), ('pharmacy.stock','agent_h_pharmacy_stock'), ('lab.pending','agent_h_lab_pending'),
  ('accountant.dues','agent_h_dues'), ('followup.due','agent_h_followups'), ('followup.schedule','agent_h_followup_schedule'),
  ('operations.bed_status','agent_h_bed_status'), ('pharmacy.writeoff_expired','agent_h_writeoff_expired')
) as x(id, h) where agent_actions.id = x.id;
update public.agent_actions set params = '{"type":"object","properties":{"patient_id":{"type":"string"},"due_on":{"type":"string","description":"YYYY-MM-DD"},"reason":{"type":"string"}},"required":["patient_id","due_on"]}'
 where id = 'followup.schedule';
update public.agent_actions set params = '{"type":"object","properties":{"bed_id":{"type":"string"},"status":{"type":"string","enum":["available","cleaning","blocked"]}},"required":["bed_id","status"]}'
 where id = 'operations.bed_status';
update public.agent_actions set params = '{"type":"object","properties":{"batch_id":{"type":"string"}},"required":["batch_id"]}'
 where id = 'pharmacy.writeoff_expired';

-- new appointment / queue handlers
create or replace function public.agent_h_queue(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; items jsonb; w int; inc text; avgw int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('token', q.token_no, 'patient', p.full_name, 'uhid', p.uhid, 'status', q.status, 'priority', q.priority,
           'wait_min', round(extract(epoch from now() - q.created_at) / 60)) order by case q.priority when 'emergency' then 0 when 'senior' then 1 else 2 end, q.token_no), '[]'),
         count(*) filter (where q.status = 'waiting')
    into items, w
    from public.opd_queue q join public.patients p on p.id = q.patient_id
   where q.hospital_id = h and q.day = d and q.status in ('waiting','called','in_consult');
  select string_agg('Token ' || q.token_no, ', ') into inc from public.opd_queue q where q.hospital_id = h and q.day = d and q.status = 'in_consult';
  select round(avg(extract(epoch from started_at - created_at) / 60)) into avgw from public.opd_queue
   where hospital_id = h and day = d and started_at is not null;
  return jsonb_build_object('summary', w || ' patient line mein' || coalesce(' · andar: ' || inc, '') || coalesce(' · aaj ka avg intezaar ' || avgw || ' min', ''),
                            'items', items, 'alert', w >= 15, 'alert_role', 'doctor');
end $$;

create or replace function public.agent_h_free_slots(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare dd date := coalesce(nullif(inp->>'day','')::date, (now() at time zone 'Asia/Kolkata')::date); s public.opd_settings; doc uuid := public.main_doctor(h);
        t time; stop time; part int; st timestamptz; free text[] := '{}'; booked int := 0;
begin
  select * into s from public.opd_settings where hospital_id = h;
  if extract(dow from dd)::int = any(s.weekly_off) then
    return jsonb_build_object('summary', to_char(dd, 'DD Mon (Dy)') || ' ko OPD band hai', 'items', '[]'::jsonb, 'alert', false); end if;
  for part in 1..2 loop
    if part = 1 then t := s.morning_start; stop := s.morning_end; elsif s.evening_start is not null then t := s.evening_start; stop := s.evening_end; else exit; end if;
    while t + make_interval(mins => s.slot_minutes) <= stop loop
      st := (dd + t) at time zone 'Asia/Kolkata';
      if st > now() and not exists (select 1 from public.appointments a where a.doctor_id = doc and a.status in ('booked','checked_in')
           and tstzrange(a.starts_at, a.ends_at) && tstzrange(st, st + make_interval(mins => s.slot_minutes))) then
        free := free || to_char(dd + t, 'HH24:MI'); else booked := booked + 1; end if;
      t := t + make_interval(mins => s.slot_minutes);
    end loop;
  end loop;
  return jsonb_build_object('summary', to_char(dd, 'DD Mon (Dy)') || ': ' || coalesce(array_length(free, 1), 0) || ' slot khali',
                            'items', jsonb_build_array(jsonb_build_object('day', dd, 'free_slots_24h', free)), 'alert', false);
end $$;

create or replace function public.agent_h_book(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare pid uuid := (inp->>'patient_id')::uuid; dd date := (inp->>'day')::date; tm time := (inp->>'time')::time;
        st timestamptz; s public.opd_settings; doc uuid := public.main_doctor(h); a public.appointments; pname text;
begin
  select full_name into pname from public.patients where id = pid and hospital_id = h;
  if pname is null then raise exception 'Patient nahi mila'; end if;
  if dd is null or tm is null then raise exception 'Din (YYYY-MM-DD) aur samay (HH:MM) dono chahiye'; end if;
  select * into s from public.opd_settings where hospital_id = h;
  st := (dd + tm) at time zone 'Asia/Kolkata';
  if st < now() then raise exception 'Beete hue samay ki appointment nahi lag sakti'; end if;
  if extract(dow from dd)::int = any(s.weekly_off) then raise exception 'Us din OPD band hai'; end if;
  if not ((tm >= s.morning_start and tm + make_interval(mins => s.slot_minutes) <= s.morning_end)
       or (s.evening_start is not null and tm >= s.evening_start and tm + make_interval(mins => s.slot_minutes) <= s.evening_end)) then
    raise exception 'Ye samay OPD time ke bahar hai'; end if;
  if exists (select 1 from public.appointments where patient_id = pid and status = 'booked' and (starts_at at time zone 'Asia/Kolkata')::date = dd) then
    raise exception 'Is patient ki us din pehle se appointment hai'; end if;
  begin
    insert into public.appointments(hospital_id, patient_id, doctor_id, starts_at, ends_at, reason, created_by)
    values (h, pid, doc, st, st + make_interval(mins => s.slot_minutes), nullif(trim(inp->>'reason'), ''), req) returning * into a;
  exception when exclusion_violation then raise exception 'Ye slot pehle se bhara hai — doosra samay chuno'; end;
  return jsonb_build_object('summary', pname || ' ki appointment ' || to_char(st at time zone 'Asia/Kolkata', 'DD Mon, HH12:MI AM') || ' ko lag gayi ✓',
                            'items', jsonb_build_array(jsonb_build_object('patient', pname, 'appointment_id', a.id)), 'alert', false);
end $$;

create or replace function public.agent_h_cancel_appt(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare a public.appointments; pname text;
begin
  if coalesce(trim(inp->>'reason'), '') = '' then raise exception 'Cancel karne ka kaaran chahiye'; end if;
  update public.appointments set status = 'cancelled', reason = coalesce(reason || ' · ', '') || 'Cancel: ' || trim(inp->>'reason')
   where id = (inp->>'appointment_id')::uuid and hospital_id = h and status = 'booked' returning * into a;
  if a.id is null then raise exception 'Booked appointment nahi mili'; end if;
  select full_name into pname from public.patients where id = a.patient_id;
  return jsonb_build_object('summary', pname || ' ki ' || to_char(a.starts_at at time zone 'Asia/Kolkata', 'DD Mon HH12:MI AM') || ' wali appointment cancel ✓',
                            'items', '[]'::jsonb, 'alert', false);
end $$;

-- today's appointments now list names + appointment ids (so chat can cancel / talk about them)
create or replace function public.agent_h_appointments_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare dd date := coalesce(nullif(inp->>'day','')::date, (now() at time zone 'Asia/Kolkata')::date); items jsonb; n int; bk int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('time', to_char(a.starts_at at time zone 'Asia/Kolkata', 'HH12:MI AM'), 'patient', p.full_name, 'uhid', p.uhid,
           'phone', p.phone, 'status', a.status, 'reason', a.reason, 'appointment_id', a.id) order by a.starts_at), '[]'),
         count(*), count(*) filter (where a.status = 'booked')
    into items, n, bk
    from public.appointments a join public.patients p on p.id = a.patient_id
   where a.hospital_id = h and (a.starts_at at time zone 'Asia/Kolkata')::date = dd and a.status <> 'cancelled';
  return jsonb_build_object('summary', to_char(dd, 'DD Mon') || ': ' || n || ' appointments (' || bk || ' abhi aane baaki)', 'items', items, 'alert', false);
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('appointment.queue','appointment','OPD line abhi','Abhi kitne patient line mein, kaun andar hai, kitna intezaar','check','low','{doctor,admin,receptionist,nurse}','{}','{appointments,patients}',9,'agent_h_queue',null),
 ('appointment.free_slots','appointment','Khali slot dikhao','Kisi din ke khali appointment slot','check','low','{doctor,admin,receptionist}','{}','{appointments}',10,'agent_h_free_slots',
   '{"type":"object","properties":{"day":{"type":"string","description":"YYYY-MM-DD (khaali = aaj)"}}}'),
 ('appointment.book','appointment','Appointment lagao','Patient ki appointment lagana (khali slot mein)','act','low','{doctor,admin,receptionist}','{}','{appointments,patients}',23,'agent_h_book',
   '{"type":"object","properties":{"patient_id":{"type":"string"},"day":{"type":"string","description":"YYYY-MM-DD"},"time":{"type":"string","description":"HH:MM 24-ghante (jaise 10:30, 17:00)"},"reason":{"type":"string"}},"required":["patient_id","day","time"]}'),
 ('appointment.cancel','appointment','Appointment cancel karo','Booked appointment cancel karna (approval ke baad)','act','controlled','{doctor,admin,receptionist}','{doctor,admin}','{appointments,patients}',24,'agent_h_cancel_appt',
   '{"type":"object","properties":{"appointment_id":{"type":"string"},"reason":{"type":"string"}},"required":["appointment_id","reason"]}')
on conflict (id) do update set agent_id=excluded.agent_id, title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk,
  requester_roles=excluded.requester_roles, approver_roles=excluded.approver_roles, tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;
update public.agent_actions set params = '{"type":"object","properties":{"day":{"type":"string","description":"YYYY-MM-DD (khaali = aaj)"}}}' where id = 'appointment.today';
update public.agent_actions set title = 'Appointments (din ke hisaab se)', description = 'Kisi din ki appointments — naam, samay, status' where id = 'appointment.today';

-- engine: dispatch by handler name (check → (h, input), act → (h, input, requester))
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
    if t.action = 'boss.daily_report' then
      for a in select * from public.agent_actions where kind = 'check' and agent_id <> 'boss' and (params is null or not (params ? 'required')) and id <> 'appointment.free_slots' order by ord loop
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
    elsif act.handler is null or act.handler !~ '^agent_h_[a-z_]+$' then
      raise exception 'Is action ka handler nahi bana: %', t.action;
    elsif act.kind = 'check' then
      execute format('select public.%I($1, $2)', act.handler) into res using t.hospital_id, t.input;
    else
      execute format('select public.%I($1, $2, $3)', act.handler) into res using t.hospital_id, t.input, t.requested_by;
    end if;

    if res is null then raise exception 'Handler ne kuch nahi lautaya: %', t.action; end if;
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

-- AI chat: actions now carry their input fields
create or replace function public.ai_chat_begin(p_agent text) returns jsonb
language plpgsql security definer set search_path = public as $$
declare a public.ai_chat_agents; g public.agents; h uuid := public.my_hospital(); r text := public.my_role(); nu int; nh int; nm text;
begin
  select * into a from public.ai_chat_agents where agent_id = p_agent;
  if a.agent_id is null then raise exception 'Ye chat agent nahi hai'; end if;
  if h is null or not (r = any(a.roles)) then raise exception 'Aapka role is AI se baat nahi kar sakta'; end if;
  select * into g from public.agents where id = p_agent;
  if g.status = 'paused' then raise exception 'Doctor ne ye agent band kiya hai'; end if;
  select count(*) into nu from public.ai_chat_usage where user_id = auth.uid() and created_at > now() - interval '1 hour';
  select count(*) into nh from public.ai_chat_usage where hospital_id = h and created_at > now() - interval '1 day';
  if nu >= 40 then raise exception 'Ek ghante mein 40 sawaal ki seema poori. Thodi der baad poochein.'; end if;
  if nh >= 400 then raise exception 'Aaj hospital ki AI seema (400 sawaal) poori. Kal phir chalega.'; end if;
  select full_name into nm from public.profiles where id = auth.uid();
  return jsonb_build_object('role', r, 'name', nm, 'tools', a.tools, 'title', a.title, 'about', g.responsibilities, 'department', g.department,
    'opd', (select jsonb_build_object('morning', to_char(morning_start, 'HH24:MI') || '-' || to_char(morning_end, 'HH24:MI'),
                                      'evening', to_char(evening_start, 'HH24:MI') || '-' || to_char(evening_end, 'HH24:MI'),
                                      'slot_minutes', slot_minutes, 'weekly_off', weekly_off) from public.opd_settings where hospital_id = h),
    'actions', (select jsonb_agg(jsonb_build_object('id', x.id, 'title', x.title, 'description', x.description, 'kind', x.kind, 'risk', x.risk, 'params', x.params))
                  from public.agent_actions x where x.id = any(a.tools) and r = any(x.requester_roles)));
end $$;
revoke all on function public.ai_chat_begin(text) from public, anon;
grant execute on function public.ai_chat_begin(text) to authenticated;

update public.ai_chat_agents set tools = '{find_patient,appointment.today,appointment.queue,appointment.free_slots,appointment.book,appointment.cancel}' where agent_id = 'appointment';
update public.ai_chat_agents set tools = '{find_patient,list_beds,reception.today,appointment.today,appointment.queue,appointment.free_slots,appointment.book,operations.beds,followup.due,followup.schedule}' where agent_id = 'reception';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{appointment.queue}')) where agent_id in ('boss','nurse');

-- ---------- night job ----------
create or replace function public.opd_night_job() returns void
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; h uuid; n int;
begin
  update public.appointments set status = 'missed' where status = 'booked' and starts_at < now() and (starts_at at time zone 'Asia/Kolkata')::date <= d;
  update public.opd_queue set status = 'left', done_at = now() where status in ('waiting','called') and day < d;
  for h in select id from public.hospitals loop
    select count(*) into n from public.appointments where hospital_id = h and status = 'booked' and (starts_at at time zone 'Asia/Kolkata')::date = d + 1;
    if n > 0 then
      perform public.agent_notify(h, 'receptionist', 'info', '📅 Kal ki ' || n || ' appointments', 'AI Agents → Appointment → "Appointments" mein kal ki list dekhein aur patients ko yaad dilaayein.', 'agent:appointment:' || (d + 1));
    end if;
  end loop;
end $$;
revoke all on function public.opd_night_job() from public, anon, authenticated;
do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname = 'vatte_opd_night';
  perform cron.schedule('vatte_opd_night', '30 15 * * *', $c$select public.opd_night_job()$c$);   -- 9:00 PM IST
end $$;

-- internal handlers never callable from the app
do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and (p.proname like 'agent\_h\_%' or p.proname in ('agent_exec','agent_cron','agent_log','agent_notify'))
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;
