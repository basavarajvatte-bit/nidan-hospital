-- (applied as migration "upi_qr_settings") Hospital UPI ID for the payment QR on every bill / receipt
alter table public.hospitals add column if not exists upi_id text;
alter table public.hospitals add column if not exists upi_name text;
create or replace function public.set_hospital_upi(p_upi text, p_name text) returns public.hospitals
language plpgsql security definer set search_path = public as $$
declare h public.hospitals; v text := lower(trim(coalesce(p_upi, '')));
begin
  if not public.has_role('{doctor,admin}') then raise exception 'UPI ID sirf Doctor / Admin badal sakte hain'; end if;
  if v <> '' and v !~ '^[a-z0-9._-]{2,256}@[a-z0-9]{2,64}$' then raise exception 'UPI ID galat lagti hai (jaise: vattehospital@okaxis)'; end if;
  update public.hospitals set upi_id = nullif(v, ''), upi_name = nullif(left(trim(coalesce(p_name, '')), 50), '')
   where id = public.my_hospital() returning * into h;
  insert into public.audit_logs(hospital_id, actor_id, action, details)
  values (h.id, auth.uid(), 'upi_changed', jsonb_build_object('upi_id', h.upi_id, 'name', h.upi_name));
  return h;
end $$;
revoke all on function public.set_hospital_upi(text, text) from public, anon;
grant execute on function public.set_hospital_upi(text, text) to authenticated;
