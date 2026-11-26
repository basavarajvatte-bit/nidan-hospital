-- =========================================================
-- VATTE HOSPITAL OS — PHASE 13 (HR + Operations + Procurement AI)
-- HR: staff list (linked to app login), daily attendance, self check-in / check-out, leave requests + approval,
--     monthly salary sheet calculated by the server, salary payment (also written in the day book as an expense)
-- Operations: equipment register with service due dates, repair / complaint tickets (any staff can raise)
-- Procurement: non-medicine purchase requests → Doctor/Admin approval → received (+ payment in day book)
-- AI: HR today, salary due, open repairs / service due, purchases waiting — all read-only
-- =========================================================

-- ---------- HR: staff ----------
alter table public.staff_members add column if not exists shift text check (shift in ('morning','evening','night','general'));
alter table public.staff_members add column if not exists left_on date;
alter table public.staff_members add column if not exists emergency_phone text;
create unique index if not exists staff_profile_uniq on public.staff_members(profile_id) where profile_id is not null;
-- staff, attendance, salaries: changes only through the functions below
drop policy if exists p_insert on public.staff_members; drop policy if exists p_update on public.staff_members;
revoke insert, update, delete on public.staff_members from authenticated;
drop policy if exists p_insert on public.attendance; drop policy if exists p_update on public.attendance;
revoke insert, update, delete on public.attendance from authenticated;
drop policy if exists p_insert on public.salaries; revoke insert, update, delete on public.salaries from authenticated;
alter table public.salaries add column if not exists note text;
alter table public.salaries add column if not exists expense_id uuid references public.expenses(id);
-- every staff can see their own staff card & attendance
drop policy if exists p_read_own on public.staff_members;
create policy p_read_own on public.staff_members for select to authenticated using (profile_id = auth.uid());
drop policy if exists p_read_own on public.attendance;
create policy p_read_own on public.attendance for select to authenticated
  using (exists (select 1 from public.staff_members s where s.id = attendance.staff_id and s.profile_id = auth.uid()));

create or replace function public.hr_save_staff(p_id uuid, p_name text, p_designation text, p_department text, p_phone text, p_joined date,
  p_salary numeric, p_shift text, p_profile uuid, p_active boolean default true, p_emergency text default null) returns public.staff_members
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); s public.staff_members; dep uuid;
begin
  if not public.has_role('{doctor,admin,hr}') then raise exception 'Staff list sirf Doctor / Admin / HR badal sakte hain'; end if;
  if coalesce(trim(p_name), '') = '' or coalesce(trim(p_designation), '') = '' then raise exception 'Naam aur pad (designation) likhein'; end if;
  if p_salary is not null and (p_salary < 0 or p_salary > 10000000) then raise exception 'Salary galat hai'; end if;
  if p_profile is not null and not exists (select 1 from public.profiles where id = p_profile and hospital_id = h) then raise exception 'Login account nahi mila'; end if;
  if coalesce(trim(p_department), '') <> '' then
    insert into public.departments(hospital_id, name) values (h, trim(p_department)) on conflict (hospital_id, name) do nothing;
    select id into dep from public.departments where hospital_id = h and name = trim(p_department);
  end if;
  if p_id is null then
    insert into public.staff_members(hospital_id, profile_id, department_id, full_name, designation, phone, joined_on, monthly_salary, shift, active, emergency_phone)
    values (h, p_profile, dep, trim(p_name), trim(p_designation), nullif(trim(p_phone), ''), p_joined, p_salary, p_shift, true, nullif(trim(p_emergency), ''))
    returning * into s;
  else
    update public.staff_members set profile_id = p_profile, department_id = dep, full_name = trim(p_name), designation = trim(p_designation),
           phone = nullif(trim(p_phone), ''), joined_on = p_joined, monthly_salary = p_salary, shift = p_shift, emergency_phone = nullif(trim(p_emergency), ''),
           active = coalesce(p_active, active),
           left_on = case when coalesce(p_active, active) = false and active then (now() at time zone 'Asia/Kolkata')::date
                          when coalesce(p_active, active) then null else left_on end
     where id = p_id and hospital_id = h returning * into s;
    if s.id is null then raise exception 'Staff nahi mila'; end if;
  end if;
  return s;
exception when unique_violation then raise exception 'Ye login account pehle se kisi aur staff se juda hai';
end $$;
revoke all on function public.hr_save_staff(uuid, text, text, text, text, date, numeric, text, uuid, boolean, text) from public, anon;
grant execute on function public.hr_save_staff(uuid, text, text, text, text, date, numeric, text, uuid, boolean, text) to authenticated;

-- ---------- HR: attendance ----------
-- p_rows: [{ "staff_id": "...", "status": "present", "shift": "morning", "overtime_hours": 0 }]
create or replace function public.hr_mark_attendance(p_day date, p_rows jsonb) returns int
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); x jsonb; n int := 0; today date := (now() at time zone 'Asia/Kolkata')::date; ot numeric;
begin
  if not public.has_role('{doctor,admin,hr}') then raise exception 'Hazri sirf Doctor / Admin / HR laga sakte hain'; end if;
  if p_day > today then raise exception 'Aage ki date ki hazri nahi lagti'; end if;
  if p_day < today - 31 then raise exception '31 din se purani hazri nahi badal sakte'; end if;
  if p_day < today - 3 and not public.has_role('{doctor,admin}') then raise exception '3 din se purani hazri sirf Doctor / Admin badal sakte hain'; end if;
  for x in select * from jsonb_array_elements(coalesce(p_rows, '[]')) loop
    if not exists (select 1 from public.staff_members where id = (x->>'staff_id')::uuid and hospital_id = h) then raise exception 'Staff nahi mila'; end if;
    if x->>'status' not in ('present','absent','leave','half_day','off') then raise exception 'Hazri ka status galat'; end if;
    ot := coalesce(nullif(x->>'overtime_hours', '')::numeric, 0);
    if ot < 0 or ot > 16 then raise exception 'Overtime 0 se 16 ghante'; end if;
    insert into public.attendance(hospital_id, staff_id, day, status, shift, overtime_hours, marked_by)
    values (h, (x->>'staff_id')::uuid, p_day, x->>'status', nullif(x->>'shift', ''), ot, auth.uid())
    on conflict (staff_id, day) do update set status = excluded.status, shift = coalesce(excluded.shift, attendance.shift),
      overtime_hours = excluded.overtime_hours, marked_by = auth.uid();
    n := n + 1;
  end loop;
  return n;
end $$;
revoke all on function public.hr_mark_attendance(date, jsonb) from public, anon;
grant execute on function public.hr_mark_attendance(date, jsonb) to authenticated;

-- self check-in / check-out (staff whose login is linked to a staff card)
create or replace function public.hr_self_check(p_out boolean default false) returns public.attendance
language plpgsql security definer set search_path = public as $$
declare s public.staff_members; a public.attendance; today date := (now() at time zone 'Asia/Kolkata')::date;
begin
  select * into s from public.staff_members where profile_id = auth.uid() and active;
  if s.id is null then raise exception 'Aapka staff card nahi juda — HR se kahein "Staff list" mein aapka login jode'; end if;
  if not p_out then
    insert into public.attendance(hospital_id, staff_id, day, status, shift, check_in, marked_by)
    values (s.hospital_id, s.id, today, 'present', s.shift, now(), auth.uid())
    on conflict (staff_id, day) do update set check_in = coalesce(attendance.check_in, now()),
      status = case when attendance.status in ('absent') then 'present' else attendance.status end
    returning * into a;
  else
    update public.attendance set check_out = now() where staff_id = s.id and day = today and check_in is not null returning * into a;
    if a.id is null then raise exception 'Pehle aaj ka check-in karein'; end if;
  end if;
  return a;
end $$;
revoke all on function public.hr_self_check(boolean) from public, anon;
grant execute on function public.hr_self_check(boolean) to authenticated;

-- ---------- HR: leave ----------
create table if not exists public.leave_requests (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  staff_id uuid not null references public.staff_members(id),
  from_day date not null,
  to_day date not null,
  kind text not null check (kind in ('casual','sick','earned','unpaid','other')),
  reason text,
  status text not null default 'pending' check (status in ('pending','approved','rejected','cancelled')),
  requested_by uuid not null references auth.users(id),
  decided_by uuid references auth.users(id),
  decided_at timestamptz,
  decision_note text,
  created_at timestamptz not null default now(),
  check (to_day >= from_day and to_day - from_day <= 60)
);
alter table public.leave_requests enable row level security;
drop policy if exists p_read on public.leave_requests;
create policy p_read on public.leave_requests for select to authenticated
  using (hospital_id = public.my_hospital() and (public.has_role('{doctor,admin,hr}')
         or exists (select 1 from public.staff_members s where s.id = leave_requests.staff_id and s.profile_id = auth.uid())));
revoke all on public.leave_requests from anon;
revoke insert, update, delete on public.leave_requests from authenticated;
grant select on public.leave_requests to authenticated;
drop trigger if exists audit on public.leave_requests;
create trigger audit after insert or update on public.leave_requests for each row execute function public.audit_row();

create or replace function public.hr_request_leave(p_staff uuid, p_from date, p_to date, p_kind text, p_reason text) returns public.leave_requests
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); s public.staff_members; l public.leave_requests;
begin
  if p_staff is null then select * into s from public.staff_members where profile_id = auth.uid() and active;
  else select * into s from public.staff_members where id = p_staff and hospital_id = h; end if;
  if s.id is null then raise exception 'Staff card nahi mila — HR se login judwayein'; end if;
  if s.profile_id is distinct from auth.uid() and not public.has_role('{doctor,admin,hr}') then raise exception 'Doosre ki chhutti sirf HR maang sakta hai'; end if;
  if p_from is null or p_to is null or p_to < p_from then raise exception 'Chhutti ki tareekh sahi likhein'; end if;
  if p_to - p_from > 60 then raise exception 'Ek baar mein 60 din tak'; end if;
  if p_from < (now() at time zone 'Asia/Kolkata')::date - 7 then raise exception '7 din se purani chhutti nahi maang sakte'; end if;
  if exists (select 1 from public.leave_requests where staff_id = s.id and status in ('pending','approved') and daterange(from_day, to_day, '[]') && daterange(p_from, p_to, '[]')) then
    raise exception 'In dino ki chhutti pehle se maangi / mili hui hai'; end if;
  insert into public.leave_requests(hospital_id, staff_id, from_day, to_day, kind, reason, requested_by)
  values (s.hospital_id, s.id, p_from, p_to, coalesce(p_kind, 'casual'), nullif(trim(p_reason), ''), auth.uid()) returning * into l;
  perform public.agent_notify(s.hospital_id, 'hr', 'info', '🙋 Chhutti ki arzi: ' || s.full_name, to_char(p_from, 'DD Mon') || ' – ' || to_char(p_to, 'DD Mon') || coalesce(' · ' || p_reason, ''), 'agent:hr:leave:' || l.id);
  perform public.agent_notify(s.hospital_id, 'doctor', 'info', '🙋 Chhutti ki arzi: ' || s.full_name, to_char(p_from, 'DD Mon') || ' – ' || to_char(p_to, 'DD Mon') || coalesce(' · ' || p_reason, ''), 'agent:hr:leave:' || l.id);
  return l;
end $$;
revoke all on function public.hr_request_leave(uuid, date, date, text, text) from public, anon;
grant execute on function public.hr_request_leave(uuid, date, date, text, text) to authenticated;

create or replace function public.hr_decide_leave(p_id uuid, p_approve boolean, p_note text default null) returns public.leave_requests
language plpgsql security definer set search_path = public as $$
declare l public.leave_requests; d date;
begin
  if not public.has_role('{doctor,admin,hr}') then raise exception 'Chhutti sirf Doctor / Admin / HR manzoor kar sakte hain'; end if;
  select * into l from public.leave_requests where id = p_id and hospital_id = public.my_hospital() for update;
  if l.id is null or l.status <> 'pending' then raise exception 'Khuli arzi nahi mili'; end if;
  if exists (select 1 from public.staff_members where id = l.staff_id and profile_id = auth.uid()) then raise exception 'Apni chhutti khud manzoor nahi kar sakte'; end if;
  update public.leave_requests set status = case when p_approve then 'approved' else 'rejected' end, decided_by = auth.uid(), decided_at = now(),
         decision_note = nullif(trim(p_note), '') where id = l.id returning * into l;
  if p_approve then
    for d in select generate_series(l.from_day, l.to_day, interval '1 day')::date loop
      insert into public.attendance(hospital_id, staff_id, day, status, marked_by) values (l.hospital_id, l.staff_id, d, 'leave', auth.uid())
      on conflict (staff_id, day) do update set status = 'leave', marked_by = auth.uid();
    end loop;
  end if;
  insert into public.notifications(hospital_id, target_user, level, title, body, source)
  select l.hospital_id, s.profile_id, 'info', case when p_approve then '✅ Chhutti manzoor' else '❌ Chhutti nahi mili' end,
         to_char(l.from_day, 'DD Mon') || ' – ' || to_char(l.to_day, 'DD Mon') || coalesce(' · ' || p_note, ''), 'agent:hr:leave:' || l.id
    from public.staff_members s where s.id = l.staff_id and s.profile_id is not null;
  return l;
end $$;
revoke all on function public.hr_decide_leave(uuid, boolean, text) from public, anon;
grant execute on function public.hr_decide_leave(uuid, boolean, text) to authenticated;

-- ---------- HR: salary sheet (server calculates) ----------
-- paid days = present + leave (except unpaid leave) + weekly off + ½ × half day; absent and unpaid leave are not paid
-- overtime pay = overtime hours × (day salary ÷ 8)
create or replace function public.hr_salary_rows(h uuid, p_month date)
returns table (staff_id uuid, name text, designation text, monthly numeric, days int, present int, half_day int, leave int, unpaid_leave int, off int,
               absent int, not_marked int, overtime numeric, paid_days numeric, payable numeric, paid numeric, due numeric)
language sql stable security definer set search_path = public as $$
  with m as (select date_trunc('month', p_month)::date as m0, (date_trunc('month', p_month) + interval '1 month - 1 day')::date as m1),
  s as (
    select st.id, st.full_name, st.designation, coalesce(st.monthly_salary, 0) monthly, st.joined_on, st.left_on,
           extract(day from m.m1)::int days,
           count(*) filter (where a.status = 'present')::int present,
           count(*) filter (where a.status = 'half_day')::int half_day,
           count(*) filter (where a.status = 'leave' and not exists (select 1 from public.leave_requests l where l.staff_id = st.id and l.kind = 'unpaid' and l.status = 'approved' and a.day between l.from_day and l.to_day))::int leave,
           count(*) filter (where a.status = 'leave' and exists (select 1 from public.leave_requests l where l.staff_id = st.id and l.kind = 'unpaid' and l.status = 'approved' and a.day between l.from_day and l.to_day))::int unpaid_leave,
           count(*) filter (where a.status = 'off')::int off,
           count(*) filter (where a.status = 'absent')::int absent,
           count(a.id)::int marked,
           coalesce(sum(a.overtime_hours), 0) overtime
      from public.staff_members st cross join m
      left join public.attendance a on a.staff_id = st.id and a.day between m.m0 and m.m1
     where st.hospital_id = h and (st.active or st.left_on >= m.m0) and (st.joined_on is null or st.joined_on <= m.m1)
     group by st.id, m.m1)
  select s.id, s.full_name, s.designation, s.monthly, s.days, s.present, s.half_day, s.leave, s.unpaid_leave, s.off, s.absent,
         greatest(least(s.days, least(coalesce(s.left_on, (select m1 from m)), (select m1 from m), (now() at time zone 'Asia/Kolkata')::date)
                                 - greatest(coalesce(s.joined_on, (select m0 from m)), (select m0 from m)) + 1) - s.marked, 0),
         s.overtime,
         s.present + s.leave + s.off + 0.5 * s.half_day,
         round(s.monthly / s.days * (s.present + s.leave + s.off + 0.5 * s.half_day) + s.overtime * s.monthly / s.days / 8, 0),
         coalesce((select sum(amount) from public.salaries sl where sl.staff_id = s.id and sl.month = (select m0 from m)), 0),
         round(s.monthly / s.days * (s.present + s.leave + s.off + 0.5 * s.half_day) + s.overtime * s.monthly / s.days / 8, 0)
           - coalesce((select sum(amount) from public.salaries sl where sl.staff_id = s.id and sl.month = (select m0 from m)), 0)
    from s order by s.full_name
$$;
revoke all on function public.hr_salary_rows(uuid, date) from public, anon, authenticated;

create or replace function public.hr_salary_sheet(p_month date)
returns table (staff_id uuid, name text, designation text, monthly numeric, days int, present int, half_day int, leave int, unpaid_leave int, off int,
               absent int, not_marked int, overtime numeric, paid_days numeric, payable numeric, paid numeric, due numeric)
language sql stable security definer set search_path = public as $$
  select * from public.hr_salary_rows(public.my_hospital(), p_month) where public.has_role('{doctor,admin,hr,accountant}')
$$;
revoke all on function public.hr_salary_sheet(date) from public, anon;
grant execute on function public.hr_salary_sheet(date) to authenticated;

create or replace function public.hr_pay_salary(p_staff uuid, p_month date, p_amount numeric, p_method text, p_note text default null) returns public.salaries
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); r record; s public.salaries; e public.expenses; m0 date := date_trunc('month', p_month)::date;
begin
  if not public.has_role('{doctor,admin,accountant}') then raise exception 'Salary sirf Doctor / Admin / Accountant de sakte hain'; end if;
  if m0 > date_trunc('month', now() at time zone 'Asia/Kolkata')::date then raise exception 'Aage ke mahine ki salary nahi'; end if;
  if p_method not in ('cash','upi','bank','other') then raise exception 'Tarika chunein'; end if;
  p_amount := round(coalesce(p_amount, 0), 2);
  if p_amount <= 0 then raise exception 'Rakam 0 se zyada'; end if;
  select * into r from public.hr_salary_rows(h, m0) x where x.staff_id = p_staff;
  if r.staff_id is null then raise exception 'Staff is mahine ki list mein nahi'; end if;
  if p_amount > r.due and not public.has_role('{doctor}') then
    raise exception 'Baaki sirf ₹% banta hai — isse zyada (advance) sirf Doctor de sakte hain', r.due; end if;
  if p_amount > r.due and coalesce(trim(p_note), '') = '' then raise exception 'Zyada / advance dene ka kaaran likhein'; end if;
  insert into public.expenses(hospital_id, category, amount, paid_to, method, note, spent_on, created_by)
  values (h, 'Salary', p_amount, r.name, p_method, 'Salary ' || to_char(m0, 'Mon YYYY') || coalesce(' · ' || nullif(trim(p_note), ''), ''),
          (now() at time zone 'Asia/Kolkata')::date, auth.uid()) returning * into e;
  insert into public.salaries(hospital_id, staff_id, month, amount, method, paid_by, note, expense_id)
  values (h, p_staff, m0, p_amount, p_method, auth.uid(), nullif(trim(p_note), ''), e.id) returning * into s;
  return s;
end $$;
revoke all on function public.hr_pay_salary(uuid, date, numeric, text, text) from public, anon;
grant execute on function public.hr_pay_salary(uuid, date, numeric, text, text) to authenticated;

-- ---------- Operations: equipment + repair tickets ----------
create table if not exists public.ops_assets (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  name text not null,
  location text,
  serial_no text,
  vendor text,
  vendor_phone text,
  last_service date,
  service_every_days int check (service_every_days between 7 and 1095),
  status text not null default 'working' check (status in ('working','down','retired')),
  created_at timestamptz not null default now()
);
create table if not exists public.ops_tickets (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  ticket_no int not null,
  title text not null,
  location text,
  asset_id uuid references public.ops_assets(id),
  priority text not null default 'normal' check (priority in ('urgent','normal','low')),
  status text not null default 'open' check (status in ('open','in_progress','done','cancelled')),
  reported_by uuid not null references auth.users(id),
  assigned_to text,
  done_note text,
  cost numeric(12,2) check (cost >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  closed_at timestamptz
);
create index if not exists ops_tickets_idx on public.ops_tickets(hospital_id, status, created_at desc);
do $$
declare t text;
begin
  foreach t in array array['ops_assets','ops_tickets'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists p_read on public.%I', t);
    execute format('create policy p_read on public.%I for select to authenticated using (hospital_id = public.my_hospital() and public.my_role() <> ''pending'')', t);
    execute format('revoke all on public.%I from anon', t);
    execute format('revoke insert, update, delete on public.%I from authenticated', t);
    execute format('grant select on public.%I to authenticated', t);
    execute format('drop trigger if exists audit on public.%I', t);
    execute format('create trigger audit after insert or update on public.%I for each row execute function public.audit_row()', t);
    execute format('drop trigger if exists no_delete on public.%I', t);
    execute format('create trigger no_delete before delete on public.%I for each row execute function public.block_delete()', t);
  end loop;
end $$;

create or replace function public.ops_save_asset(p_id uuid, p_name text, p_location text, p_serial text, p_vendor text, p_vendor_phone text,
  p_last_service date, p_every int, p_status text) returns public.ops_assets
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); a public.ops_assets;
begin
  if not public.has_role('{doctor,admin,hr}') then raise exception 'Equipment list sirf Doctor / Admin / HR badal sakte hain'; end if;
  if coalesce(trim(p_name), '') = '' then raise exception 'Machine / saaman ka naam likhein'; end if;
  if p_last_service > (now() at time zone 'Asia/Kolkata')::date then raise exception 'Service ki date aage ki nahi ho sakti'; end if;
  if p_id is null then
    insert into public.ops_assets(hospital_id, name, location, serial_no, vendor, vendor_phone, last_service, service_every_days, status)
    values (h, trim(p_name), nullif(trim(p_location), ''), nullif(trim(p_serial), ''), nullif(trim(p_vendor), ''), nullif(trim(p_vendor_phone), ''),
            p_last_service, p_every, coalesce(p_status, 'working')) returning * into a;
  else
    update public.ops_assets set name = trim(p_name), location = nullif(trim(p_location), ''), serial_no = nullif(trim(p_serial), ''),
           vendor = nullif(trim(p_vendor), ''), vendor_phone = nullif(trim(p_vendor_phone), ''), last_service = p_last_service,
           service_every_days = p_every, status = coalesce(p_status, status)
     where id = p_id and hospital_id = h returning * into a;
    if a.id is null then raise exception 'Machine nahi mili'; end if;
  end if;
  return a;
end $$;
revoke all on function public.ops_save_asset(uuid, text, text, text, text, text, date, int, text) from public, anon;
grant execute on function public.ops_save_asset(uuid, text, text, text, text, text, date, int, text) to authenticated;

create or replace function public.ops_open_ticket(p_title text, p_location text, p_asset uuid, p_priority text) returns public.ops_tickets
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); t public.ops_tickets;
begin
  if h is null or public.my_role() = 'pending' then raise exception 'Permission nahi'; end if;
  if length(coalesce(trim(p_title), '')) < 3 then raise exception 'Kya kharab hai, likhein'; end if;
  if p_asset is not null and not exists (select 1 from public.ops_assets where id = p_asset and hospital_id = h) then raise exception 'Machine nahi mili'; end if;
  insert into public.ops_tickets(hospital_id, ticket_no, title, location, asset_id, priority, reported_by)
  values (h, public.next_number(h, 'ops_ticket'), left(trim(p_title), 300), nullif(trim(p_location), ''), p_asset, coalesce(p_priority, 'normal'), auth.uid())
  returning * into t;
  if p_asset is not null and p_priority = 'urgent' then update public.ops_assets set status = 'down' where id = p_asset; end if;
  perform public.agent_notify(h, 'admin', case when t.priority = 'urgent' then 'warning' else 'info' end, '🛠️ #' || t.ticket_no || ' ' || t.title, coalesce(t.location, ''), 'agent:ops:ticket:' || t.id);
  if t.priority = 'urgent' then
    perform public.agent_notify(h, 'doctor', 'warning', '🛠️ URGENT #' || t.ticket_no || ' ' || t.title, coalesce(t.location, ''), 'agent:ops:ticket:' || t.id);
  end if;
  return t;
end $$;
revoke all on function public.ops_open_ticket(text, text, uuid, text) from public, anon;
grant execute on function public.ops_open_ticket(text, text, uuid, text) to authenticated;

create or replace function public.ops_update_ticket(p_id uuid, p_status text, p_assigned text default null, p_note text default null, p_cost numeric default null)
returns public.ops_tickets
language plpgsql security definer set search_path = public as $$
declare t public.ops_tickets;
begin
  if not public.has_role('{doctor,admin,hr}') and not exists (select 1 from public.ops_tickets where id = p_id and reported_by = auth.uid()) then
    raise exception 'Ticket sirf Doctor / Admin / HR ya likhne wala badal sakta hai'; end if;
  if p_status not in ('open','in_progress','done','cancelled') then raise exception 'Status galat'; end if;
  if p_status = 'done' and coalesce(trim(p_note), '') = '' then raise exception 'Kya theek kiya, likhein'; end if;
  if p_cost is not null and (p_cost < 0 or p_cost > 10000000) then raise exception 'Kharcha galat'; end if;
  update public.ops_tickets set status = p_status, assigned_to = coalesce(nullif(trim(p_assigned), ''), assigned_to),
         done_note = coalesce(nullif(trim(p_note), ''), done_note), cost = coalesce(p_cost, cost), updated_at = now(),
         closed_at = case when p_status in ('done','cancelled') then now() else null end
   where id = p_id and hospital_id = public.my_hospital() and status not in ('done','cancelled') returning * into t;
  if t.id is null then raise exception 'Khula ticket nahi mila'; end if;
  if p_status = 'done' and t.asset_id is not null then
    update public.ops_assets set status = 'working' where id = t.asset_id and status = 'down'
      and not exists (select 1 from public.ops_tickets x where x.asset_id = t.asset_id and x.id <> t.id and x.status in ('open','in_progress') and x.priority = 'urgent');
  end if;
  insert into public.notifications(hospital_id, target_user, level, title, body, source)
  select t.hospital_id, t.reported_by, 'info', '🛠️ #' || t.ticket_no || ': ' || case p_status when 'done' then 'theek ho gaya ✓' when 'in_progress' then 'kaam shuru' when 'cancelled' then 'cancel' else 'khula' end,
         coalesce(t.done_note, t.title), 'agent:ops:ticket:' || t.id || ':' || p_status
   where t.reported_by <> auth.uid();
  return t;
end $$;
revoke all on function public.ops_update_ticket(uuid, text, text, text, numeric) from public, anon;
grant execute on function public.ops_update_ticket(uuid, text, text, text, numeric) to authenticated;

-- ---------- Procurement (non-medicine purchases) ----------
alter table public.purchases add column if not exists purpose text not null default 'pharmacy';
do $$ begin
  alter table public.purchases add constraint purchases_purpose_chk check (purpose in ('pharmacy','general'));
exception when duplicate_object then null; end $$;
alter table public.purchases add column if not exists note text;
alter table public.purchases add column if not exists decision_note text;
alter table public.purchases add column if not exists expense_id uuid references public.expenses(id);
-- requester can see own requests
drop policy if exists p_read_own on public.purchases;
create policy p_read_own on public.purchases for select to authenticated using (hospital_id = public.my_hospital() and created_by = auth.uid());
drop policy if exists p_read_own on public.purchase_items;
create policy p_read_own on public.purchase_items for select to authenticated
  using (exists (select 1 from public.purchases p where p.id = purchase_items.purchase_id and p.created_by = auth.uid()));
-- doctor/admin/hr/accountant see general purchases
drop policy if exists p_read_general on public.purchases;
create policy p_read_general on public.purchases for select to authenticated
  using (hospital_id = public.my_hospital() and purpose = 'general' and public.has_role('{doctor,admin,hr,accountant}'));
drop policy if exists p_read_general on public.purchase_items;
create policy p_read_general on public.purchase_items for select to authenticated
  using (exists (select 1 from public.purchases p where p.id = purchase_items.purchase_id and p.purpose = 'general') and public.has_role('{doctor,admin,hr,accountant}'));

-- p_items: [{ "description": "A4 paper 5 rim", "quantity": 1, "rate": 1200 }]
create or replace function public.proc_request(p_supplier text, p_items jsonb, p_note text) returns public.purchases
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); p public.purchases; s uuid; x jsonb; tot numeric := 0; q int; r numeric;
begin
  if h is null or public.my_role() = 'pending' then raise exception 'Permission nahi'; end if;
  if jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) = 0 then raise exception 'Kam se kam ek cheez likhein'; end if;
  if jsonb_array_length(p_items) > 50 then raise exception 'Ek baar mein 50 cheez tak'; end if;
  if coalesce(trim(p_note), '') = '' then raise exception 'Kis kaam ke liye chahiye, likhein'; end if;
  if coalesce(trim(p_supplier), '') <> '' then
    insert into public.suppliers(hospital_id, name) values (h, trim(p_supplier)) on conflict (hospital_id, name) do nothing;
    select id into s from public.suppliers where hospital_id = h and name = trim(p_supplier);
  end if;
  insert into public.purchases(hospital_id, supplier_id, kind, status, purpose, note, total, created_by)
  values (h, s, 'request', 'pending_approval', 'general', trim(p_note), 0, auth.uid()) returning * into p;
  for x in select * from jsonb_array_elements(p_items) loop
    q := coalesce((x->>'quantity')::int, 0); r := coalesce(nullif(x->>'rate', '')::numeric, 0);
    if coalesce(trim(x->>'description'), '') = '' then raise exception 'Har cheez ka naam likhein'; end if;
    if q <= 0 or q > 100000 or r < 0 or r > 10000000 then raise exception '%: quantity / rate galat', x->>'description'; end if;
    insert into public.purchase_items(hospital_id, purchase_id, description, quantity, rate) values (h, p.id, left(trim(x->>'description'), 200), q, r);
    tot := tot + q * r;
  end loop;
  update public.purchases set total = round(tot, 2) where id = p.id returning * into p;
  perform public.agent_notify(h, 'doctor', 'info', '🛒 Kharid ki maang: ₹' || to_char(tot, 'FM99,99,990'), trim(p_note), 'agent:proc:' || p.id);
  perform public.agent_notify(h, 'admin', 'info', '🛒 Kharid ki maang: ₹' || to_char(tot, 'FM99,99,990'), trim(p_note), 'agent:proc:' || p.id);
  return p;
end $$;
revoke all on function public.proc_request(text, jsonb, text) from public, anon;
grant execute on function public.proc_request(text, jsonb, text) to authenticated;

create or replace function public.proc_decide(p_id uuid, p_approve boolean, p_note text default null) returns public.purchases
language plpgsql security definer set search_path = public as $$
declare p public.purchases;
begin
  if not public.has_role('{doctor,admin}') then raise exception 'Kharid sirf Doctor / Admin manzoor kar sakte hain'; end if;
  select * into p from public.purchases where id = p_id and hospital_id = public.my_hospital() and purpose = 'general' for update;
  if p.id is null or p.status <> 'pending_approval' then raise exception 'Khuli maang nahi mili'; end if;
  if p.created_by = auth.uid() and p.total > 5000 and not public.has_role('{doctor}') then raise exception '₹5000 se badi apni maang khud manzoor nahi kar sakte'; end if;
  if not p_approve and coalesce(trim(p_note), '') = '' then raise exception 'Mana karne ka kaaran likhein'; end if;
  update public.purchases set status = case when p_approve then 'approved' else 'cancelled' end, approved_by = case when p_approve then auth.uid() end,
         decision_note = nullif(trim(p_note), '') where id = p.id returning * into p;
  insert into public.notifications(hospital_id, target_user, level, title, body, source)
  values (p.hospital_id, p.created_by, 'info', case when p_approve then '✅ Kharid manzoor' else '❌ Kharid mana' end, coalesce(p_note, p.note), 'agent:proc:' || p.id || ':d');
  return p;
end $$;
revoke all on function public.proc_decide(uuid, boolean, text) from public, anon;
grant execute on function public.proc_decide(uuid, boolean, text) to authenticated;

create or replace function public.proc_receive(p_id uuid, p_invoice_no text, p_amount numeric, p_method text) returns public.purchases
language plpgsql security definer set search_path = public as $$
declare p public.purchases; e public.expenses; sup text;
begin
  if not public.has_role('{doctor,admin,accountant,hr}') then raise exception 'Permission nahi'; end if;
  select * into p from public.purchases where id = p_id and hospital_id = public.my_hospital() and purpose = 'general' for update;
  if p.id is null or p.status <> 'approved' then raise exception 'Manzoor hui kharid nahi mili'; end if;
  if p_amount is not null and p_amount > 0 then
    if not public.has_role('{doctor,admin,accountant}') then raise exception 'Paisa sirf Doctor / Admin / Accountant de sakte hain'; end if;
    if p_method not in ('cash','upi','card','bank','other') then raise exception 'Tarika chunein'; end if;
    if p_amount > p.total * 1.2 + 100 and not public.has_role('{doctor}') then raise exception 'Manzoor rakam (₹%) se bahut zyada — Doctor se karwayein', p.total; end if;
    select name into sup from public.suppliers where id = p.supplier_id;
    insert into public.expenses(hospital_id, category, amount, paid_to, method, note, spent_on, created_by)
    values (p.hospital_id, 'Purchase', round(p_amount, 2), sup, p_method, 'Kharid: ' || p.note || coalesce(' · bill ' || nullif(trim(p_invoice_no), ''), ''),
            (now() at time zone 'Asia/Kolkata')::date, auth.uid()) returning * into e;
  end if;
  update public.purchases set status = 'received', supplier_invoice_no = nullif(trim(p_invoice_no), ''), expense_id = e.id where id = p.id returning * into p;
  return p;
end $$;
revoke all on function public.proc_receive(uuid, text, numeric, text) from public, anon;
grant execute on function public.proc_receive(uuid, text, numeric, text) to authenticated;

-- ---------- AI handlers (read-only) ----------
create or replace function public.agent_h_hr_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; tot int; pr int; ab int; lv int; nm int; pend int; items jsonb;
begin
  select count(*), count(*) filter (where a.status in ('present','half_day')), count(*) filter (where a.status = 'absent'),
         count(*) filter (where a.status = 'leave'), count(*) filter (where a.id is null),
         coalesce(jsonb_agg(jsonb_build_object('staff', s.full_name, 'pad', s.designation, 'hazri', coalesce(a.status, 'nahi lagi'),
                  'check_in', to_char(a.check_in at time zone 'Asia/Kolkata', 'HH12:MI AM')) order by s.full_name), '[]')
    into tot, pr, ab, lv, nm, items
    from public.staff_members s left join public.attendance a on a.staff_id = s.id and a.day = d
   where s.hospital_id = h and s.active;
  select count(*) into pend from public.leave_requests where hospital_id = h and status = 'pending';
  return jsonb_build_object('summary', case when tot = 0 then 'Staff list khaali hai (HR → Staff mein jodein)'
           else pr || '/' || tot || ' staff haazir · ' || ab || ' gair-haazir · ' || lv || ' chhutti' || case when nm > 0 then ' · ' || nm || ' ki hazri nahi lagi' else '' end
                || case when pend > 0 then ' · ' || pend || ' chhutti arzi baaki' else '' end end,
    'items', items, 'alert', pend > 0 or (nm > 0 and extract(hour from now() at time zone 'Asia/Kolkata') >= 11), 'alert_role', 'hr');
end $$;

create or replace function public.agent_h_salary_due(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare m date := coalesce(nullif(inp->>'month','')::date, (date_trunc('month', now() at time zone 'Asia/Kolkata') - interval '1 month')::date); items jsonb; n int; amt numeric;
begin
  select coalesce(jsonb_agg(jsonb_build_object('staff', name, 'banta', payable, 'diya', paid, 'baaki', due, 'paid_days', paid_days, 'absent', absent, 'hazri_nahi_lagi', not_marked)), '[]'),
         count(*) filter (where due > 0), coalesce(sum(due) filter (where due > 0), 0)
    into items, n, amt from public.hr_salary_rows(h, m);
  return jsonb_build_object('summary', to_char(m, 'Mon YYYY') || ': ' || n || ' staff ki salary baaki · ₹' || to_char(amt, 'FM99,99,990'), 'items', items, 'alert', false);
end $$;

create or replace function public.agent_h_ops_tickets(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare tk jsonb; nt int; nu int; sv jsonb; ns int; dn int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('no', ticket_no, 'kya', title, 'kahan', location, 'priority', priority, 'status', status,
           'din', (now()::date - created_at::date)) order by priority = 'urgent' desc, created_at), '[]'),
         count(*), count(*) filter (where priority = 'urgent')
    into tk, nt, nu from public.ops_tickets where hospital_id = h and status in ('open','in_progress');
  select coalesce(jsonb_agg(jsonb_build_object('machine', name, 'kahan', location, 'service_due', last_service + service_every_days, 'vendor', vendor, 'phone', vendor_phone)
           order by last_service + service_every_days), '[]'), count(*)
    into sv, ns from public.ops_assets
   where hospital_id = h and status <> 'retired' and service_every_days is not null and (last_service is null or last_service + service_every_days <= current_date + 7);
  select count(*) into dn from public.ops_assets where hospital_id = h and status = 'down';
  return jsonb_build_object('summary', nt || ' repair khule (' || nu || ' urgent) · ' || ns || ' machine ki service due · ' || dn || ' machine band',
    'items', jsonb_build_object('tickets', tk, 'service_due', sv), 'alert', nu > 0 or dn > 0, 'alert_role', 'admin');
end $$;

create or replace function public.agent_h_proc_pending(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; np int; na int; amt numeric;
begin
  select coalesce(jsonb_agg(jsonb_build_object('kya', p.note, 'rakam', p.total, 'status', p.status, 'maanga', pr.full_name,
           'din', (now()::date - p.created_at::date)) order by p.created_at), '[]'),
         count(*) filter (where p.status = 'pending_approval'), count(*) filter (where p.status = 'approved'),
         coalesce(sum(p.total) filter (where p.status = 'pending_approval'), 0)
    into items, np, na, amt
    from public.purchases p left join public.profiles pr on pr.id = p.created_by
   where p.hospital_id = h and p.purpose = 'general' and p.status in ('pending_approval','approved');
  return jsonb_build_object('summary', np || ' kharid manzoori ke liye (₹' || to_char(amt, 'FM99,99,990') || ') · ' || na || ' manzoor, maal aana baaki',
                            'items', items, 'alert', np > 0, 'alert_role', 'doctor');
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('hr.today','hr','Aaj ki hazri','Aaj kaun haazir, gair-haazir, chhutti par, kiski hazri nahi lagi, chhutti ki baaki arzi','check','low','{doctor,admin,hr}','{}','{staff_members,attendance,leave_requests}',13,'agent_h_hr_today', null),
 ('hr.salary_due','hr','Salary baaki','Pichhle (ya chune) mahine ki banti salary, di gayi, baaki','check','low','{doctor,admin,hr,accountant}','{}','{staff_members,attendance,salaries}',14,'agent_h_salary_due',
   '{"type":"object","properties":{"month":{"type":"string","description":"YYYY-MM-01 (khaali = pichhla mahina)"}}}'),
 ('operations.tickets','operations','Repair aur service','Khule repair / shikayat, service due machine, band machine','check','low','{doctor,admin,hr,nurse,receptionist}','{}','{ops_tickets,ops_assets}',15,'agent_h_ops_tickets', null),
 ('procurement.pending','procurement','Kharid baaki','Manzoori ke liye kharid ki maang, aur manzoor par maal aana baaki','check','low','{doctor,admin,accountant,hr}','{}','{purchases,purchase_items}',16,'agent_h_proc_pending', null)
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;

update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{leave_requests,departments}')) where id = 'hr';
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{ops_tickets,ops_assets}')) where id = 'operations';
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{expenses}')) where id = 'procurement';
insert into public.ai_chat_agents(agent_id, title, roles, tools) values
 ('hr','HR AI','{doctor,admin,hr}','{hr.today,hr.salary_due}'),
 ('procurement','Kharid AI','{doctor,admin,accountant,hr}','{procurement.pending,pharmacy.reorder}')
on conflict (agent_id) do update set title=excluded.title, roles=excluded.roles, tools=excluded.tools;
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{operations.tickets}')) where agent_id = 'operations';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{hr.today,operations.tickets,procurement.pending}')) where agent_id = 'boss';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{hr.salary_due}')) where agent_id = 'accountant';

-- 11:00 AM IST: hazri not marked → HR reminder; 9:00 AM: service due / urgent repairs → admin
create or replace function public.hr_morning_job() returns void
language plpgsql security definer set search_path = public as $$
declare h uuid; d date := (now() at time zone 'Asia/Kolkata')::date; n int;
begin
  for h in select id from public.hospitals loop
    select count(*) into n from public.staff_members s where s.hospital_id = h and s.active
       and not exists (select 1 from public.attendance a where a.staff_id = s.id and a.day = d);
    if n > 0 then
      perform public.agent_notify(h, 'hr', 'warning', '🕚 ' || n || ' staff ki aaj hazri nahi lagi', 'HR → Hazri mein laga dein.', 'agent:hr:att:' || d);
    end if;
  end loop;
end $$;
revoke all on function public.hr_morning_job() from public, anon, authenticated;
do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname in ('vatte_hr_attendance','vatte_ops_morning');
  perform cron.schedule('vatte_hr_attendance', '30 5 * * *', $c$select public.hr_morning_job()$c$);              -- 11:00 AM IST
  perform cron.schedule('vatte_ops_morning', '30 3 * * *', $c$select public.agent_cron('operations.tickets')$c$);  -- 9:00 AM IST
end $$;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;
