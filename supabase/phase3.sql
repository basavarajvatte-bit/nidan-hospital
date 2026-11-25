-- =========================================================
-- NIDAN HOSPITAL OS — PHASE 3 (Reception)
-- Duplicate patient check, safe admit / discharge, room + bed setup.
-- All functions run with the caller's own permissions (RLS applies).
-- =========================================================

create schema if not exists extensions;
create extension if not exists pg_trgm with schema extensions;

-- Current age: from DOB if known, else age at registration + years passed
create or replace function public.patient_age(p public.patients) returns int
language sql stable set search_path = public as $$
  select coalesce(
    extract(year from age(p.dob))::int,
    p.age_years + extract(year from age(p.created_at))::int)
$$;

-- Possible duplicates: same phone, same ABHA, or very similar name with similar age
create or replace function public.find_duplicate_patients(
  p_name text, p_phone text default null, p_age int default null, p_abha text default null)
returns table (id uuid, uhid text, full_name text, gender text, age int, phone text, reason text)
language sql stable security invoker set search_path = public, extensions as $$
  select p.id, p.uhid, p.full_name, p.gender, public.patient_age(p), p.phone,
    case
      when nullif(trim(p_abha), '') is not null and p.abha_id = trim(p_abha) then 'Same ABHA'
      when nullif(trim(p_phone), '') is not null and p.phone = trim(p_phone) then 'Same phone'
      else 'Similar name & age'
    end
  from public.patients p
  where p.hospital_id = public.my_hospital()
    and (
      (nullif(trim(p_abha), '') is not null and p.abha_id = trim(p_abha))
      or (nullif(trim(p_phone), '') is not null and p.phone = trim(p_phone))
      or (similarity(lower(p.full_name), lower(trim(p_name))) > 0.45
          and (p_age is null or public.patient_age(p) is null
               or abs(public.patient_age(p) - p_age) <= 2))
    )
  order by p.created_at desc
  limit 5
$$;

-- Admit: creates IPD visit + admission + marks bed occupied, all-or-nothing
create or replace function public.admit_patient(
  p_patient uuid, p_bed uuid, p_doctor uuid default null, p_complaint text default null)
returns uuid
language plpgsql security invoker set search_path = public as $$
declare enc uuid; adm uuid;
begin
  perform 1 from public.beds where id = p_bed and status = 'available' for update;
  if not found then raise exception 'Ye bed khali nahi hai'; end if;
  if exists (select 1 from public.admissions where patient_id = p_patient and status = 'admitted') then
    raise exception 'Ye patient pehle se admit hai';
  end if;
  insert into public.encounters(patient_id, kind, doctor_id, chief_complaint)
  values (p_patient, 'ipd', p_doctor, p_complaint) returning id into enc;
  insert into public.admissions(patient_id, encounter_id, bed_id)
  values (p_patient, enc, p_bed) returning id into adm;
  update public.beds set status = 'occupied' where id = p_bed;
  return adm;
end $$;

-- Discharge: closes admission + visit, bed goes to cleaning
create or replace function public.discharge_patient(p_admission uuid, p_summary text default null)
returns void
language plpgsql security invoker set search_path = public as $$
declare a public.admissions;
begin
  select * into a from public.admissions where id = p_admission and status = 'admitted' for update;
  if not found then raise exception 'Ye admission chalu nahi hai'; end if;
  update public.admissions
     set status = 'discharged', discharged_at = now(),
         discharge_summary = coalesce(nullif(trim(p_summary), ''), discharge_summary)
   where id = p_admission;
  update public.encounters set status = 'closed', ended_at = now()
   where id = a.encounter_id and status = 'open';
  if a.bed_id is not null then
    update public.beds set status = 'cleaning' where id = a.bed_id;
  end if;
end $$;

-- Room with N beds in one go (doctor/admin only, via RLS)
create or replace function public.add_room_with_beds(p_name text, p_kind text, p_beds int)
returns uuid
language plpgsql security invoker set search_path = public as $$
declare r uuid; i int;
begin
  if p_beds < 1 or p_beds > 100 then raise exception 'Beds 1 se 100 ke beech'; end if;
  insert into public.rooms(name, kind) values (trim(p_name), p_kind) returning id into r;
  for i in 1..p_beds loop
    insert into public.beds(room_id, label) values (r, trim(p_name) || '-' || i);
  end loop;
  return r;
end $$;

revoke execute on function public.find_duplicate_patients(text, text, int, text) from public, anon;
revoke execute on function public.admit_patient(uuid, uuid, uuid, text) from public, anon;
revoke execute on function public.discharge_patient(uuid, text) from public, anon;
revoke execute on function public.add_room_with_beds(text, text, int) from public, anon;
revoke execute on function public.patient_age(public.patients) from public, anon;
grant execute on function public.find_duplicate_patients(text, text, int, text) to authenticated;
grant execute on function public.admit_patient(uuid, uuid, uuid, text) to authenticated;
grant execute on function public.discharge_patient(uuid, text) to authenticated;
grant execute on function public.add_room_with_beds(text, text, int) to authenticated;
grant execute on function public.patient_age(public.patients) to authenticated;
