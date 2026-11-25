-- =========================================================
-- NIDAN HOSPITAL OS — PHASE 2 DATABASE
-- All core hospital tables + per-hospital isolation + role rules,
-- tamper-proof clinical & money records, UHID, no double booking,
-- automatic audit log, AI agent registry.
-- Requires phase1.sql first.
-- =========================================================

create extension if not exists btree_gist;

-- ---------- helpers ----------
create or replace function public.has_role(roles text[]) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select role from public.profiles where id = auth.uid()) = any(roles), false)
$$;
revoke execute on function public.has_role(text[]) from public, anon;
grant execute on function public.has_role(text[]) to authenticated;

-- Block edits/deletes on records that must never change (corrections = new row).
create or replace function public.block_change() returns trigger
language plpgsql as $$
begin
  raise exception '% records cannot be changed or deleted. Add a correction entry instead.', tg_table_name;
end $$;

-- Block deletes only.
create or replace function public.block_delete() returns trigger
language plpgsql as $$
begin
  raise exception '% records cannot be deleted.', tg_table_name;
end $$;

-- Audit every insert/update/delete (stores ids + what changed, not full patient data).
create or replace function public.audit_row() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  rec jsonb := to_jsonb(coalesce(new, old));
  changed text[];
begin
  if tg_op = 'UPDATE' then
    select array_agg(n.key) into changed
    from jsonb_each(to_jsonb(new)) n join jsonb_each(to_jsonb(old)) o using (key)
    where n.value is distinct from o.value;
  end if;
  insert into public.audit_logs(hospital_id, actor_id, action, details)
  values ((rec->>'hospital_id')::uuid, auth.uid(), lower(tg_op) || ':' || tg_table_name,
          jsonb_build_object('row_id', rec->>'id', 'changed', changed));
  return coalesce(new, old);
end $$;
revoke execute on function public.audit_row() from public, anon, authenticated;

-- ---------- structure ----------
create table if not exists public.departments (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  name text not null,
  created_at timestamptz not null default now(),
  unique (hospital_id, name)
);

create table if not exists public.staff_members (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  profile_id uuid references public.profiles(id) on delete set null,
  department_id uuid references public.departments(id),
  full_name text not null,
  designation text not null,
  phone text,
  joined_on date,
  monthly_salary numeric(12,2) check (monthly_salary >= 0),
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.hospital_counters (
  hospital_id uuid not null references public.hospitals(id),
  name text not null,
  value bigint not null default 0,
  primary key (hospital_id, name)
);

create or replace function public.next_number(h uuid, counter text) returns bigint
language plpgsql security definer set search_path = public as $$
declare v bigint;
begin
  insert into public.hospital_counters(hospital_id, name, value) values (h, counter, 1)
  on conflict (hospital_id, name) do update set value = hospital_counters.value + 1
  returning value into v;
  return v;
end $$;
revoke execute on function public.next_number(uuid, text) from public, anon, authenticated;

-- ---------- patients ----------
create table if not exists public.patients (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  uhid text,
  full_name text not null,
  gender text check (gender in ('male','female','other')),
  dob date,
  age_years int check (age_years between 0 and 130),
  phone text,
  address text,
  abha_id text,
  allergies text,
  blood_group text,
  created_by uuid default auth.uid() references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  unique (hospital_id, uhid)
);
create index if not exists patients_phone_idx on public.patients(hospital_id, phone);
create index if not exists patients_name_idx on public.patients(hospital_id, lower(full_name));

create or replace function public.set_uhid() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.uhid is null or new.uhid = '' then
    new.uhid := 'NH' || to_char(now() at time zone 'Asia/Kolkata', 'YY')
                || lpad(public.next_number(new.hospital_id, 'uhid')::text, 6, '0');
  end if;
  return new;
end $$;
drop trigger if exists patients_uhid on public.patients;
create trigger patients_uhid before insert on public.patients
  for each row execute function public.set_uhid();

create table if not exists public.encounters (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  kind text not null check (kind in ('opd','ipd','emergency')),
  status text not null default 'open' check (status in ('open','closed','cancelled')),
  doctor_id uuid references public.profiles(id),
  chief_complaint text,
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  created_by uuid default auth.uid() references auth.users(id) on delete set null
);
create index if not exists encounters_patient_idx on public.encounters(patient_id, started_at desc);
create index if not exists encounters_day_idx on public.encounters(hospital_id, started_at desc);

-- ---------- appointments (no double booking) ----------
create table if not exists public.appointments (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  doctor_id uuid not null references public.profiles(id),
  starts_at timestamptz not null,
  ends_at timestamptz not null,
  status text not null default 'booked'
    check (status in ('booked','checked_in','completed','cancelled','missed')),
  reason text,
  created_by uuid default auth.uid() references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  check (ends_at > starts_at),
  constraint no_double_booking exclude using gist (
    doctor_id with =, tstzrange(starts_at, ends_at) with &&
  ) where (status in ('booked','checked_in'))
);
create index if not exists appointments_day_idx on public.appointments(hospital_id, starts_at);

-- ---------- rooms, beds, admissions ----------
create table if not exists public.rooms (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  name text not null,
  kind text not null default 'ward' check (kind in ('ward','private','icu','ot','opd','other')),
  unique (hospital_id, name)
);

create table if not exists public.beds (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  room_id uuid not null references public.rooms(id),
  label text not null,
  status text not null default 'available'
    check (status in ('available','occupied','cleaning','blocked')),
  unique (room_id, label)
);

create table if not exists public.admissions (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  bed_id uuid references public.beds(id),
  admitted_at timestamptz not null default now(),
  discharged_at timestamptz,
  status text not null default 'admitted' check (status in ('admitted','discharged','transferred','lama','expired')),
  discharge_summary text,
  created_by uuid default auth.uid() references auth.users(id) on delete set null
);
create unique index if not exists one_patient_per_bed
  on public.admissions(bed_id) where status = 'admitted';

-- ---------- clinical records ----------
create table if not exists public.vitals (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  bp_systolic int check (bp_systolic between 30 and 300),
  bp_diastolic int check (bp_diastolic between 10 and 200),
  pulse int check (pulse between 10 and 300),
  temperature_f numeric(4,1) check (temperature_f between 85 and 115),
  spo2 int check (spo2 between 30 and 100),
  resp_rate int check (resp_rate between 2 and 80),
  intake_ml int check (intake_ml >= 0),
  output_ml int check (output_ml >= 0),
  corrects_id uuid references public.vitals(id),
  recorded_by uuid not null default auth.uid() references auth.users(id),
  recorded_at timestamptz not null default now()
);
create index if not exists vitals_patient_idx on public.vitals(patient_id, recorded_at desc);

create table if not exists public.nursing_notes (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  kind text not null default 'note' check (kind in ('note','handover','incident')),
  note text not null,
  corrects_id uuid references public.nursing_notes(id),
  created_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.doctor_orders (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  order_text text not null,
  status text not null default 'active' check (status in ('active','done','stopped')),
  ordered_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.prescriptions (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  items jsonb not null default '[]'::jsonb,  -- [{medicine, dose, frequency, days, notes}]
  advice text,
  prescribed_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.medication_administrations (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  order_id uuid references public.doctor_orders(id),
  medicine_name text not null,
  dose text not null,
  route text,
  status text not null default 'given' check (status in ('given','held','refused','missed')),
  remarks text,
  given_by uuid not null default auth.uid() references auth.users(id),
  given_at timestamptz not null default now()
);

create table if not exists public.medical_documents (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  title text not null,
  kind text check (kind in ('report','discharge_summary','prescription','image','consent','other')),
  storage_path text not null,
  uploaded_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

-- ---------- laboratory ----------
create table if not exists public.lab_tests (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  name text not null,
  price numeric(10,2) not null default 0 check (price >= 0),
  normal_range text,
  active boolean not null default true,
  unique (hospital_id, name)
);

create table if not exists public.lab_orders (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  test_id uuid not null references public.lab_tests(id),
  status text not null default 'ordered'
    check (status in ('ordered','sample_collected','processing','reported','cancelled')),
  result text,
  is_critical boolean not null default false,
  ordered_by uuid not null default auth.uid() references auth.users(id),
  ordered_at timestamptz not null default now(),
  sample_collected_at timestamptz,
  reported_by uuid references auth.users(id),
  reported_at timestamptz
);
create index if not exists lab_orders_status_idx on public.lab_orders(hospital_id, status);

-- ---------- pharmacy & procurement ----------
create table if not exists public.suppliers (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  name text not null,
  phone text,
  gstin text,
  address text,
  unique (hospital_id, name)
);

create table if not exists public.medicines (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  name text not null,
  generic_name text,
  form text,
  strength text,
  mrp numeric(10,2) check (mrp >= 0),
  reorder_level int not null default 10 check (reorder_level >= 0),
  active boolean not null default true,
  unique (hospital_id, name, strength)
);

create table if not exists public.medicine_batches (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  medicine_id uuid not null references public.medicines(id),
  batch_no text not null,
  expiry_date date not null,
  quantity int not null check (quantity >= 0),
  purchase_price numeric(10,2) check (purchase_price >= 0),
  mrp numeric(10,2) check (mrp >= 0),
  unique (medicine_id, batch_no)
);
create index if not exists batches_expiry_idx on public.medicine_batches(hospital_id, expiry_date);

create table if not exists public.purchases (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  supplier_id uuid references public.suppliers(id),
  kind text not null default 'order' check (kind in ('request','quotation','order','received')),
  status text not null default 'draft' check (status in ('draft','pending_approval','approved','received','cancelled')),
  supplier_invoice_no text,
  total numeric(12,2) not null default 0 check (total >= 0),
  approved_by uuid references auth.users(id),
  created_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.purchase_items (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  purchase_id uuid not null references public.purchases(id) on delete cascade,
  medicine_id uuid references public.medicines(id),
  description text,
  quantity int not null check (quantity > 0),
  rate numeric(10,2) not null check (rate >= 0)
);

-- ---------- money (append-only) ----------
create table if not exists public.invoices (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  invoice_no text,
  patient_id uuid references public.patients(id),
  encounter_id uuid references public.encounters(id),
  category text not null check (category in ('opd','ipd','pharmacy','lab','other')),
  total numeric(12,2) not null default 0 check (total >= 0),
  discount numeric(12,2) not null default 0 check (discount >= 0),
  status text not null default 'unpaid' check (status in ('unpaid','partial','paid','cancelled')),
  cancel_reason text,
  created_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now(),
  unique (hospital_id, invoice_no)
);

create or replace function public.set_invoice_no() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.invoice_no is null or new.invoice_no = '' then
    new.invoice_no := 'INV' || to_char(now() at time zone 'Asia/Kolkata', 'YYMM')
                      || lpad(public.next_number(new.hospital_id, 'invoice')::text, 6, '0');
  end if;
  return new;
end $$;
drop trigger if exists invoices_no on public.invoices;
create trigger invoices_no before insert on public.invoices
  for each row execute function public.set_invoice_no();

create table if not exists public.invoice_items (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  invoice_id uuid not null references public.invoices(id),
  description text not null,
  batch_id uuid references public.medicine_batches(id),
  lab_order_id uuid references public.lab_orders(id),
  quantity int not null default 1 check (quantity > 0),
  rate numeric(10,2) not null check (rate >= 0)
);

create table if not exists public.payments (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  invoice_id uuid references public.invoices(id),
  amount numeric(12,2) not null check (amount <> 0),   -- negative = refund/correction
  method text not null check (method in ('cash','upi','card','bank','other')),
  reference text,
  reverses_id uuid references public.payments(id),
  note text,
  received_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists payments_day_idx on public.payments(hospital_id, created_at desc);

create table if not exists public.expenses (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  category text not null,
  amount numeric(12,2) not null check (amount <> 0),
  paid_to text,
  method text not null check (method in ('cash','upi','card','bank','other')),
  reverses_id uuid references public.expenses(id),
  note text,
  spent_on date not null default (now() at time zone 'Asia/Kolkata')::date,
  created_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.salaries (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  staff_id uuid not null references public.staff_members(id),
  month date not null,
  amount numeric(12,2) not null check (amount <> 0),
  method text not null check (method in ('cash','upi','card','bank','other')),
  reverses_id uuid references public.salaries(id),
  paid_by uuid not null default auth.uid() references auth.users(id),
  paid_at timestamptz not null default now()
);

-- ---------- HR ----------
create table if not exists public.attendance (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  staff_id uuid not null references public.staff_members(id),
  day date not null,
  status text not null check (status in ('present','absent','leave','half_day','off')),
  shift text check (shift in ('morning','evening','night','general')),
  check_in timestamptz,
  check_out timestamptz,
  overtime_hours numeric(4,1) not null default 0 check (overtime_hours >= 0),
  marked_by uuid default auth.uid() references auth.users(id),
  unique (staff_id, day)
);

-- ---------- follow-ups & notifications ----------
create table if not exists public.follow_ups (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  due_on date not null,
  reason text,
  status text not null default 'pending' check (status in ('pending','done','missed','cancelled')),
  feedback text,
  created_by uuid default auth.uid() references auth.users(id) on delete set null,
  created_at timestamptz not null default now()
);
create index if not exists follow_ups_due_idx on public.follow_ups(hospital_id, status, due_on);

create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  target_role text,
  target_user uuid references auth.users(id) on delete cascade,
  level text not null default 'info' check (level in ('info','warning','critical')),
  title text not null,
  body text,
  source text,
  read_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists notifications_target_idx on public.notifications(hospital_id, created_at desc);

-- ---------- AI agents ----------
create table if not exists public.agents (
  id text primary key,
  name text not null,
  department text not null,
  responsibilities text not null,
  allowed_tables text[] not null default '{}',
  status text not null default 'planned' check (status in ('planned','active','paused','error'))
);

create table if not exists public.agent_tasks (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  agent_id text not null references public.agents(id),
  requested_by uuid default auth.uid() references auth.users(id) on delete set null,
  parent_task_id uuid references public.agent_tasks(id),
  input jsonb not null default '{}'::jsonb,
  risk text not null default 'low' check (risk in ('low','controlled','high')),
  status text not null default 'queued'
    check (status in ('queued','running','waiting_approval','approved','rejected','done','failed')),
  approved_by uuid references auth.users(id),
  result jsonb,
  error text,
  attempts int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists agent_tasks_status_idx on public.agent_tasks(hospital_id, status, created_at desc);

create table if not exists public.agent_logs (
  id bigint generated always as identity primary key,
  hospital_id uuid not null references public.hospitals(id),
  task_id uuid references public.agent_tasks(id),
  agent_id text references public.agents(id),
  level text not null default 'info' check (level in ('info','warning','error')),
  message text not null,
  created_at timestamptz not null default now()
);

insert into public.agents(id, name, department, responsibilities, allowed_tables) values
 ('boss','Hospital Boss AI','Administration','Supervises all agents, collects reports, finds problems, informs doctor', '{agent_tasks,agent_logs,notifications}'),
 ('nurse','AI Nursing Sister','Nursing','Vitals, nursing notes, medication records, handover, abnormal vital alerts', '{patients,encounters,vitals,nursing_notes,medication_administrations,doctor_orders}'),
 ('appointment','AI Appointment Agent','Front Office','Book/cancel/reschedule, OPD queue, reminders, missed appointments', '{appointments,patients}'),
 ('reception','AI Receptionist','Front Office','Registration, UHID, patient search, OPD/IPD check-in/out', '{patients,encounters,admissions,beds}'),
 ('accountant','AI Accountant','Accounts','Billing, payments, expenses, reconciliation, P&L', '{invoices,invoice_items,payments,expenses,salaries}'),
 ('pharmacy','AI Pharmacy Manager','Pharmacy','Inventory, batches, expiry, stock alerts, sales', '{medicines,medicine_batches,suppliers,purchases,purchase_items,invoices,invoice_items}'),
 ('lab','AI Laboratory Manager','Laboratory','Test bookings, samples, reports, critical alerts', '{lab_tests,lab_orders}'),
 ('followup','AI Follow-up Manager','Patient Care','Discharge/OPD follow-ups, reminders, feedback', '{follow_ups,patients,appointments}'),
 ('hr','AI HR Manager','HR','Staff, attendance, shifts, leave, salary records', '{staff_members,attendance,salaries}'),
 ('operations','AI Operations Manager','Operations','Beds, rooms, ICU occupancy, equipment, housekeeping', '{rooms,beds,admissions}'),
 ('procurement','AI Procurement Manager','Procurement','Vendors, purchase requests, quotations, orders', '{suppliers,purchases,purchase_items}'),
 ('records','AI Medical Records Manager','Medical Records','History, prescriptions, investigations, allergies, documents', '{patients,prescriptions,lab_orders,medical_documents,admissions}'),
 ('quality','AI Quality & Compliance Manager','Quality','Checklists, audits, incidents, infection control, BMW records', '{audit_logs,nursing_notes}')
on conflict (id) do update set name = excluded.name, department = excluded.department,
  responsibilities = excluded.responsibilities, allowed_tables = excluded.allowed_tables;

-- ---------- Row Level Security (who can see / write what) ----------
-- rules: table, read roles, insert roles, update roles, delete roles
do $$
declare
  r record;
  all_staff text := '{doctor,admin,receptionist,nurse,accountant,pharmacist,lab,hr}';
begin
  for r in select * from (values
    ('departments',       all_staff,                                   '{doctor,admin}',                     '{doctor,admin}',            '{doctor,admin}'),
    ('staff_members',     '{doctor,admin,hr,accountant}',              '{doctor,admin,hr}',                  '{doctor,admin,hr}',         '{}'),
    ('patients',          all_staff,                                   '{doctor,admin,receptionist,nurse}',  '{doctor,admin,receptionist,nurse}', '{}'),
    ('encounters',        '{doctor,admin,receptionist,nurse,accountant,lab,pharmacist}', '{doctor,admin,receptionist,nurse}', '{doctor,admin,receptionist,nurse}', '{}'),
    ('appointments',      '{doctor,admin,receptionist,nurse}',         '{doctor,admin,receptionist}',        '{doctor,admin,receptionist}', '{}'),
    ('rooms',             all_staff,                                   '{doctor,admin}',                     '{doctor,admin}',            '{doctor,admin}'),
    ('beds',              all_staff,                                   '{doctor,admin}',                     '{doctor,admin,receptionist,nurse}', '{doctor,admin}'),
    ('admissions',        '{doctor,admin,receptionist,nurse,accountant}', '{doctor,admin,receptionist}',     '{doctor,admin,receptionist}', '{}'),
    ('vitals',            '{doctor,admin,nurse}',                      '{doctor,nurse}',                     '{}',                        '{}'),
    ('nursing_notes',     '{doctor,admin,nurse}',                      '{doctor,nurse}',                     '{}',                        '{}'),
    ('doctor_orders',     '{doctor,admin,nurse}',                      '{doctor}',                           '{doctor,nurse}',            '{}'),
    ('prescriptions',     '{doctor,admin,nurse,pharmacist}',           '{doctor}',                           '{}',                        '{}'),
    ('medication_administrations', '{doctor,admin,nurse}',             '{doctor,nurse}',                     '{}',                        '{}'),
    ('medical_documents', '{doctor,admin,nurse}',                      '{doctor,admin,nurse}',               '{}',                        '{}'),
    ('lab_tests',         all_staff,                                   '{doctor,admin,lab}',                 '{doctor,admin,lab}',        '{}'),
    ('lab_orders',        '{doctor,admin,nurse,lab,accountant}',       '{doctor,nurse,lab}',                 '{doctor,lab}',              '{}'),
    ('suppliers',         '{doctor,admin,pharmacist,accountant}',      '{doctor,admin,pharmacist}',          '{doctor,admin,pharmacist}', '{}'),
    ('medicines',         all_staff,                                   '{doctor,admin,pharmacist}',          '{doctor,admin,pharmacist}', '{}'),
    ('medicine_batches',  '{doctor,admin,pharmacist,nurse}',           '{doctor,admin,pharmacist}',          '{doctor,admin,pharmacist}', '{}'),
    ('purchases',         '{doctor,admin,pharmacist,accountant}',      '{doctor,admin,pharmacist}',          '{doctor,admin,pharmacist}', '{}'),
    ('purchase_items',    '{doctor,admin,pharmacist,accountant}',      '{doctor,admin,pharmacist}',          '{doctor,admin,pharmacist}', '{doctor,admin,pharmacist}'),
    ('invoices',          '{doctor,admin,accountant,receptionist,pharmacist,lab}', '{doctor,admin,accountant,receptionist,pharmacist,lab}', '{doctor,admin,accountant}', '{}'),
    ('invoice_items',     '{doctor,admin,accountant,receptionist,pharmacist,lab}', '{doctor,admin,accountant,receptionist,pharmacist,lab}', '{}', '{}'),
    ('payments',          '{doctor,admin,accountant,receptionist,pharmacist,lab}', '{doctor,admin,accountant,receptionist,pharmacist,lab}', '{}', '{}'),
    ('expenses',          '{doctor,admin,accountant}',                 '{doctor,admin,accountant}',          '{}',                        '{}'),
    ('salaries',          '{doctor,admin,accountant,hr}',              '{doctor,admin,accountant}',          '{}',                        '{}'),
    ('attendance',        '{doctor,admin,hr}',                         '{doctor,admin,hr}',                  '{doctor,admin,hr}',         '{}'),
    ('follow_ups',        '{doctor,admin,receptionist,nurse}',         '{doctor,admin,receptionist,nurse}',  '{doctor,admin,receptionist,nurse}', '{}'),
    ('agent_logs',        '{doctor,admin}',                            '{}',                                 '{}',                        '{}')
  ) as t(tbl, rd, ins, upd, del)
  loop
    execute format('alter table public.%I enable row level security', r.tbl);
    execute format('revoke all on public.%I from anon', r.tbl);
    execute format('drop policy if exists p_read on public.%I', r.tbl);
    execute format('drop policy if exists p_insert on public.%I', r.tbl);
    execute format('drop policy if exists p_update on public.%I', r.tbl);
    execute format('drop policy if exists p_delete on public.%I', r.tbl);
    execute format('grant select on public.%I to authenticated', r.tbl);
    execute format('create policy p_read on public.%I for select to authenticated
                    using (hospital_id = public.my_hospital() and public.has_role(%L))', r.tbl, r.rd);
    if r.ins <> '{}' then
      execute format('grant insert on public.%I to authenticated', r.tbl);
      execute format('create policy p_insert on public.%I for insert to authenticated
                      with check (hospital_id = public.my_hospital() and public.has_role(%L))', r.tbl, r.ins);
    else
      execute format('revoke insert on public.%I from authenticated', r.tbl);
    end if;
    if r.upd <> '{}' then
      execute format('grant update on public.%I to authenticated', r.tbl);
      execute format('create policy p_update on public.%I for update to authenticated
                      using (hospital_id = public.my_hospital() and public.has_role(%L))
                      with check (hospital_id = public.my_hospital())', r.tbl, r.upd);
    else
      execute format('revoke update on public.%I from authenticated', r.tbl);
    end if;
    if r.del <> '{}' then
      execute format('grant delete on public.%I to authenticated', r.tbl);
      execute format('create policy p_delete on public.%I for delete to authenticated
                      using (hospital_id = public.my_hospital() and public.has_role(%L))', r.tbl, r.del);
    else
      execute format('revoke delete on public.%I from authenticated', r.tbl);
    end if;
  end loop;
end $$;

-- hospital_counters: nobody from the app (only via functions)
alter table public.hospital_counters enable row level security;
revoke all on public.hospital_counters from anon, authenticated;

-- agents registry: every signed-in staff can read; nobody edits from the app
alter table public.agents enable row level security;
drop policy if exists p_read on public.agents;
create policy p_read on public.agents for select to authenticated using (true);
revoke all on public.agents from anon;
revoke insert, update, delete on public.agents from authenticated;
grant select on public.agents to authenticated;

-- agent_tasks: staff create tasks; see their own (doctor/admin see all); results written by server only
alter table public.agent_tasks enable row level security;
drop policy if exists p_read on public.agent_tasks;
drop policy if exists p_insert on public.agent_tasks;
create policy p_read on public.agent_tasks for select to authenticated
  using (hospital_id = public.my_hospital()
         and (requested_by = auth.uid() or public.has_role('{doctor,admin}')));
create policy p_insert on public.agent_tasks for insert to authenticated
  with check (hospital_id = public.my_hospital() and requested_by = auth.uid()
              and status = 'queued' and public.my_role() <> 'pending');
revoke all on public.agent_tasks from anon;
revoke update, delete on public.agent_tasks from authenticated;
grant select, insert on public.agent_tasks to authenticated;

-- notifications: see your own or your role's; can only mark as read
alter table public.notifications enable row level security;
drop policy if exists p_read on public.notifications;
drop policy if exists p_insert on public.notifications;
drop policy if exists p_update on public.notifications;
create policy p_read on public.notifications for select to authenticated
  using (hospital_id = public.my_hospital() and (
         target_user = auth.uid()
      or (target_user is null and target_role = public.my_role())
      or (target_user is null and target_role is null and public.my_role() <> 'pending')));
create policy p_insert on public.notifications for insert to authenticated
  with check (hospital_id = public.my_hospital() and public.my_role() <> 'pending');
create policy p_update on public.notifications for update to authenticated
  using (hospital_id = public.my_hospital() and (target_user = auth.uid()
         or (target_user is null and (target_role = public.my_role() or target_role is null))))
  with check (hospital_id = public.my_hospital());
revoke all on public.notifications from anon;
revoke update, delete on public.notifications from authenticated;
grant select, insert on public.notifications to authenticated;
grant update (read_at) on public.notifications to authenticated;

-- ---------- tamper-proof records ----------
do $$
declare t text;
begin
  -- never edited or deleted (corrections are new rows)
  foreach t in array array['vitals','nursing_notes','medication_administrations','prescriptions',
                           'payments','expenses','salaries','invoice_items','audit_logs','agent_logs']
  loop
    execute format('drop trigger if exists no_change on public.%I', t);
    execute format('create trigger no_change before update or delete on public.%I
                    for each row execute function public.block_change()', t);
  end loop;
  -- can be updated (status etc.) but never deleted
  foreach t in array array['patients','encounters','appointments','admissions','doctor_orders',
                           'lab_orders','invoices','medicine_batches','purchases','follow_ups',
                           'staff_members','attendance','medical_documents','agent_tasks']
  loop
    execute format('drop trigger if exists no_delete on public.%I', t);
    execute format('create trigger no_delete before delete on public.%I
                    for each row execute function public.block_delete()', t);
  end loop;
  -- audit trail on every important table
  foreach t in array array['patients','encounters','appointments','admissions','beds','vitals',
                           'nursing_notes','doctor_orders','prescriptions','medication_administrations',
                           'medical_documents','lab_orders','medicines','medicine_batches','purchases',
                           'invoices','payments','expenses','salaries','staff_members','attendance',
                           'follow_ups']
  loop
    execute format('drop trigger if exists audit on public.%I', t);
    execute format('create trigger audit after insert or update or delete on public.%I
                    for each row execute function public.audit_row()', t);
  end loop;
end $$;

-- created_by / recorded_by fields must be the real logged-in user (no faking)
create or replace function public.force_actor() returns trigger
language plpgsql as $$
declare col text := tg_argv[0];
begin
  if auth.uid() is not null then
    new := jsonb_populate_record(new, jsonb_build_object(col, auth.uid()));
  end if;
  return new;
end $$;

do $$
declare r record;
begin
  for r in select * from (values
    ('patients','created_by'),('encounters','created_by'),('appointments','created_by'),
    ('admissions','created_by'),('vitals','recorded_by'),('nursing_notes','created_by'),
    ('doctor_orders','ordered_by'),('prescriptions','prescribed_by'),
    ('medication_administrations','given_by'),('medical_documents','uploaded_by'),
    ('lab_orders','ordered_by'),('purchases','created_by'),('invoices','created_by'),
    ('payments','received_by'),('expenses','created_by'),('salaries','paid_by'),
    ('attendance','marked_by'),('follow_ups','created_by'),('agent_tasks','requested_by')
  ) as t(tbl, col)
  loop
    execute format('drop trigger if exists force_actor on public.%I', r.tbl);
    execute format('create trigger force_actor before insert on public.%I
                    for each row execute function public.force_actor(%L)', r.tbl, r.col);
  end loop;
end $$;

-- ---------- hardening ----------
alter function public.block_change() set search_path = public;
alter function public.block_delete() set search_path = public;
alter function public.force_actor() set search_path = public;
revoke execute on function public.set_uhid() from public, anon, authenticated;
revoke execute on function public.set_invoice_no() from public, anon, authenticated;
