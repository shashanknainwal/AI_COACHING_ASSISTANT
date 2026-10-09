-- Daily cap on Claude-backed actions (tutor answers, rubric grading, role-play turns).
-- use_ai_call() counts one call for the signed-in user and returns today's total;
-- the app refuses the call when the total is over AI_DAILY_LIMIT.

create table if not exists public.ai_usage (
  user_id uuid not null references auth.users (id) on delete cascade,
  day date not null default current_date,
  calls integer not null default 0,
  primary key (user_id, day)
);

alter table public.ai_usage enable row level security;
drop policy if exists "Users read own AI usage" on public.ai_usage;
create policy "Users read own AI usage" on public.ai_usage for select to authenticated using ((select auth.uid()) = user_id);

create or replace function public.use_ai_call() returns integer
language plpgsql security definer set search_path = public as $fn$
declare
  total integer;
begin
  if auth.uid() is null then
    raise exception 'not signed in';
  end if;
  insert into public.ai_usage (user_id, day, calls) values (auth.uid(), current_date, 1)
  on conflict (user_id, day) do update set calls = public.ai_usage.calls + 1
  returning calls into total;
  return total;
end
$fn$;

revoke all on function public.use_ai_call() from public, anon;
grant execute on function public.use_ai_call() to authenticated;
