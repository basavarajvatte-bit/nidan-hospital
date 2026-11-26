-- =========================================================
-- VATTE HOSPITAL OS — PHASE 8 (AI Chat: Sister AI + Reception AI)
-- Server function: supabase/functions/agent-chat (Gemini). Secret needed: GEMINI_API_KEY (optional GEMINI_MODEL).
-- Limits: 40 questions / user / hour, 400 / hospital / day. Chat text is not stored; only usage counts + tool names.
-- (Applied as migration "phase8_ai_chat" — same SQL as below.)
-- =========================================================

create table if not exists public.ai_chat_usage (
  id bigint generated always as identity primary key,
  hospital_id uuid not null references public.hospitals(id),
  user_id uuid not null references auth.users(id) on delete cascade,
  agent_id text not null references public.agents(id),
  tools_used text[] not null default '{}',
  ok boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists ai_chat_usage_user_idx on public.ai_chat_usage(user_id, created_at desc);
alter table public.ai_chat_usage enable row level security;
drop policy if exists p_read on public.ai_chat_usage;
create policy p_read on public.ai_chat_usage for select to authenticated
  using (hospital_id = public.my_hospital() and (user_id = auth.uid() or public.has_role('{doctor,admin}')));
revoke all on public.ai_chat_usage from anon;
revoke insert, update, delete on public.ai_chat_usage from authenticated;
grant select on public.ai_chat_usage to authenticated;

create table if not exists public.ai_chat_agents (
  agent_id text primary key references public.agents(id),
  title text not null,
  roles text[] not null,
  tools text[] not null
);
alter table public.ai_chat_agents enable row level security;
drop policy if exists p_read on public.ai_chat_agents;
create policy p_read on public.ai_chat_agents for select to authenticated using (true);
revoke all on public.ai_chat_agents from anon;
revoke insert, update, delete on public.ai_chat_agents from authenticated;
grant select on public.ai_chat_agents to authenticated;
insert into public.ai_chat_agents values
 ('nurse','Sister AI','{doctor,admin,nurse}',
  '{find_patient,latest_vitals,list_beds,nurse.overdue_vitals,operations.beds,followup.due,followup.schedule,operations.bed_status}'),
 ('reception','Reception AI','{doctor,admin,receptionist}',
  '{find_patient,list_beds,reception.today,appointment.today,operations.beds,followup.due,followup.schedule}')
on conflict (agent_id) do update set title=excluded.title, roles=excluded.roles, tools=excluded.tools;

create or replace function public.ai_chat_begin(p_agent text) returns jsonb
language plpgsql security definer set search_path = public as $$
declare a public.ai_chat_agents; h uuid := public.my_hospital(); r text := public.my_role(); nu int; nh int; nm text;
begin
  select * into a from public.ai_chat_agents where agent_id = p_agent;
  if a.agent_id is null then raise exception 'Ye chat agent nahi hai'; end if;
  if h is null or not (r = any(a.roles)) then raise exception 'Aapka role is AI se baat nahi kar sakta'; end if;
  if (select status from public.agents where id = p_agent) = 'paused' then raise exception 'Doctor ne ye agent band kiya hai'; end if;
  select count(*) into nu from public.ai_chat_usage where user_id = auth.uid() and created_at > now() - interval '1 hour';
  select count(*) into nh from public.ai_chat_usage where hospital_id = h and created_at > now() - interval '1 day';
  if nu >= 40 then raise exception 'Ek ghante mein 40 sawaal ki seema poori. Thodi der baad poochein.'; end if;
  if nh >= 400 then raise exception 'Aaj hospital ki AI seema (400 sawaal) poori. Kal phir chalega.'; end if;
  select full_name into nm from public.profiles where id = auth.uid();
  return jsonb_build_object('role', r, 'name', nm, 'tools', a.tools, 'title', a.title,
                            'actions', (select jsonb_agg(jsonb_build_object('id', x.id, 'title', x.title, 'description', x.description, 'kind', x.kind, 'risk', x.risk))
                                          from public.agent_actions x where x.id = any(a.tools) and r = any(x.requester_roles)));
end $$;
revoke all on function public.ai_chat_begin(text) from public, anon;
grant execute on function public.ai_chat_begin(text) to authenticated;

create or replace function public.ai_chat_end(p_agent text, p_tools text[], p_ok boolean) returns void
language plpgsql security definer set search_path = public as $$
begin
  if public.my_hospital() is null or not exists (select 1 from public.ai_chat_agents where agent_id = p_agent) then return; end if;
  insert into public.ai_chat_usage(hospital_id, user_id, agent_id, tools_used, ok)
  values (public.my_hospital(), auth.uid(), p_agent, coalesce(p_tools[1:10], '{}'), coalesce(p_ok, true));
end $$;
revoke all on function public.ai_chat_end(text, text[], boolean) from public, anon;
grant execute on function public.ai_chat_end(text, text[], boolean) to authenticated;
