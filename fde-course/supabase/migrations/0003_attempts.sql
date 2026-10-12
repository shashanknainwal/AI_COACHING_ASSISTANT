-- Graded attempts, drill attempts and the site-wide daily AI breaker.
-- Safe to run more than once. Requires 0001_init.sql and 0002_ai_usage.sql.
-- Same content as supabase/setup_attempts_single_statement.sql (one statement, for Vercel → Storage → Query).

-- Every graded attempt (written, roleplay); never overwritten. Inserted only by the server (secret key).
create table if not exists public.grade_attempts (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  lesson_id text not null check (char_length(lesson_id) <= 200),
  track text,
  percent int not null,
  passed boolean not null,
  result jsonb not null,
  transcript jsonb,
  loop_mode boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists grade_attempts_user_lesson_idx on public.grade_attempts (user_id, lesson_id, created_at);

alter table public.grade_attempts enable row level security;
drop policy if exists "Users read own grade attempts" on public.grade_attempts;
create policy "Users read own grade attempts" on public.grade_attempts
  for select to authenticated
  using ((select auth.uid()) = user_id);

-- Every drill attempt. The browser posts it; the server checks the user and lesson and inserts it.
create table if not exists public.drill_attempts (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  lesson_id text not null check (char_length(lesson_id) <= 200),
  started_at timestamptz not null,
  finished_at timestamptz,
  time_limit_min int not null,
  extended boolean not null default false,
  level_ms int[] not null default '{}',
  cleared int not null default 0,
  cleared_in_time int not null default 0,
  loop_mode boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists drill_attempts_user_lesson_idx on public.drill_attempts (user_id, lesson_id, started_at);

alter table public.drill_attempts enable row level security;
drop policy if exists "Users read own drill attempts" on public.drill_attempts;
create policy "Users read own drill attempts" on public.drill_attempts
  for select to authenticated
  using ((select auth.uid()) = user_id);

-- Site-wide daily AI breaker (AI_GLOBAL_DAILY_LIMIT). Sums today's per-user counts from
-- ai_usage, capping each user at per_user_cap (the per-user daily limit) so nobody can push
-- the site total up by calling use_ai_call() directly. Read-only.
create index if not exists ai_usage_day_idx on public.ai_usage (day);

create or replace function public.ai_usage_global_today(per_user_cap integer) returns integer
language sql stable security definer set search_path = public as $fn$
  select coalesce(sum(least(calls, greatest(per_user_cap, 0))), 0)::integer
  from public.ai_usage
  where day = current_date
$fn$;

revoke all on function public.ai_usage_global_today(integer) from public, anon;
grant execute on function public.ai_usage_global_today(integer) to authenticated, service_role;
