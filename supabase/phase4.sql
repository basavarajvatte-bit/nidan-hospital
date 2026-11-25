-- =========================================================
-- NIDAN HOSPITAL OS — PHASE 4 (Doctor Dashboard)
-- One call returns all dashboard numbers for "today" (India time).
-- Runs with the caller's permissions, so it only counts what they may see.
-- =========================================================

create or replace function public.dashboard_summary() returns jsonb
language plpgsql stable security invoker set search_path = public as $$
declare
  h uuid := public.my_hospital();
  day_start timestamptz := (date_trunc('day', now() at time zone 'Asia/Kolkata')) at time zone 'Asia/Kolkata';
  day_end   timestamptz := day_start + interval '1 day';
  today date := (now() at time zone 'Asia/Kolkata')::date;
  res jsonb;
begin
  if not public.has_role('{doctor,admin}') then
    raise exception 'Dashboard sirf doctor/admin ke liye hai';
  end if;

  select jsonb_build_object(
    'patients_today',   (select count(distinct patient_id) from encounters where hospital_id = h and started_at >= day_start and started_at < day_end),
    'new_patients',     (select count(*) from patients where hospital_id = h and created_at >= day_start and created_at < day_end),
    'opd_today',        (select count(*) from encounters where hospital_id = h and kind in ('opd','emergency') and started_at >= day_start and started_at < day_end),
    'opd_waiting',      (select count(*) from encounters where hospital_id = h and kind in ('opd','emergency') and status = 'open'),
    'ipd_now',          (select count(*) from admissions where hospital_id = h and status = 'admitted'),
    'beds_free',        (select count(*) from beds where hospital_id = h and status = 'available'),
    'beds_total',       (select count(*) from beds where hospital_id = h),
    'appointments_today', (select count(*) from appointments where hospital_id = h and starts_at >= day_start and starts_at < day_end and status <> 'cancelled'),
    'appointments_pending', (select count(*) from appointments where hospital_id = h and starts_at >= day_start and starts_at < day_end and status = 'booked'),
    'revenue_today',    (select coalesce(sum(amount), 0) from payments where hospital_id = h and created_at >= day_start and created_at < day_end),
    'expenses_today',   (select coalesce(sum(amount), 0) from expenses where hospital_id = h and spent_on = today),
    'outstanding',      (select coalesce(sum(greatest(i.total - i.discount - coalesce(p.paid, 0), 0)), 0)
                           from invoices i
                           left join (select invoice_id, sum(amount) paid from payments where hospital_id = h group by invoice_id) p
                             on p.invoice_id = i.id
                          where i.hospital_id = h and i.status <> 'cancelled'),
    'low_stock',        (select count(*) from medicines m
                          where m.hospital_id = h and m.active
                            and coalesce((select sum(quantity) from medicine_batches b
                                           where b.medicine_id = m.id and b.expiry_date > today), 0) < m.reorder_level),
    'expiring_soon',    (select count(*) from medicine_batches where hospital_id = h and quantity > 0
                            and expiry_date between today and today + 30),
    'lab_pending',      (select count(*) from lab_orders where hospital_id = h and status in ('ordered','sample_collected','processing')),
    'lab_critical',     (select count(*) from lab_orders where hospital_id = h and is_critical and reported_at >= day_start - interval '1 day'),
    'staff_total',      (select count(*) from staff_members where hospital_id = h and active),
    'staff_present',    (select count(*) from attendance where hospital_id = h and day = today and status in ('present','half_day')),
    'tasks_pending',    (select count(*) from agent_tasks where hospital_id = h and status in ('queued','running','waiting_approval')),
    'tasks_approval',   (select count(*) from agent_tasks where hospital_id = h and status = 'waiting_approval'),
    'critical_alerts',  (select count(*) from notifications where hospital_id = h and level = 'critical' and read_at is null),
    'as_of',            now()
  ) into res;
  return res;
end $$;

revoke execute on function public.dashboard_summary() from public, anon;
grant execute on function public.dashboard_summary() to authenticated;
