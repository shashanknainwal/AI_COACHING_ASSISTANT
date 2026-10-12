-- Same as migrations/0003_attempts.sql, wrapped in one DO statement for SQL tools that run
-- a single statement at a time (for example Vercel's Storage → Query, with Read-only off).
-- Run setup_ai_usage_single_statement.sql first. Safe to run more than once.
do $setup$
begin
  execute $q$
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
    )
  $q$;
  execute 'create index if not exists grade_attempts_user_lesson_idx on public.grade_attempts (user_id, lesson_id, created_at)';
  execute 'alter table public.grade_attempts enable row level security';
  execute 'drop policy if exists "Users read own grade attempts" on public.grade_attempts';
  execute 'create policy "Users read own grade attempts" on public.grade_attempts for select to authenticated using ((select auth.uid()) = user_id)';

  execute $q$
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
    )
  $q$;
  execute 'create index if not exists drill_attempts_user_lesson_idx on public.drill_attempts (user_id, lesson_id, started_at)';
  execute 'alter table public.drill_attempts enable row level security';
  execute 'drop policy if exists "Users read own drill attempts" on public.drill_attempts';
  execute 'create policy "Users read own drill attempts" on public.drill_attempts for select to authenticated using ((select auth.uid()) = user_id)';

  execute 'create index if not exists ai_usage_day_idx on public.ai_usage (day)';
  execute $q$
    create or replace function public.ai_usage_global_today(per_user_cap integer) returns integer
    language sql stable security definer set search_path = public as $fn$
      select coalesce(sum(least(calls, greatest(per_user_cap, 0))), 0)::integer
      from public.ai_usage
      where day = current_date
    $fn$
  $q$;
  execute 'revoke all on function public.ai_usage_global_today(integer) from public, anon';
  execute 'grant execute on function public.ai_usage_global_today(integer) to authenticated, service_role';
end
$setup$;
