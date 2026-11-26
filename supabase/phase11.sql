-- =========================================================
-- VATTE HOSPITAL OS — PHASE 11 (Pharmacy AI)
-- • Medicine list with schedule (OTC / H / H1 / X), GST %, rack
-- • Stock changes ONLY through server functions; every +/- is written in stock_moves (append-only, never edited)
-- • Maal aaya (purchase receive): batch + expiry + MRP check, supplier auto-created
-- • Becho (sale): server picks batch by earliest expiry (FEFO), never sells expired, price = batch MRP, bill made by server
-- • Schedule H1 / X need doctor name (H1 register); pharmacist can take payment for pharmacy bills
-- • Sale cancel (stock back), damage / count correction with reason
-- • Pharmacy AI: find medicine, today's sale, reorder list (read-only); order draft needs Doctor/Admin approval
-- =========================================================

-- ---------- medicine extra fields ----------
alter table public.medicines add column if not exists schedule text not null default 'OTC';
alter table public.medicines add column if not exists gst_pct numeric(5,2) not null default 12;
alter table public.medicines add column if not exists rack text;
do $$ begin
  alter table public.medicines add constraint medicines_schedule_chk check (schedule in ('OTC','H','H1','X'));
exception when duplicate_object then null; end $$;
do $$ begin
  alter table public.medicines add constraint medicines_gst_chk check (gst_pct in (0,5,12,18,28));
exception when duplicate_object then null; end $$;

alter table public.invoices add column if not exists rx_doctor text;     -- prescribing doctor (pharmacy bills)
alter table public.invoices add column if not exists rx_note text;

-- ---------- stock ledger (append-only) ----------
create table if not exists public.stock_moves (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null references public.hospitals(id),
  medicine_id uuid not null references public.medicines(id),
  batch_id uuid not null references public.medicine_batches(id),
  change int not null check (change <> 0),
  kind text not null check (kind in ('purchase','sale','sale_cancel','writeoff','adjust')),
  ref_id uuid,
  note text,
  balance int not null check (balance >= 0),
  by_user uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists stock_moves_med_idx on public.stock_moves(hospital_id, medicine_id, created_at desc);
create index if not exists stock_moves_day_idx on public.stock_moves(hospital_id, created_at desc);
alter table public.stock_moves enable row level security;
drop policy if exists p_read on public.stock_moves;
create policy p_read on public.stock_moves for select to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,pharmacist}'));
revoke all on public.stock_moves from anon;
revoke insert, update, delete on public.stock_moves from authenticated;
grant select on public.stock_moves to authenticated;
drop trigger if exists no_change on public.stock_moves;
create trigger no_change before update or delete on public.stock_moves for each row execute function public.block_change();

-- batches & purchases: no direct writes from the app any more (only the functions below)
drop policy if exists p_insert on public.medicine_batches; drop policy if exists p_update on public.medicine_batches;
revoke insert, update, delete on public.medicine_batches from authenticated;
drop policy if exists p_insert on public.purchases; drop policy if exists p_update on public.purchases;
revoke insert, update, delete on public.purchases from authenticated;
drop policy if exists p_insert on public.purchase_items; drop policy if exists p_update on public.purchase_items; drop policy if exists p_delete on public.purchase_items;
revoke insert, update, delete on public.purchase_items from authenticated;
drop trigger if exists no_change on public.purchase_items;
create trigger no_change before update or delete on public.purchase_items for each row execute function public.block_change();

-- one internal helper: change a batch and write the ledger line
create or replace function public.stock_move(h uuid, p_batch uuid, p_change int, p_kind text, p_ref uuid, p_note text, p_by uuid) returns int
language plpgsql security definer set search_path = public as $$
declare b public.medicine_batches;
begin
  select * into b from public.medicine_batches where id = p_batch and hospital_id = h for update;
  if b.id is null then raise exception 'Batch nahi mila'; end if;
  if b.quantity + p_change < 0 then raise exception 'Stock kam hai (batch % mein sirf %)', b.batch_no, b.quantity; end if;
  update public.medicine_batches set quantity = quantity + p_change where id = b.id;
  insert into public.stock_moves(hospital_id, medicine_id, batch_id, change, kind, ref_id, note, balance, by_user)
  values (h, b.medicine_id, b.id, p_change, p_kind, p_ref, p_note, b.quantity + p_change, p_by);
  return b.quantity + p_change;
end $$;
revoke all on function public.stock_move(uuid, uuid, int, text, uuid, text, uuid) from public, anon, authenticated;

-- ---------- medicine list (add / edit) ----------
create or replace function public.pharmacy_save_medicine(p_id uuid, p_name text, p_generic text, p_form text, p_strength text,
  p_mrp numeric, p_reorder int, p_schedule text, p_gst numeric, p_rack text, p_active boolean default true) returns public.medicines
language plpgsql security definer set search_path = public as $$
declare m public.medicines; h uuid := public.my_hospital();
begin
  if not public.has_role('{doctor,admin,pharmacist}') then raise exception 'Dawa list sirf Pharmacist / Doctor / Admin badal sakte hain'; end if;
  if coalesce(trim(p_name), '') = '' then raise exception 'Dawa ka naam likhein'; end if;
  if p_mrp is not null and (p_mrp < 0 or p_mrp > 100000) then raise exception 'MRP galat hai'; end if;
  if coalesce(p_reorder, 0) < 0 or coalesce(p_reorder, 0) > 100000 then raise exception 'Reorder level galat hai'; end if;
  if p_id is null then
    insert into public.medicines(hospital_id, name, generic_name, form, strength, mrp, reorder_level, schedule, gst_pct, rack, active)
    values (h, trim(p_name), nullif(trim(p_generic), ''), nullif(trim(p_form), ''), nullif(trim(p_strength), ''), p_mrp,
            coalesce(p_reorder, 10), coalesce(p_schedule, 'OTC'), coalesce(p_gst, 12), nullif(trim(p_rack), ''), coalesce(p_active, true))
    returning * into m;
  else
    update public.medicines set name = trim(p_name), generic_name = nullif(trim(p_generic), ''), form = nullif(trim(p_form), ''),
           strength = nullif(trim(p_strength), ''), mrp = p_mrp, reorder_level = coalesce(p_reorder, reorder_level),
           schedule = coalesce(p_schedule, schedule), gst_pct = coalesce(p_gst, gst_pct), rack = nullif(trim(p_rack), ''), active = coalesce(p_active, active)
     where id = p_id and hospital_id = h returning * into m;
    if m.id is null then raise exception 'Dawa nahi mili'; end if;
  end if;
  return m;
exception when unique_violation then raise exception 'Is naam + strength ki dawa pehle se list mein hai';
end $$;
revoke all on function public.pharmacy_save_medicine(uuid, text, text, text, text, numeric, int, text, numeric, text, boolean) from public, anon;
grant execute on function public.pharmacy_save_medicine(uuid, text, text, text, text, numeric, int, text, numeric, text, boolean) to authenticated;

-- ---------- stock list (search) ----------
create or replace function public.pharmacy_stock(p_q text default null)
returns table (medicine_id uuid, name text, generic_name text, form text, strength text, schedule text, rack text, mrp numeric,
               reorder_level int, active boolean, stock int, expired_qty int, next_expiry date, batches jsonb)
language sql stable security definer set search_path = public as $$
  select m.id, m.name, m.generic_name, m.form, m.strength, m.schedule, m.rack, m.mrp, m.reorder_level, m.active,
         coalesce(sum(b.quantity) filter (where b.expiry_date >= current_date), 0)::int,
         coalesce(sum(b.quantity) filter (where b.expiry_date < current_date), 0)::int,
         min(b.expiry_date) filter (where b.expiry_date >= current_date and b.quantity > 0),
         coalesce(jsonb_agg(jsonb_build_object('batch_id', b.id, 'batch', b.batch_no, 'expiry', b.expiry_date, 'qty', b.quantity, 'mrp', b.mrp)
                            order by b.expiry_date) filter (where b.quantity > 0), '[]')
    from public.medicines m left join public.medicine_batches b on b.medicine_id = m.id
   where m.hospital_id = public.my_hospital() and public.has_role('{doctor,admin,pharmacist,nurse}')
     and (coalesce(trim(p_q), '') = '' or m.name ilike '%' || trim(p_q) || '%' or m.generic_name ilike '%' || trim(p_q) || '%')
   group by m.id
   order by m.name
   limit 300
$$;
revoke all on function public.pharmacy_stock(text) from public, anon;
grant execute on function public.pharmacy_stock(text) to authenticated;

-- ---------- maal aaya (purchase receive) ----------
-- p_items: [{ "medicine_id": "...", "batch_no": "A12", "expiry": "2027-08-31", "quantity": 100, "free_qty": 10, "purchase_price": 1.5, "mrp": 2.2 }]
create or replace function public.pharmacy_receive(p_supplier_name text, p_invoice_no text, p_items jsonb) returns public.purchases
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); s uuid; p public.purchases; x jsonb; m public.medicines; b public.medicine_batches;
        q int; fq int; pp numeric; mr numeric; ex date; tot numeric := 0;
begin
  if not public.has_role('{doctor,admin,pharmacist}') then raise exception 'Maal sirf Pharmacist / Doctor / Admin chadha sakte hain'; end if;
  if coalesce(trim(p_supplier_name), '') = '' then raise exception 'Supplier ka naam likhein'; end if;
  if coalesce(trim(p_invoice_no), '') = '' then raise exception 'Supplier ke bill ka number likhein'; end if;
  if jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) = 0 then raise exception 'Kam se kam ek dawa daalein'; end if;
  if jsonb_array_length(p_items) > 100 then raise exception 'Ek baar mein 100 line tak'; end if;
  insert into public.suppliers(hospital_id, name) values (h, trim(p_supplier_name)) on conflict (hospital_id, name) do nothing;
  select id into s from public.suppliers where hospital_id = h and name = trim(p_supplier_name);
  if exists (select 1 from public.purchases where hospital_id = h and supplier_id = s and supplier_invoice_no = trim(p_invoice_no) and status = 'received') then
    raise exception 'Is supplier ka bill % pehle hi chadh chuka hai', trim(p_invoice_no); end if;
  insert into public.purchases(hospital_id, supplier_id, kind, status, supplier_invoice_no, total, created_by)
  values (h, s, 'received', 'received', trim(p_invoice_no), 0, auth.uid()) returning * into p;
  for x in select * from jsonb_array_elements(p_items) loop
    select * into m from public.medicines where id = (x->>'medicine_id')::uuid and hospital_id = h;
    if m.id is null then raise exception 'Dawa list mein nahi hai — pehle "Dawa list" mein jodein'; end if;
    q := coalesce((x->>'quantity')::int, 0); fq := coalesce((x->>'free_qty')::int, 0);
    pp := (x->>'purchase_price')::numeric; mr := (x->>'mrp')::numeric; ex := (x->>'expiry')::date;
    if coalesce(trim(x->>'batch_no'), '') = '' then raise exception '%: batch number likhein', m.name; end if;
    if q <= 0 or q > 100000 or fq < 0 or fq > 100000 then raise exception '%: quantity galat hai', m.name; end if;
    if ex is null or ex <= current_date then raise exception '%: expiry aaj ke baad ki honi chahiye (expired maal mat lo)', m.name; end if;
    if pp is null or pp < 0 or mr is null or mr <= 0 then raise exception '%: kharid rate aur MRP dono likhein', m.name; end if;
    if pp > mr then raise exception '%: kharid rate (₹%) MRP (₹%) se zyada nahi ho sakta', m.name, pp, mr; end if;
    select * into b from public.medicine_batches where medicine_id = m.id and batch_no = upper(trim(x->>'batch_no'));
    if b.id is null then
      insert into public.medicine_batches(hospital_id, medicine_id, batch_no, expiry_date, quantity, purchase_price, mrp)
      values (h, m.id, upper(trim(x->>'batch_no')), ex, 0, pp, mr) returning * into b;
    elsif b.expiry_date <> ex then
      raise exception '%: batch % pehle expiry % ke saath aaya tha — expiry check karein', m.name, b.batch_no, b.expiry_date;
    else
      update public.medicine_batches set purchase_price = pp, mrp = mr where id = b.id;
    end if;
    perform public.stock_move(h, b.id, q + fq, 'purchase', p.id, trim(p_invoice_no) || case when fq > 0 then ' (+' || fq || ' free)' else '' end, auth.uid());
    insert into public.purchase_items(hospital_id, purchase_id, medicine_id, description, quantity, rate)
    values (h, p.id, m.id, m.name || coalesce(' ' || m.strength, '') || ' · ' || b.batch_no || ' · exp ' || to_char(ex, 'MM/YY')
                         || case when fq > 0 then ' · +' || fq || ' free' else '' end, q, pp);
    tot := tot + q * pp;
    if m.mrp is null or m.mrp <> mr then update public.medicines set mrp = mr where id = m.id; end if;
  end loop;
  update public.purchases set total = round(tot, 2) where id = p.id returning * into p;
  return p;
end $$;
revoke all on function public.pharmacy_receive(text, text, jsonb) from public, anon;
grant execute on function public.pharmacy_receive(text, text, jsonb) to authenticated;

-- ---------- becho (sale → pharmacy bill) ----------
-- p_items: [{ "medicine_id": "...", "quantity": 10 }]   — the server chooses the batch (earliest expiry first) and the price (batch MRP)
create or replace function public.pharmacy_sell(p_patient uuid, p_items jsonb, p_discount numeric default 0, p_discount_reason text default null,
  p_rx_doctor text default null, p_rx_note text default null) returns public.invoices
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); i public.invoices; x jsonb; m public.medicines; b record; need int; take int;
        total numeric := 0; lines jsonb := '[]'; l jsonb; enc uuid; needs_rx boolean := false;
begin
  if not public.has_role('{doctor,admin,pharmacist}') then raise exception 'Dawa sirf Pharmacist / Doctor / Admin bech sakte hain'; end if;
  if not exists (select 1 from public.patients where id = p_patient and hospital_id = h) then raise exception 'Patient nahi mila (pehle Reception mein register karein)'; end if;
  if jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) = 0 then raise exception 'Kam se kam ek dawa daalein'; end if;
  if jsonb_array_length(p_items) > 50 then raise exception 'Ek bill mein 50 dawa tak'; end if;
  for x in select * from jsonb_array_elements(p_items) loop
    select * into m from public.medicines where id = (x->>'medicine_id')::uuid and hospital_id = h;
    if m.id is null then raise exception 'Dawa nahi mili'; end if;
    if not m.active then raise exception '% band (inactive) hai', m.name; end if;
    if m.schedule in ('H1','X') then needs_rx := true; end if;
    need := coalesce((x->>'quantity')::int, 0);
    if need <= 0 or need > 5000 then raise exception '%: quantity galat hai', m.name; end if;
    -- FEFO: earliest expiry first, never expired
    for b in select * from public.medicine_batches where medicine_id = m.id and hospital_id = h and quantity > 0 and expiry_date >= current_date
              order by expiry_date, batch_no for update loop
      exit when need = 0;
      take := least(need, b.quantity);
      if coalesce(b.mrp, m.mrp) is null then raise exception '%: batch % ka MRP nahi hai', m.name, b.batch_no; end if;
      lines := lines || jsonb_build_object('batch_id', b.id, 'quantity', take, 'rate', coalesce(b.mrp, m.mrp),
                 'description', m.name || coalesce(' ' || m.strength, '') || ' (B:' || b.batch_no || ' Exp ' || to_char(b.expiry_date, 'MM/YY') || ')');
      total := total + take * coalesce(b.mrp, m.mrp); need := need - take;
    end loop;
    if need > 0 then raise exception '%: stock kam hai — % aur chahiye', m.name, need; end if;
  end loop;
  if needs_rx and coalesce(trim(p_rx_doctor), '') = '' then raise exception 'Schedule H1 / X dawa ke liye doctor ka naam (parchi) likhna zaroori hai'; end if;
  p_discount := round(coalesce(p_discount, 0), 2);
  if p_discount < 0 or p_discount > total then raise exception 'Discount bill se zyada nahi ho sakta'; end if;
  if p_discount > 0 and coalesce(trim(p_discount_reason), '') = '' then raise exception 'Discount ka kaaran likhna zaroori hai'; end if;
  if p_discount > total * 0.10 and not public.has_role('{doctor}') then raise exception '10%% se zyada discount sirf Doctor de sakte hain'; end if;
  select id into enc from public.encounters where patient_id = p_patient and hospital_id = h and status = 'open' order by started_at desc limit 1;
  insert into public.invoices(hospital_id, patient_id, encounter_id, category, total, discount, discount_reason, status, created_by, rx_doctor, rx_note)
  values (h, p_patient, enc, 'pharmacy', round(total, 2), p_discount, nullif(trim(p_discount_reason), ''), 'unpaid', auth.uid(),
          nullif(trim(p_rx_doctor), ''), nullif(trim(p_rx_note), '')) returning * into i;
  for l in select * from jsonb_array_elements(lines) loop
    insert into public.invoice_items(hospital_id, invoice_id, description, batch_id, quantity, rate)
    values (h, i.id, l->>'description', (l->>'batch_id')::uuid, (l->>'quantity')::int, (l->>'rate')::numeric);
    perform public.stock_move(h, (l->>'batch_id')::uuid, -(l->>'quantity')::int, 'sale', i.id, i.invoice_no, auth.uid());
  end loop;
  perform public.refresh_invoice_status(i.id);
  select * into i from public.invoices where id = i.id;
  return i;
end $$;
revoke all on function public.pharmacy_sell(uuid, jsonb, numeric, text, text, text) from public, anon;
grant execute on function public.pharmacy_sell(uuid, jsonb, numeric, text, text, text) to authenticated;

-- ---------- payments: pharmacist may take payment for pharmacy bills ----------
create or replace function public.record_payment(p_invoice uuid, p_amount numeric, p_method text, p_reference text default null, p_note text default null)
returns public.payments
language plpgsql security definer set search_path = public as $$
declare i public.invoices; p public.payments; due numeric;
begin
  select * into i from public.invoices where id = p_invoice and hospital_id = public.my_hospital() for update;
  if i.id is null then raise exception 'Bill nahi mila'; end if;
  if not (public.has_role('{doctor,admin,accountant,receptionist}') or (i.category = 'pharmacy' and public.has_role('{pharmacist}'))) then
    raise exception 'Payment lene ki permission nahi'; end if;
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

-- ---------- sale cancel (stock goes back) ----------
create or replace function public.pharmacy_cancel_sale(p_invoice uuid, p_reason text) returns public.invoices
language plpgsql security definer set search_path = public as $$
declare h uuid := public.my_hospital(); i public.invoices; it record;
begin
  if not public.has_role('{doctor,admin,pharmacist}') then raise exception 'Permission nahi'; end if;
  if coalesce(trim(p_reason), '') = '' then raise exception 'Cancel ka kaaran likhein'; end if;
  select * into i from public.invoices where id = p_invoice and hospital_id = h and category = 'pharmacy' for update;
  if i.id is null then raise exception 'Pharmacy bill nahi mila'; end if;
  if i.status = 'cancelled' then raise exception 'Bill pehle se cancel hai'; end if;
  if public.has_role('{pharmacist}') and (i.created_at at time zone 'Asia/Kolkata')::date <> (now() at time zone 'Asia/Kolkata')::date then
    raise exception 'Purana bill sirf Doctor / Admin cancel kar sakte hain'; end if;
  if public.invoice_paid(i.id) <> 0 then raise exception 'Is bill par payment hai — pehle Accounts se refund karein, phir cancel'; end if;
  update public.invoices set status = 'cancelled', cancel_reason = trim(p_reason), cancelled_by = auth.uid(), cancelled_at = now()
   where id = i.id returning * into i;
  for it in select * from public.invoice_items where invoice_id = i.id and batch_id is not null loop
    perform public.stock_move(h, it.batch_id, it.quantity, 'sale_cancel', i.id, 'Cancel ' || i.invoice_no || ': ' || trim(p_reason), auth.uid());
  end loop;
  return i;
end $$;
revoke all on function public.pharmacy_cancel_sale(uuid, text) from public, anon;
grant execute on function public.pharmacy_cancel_sale(uuid, text) to authenticated;

-- ---------- damage / count correction ----------
create or replace function public.pharmacy_adjust(p_batch uuid, p_change int, p_reason text) returns int
language plpgsql security definer set search_path = public as $$
begin
  if not public.has_role('{doctor,admin,pharmacist}') then raise exception 'Permission nahi'; end if;
  if coalesce(p_change, 0) = 0 or abs(p_change) > 100000 then raise exception 'Kitna kam / zyada karna hai, likhein'; end if;
  if coalesce(trim(p_reason), '') = '' then raise exception 'Kaaran likhein (jaise: toot gayi, ginti mein fark)'; end if;
  if p_change > 0 and not public.has_role('{doctor,admin}') then raise exception 'Stock badhana sirf Doctor / Admin kar sakte hain (naya maal "Maal aaya" se chadhayein)'; end if;
  return public.stock_move(public.my_hospital(), p_batch, p_change, 'adjust', null, trim(p_reason), auth.uid());
end $$;
revoke all on function public.pharmacy_adjust(uuid, int, text) from public, anon;
grant execute on function public.pharmacy_adjust(uuid, int, text) to authenticated;

-- expired write-off (approved through the agent) now also writes the ledger
create or replace function public.agent_h_writeoff_expired(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare bid uuid := (inp->>'batch_id')::uuid; ex date; q int; nm text; bn text;
begin
  select b.expiry_date, b.quantity, m.name, b.batch_no into ex, q, nm, bn
    from public.medicine_batches b join public.medicines m on m.id = b.medicine_id where b.id = bid and b.hospital_id = h for update;
  if ex is null then raise exception 'Batch nahi mila'; end if;
  if ex >= current_date then raise exception 'Ye batch abhi expire nahi hua (expiry %)', ex; end if;
  if q > 0 then perform public.stock_move(h, bid, -q, 'writeoff', null, 'Expired write-off (approved)', req); end if;
  return jsonb_build_object('summary', nm || ' batch ' || bn || ': ' || q || ' expired stock zero kiya ✓', 'items', '[]'::jsonb, 'alert', false);
end $$;

-- ---------- reorder suggestion ----------
create or replace function public.pharmacy_reorder_rows(h uuid)
returns table (medicine_id uuid, name text, stock int, reorder_level int, sold_30d int, suggest int, last_rate numeric, last_supplier text)
language sql stable security definer set search_path = public as $$
  select m.id, m.name || coalesce(' ' || m.strength, ''), s.stock, m.reorder_level, s.sold,
         greatest(m.reorder_level * 2 - s.stock, s.sold - s.stock, 1),
         (select pi.rate from public.purchase_items pi join public.purchases p on p.id = pi.purchase_id
           where pi.medicine_id = m.id and p.status = 'received' order by p.created_at desc limit 1),
         (select su.name from public.purchase_items pi join public.purchases p on p.id = pi.purchase_id join public.suppliers su on su.id = p.supplier_id
           where pi.medicine_id = m.id and p.status = 'received' order by p.created_at desc limit 1)
    from public.medicines m
    cross join lateral (select coalesce((select sum(quantity) from public.medicine_batches b where b.medicine_id = m.id and b.expiry_date >= current_date), 0)::int as stock,
                               coalesce((select -sum(change) from public.stock_moves sm where sm.medicine_id = m.id and sm.kind in ('sale','sale_cancel')
                                          and sm.created_at > now() - interval '30 days'), 0)::int as sold) s
   where m.hospital_id = h and m.active and m.reorder_level > 0 and s.stock < m.reorder_level
   order by s.stock, m.name
$$;
revoke all on function public.pharmacy_reorder_rows(uuid) from public, anon, authenticated;

create or replace function public.pharmacy_reorder()
returns table (medicine_id uuid, name text, stock int, reorder_level int, sold_30d int, suggest int, last_rate numeric, last_supplier text)
language sql stable security definer set search_path = public as $$
  select * from public.pharmacy_reorder_rows(public.my_hospital()) where public.has_role('{doctor,admin,pharmacist}')
$$;
revoke all on function public.pharmacy_reorder() from public, anon;
grant execute on function public.pharmacy_reorder() to authenticated;

-- ---------- Pharmacy AI handlers ----------
create or replace function public.agent_h_find_medicine(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare q text := trim(coalesce(inp->>'query', '')); items jsonb; n int;
begin
  if length(q) < 2 then raise exception 'Dawa ka naam (kam se kam 2 akshar) do'; end if;
  select coalesce(jsonb_agg(jsonb_build_object('medicine', name, 'generic', generic_name, 'strength', strength, 'schedule', schedule, 'rack', rack,
           'stock', stock, 'mrp', mrp, 'next_expiry', next_expiry, 'kam_stock', stock < reorder_level) order by name), '[]'), count(*)
    into items, n
    from (select m.name, m.generic_name, m.strength, m.schedule, m.rack, m.mrp, m.reorder_level,
                 coalesce(sum(b.quantity) filter (where b.expiry_date >= current_date), 0) stock,
                 min(b.expiry_date) filter (where b.expiry_date >= current_date and b.quantity > 0) next_expiry
            from public.medicines m left join public.medicine_batches b on b.medicine_id = m.id
           where m.hospital_id = h and m.active and (m.name ilike '%' || q || '%' or m.generic_name ilike '%' || q || '%')
           group by m.id limit 15) s;
  return jsonb_build_object('summary', case when n = 0 then '"' || q || '" naam ki koi dawa list mein nahi' else n || ' dawa mili' end, 'items', items, 'alert', false);
end $$;

create or replace function public.agent_h_pharmacy_sales(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare d date := coalesce(nullif(inp->>'day','')::date, (now() at time zone 'Asia/Kolkata')::date); n int; amt numeric; paid numeric; top jsonb; h1 int;
begin
  select count(*), coalesce(sum(total - discount), 0), coalesce(sum(public.invoice_paid(id)), 0), count(*) filter (where rx_doctor is not null)
    into n, amt, paid, h1
    from public.invoices where hospital_id = h and category = 'pharmacy' and status <> 'cancelled' and (created_at at time zone 'Asia/Kolkata')::date = d;
  select coalesce(jsonb_agg(jsonb_build_object('medicine', nm, 'qty', q) order by q desc), '[]') into top
    from (select m.name nm, -sum(sm.change) q from public.stock_moves sm join public.medicines m on m.id = sm.medicine_id
           where sm.hospital_id = h and sm.kind in ('sale','sale_cancel') and (sm.created_at at time zone 'Asia/Kolkata')::date = d
           group by m.name having -sum(sm.change) > 0 order by 2 desc limit 5) t;
  return jsonb_build_object('summary', to_char(d, 'DD Mon') || ': ' || n || ' pharmacy bill · ₹' || to_char(amt, 'FM99,99,990') || ' ki bikri · mila ₹' || to_char(paid, 'FM99,99,990')
           || case when amt - paid > 0 then ' · baaki ₹' || to_char(amt - paid, 'FM99,99,990') else '' end,
    'items', jsonb_build_object('top_medicines', top, 'parchi_wale_bill', h1), 'alert', false);
end $$;

create or replace function public.agent_h_reorder(h uuid, inp jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare items jsonb; n int;
begin
  select coalesce(jsonb_agg(jsonb_build_object('medicine', name, 'stock', stock, 'reorder_level', reorder_level, 'sold_30_din', sold_30d,
           'mangao', suggest, 'last_rate', last_rate, 'supplier', last_supplier)), '[]'), count(*)
    into items, n from public.pharmacy_reorder_rows(h);
  return jsonb_build_object('summary', case when n = 0 then 'Sab dawa ka stock theek hai ✓' else n || ' dawa mangwani hai' end,
                            'items', items, 'alert', n > 0, 'alert_role', 'pharmacist');
end $$;

-- controlled action: after Doctor/Admin approval, make a purchase order list (status approved) from the reorder list
create or replace function public.agent_h_order_draft(h uuid, inp jsonb, req uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare p public.purchases; n int; tot numeric;
begin
  select count(*) into n from public.pharmacy_reorder_rows(h);
  if n = 0 then raise exception 'Koi dawa kam nahi hai — order ki zaroorat nahi'; end if;
  insert into public.purchases(hospital_id, kind, status, total, created_by, approved_by)
  values (h, 'request', 'approved', 0, req, (select approved_by from public.agent_tasks where hospital_id = h and action = 'pharmacy.order_draft' and status = 'running' order by updated_at desc limit 1))
  returning * into p;
  insert into public.purchase_items(hospital_id, purchase_id, medicine_id, description, quantity, rate)
  select h, p.id, medicine_id, name || coalesce(' · last: ' || last_supplier, ''), suggest, coalesce(last_rate, 0) from public.pharmacy_reorder_rows(h);
  select coalesce(sum(quantity * rate), 0) into tot from public.purchase_items where purchase_id = p.id;
  update public.purchases set total = round(tot, 2) where id = p.id;
  perform public.agent_notify(h, 'pharmacist', 'info', '📦 Order list taiyaar (' || n || ' dawa)', 'Pharmacy → 📦 Order mein dekhein aur supplier ko bhejein.', 'agent:pharmacy:order:' || p.id);
  return jsonb_build_object('summary', n || ' dawa ki order list bani ✓ (andaazan ₹' || to_char(tot, 'FM99,99,990') || ') — Pharmacy → 📦 Order mein dekhein',
                            'items', jsonb_build_array(jsonb_build_object('purchase_id', p.id)), 'alert', false);
end $$;

-- mark an order list as sent / cancelled (pharmacist)
create or replace function public.pharmacy_order_status(p_purchase uuid, p_status text) returns public.purchases
language plpgsql security definer set search_path = public as $$
declare p public.purchases;
begin
  if not public.has_role('{doctor,admin,pharmacist}') then raise exception 'Permission nahi'; end if;
  if p_status not in ('received','cancelled') then raise exception 'Status galat'; end if;
  update public.purchases set status = p_status where id = p_purchase and hospital_id = public.my_hospital() and kind = 'request' and status = 'approved'
  returning * into p;
  if p.id is null then raise exception 'Khula order nahi mila'; end if;
  return p;
end $$;
revoke all on function public.pharmacy_order_status(uuid, text) from public, anon;
grant execute on function public.pharmacy_order_status(uuid, text) to authenticated;

insert into public.agent_actions(id, agent_id, title, description, kind, risk, requester_roles, approver_roles, tables, ord, handler, params) values
 ('pharmacy.find_medicine','pharmacy','Dawa dhoondo','Dawa ka stock, MRP, rack aur agli expiry (naam ya generic naam se)','check','low','{doctor,admin,pharmacist,nurse}','{}','{medicines,medicine_batches}',6,'agent_h_find_medicine',
   '{"type":"object","properties":{"query":{"type":"string","description":"dawa ka naam ya generic naam"}},"required":["query"]}'),
 ('pharmacy.sales_today','pharmacy','Aaj ki pharmacy bikri','Aaj kitne pharmacy bill, kitni bikri, kitna paisa mila, sabse zyada biki dawa','check','low','{doctor,admin,pharmacist}','{}','{invoices,stock_moves,medicines}',7,'agent_h_pharmacy_sales',
   '{"type":"object","properties":{"day":{"type":"string","description":"YYYY-MM-DD (khaali = aaj)"}}}'),
 ('pharmacy.reorder','pharmacy','Kya mangwana hai?','Reorder level se kam dawa, pichhle 30 din ki bikri aur kitna mangwana chahiye','check','low','{doctor,admin,pharmacist}','{}','{medicines,medicine_batches,stock_moves,purchases}',8,'agent_h_reorder', null),
 ('pharmacy.order_draft','pharmacy','Order list banao','Kam stock wali dawa ki purchase order list banana (Doctor/Admin ki approval se)','act','controlled','{doctor,admin,pharmacist}','{doctor,admin}','{purchases,purchase_items}',23,'agent_h_order_draft', null)
on conflict (id) do update set title=excluded.title, description=excluded.description, kind=excluded.kind, risk=excluded.risk, requester_roles=excluded.requester_roles,
  approver_roles=excluded.approver_roles, tables=excluded.tables, ord=excluded.ord, handler=excluded.handler, params=excluded.params;

update public.agents set allowed_tables = array(select distinct unnest(allowed_tables || '{stock_moves,patients}')) where id = 'pharmacy';
update public.ai_chat_agents set roles = '{doctor,admin,pharmacist}',
  tools = '{pharmacy.stock,pharmacy.find_medicine,pharmacy.sales_today,pharmacy.reorder,pharmacy.order_draft}' where agent_id = 'pharmacy';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{pharmacy.sales_today,pharmacy.reorder}')) where agent_id = 'boss';
update public.ai_chat_agents set tools = array(select distinct unnest(tools || '{pharmacy.find_medicine}')) where agent_id = 'nurse';

-- morning check for the pharmacist (9:15 AM IST): expiry + low stock → notification
do $$
begin
  perform cron.unschedule(jobname) from cron.job where jobname = 'vatte_pharmacy_morning';
  perform cron.schedule('vatte_pharmacy_morning', '45 3 * * *', $c$select public.agent_cron('pharmacy.stock')$c$);
end $$;

-- ---------- starter medicine list (no stock; pharmacist adds stock with "Maal aaya") ----------
insert into public.medicines(hospital_id, name, generic_name, form, strength, mrp, reorder_level, schedule, gst_pct)
select h.id, x.n, x.g, x.f, x.s, null, x.r, x.sc, x.gst from public.hospitals h, (values
  ('Paracetamol','Paracetamol','Tablet','500 mg',50,'OTC',12),
  ('Paracetamol Syrup','Paracetamol','Syrup','125 mg/5 ml',10,'OTC',12),
  ('Cetirizine','Cetirizine','Tablet','10 mg',30,'OTC',12),
  ('Pantoprazole','Pantoprazole','Tablet','40 mg',30,'H',12),
  ('Ondansetron','Ondansetron','Tablet','4 mg',20,'H',12),
  ('Amoxicillin','Amoxicillin','Capsule','500 mg',30,'H1',12),
  ('Azithromycin','Azithromycin','Tablet','500 mg',15,'H1',12),
  ('Metformin','Metformin','Tablet','500 mg',50,'H',12),
  ('Amlodipine','Amlodipine','Tablet','5 mg',50,'H',12),
  ('ORS','Oral rehydration salts','Sachet','21 g',30,'OTC',12),
  ('Normal Saline','Sodium chloride 0.9%','IV fluid','500 ml',20,'H',12),
  ('Diclofenac Injection','Diclofenac','Injection','75 mg/ml',10,'H',12)
) as x(n, g, f, s, r, sc, gst) on conflict do nothing;

do $$
declare f text;
begin
  for f in select p.oid::regprocedure::text from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname like 'agent\_h\_%'
  loop execute format('revoke all on function %s from public, anon, authenticated', f); end loop;
end $$;
