-- =========================================================
-- NIDAN HOSPITAL OS — PHASE 1 DATABASE
-- Hospitals, staff profiles with roles, audit log, security rules.
-- Run this whole file once in Supabase > SQL Editor.
-- Safe to run again (it skips what already exists).
-- =========================================================

create extension if not exists pgcrypto;

-- 1) Hospitals (multi-hospital ready)
create table if not exists public.hospitals (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

-- 2) Staff profiles (one per login)
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  hospital_id uuid not null references public.hospitals(id),
  full_name text not null default '',
  role text not null default 'pending'
    check (role in ('doctor','admin','receptionist','nurse','accountant',
                    'pharmacist','lab','hr','pending')),
  created_at timestamptz not null default now()
);
create index if not exists profiles_hospital_idx on public.profiles(hospital_id);

-- 3) Audit log (never edited from the app)
create table if not exists public.audit_logs (
  id bigint generated always as identity primary key,
  hospital_id uuid references public.hospitals(id),
  actor_id uuid references auth.users(id) on delete set null,
  action text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists audit_hospital_time_idx on public.audit_logs(hospital_id, created_at desc);

-- 4) Helper functions (who am I?)
create or replace function public.my_hospital() returns uuid
language sql stable security definer set search_path = public as $$
  select hospital_id from public.profiles where id = auth.uid()
$$;

create or replace function public.my_role() returns text
language sql stable security definer set search_path = public as $$
  select role from public.profiles where id = auth.uid()
$$;

-- 5) New signup -> profile. First person ever = doctor (owner).
--    Everyone after that = 'pending' until the doctor gives a role.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  h uuid;
  is_first boolean;
  r text;
begin
  perform pg_advisory_xact_lock(424242);
  select not exists (select 1 from public.profiles) into is_first;
  if is_first then
    insert into public.hospitals(name) values ('Nidan Hospital') returning id into h;
    r := 'doctor';
  else
    select id into h from public.hospitals order by created_at limit 1;
    r := 'pending';
  end if;

  insert into public.profiles(id, hospital_id, full_name, role)
  values (new.id, h, coalesce(new.raw_user_meta_data->>'full_name', ''), r);

  insert into public.audit_logs(hospital_id, actor_id, action, details)
  values (h, new.id, 'staff_signup', jsonb_build_object('role', r));
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 6) Only doctor/admin can change roles (and never their own)
create or replace function public.set_staff_role(target uuid, new_role text) returns void
language plpgsql security definer set search_path = public as $$
declare
  old_role text;
  t_hospital uuid;
begin
  if public.my_role() not in ('doctor','admin') then
    raise exception 'Permission nahi hai';
  end if;
  if target = auth.uid() then
    raise exception 'Apna khud ka role nahi badal sakte';
  end if;
  if new_role not in ('doctor','admin','receptionist','nurse','accountant',
                      'pharmacist','lab','hr','pending') then
    raise exception 'Galat role';
  end if;

  select role, hospital_id into old_role, t_hospital
  from public.profiles where id = target for update;

  if t_hospital is null or t_hospital <> public.my_hospital() then
    raise exception 'Ye staff aapke hospital ka nahi hai';
  end if;
  if new_role = 'doctor' and public.my_role() <> 'doctor' then
    raise exception 'Sirf doctor naya doctor bana sakta hai';
  end if;

  update public.profiles set role = new_role where id = target;

  insert into public.audit_logs(hospital_id, actor_id, action, details)
  values (t_hospital, auth.uid(), 'role_changed',
          jsonb_build_object('staff', target, 'from', old_role, 'to', new_role));
end $$;

-- 7) Security rules (Row Level Security)
alter table public.hospitals  enable row level security;
alter table public.profiles   enable row level security;
alter table public.audit_logs enable row level security;

drop policy if exists "see own hospital" on public.hospitals;
create policy "see own hospital" on public.hospitals
  for select to authenticated using (id = public.my_hospital());

drop policy if exists "see staff of own hospital" on public.profiles;
create policy "see staff of own hospital" on public.profiles
  for select to authenticated using (hospital_id = public.my_hospital());
-- No insert/update/delete policies on profiles: changes only via functions above.

drop policy if exists "doctor/admin read audit" on public.audit_logs;
create policy "doctor/admin read audit" on public.audit_logs
  for select to authenticated
  using (hospital_id = public.my_hospital() and public.my_role() in ('doctor','admin'));
-- No insert/update/delete policies on audit_logs: app can never edit it.

-- Table access for logged-in users (rows are still filtered by the rules above)
grant usage on schema public to authenticated;
grant select on public.hospitals, public.profiles, public.audit_logs to authenticated;
revoke all on public.hospitals, public.profiles, public.audit_logs from anon;

revoke all on function public.set_staff_role(uuid, text) from public, anon;
grant execute on function public.set_staff_role(uuid, text) to authenticated;
grant execute on function public.my_hospital() to authenticated;
grant execute on function public.my_role() to authenticated;
