-- =========================================================
-- VATTE HOSPITAL OS — PHASE 10 (Accountant AI: billing, payments, tamper-proof ledger)
-- • Rate list (service_charges) — doctor/admin/accountant set prices
-- • Bills are made ONLY through create_bill(): total is calculated by the server, never typed in
-- • Payments / refunds / expenses are append-only (a mistake is fixed by a reverse entry, never edited)
-- • Discount needs a reason; more than 10% needs the doctor
-- • Day book with running balance, daily cash closing, bill suggestions from visit / admission / lab
-- • AI agents can READ accounts (today's collection, dues, patient balance) — they never create or change money records
-- =========================================================

-- ---------- rate list ----------
create table if not exists public.service_charges (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  name text not null,
  category text not null check (category in ('opd','ipd','lab','procedure','bed','pharmacy','other')),
  price numeric(10,2) not null check (price >= 0),
  per_day boolean not null default false,
  active boolean not null default true,
  unique (hospital_id, name)
);
alter table public.service_charges enable row level security;
drop policy if exists p_read on public.service_charges;
drop policy if exists p_insert on public.service_charges;
drop policy if exists p_update on public.service_charges;
create policy p_read on public.service_charges for select to authenticated using (hospital_id = public.my_hospital() and public.my_role() <> 'pending');
create policy p_insert on public.service_charges for insert to authenticated with check (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,accountant}'));
create policy p_update on public.service_charges for update to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,accountant}'));
revoke all on public.service_charges from anon;
grant select, insert, update on public.service_charges to authenticated;
drop trigger if exists audit on public.service_charges;
create trigger audit after insert or update on public.service_charges for each row execute function public.audit_row();
insert into public.service_charges(hospital_id, name, category, price, per_day)
select h.id, x.n, x.c, x.p, x.d from public.hospitals h, (values
  ('OPD consultation','opd',200,false), ('Follow-up consultation','opd',100,false), ('Emergency consultation','opd',500,false),
  ('Injection charge','procedure',50,false), ('Dressing','procedure',100,false), ('ECG','procedure',200,false), ('Nebulisation','procedure',100,false),
  ('General ward bed (per day)','bed',500,true), ('Nursing charge (per day)','ipd',300,true), ('Doctor visit (IPD, per day)','ipd',300,true)
) as x(n, c, p, d) on conflict do nothing;

-- ---------- extra bill fields ----------
alter table public.invoices add column if not exists discount_reason text;
alter table public.invoices add column if not exists cancelled_by uuid references auth.users(id);
alter table public.invoices add column if not exists cancelled_at timestamptz;
alter table public.invoice_items add column if not exists charge_id uuid references public.service_charges(id);

-- money tables: changes only through the functions below
drop policy if exists p_insert on public.invoices;      revoke insert, update on public.invoices from authenticated;
drop policy if exists p_update on public.invoices;
drop policy if exists p_insert on public.invoice_items; revoke insert on public.invoice_items from authenticated;
drop policy if exists p_insert on public.payments;      revoke insert on public.payments from authenticated;
drop policy if exists p_insert on public.expenses;      revoke insert on public.expenses from authenticated;

-- a bill's amounts can never be edited (only its status, by the functions)
create or replace function public.guard_invoice() returns trigger
language plpgsql set search_path = public as $$
begin
  if new.total is distinct from old.total or new.discount is distinct from old.discount or new.patient_id is distinct from old.patient_id
     or new.invoice_no is distinct from old.invoice_no or new.category is distinct from old.category or new.created_at is distinct from old.created_at
     or new.created_by is distinct from old.created_by or new.hospital_id is distinct from old.hospital_id then
    raise exception 'Bill ki rakam / patient badla nahi ja sakta — galti ho to bill cancel karke naya banayein';
  end if;
  if old.status = 'cancelled' and new.status <> 'cancelled' then raise exception 'Cancel hua bill wapas chalu nahi ho sakta'; end if;
  return new;
end $$;
drop trigger if exists guard_invoice on public.invoices;
create trigger guard_invoice before update on public.invoices for each row execute function public.guard_invoice();

-- paid amount & status of one bill
create or replace function public.invoice_paid(p_invoice uuid) returns numeric
language sql stable security definer set search_path = public as $$
  select coalesce(sum(amount), 0) from public.payments where invoice_id = p_invoice
$$;
revoke all on function public.invoice_paid(uuid) from public, anon;
grant execute on function public.invoice_paid(uuid) to authenticated;

create or replace function public.refresh_invoice_status(p_invoice uuid) returns void
language plpgsql security definer set search_path = public as $$
declare i public.invoices; paid numeric;
begin
  select * into i from public.invoices where id = p_invoice for update;
  if i.status = 'cancelled' then return; end if;
  paid := public.invoice_paid(p_invoice);
  update public.invoices set status = case when paid >= i.total - i.discount and i.total - i.discount > 0 then 'paid'
                                            when i.total - i.discount = 0 then 'paid'
                                            when paid > 0 then 'partial' else 'unpaid' end
   where id = p_invoice;
end $$;
revoke all on function public.refresh_invoice_status(uuid) from public, anon, authenticated;

-- ---------- create a bill ----------
-- p_items: [{ "description": "...", "quantity": 1, "rate": 200, "charge_id": "...", "lab_order_id": "..." }]
create or replace function public.create_bill(p_patient uuid, p_category text, p_items jsonb, p_discount numeric default 0,
  p_discount_reason text default null, p_encounter uuid default null) returns public.invoices
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); i public.invoices; x jsonb; total numeric := 0; q int; r numeric; n int := 0;
begin
  if not public.has_role('{doctor,admin,accountant,receptionist}') then raise exception 'Bill sirf Reception / Accountant / Doctor / Admin bana sakte hain'; end if;
  if not exists (select 1 from public.patients where id = p_patient and hospital_id = h) then raise exception 'Patient nahi mila'; end if;
  if p_encounter is not null and not exists (select 1 from public.encounters where id = p_encounter and patient_id = p_patient) then raise exception 'Visit is patient ka nahi hai'; end if;
  if jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) = 0 then raise exception 'Bill mein kam se kam ek cheez daalein'; end if;
  for x in select * from jsonb_array_elements(p_items) loop
    q := coalesce((x->>'quantity')::int, 1); r := (x->>'rate')::numeric;
    if coalesce(trim(x->>'description'), '') = '' then raise exception 'Har cheez ka naam likhein'; end if;
    if q is null or q <= 0 or q > 1000 then raise exception 'Quantity galat hai: %', x->>'description'; end if;
    if r is null or r < 0 or r > 1000000 then raise exception 'Rate galat hai: %', x->>'description'; end if;
    total := total + q * r; n := n + 1;
  end loop;
  p_discount := round(coalesce(p_discount, 0), 2);
  if p_discount < 0 or p_discount > total then raise exception 'Discount bill se zyada nahi ho sakta'; end if;
  if p_discount > 0 and coalesce(trim(p_discount_reason), '') = '' then raise exception 'Discount ka kaaran likhna zaroori hai'; end if;
  if p_discount > total * 0.10 and not public.has_role('{doctor}') then raise exception '10%% se zyada discount sirf Doctor de sakte hain'; end if;
  insert into public.invoices(hospital_id, patient_id, encounter_id, category, total, discount, discount_reason, status, created_by)
  values (h, p_patient, p_encounter, p_category, round(total, 2), p_discount, nullif(trim(p_discount_reason), ''), 'unpaid', auth.uid()) returning * into i;
  insert into public.invoice_items(hospital_id, invoice_id, description, quantity, rate, charge_id, lab_order_id)
  select h, i.id, trim(e->>'description'), coalesce((e->>'quantity')::int, 1), (e->>'rate')::numeric,
         nullif(e->>'charge_id', '')::uuid, nullif(e->>'lab_order_id', '')::uuid
    from jsonb_array_elements(p_items) e;
  perform public.refresh_invoice_status(i.id);
  select * into i from public.invoices where id = i.id;
  return i;
end $$;
revoke all on function public.create_bill(uuid, text, jsonb, numeric, text, uuid) from public, anon;
grant execute on function public.create_bill(uuid, text, jsonb, numeric, text, uuid) to authenticated;

-- ---------- payments ----------
create or replace function public.record_payment(p_invoice uuid, p_amount numeric, p_method text, p_reference text default null, p_note text default null)
returns public.payments
language plpgsql security definer set search_path = public as $$
declare i public.invoices; p public.payments; due numeric;
begin
  if not public.has_role('{doctor,admin,accountant,receptionist}') then raise exception 'Payment lene ki permission nahi'; end if;
  select * into i from public.invoices where id = p_invoice and hospital_id = public.my_hospital() for update;
  if i.id is null then raise exception 'Bill nahi mila'; end if;
  if i.status = 'cancelled' then raise exception 'Cancel hue bill par payment nahi le sakte'; end if;
  p_amount := round(coalesce(p_amount, 0), 2);
  due := i.total - i.discount - public.invoice_paid(i.id);
  if p_amount <= 0 then raise exception 'Rakam 0 se zyada honi chahiye'; end if;
  if p_amount > due then raise exception 'Baaki sirf ₹% hai — isse zyada nahi le sakte', due; end if;
  if p_method not in ('cash','upi','card','bank','other') then raise exception 'Payment ka tarika chunein'; end if;
  if p_method in ('upi','card','bank') and coalesce(trim(p_reference), '') = '' then raise exception 'UPI / card / bank ka transaction number (reference) likhein'; end if;
  insert into public.payments(hospital_id, invoice_id, amount, method, reference, note, received_by)
  values (i.hospital_id, i.id, p_amount, p_method, nullif(trim(p_reference), ''), nullif(trim(p_note), ''), auth.uid()) returning * into p;
  perform public.refresh_invoice_status(i.id);
  return p;
end $$;
revoke all on function public.record_payment(uuid, numeric, text, text, text) from public, anon;
grant execute on function public.record_payment(uuid, numeric, text, text, text) to authenticated;

-- refund = a reverse (negative) entry pointing at the original payment
create or replace function public.refund_payment(p_payment uuid, p_reason text) returns public.payments
language plpgsql security definer set search_path = public as $$
declare o public.payments; p public.payments; already numeric;
begin
  if not public.has_role('{doctor,admin,accountant}') then raise exception 'Refund sirf Doctor / Admin / Accountant kar sakte hain'; end if;
  if coalesce(trim(p_reason), '') = '' then raise exception 'Refund ka kaaran likhein'; end if;
  select * into o from public.payments where id = p_payment and hospital_id = public.my_hospital() for update;
  if o.id is null or o.amount <= 0 then raise exception 'Asli payment nahi mili'; end if;
  select coalesce(-sum(amount), 0) into already from public.payments where reverses_id = o.id;
  if already >= o.amount then raise exception 'Is payment ka refund pehle hi ho chuka hai'; end if;
  insert into public.payments(hospital_id, invoice_id, amount, method, reference, reverses_id, note, received_by)
  values (o.hospital_id, o.invoice_id, -(o.amount - already), o.method, o.reference, o.id, 'Refund: ' || trim(p_reason), auth.uid()) returning * into p;
  perform public.refresh_invoice_status(o.invoice_id);
  return p;
end $$;
revoke all on function public.refund_payment(uuid, text) from public, anon;
grant execute on function public.refund_payment(uuid, text) to authenticated;

create or replace function public.cancel_bill(p_invoice uuid, p_reason text) returns public.invoices
language plpgsql security definer set search_path = public as $$
declare i public.invoices;
begin
  if not public.has_role('{doctor,admin,accountant}') then raise exception 'Bill cancel sirf Doctor / Admin / Accountant kar sakte hain'; end if;
  if coalesce(trim(p_reason), '') = '' then raise exception 'Cancel ka kaaran likhein'; end if;
  select * into i from public.invoices where id = p_invoice and hospital_id = public.my_hospital() for update;
  if i.id is null then raise exception 'Bill nahi mila'; end if;
  if i.status = 'cancelled' then raise exception 'Bill pehle se cancel hai'; end if;
  if public.invoice_paid(i.id) <> 0 then raise exception 'Is bill par payment hai — pehle refund karein, phir cancel'; end if;
  update public.invoices set status = 'cancelled', cancel_reason = trim(p_reason), cancelled_by = auth.uid(), cancelled_at = now()
   where id = i.id returning * into i;
  return i;
end $$;
revoke all on function public.cancel_bill(uuid, text) from public, anon;
grant execute on function public.cancel_bill(uuid, text) to authenticated;

-- ---------- expenses ----------
create or replace function public.record_expense(p_category text, p_amount numeric, p_paid_to text, p_method text, p_note text default null, p_day date default null)
returns public.expenses
language plpgsql security definer set search_path = public as $$
declare e public.expenses;
begin
  if not public.has_role('{doctor,admin,accountant}') then raise exception 'Kharcha sirf Doctor / Admin / Accountant likh sakte hain'; end if;
  if coalesce(trim(p_category), '') = '' then raise exception 'Kharche ki category likhein'; end if;
  if coalesce(p_amount, 0) <= 0 then raise exception 'Rakam 0 se zyada honi chahiye'; end if;
  if p_method not in ('cash','upi','card','bank','other') then raise exception 'Tarika chunein'; end if;
  if p_day is not null and (p_day > (now() at time zone 'Asia/Kolkata')::date or p_day < (now() at time zone 'Asia/Kolkata')::date - 31) then
    raise exception 'Kharche ki date aaj ya pichhle 31 din mein honi chahiye'; end if;
  insert into public.expenses(hospital_id, category, amount, paid_to, method, note, spent_on, created_by)
  values (public.my_hospital(), trim(p_category), round(p_amount, 2), nullif(trim(p_paid_to), ''), p_method, nullif(trim(p_note), ''),
          coalesce(p_day, (now() at time zone 'Asia/Kolkata')::date), auth.uid()) returning * into e;
  return e;
end $$;
revoke all on function public.record_expense(text, numeric, text, text, text, date) from public, anon;
grant execute on function public.record_expense(text, numeric, text, text, text, date) to authenticated;

create or replace function public.reverse_expense(p_expense uuid, p_reason text) returns public.expenses
language plpgsql security definer set search_path = public as $$
declare o public.expenses; e public.expenses;
begin
  if not public.has_role('{doctor,admin,accountant}') then raise exception 'Permission nahi'; end if;
  if coalesce(trim(p_reason), '') = '' then raise exception 'Kaaran likhein'; end if;
  select * into o from public.expenses where id = p_expense and hospital_id = public.my_hospital() and amount > 0;
  if o.id is null then raise exception 'Kharcha nahi mila'; end if;
  if exists (select 1 from public.expenses where reverses_id = o.id) then raise exception 'Ye kharcha pehle hi ulta (reverse) ho chuka hai'; end if;
  insert into public.expenses(hospital_id, category, amount, paid_to, method, reverses_id, note, spent_on, created_by)
  values (o.hospital_id, o.category, -o.amount, o.paid_to, o.method, o.id, 'Galat entry ulti: ' || trim(p_reason), (now() at time zone 'Asia/Kolkata')::date, auth.uid())
  returning * into e;
  return e;
end $$;
revoke all on function public.reverse_expense(uuid, text) from public, anon;
grant execute on function public.reverse_expense(uuid, text) to authenticated;

-- ---------- day book (every rupee in and out, in time order, with running balance) ----------
create or replace function public.day_book(p_from date, p_to date)
returns table (at timestamptz, kind text, method text, amount numeric, balance numeric, detail text, ref_id uuid)
language sql stable security definer set search_path = public as $$
  with rows as (
    select p.created_at as at, case when p.amount < 0 then 'refund' else 'payment' end as kind, p.method, p.amount,
           coalesce(i.invoice_no, '') || ' · ' || coalesce(pt.full_name, '') || coalesce(' · ' || p.note, '') as detail, p.id as ref_id
      from public.payments p left join public.invoices i on i.id = p.invoice_id left join public.patients pt on pt.id = i.patient_id
     where p.hospital_id = public.my_hospital() and (p.created_at at time zone 'Asia/Kolkata')::date between p_from and p_to
    union all
    select e.created_at, case when e.amount < 0 then 'expense_reversed' else 'expense' end, e.method, -e.amount,
           e.category || coalesce(' · ' || e.paid_to, '') || coalesce(' · ' || e.note, ''), e.id
      from public.expenses e where e.hospital_id = public.my_hospital() and e.spent_on between p_from and p_to
  )
  select at, kind, method, amount, sum(amount) over (order by at, ref_id rows unbounded preceding) as balance, detail, ref_id
    from rows
   where public.has_role('{doctor,admin,accountant}')
   order by at, ref_id
$$;
revoke all on function public.day_book(date, date) from public, anon;
grant execute on function public.day_book(date, date) to authenticated;

-- ---------- daily cash closing ----------
create table if not exists public.cash_closings (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  day date not null,
  expected_cash numeric(12,2) not null,
  counted_cash numeric(12,2) not null check (counted_cash >= 0),
  difference numeric(12,2) not null,
  note text,
  closed_by uuid not null references auth.users(id),
  closed_at timestamptz not null default now(),
  unique (hospital_id, day)
);
alter table public.cash_closings enable row level security;
drop policy if exists p_read on public.cash_closings;
create policy p_read on public.cash_closings for select to authenticated using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,accountant}'));
revoke all on public.cash_closings from anon;
revoke insert, update, delete on public.cash_closings from authenticated;
grant select on public.cash_closings to authenticated;
drop trigger if exists no_change on public.cash_closings;
create trigger no_change before update or delete on public.cash_closings for each row execute function public.block_change();

create or replace function public.close_cash(p_day date, p_counted numeric, p_note text default null) returns public.cash_closings
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); exp numeric; c public.cash_closings;
begin
  if not public.has_role('{doctor,admin,accountant}') then raise exception 'Cash close sirf Doctor / Admin / Accountant kar sakte hain'; end if;
  if p_day > (now() at time zone 'Asia/Kolkata')::date then raise exception 'Aage ki date ka cash close nahi ho sakta'; end if;
  select coalesce(sum(amount), 0) into exp from public.payments where hospital_id = h and method = 'cash' and (created_at at time zone 'Asia/Kolkata')::date = p_day;
  exp := exp - coalesce((select sum(amount) from public.expenses where hospital_id = h and method = 'cash' and spent_on = p_day), 0);
  if abs(coalesce(p_counted, 0) - exp) > 0 and coalesce(trim(p_note), '') = '' then raise exception 'Cash mein fark (₹%) hai — kaaran likhein', round(p_counted - exp, 2); end if;
  insert into public.cash_closings(hospital_id, day, expected_cash, counted_cash, difference, note, closed_by)
  values (h, p_day, exp, round(p_counted, 2), round(p_counted - exp, 2), nullif(trim(p_note), ''), auth.uid()) returning * into c;
  return c;
exception when unique_violation then raise exception 'Is din ka cash pehle hi close ho chuka hai';
end $$;
revoke all on function public.close_cash(date, numeric, text) from public, anon;
grant execute on function public.close_cash(date, numeric, text) to authenticated;

-- ---------- bill suggestions (from visit / admission / lab) ----------
create or replace function public.suggest_bill(p_patient uuid) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare h uuid := public.my_hospital(); items jsonb := '[]'; e record; a record; days int; c record; enc uuid;
begin
  if not public.has_role('{doctor,admin,accountant,receptionist}') then raise exception 'Permission nahi'; end if;
  -- today's / open OPD visit without a bill → consultation
  select * into e from public.encounters where patient_id = p_patient and hospital_id = h and kind in ('opd','emergency')
     and (status = 'open' or (started_at at time zone 'Asia/Kolkata')::date = (now() at time zone 'Asia/Kolkata')::date)
     and not exists (select 1 from public.invoices i where i.encounter_id = encounters.id and i.status <> 'cancelled')
   order by started_at desc limit 1;
  if e.id is not null then
    enc := e.id;
    select * into c from public.service_charges where hospital_id = h and active and name = case when e.kind = 'emergency' then 'Emergency consultation' else 'OPD consultation' end;
    if c.id is not null then items := items || jsonb_build_object('description', c.name, 'quantity', 1, 'rate', c.price, 'charge_id', c.id); end if;
  end if;
  -- admission → per-day charges
  select ad.*, en.id as enc_id into a from public.admissions ad left join public.encounters en on en.id = ad.encounter_id
   where ad.patient_id = p_patient and ad.hospital_id = h and (ad.status = 'admitted' or ad.discharged_at > now() - interval '2 days')
     and not exists (select 1 from public.invoices i where i.encounter_id = ad.encounter_id and i.category = 'ipd' and i.status <> 'cancelled')
   order by ad.admitted_at desc limit 1;
  if a.id is not null then
    enc := coalesce(a.enc_id, enc);
    days := greatest(1, ceil(extract(epoch from coalesce(a.discharged_at, now()) - a.admitted_at) / 86400.0)::int);
    for c in select * from public.service_charges where hospital_id = h and active and per_day order by category, name loop
      items := items || jsonb_build_object('description', c.name, 'quantity', days, 'rate', c.price, 'charge_id', c.id);
    end loop;
  end if;
  -- lab tests not billed yet
  for c in select o.id, t.name, t.price from public.lab_orders o join public.lab_tests t on t.id = o.test_id
            where o.patient_id = p_patient and o.hospital_id = h and o.status <> 'cancelled'
              and not exists (select 1 from public.invoice_items ii join public.invoices i on i.id = ii.invoice_id where ii.lab_order_id = o.id and i.status <> 'cancelled') loop
    items := items || jsonb_build_object('description', 'Lab: ' || c.name, 'quantity', 1, 'rate', c.price, 'lab_order_id', c.id);
  end loop;
  return jsonb_build_object('encounter_id', enc, 'category', case when a.id is not null then 'ipd' else 'opd' end, 'items', items,
                            'admitted_days', days);
end $$;
revoke all on function public.suggest_bill(uuid) from public, anon;
grant execute on function public.suggest_bill(uuid) to authenticated;

-- ---------- accountant agent: read-only checks ----------
create or replace function public.agent_h_dues(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; n int; amt numeric;
begin
  select coalesce(jsonb_agg(jsonb_build_object('invoice', invoice_no, 'patient', patient, 'uhid', uhid, 'phone', phone, 'bill', net, 'paid', paid, 'baaki', net - paid,
           'date', to_char(created_at at time zone 'Asia/Kolkata', 'DD Mon')) order by net - paid desc), '[]'), count(*), coalesce(sum(net - paid), 0)
    into items, n, amt
    from (select i.invoice_no, p.full_name patient, p.uhid, p.phone, i.created_at, i.total - i.discount net, public.invoice_paid(i.id) paid
            from public.invoices i join public.patients p on p.id = i.patient_id
           where i.hospital_id = h and i.status in ('unpaid','partial')) s;
  return jsonb_build_object('summary', n || ' bill baaki · kul baaki ₹' || to_char(amt, 'FM99,99,99,990'), 'items', items, 'alert', false);
end $$;

create or replace function public.agent_h_money_today(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := coalesce(nullif(inp->>'day','')::date, (now() at time zone 'Asia/Kolkata')::date); bym jsonb; inn numeric; refund numeric; exp numeric; cash numeric; bills int; closed boolean;
begin
  select coalesce(jsonb_object_agg(method, s), '{}'), coalesce(sum(s), 0) into bym, inn
    from (select method, sum(amount) s from public.payments where hospital_id = h and amount > 0 and (created_at at time zone 'Asia/Kolkata')::date = d group by method) x;
  select coalesce(-sum(amount), 0) into refund from public.payments where hospital_id = h and amount < 0 and (created_at at time zone 'Asia/Kolkata')::date = d;
  select coalesce(sum(amount), 0) into exp from public.expenses where hospital_id = h and spent_on = d;
  select coalesce(sum(amount), 0) into cash from public.payments where hospital_id = h and method = 'cash' and (created_at at time zone 'Asia/Kolkata')::date = d;
  cash := cash - coalesce((select sum(amount) from public.expenses where hospital_id = h and method = 'cash' and spent_on = d), 0);
  select count(*) into bills from public.invoices where hospital_id = h and status <> 'cancelled' and (created_at at time zone 'Asia/Kolkata')::date = d;
  closed := exists (select 1 from public.cash_closings where hospital_id = h and day = d);
  return jsonb_build_object('summary', to_char(d, 'DD Mon') || ': aaya ₹' || to_char(inn, 'FM99,99,990') || coalesce(' · refund ₹' || nullif(to_char(refund, 'FM99,99,990'), '0'), '')
      || ' · kharcha ₹' || to_char(exp, 'FM99,99,990') || ' · galle mein cash ₹' || to_char(cash, 'FM99,99,990') || ' · ' || bills || ' naye bill'
      || case when closed then ' · cash close ✓' else '' end,
    'items', jsonb_build_array(jsonb_build_object('by_method', bym, 'in', inn, 'refund', refund, 'expense', exp, 'cash_in_hand', cash, 'bills', bills, 'cash_closed', closed)),
    'alert', false);
end $$;

create or replace function public.agent_h_patient_balance(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare pid uuid := (inp->>'patient_id')::uuid; items jsonb; due numeric; nm text;
begin
  select full_name into nm from public.patients where id = pid and hospital_id = h;
  if nm is null then raise exception 'Patient nahi mila'; end if;
  select coalesce(jsonb_agg(jsonb_build_object('invoice', i.invoice_no, 'date', to_char(i.created_at at time zone 'Asia/Kolkata', 'DD Mon YY'), 'category', i.category,
           'bill', i.total - i.discount, 'paid', public.invoice_paid(i.id), 'status', i.status) order by i.created_at desc), '[]'),
         coalesce(sum(i.total - i.discount - public.invoice_paid(i.id)) filter (where i.status in ('unpaid','partial')), 0)
    into items, due
    from public.invoices i where i.patient_id = pid and i.hospital_id = h and i.status <> 'cancelled';
  return jsonb_build_object('summary', nm || ': baaki ₹' || to_char(due, 'FM99,99,990'), 'items', items, 'alert', false);
end $$;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('accountant.today','accountant','Aaj ka hisaab','Aaj kitna paisa aaya (cash/UPI/card), refund, kharcha, galle mein cash','check','low','{doctor,admin,accountant}','{}','{payments,expenses,invoices}',11,'agent_h_money_today',
   '{"type":"object","properties":{"day":{"type":"string","description":"YYYY-MM-DD (khaali = aaj)"}}}'),
 ('accountant.patient_balance','accountant','Patient ka baaki','Ek patient ke saare bill aur kitna baaki','check','low','{doctor,admin,accountant,receptionist}','{}','{invoices,payments,patients}',12,'agent_h_patient_balance',
   '{"type":"object","properties":{"patient_id":{"type":"string"}},"required":["patient_id"]}')
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;
update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{patients,cash_closings}')) where id = 'accountant';
update public.ai_chat_agents set roles = '{doctor,admin,accountant}', tools = '{find_patient,accountant.today,accountant.dues,accountant.patient_balance}' where agent_id = 'accountant';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{accountant.today}')) where agent_id = 'boss';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{accountant.patient_balance}')) where agent_id = 'reception';

-- evening reminder: cash not closed by 9:30 PM
create or replace function public.accounts_night_job() returns void
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Asia/Kolkata')::date; h uuid;
begin
  for h in select id from public.hospitals loop
    if exists (select 1 from public.payments where hospital_id = h and (created_at at time zone 'Asia/Kolkata')::date = d)
       and not exists (select 1 from public.cash_closings where hospital_id = h and day = d) then
      perform public.agent_notify(h, 'accountant', 'warning', '💵 Aaj ka cash close nahi hua', 'Accounts → 💵 Cash close mein aaj ka cash gin kar close karein.', 'agent:accountant:close:' || d);
      perform public.agent_notify(h, 'doctor', 'info', '💵 Aaj ka cash close nahi hua', 'Accountant ko yaad dilaayein.', 'agent:accountant:close:' || d);
    end if;
  end loop;
end $$;
revoke all on function public.accounts_night_job() from public, anon, authenticated;
do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname = 'vatte_accounts_night';
  perform cron.schedule('vatte_accounts_night', '0 16 * * *', $c$select public.accounts_night_job()$c$);   -- 9:30 PM IST
end $$;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;
