-- =========================================================
-- VATTE HOSPITAL OS — PHASE 5 (Nursing Sister)
-- Abnormal vital alert -> doctor notification (fixed safety limits, not a diagnosis)
-- Nurse can mark a doctor order done/stopped but can never change what the doctor wrote.
-- =========================================================

-- Safety limits used for alerts (can be tuned later per hospital)
create or replace function public.vital_flags(v public.vitals) returns text[]
language sql immutable set search_path = public as $$
  select array_remove(array[
    case when v.bp_systolic >= 180 then 'BP bahut high (' || v.bp_systolic || '/' || coalesce(v.bp_diastolic::text,'?') || ')'
         when v.bp_systolic < 90  then 'BP low (' || v.bp_systolic || '/' || coalesce(v.bp_diastolic::text,'?') || ')' end,
    case when v.bp_diastolic >= 120 then 'Diastolic bahut high (' || v.bp_diastolic || ')' end,
    case when v.pulse > 130 then 'Pulse tez (' || v.pulse || ')'
         when v.pulse < 50  then 'Pulse dheema (' || v.pulse || ')' end,
    case when v.spo2 < 92 then 'SpO2 kam (' || v.spo2 || '%)' end,
    case when v.temperature_f >= 103 then 'Tez bukhar (' || v.temperature_f || '°F)'
         when v.temperature_f < 95   then 'Temperature kam (' || v.temperature_f || '°F)' end,
    case when v.resp_rate > 28 then 'Saans tez (' || v.resp_rate || '/min)'
         when v.resp_rate < 10 then 'Saans dheemi (' || v.resp_rate || '/min)' end
  ], null)
$$;

create or replace function public.alert_abnormal_vitals() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  flags text[] := public.vital_flags(new);
  pname text; puhid text; bed text;
begin
  if coalesce(array_length(flags, 1), 0) = 0 then return new; end if;
  select full_name, uhid into pname, puhid from public.patients where id = new.patient_id;
  select b.label into bed from public.admissions a join public.beds b on b.id = a.bed_id
   where a.patient_id = new.patient_id and a.status = 'admitted' limit 1;
  insert into public.notifications(hospital_id, target_role, level, title, body, source)
  values (new.hospital_id, 'doctor', 'critical',
          '🚨 ' || pname || coalesce(' — Bed ' || bed, '') || ': ' || array_to_string(flags, ', '),
          'UHID ' || puhid || '. Sister ne ' || to_char(new.recorded_at at time zone 'Asia/Kolkata', 'HH12:MI AM')
            || ' par record kiya. Turant dekhein.',
          'nurse');
  insert into public.notifications(hospital_id, target_role, level, title, body, source)
  values (new.hospital_id, 'nurse', 'warning',
          pname || ': ' || array_to_string(flags, ', '),
          'Doctor ko alert bhej diya gaya hai. Doctor ke order ka intezaar karein / dobara check karein.',
          'nurse');
  return new;
end $$;
drop trigger if exists vitals_alert on public.vitals;
create trigger vitals_alert after insert on public.vitals
  for each row execute function public.alert_abnormal_vitals();

-- Doctor orders: only a doctor may change the order text / create; nurse may only change status
create or replace function public.guard_doctor_orders() returns trigger
language plpgsql set search_path = public as $$
begin
  if not public.has_role('{doctor}') and auth.uid() is not null then
    if new.order_text is distinct from old.order_text
       or new.patient_id is distinct from old.patient_id
       or new.ordered_by is distinct from old.ordered_by
       or new.encounter_id is distinct from old.encounter_id then
      raise exception 'Sister doctor ka order badal nahi sakti, sirf "Ho gaya" / "Band" mark kar sakti hai';
    end if;
  end if;
  return new;
end $$;
drop trigger if exists guard_orders on public.doctor_orders;
create trigger guard_orders before update on public.doctor_orders
  for each row execute function public.guard_doctor_orders();

revoke execute on function public.alert_abnormal_vitals() from public, anon, authenticated;
revoke execute on function public.guard_doctor_orders() from public, anon, authenticated;
revoke execute on function public.vital_flags(public.vitals) from public, anon;
grant execute on function public.vital_flags(public.vitals) to authenticated;
