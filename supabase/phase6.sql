-- =========================================================
-- VATTE HOSPITAL OS — PHASE 6 (Nidan: clinical history-taking engine)
-- Question library (shared, read-only for staff), history sessions, answers,
-- red-flag alerts to doctor. AI never diagnoses: the app only lists
-- "possibilities for the doctor to consider" from the answers.
-- Primary reference: Hutchison's Clinical Methods, 24th ed. (2018).
-- Question seed data: supabase/phase6_questions.sql
-- =========================================================

create table if not exists public.hx_complaints (
  id text primary key,
  system text not null,
  name_en text not null,
  name_hi text not null,
  name_mr text not null,
  icon text,
  ord int not null default 100,
  source text,
  active boolean not null default true
);

create table if not exists public.hx_questions (
  id text primary key,
  complaint_id text references public.hx_complaints(id),   -- null = general section
  section text not null check (section in
    ('safety','identification','hopi','associated','redflag','risk','past','drug','allergy',
     'family','personal','ice','ros','obstetric','pediatric','geriatric')),
  ord int not null default 100,
  qtype text not null check (qtype in ('yesno','choice','multi','number','text','scale')),
  options jsonb,                         -- [{v:'sudden', en:'Sudden', hi:'अचानक', mr:'अचानक'}]
  text_en text not null,                 -- clinical wording (for doctor / report)
  text_hi text not null,                 -- patient-friendly Hindi
  text_mr text not null,                 -- patient-friendly Marathi
  clinical_term text,                    -- term used in the report, e.g. 'Orthopnoea'
  dedupe_key text,                       -- same key = same fact, ask only once per session
  show_if jsonb,                         -- {"q":"cp_site","in":["central"]} or {"q":"x","eq":"yes"}
  applies_to jsonb,                      -- {"sex":"female","min_age":12,"max_age":55}
  red_flag boolean not null default false,
  red_flag_note text,
  positive_means text,                   -- what a YES / positive answer points towards
  negative_means text,                   -- what a NO helps make less likely
  differentials text[] not null default '{}',
  source text,                           -- e.g. 'Hutchison 24e, Ch 13, p189-192'
  reviewed_on date not null default current_date,
  active boolean not null default true
);
create index if not exists hx_questions_complaint_idx on public.hx_questions(complaint_id, section, ord);

create table if not exists public.hx_sessions (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  patient_id uuid not null references public.patients(id),
  encounter_id uuid references public.encounters(id),
  status text not null default 'in_progress' check (status in ('in_progress','completed','reviewed')),
  language text not null default 'hi' check (language in ('en','hi','mr')),
  informant text not null default 'self',
  reliability text not null default 'reliable' check (reliability in ('reliable','partly','unreliable')),
  complaints jsonb not null default '[]'::jsonb,  -- [{id, own_words, duration, onset, severity, status}]
  emergency boolean not null default false,
  height_cm numeric(5,1), weight_kg numeric(5,1), blood_sugar int,
  doctor_notes text,
  created_by uuid not null default auth.uid() references auth.users(id),
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  reviewed_by uuid references auth.users(id),
  reviewed_at timestamptz
);
create index if not exists hx_sessions_patient_idx on public.hx_sessions(patient_id, created_at desc);
create index if not exists hx_sessions_status_idx on public.hx_sessions(hospital_id, status, created_at desc);

create table if not exists public.hx_answers (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  session_id uuid not null references public.hx_sessions(id),
  question_id text not null references public.hx_questions(id),
  value jsonb not null,       -- "yes" | "no" | "unknown" | "na" | "unable" | "choice" | ["a","b"] | 5 | "text"
  answered_by uuid not null default auth.uid() references auth.users(id),
  answered_at timestamptz not null default now(),
  unique (session_id, question_id)
);
create index if not exists hx_answers_session_idx on public.hx_answers(session_id);

-- ---------- permissions ----------
alter table public.hx_complaints enable row level security;
alter table public.hx_questions  enable row level security;
alter table public.hx_sessions   enable row level security;
alter table public.hx_answers    enable row level security;

drop policy if exists p_read on public.hx_complaints;
create policy p_read on public.hx_complaints for select to authenticated using (public.my_role() <> 'pending');
drop policy if exists p_read on public.hx_questions;
create policy p_read on public.hx_questions for select to authenticated using (public.my_role() <> 'pending');
revoke all on public.hx_complaints, public.hx_questions from anon;
revoke insert, update, delete on public.hx_complaints, public.hx_questions from authenticated;
grant select on public.hx_complaints, public.hx_questions to authenticated;

drop policy if exists p_read on public.hx_sessions;
drop policy if exists p_insert on public.hx_sessions;
drop policy if exists p_update on public.hx_sessions;
create policy p_read on public.hx_sessions for select to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse,receptionist}'));
create policy p_insert on public.hx_sessions for insert to authenticated
  with check (hospital_id = public.my_hospital() and public.has_role('{doctor,nurse,receptionist}'));
create policy p_update on public.hx_sessions for update to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,nurse,receptionist}')
         and (status <> 'reviewed'))
  with check (hospital_id = public.my_hospital());

drop policy if exists p_read on public.hx_answers;
drop policy if exists p_insert on public.hx_answers;
drop policy if exists p_update on public.hx_answers;
create policy p_read on public.hx_answers for select to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,admin,nurse,receptionist}'));
create policy p_insert on public.hx_answers for insert to authenticated
  with check (hospital_id = public.my_hospital() and public.has_role('{doctor,nurse,receptionist}')
    and exists (select 1 from public.hx_sessions s where s.id = session_id and s.status = 'in_progress'));
create policy p_update on public.hx_answers for update to authenticated
  using (hospital_id = public.my_hospital() and public.has_role('{doctor,nurse,receptionist}')
    and exists (select 1 from public.hx_sessions s where s.id = session_id and s.status = 'in_progress'))
  with check (hospital_id = public.my_hospital());

revoke all on public.hx_sessions, public.hx_answers from anon;
revoke delete on public.hx_sessions, public.hx_answers from authenticated;
grant select, insert, update on public.hx_sessions, public.hx_answers to authenticated;

-- Only a doctor can mark a history "reviewed"; nobody can un-review it.
create or replace function public.guard_hx_session() returns trigger
language plpgsql set search_path = public as $$
begin
  if new.status = 'reviewed' and old.status <> 'reviewed' then
    if not public.has_role('{doctor}') then raise exception 'Sirf doctor history review kar sakte hain'; end if;
    new.reviewed_by := auth.uid(); new.reviewed_at := now();
  end if;
  if new.status = 'completed' and old.status = 'in_progress' then new.completed_at := now(); end if;
  if old.status = 'reviewed' and auth.uid() is not null then
    raise exception 'Review ho chuki history badli nahi ja sakti';
  end if;
  return new;
end $$;
drop trigger if exists guard_hx on public.hx_sessions;
create trigger guard_hx before update on public.hx_sessions
  for each row execute function public.guard_hx_session();

-- Red-flag answer (YES) or emergency screen -> critical alert to doctor
create or replace function public.hx_red_flag_alert() returns trigger
language plpgsql security definer set search_path = public as $$
declare q public.hx_questions; pname text; puhid text;
begin
  select * into q from public.hx_questions where id = new.question_id;
  if not q.red_flag or new.value <> '"yes"'::jsonb then return new; end if;
  if tg_op = 'UPDATE' and old.value = new.value then return new; end if;
  select p.full_name, p.uhid into pname, puhid
    from public.hx_sessions s join public.patients p on p.id = s.patient_id where s.id = new.session_id;
  insert into public.notifications(hospital_id, target_role, level, title, body, source)
  values (new.hospital_id, 'doctor', 'critical',
          '🚩 ' || pname || ': ' || coalesce(q.red_flag_note, q.text_en),
          'UHID ' || puhid || '. Nidan history mein khatre ka nishan mila. Turant dekhein.', 'nidan');
  if q.section = 'safety' then
    update public.hx_sessions set emergency = true where id = new.session_id;
  end if;
  return new;
end $$;
drop trigger if exists hx_red_flag on public.hx_answers;
create trigger hx_red_flag after insert or update on public.hx_answers
  for each row execute function public.hx_red_flag_alert();

-- audit trail + who-did-it
drop trigger if exists audit on public.hx_sessions;
create trigger audit after insert or update on public.hx_sessions for each row execute function public.audit_row();
drop trigger if exists audit on public.hx_answers;
create trigger audit after insert or update on public.hx_answers for each row execute function public.audit_row();
drop trigger if exists force_actor on public.hx_sessions;
create trigger force_actor before insert on public.hx_sessions for each row execute function public.force_actor('created_by');
drop trigger if exists force_actor on public.hx_answers;
create trigger force_actor before insert or update on public.hx_answers for each row execute function public.force_actor('answered_by');
drop trigger if exists no_delete on public.hx_sessions;
create trigger no_delete before delete on public.hx_sessions for each row execute function public.block_delete();

revoke execute on function public.guard_hx_session() from public, anon, authenticated;
revoke execute on function public.hx_red_flag_alert() from public, anon, authenticated;
