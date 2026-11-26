-- =========================================================
-- VATTE HOSPITAL OS — PHASE 8b: saved AI conversations + which AI answered
-- Every chat (question + answer) is kept in the hospital's own Supabase database.
-- Staff see only their own chats; doctor/admin can read all (for checking). Messages can never be edited or deleted.
-- =========================================================
create table if not exists public.ai_conversations (
  id uuid primary key default gen_random_uuid(),
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  agent_id text not null references public.agents(id),
  title text not null default 'Nayi baat',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists ai_conv_user_idx on public.ai_conversations(user_id, updated_at desc);

create table if not exists public.ai_messages (
  id bigint generated always as identity primary key,
  conversation_id uuid not null references public.ai_conversations(id) on delete cascade,
  hospital_id uuid not null default public.my_hospital() references public.hospitals(id),
  role text not null check (role in ('user','assistant')),
  content text not null check (length(content) <= 8000),
  provider text,            -- which AI answered (groq / gemini / mistral)
  ms int,                   -- how long it took
  tools text[] not null default '{}',
  created_at timestamptz not null default now()
);
create index if not exists ai_msg_conv_idx on public.ai_messages(conversation_id, id);

alter table public.ai_conversations enable row level security;
alter table public.ai_messages enable row level security;
drop policy if exists p_read on public.ai_conversations;
drop policy if exists p_insert on public.ai_conversations;
drop policy if exists p_update on public.ai_conversations;
create policy p_read on public.ai_conversations for select to authenticated
  using (hospital_id = public.my_hospital() and (user_id = auth.uid() or public.has_role('{doctor,admin}')));
create policy p_insert on public.ai_conversations for insert to authenticated
  with check (hospital_id = public.my_hospital() and user_id = auth.uid() and public.my_role() <> 'pending');
create policy p_update on public.ai_conversations for update to authenticated
  using (hospital_id = public.my_hospital() and user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists p_read on public.ai_messages;
drop policy if exists p_insert on public.ai_messages;
create policy p_read on public.ai_messages for select to authenticated
  using (hospital_id = public.my_hospital() and exists (select 1 from public.ai_conversations c where c.id = conversation_id
         and (c.user_id = auth.uid() or public.has_role('{doctor,admin}'))));
create policy p_insert on public.ai_messages for insert to authenticated
  with check (hospital_id = public.my_hospital() and exists (select 1 from public.ai_conversations c where c.id = conversation_id and c.user_id = auth.uid()));

revoke all on public.ai_conversations, public.ai_messages from anon;
grant select, insert on public.ai_conversations, public.ai_messages to authenticated;
grant update (title, updated_at) on public.ai_conversations to authenticated;
revoke update, delete on public.ai_messages from authenticated;

drop trigger if exists no_change on public.ai_messages;
create trigger no_change before update or delete on public.ai_messages for each row execute function public.block_change();
drop trigger if exists no_delete on public.ai_conversations;
create trigger no_delete before delete on public.ai_conversations for each row execute function public.block_delete();
