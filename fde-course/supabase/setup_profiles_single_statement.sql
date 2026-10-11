-- Same as migrations/0004_profiles.sql, wrapped in one DO statement for SQL tools that run
-- a single statement at a time (for example Vercel's Storage → Query, with Read-only off).
-- Safe to run more than once.
do $setup$
begin
  execute $q$
    create table if not exists public.profiles (
      user_id uuid primary key references auth.users (id) on delete cascade,
      handle text unique check (handle is null or handle ~ '^[a-z0-9-]{3,30}$'),
      public_profile boolean not null default false,
      target_role text check (target_role is null or target_role in ('engineer', 'architect', 'fde')),
      interview_date date,
      hours_per_week int check (hours_per_week is null or hours_per_week between 1 and 80),
      background text check (background is null or char_length(background) <= 500),
      diagnostic jsonb check (diagnostic is null or pg_column_size(diagnostic) <= 32000),
      loop_mode jsonb,
      nudges boolean not null default true,
      capstone_url text check (capstone_url is null or (capstone_url ~ '^https://' and char_length(capstone_url) <= 300)),
      last_nudge_at timestamptz,
      updated_at timestamptz not null default now()
    )
  $q$;
  execute 'alter table public.profiles add column if not exists capstone_url text';
  execute 'alter table public.profiles add column if not exists last_nudge_at timestamptz';
  execute 'alter table public.profiles enable row level security';
  execute 'drop policy if exists "Users read own profile" on public.profiles';
  execute 'create policy "Users read own profile" on public.profiles for select to authenticated using ((select auth.uid()) = user_id)';
  execute 'drop policy if exists "Users insert own profile" on public.profiles';
  execute 'create policy "Users insert own profile" on public.profiles for insert to authenticated with check ((select auth.uid()) = user_id)';
  execute 'drop policy if exists "Users update own profile" on public.profiles';
  execute 'create policy "Users update own profile" on public.profiles for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id)';

  execute $q$
    create table if not exists public.outcomes (
      id bigint generated always as identity primary key,
      user_id uuid not null references auth.users (id) on delete cascade,
      track text,
      result text not null check (result in ('offer', 'no-offer', 'pending', 'withdrew')),
      company text check (company is null or char_length(company) <= 120),
      note text check (note is null or char_length(note) <= 2000),
      consent_quote boolean not null default false,
      created_at timestamptz not null default now()
    )
  $q$;
  execute 'create index if not exists outcomes_user_idx on public.outcomes (user_id, created_at)';
  execute 'alter table public.outcomes enable row level security';
  execute 'drop policy if exists "Users read own outcomes" on public.outcomes';
  execute 'create policy "Users read own outcomes" on public.outcomes for select to authenticated using ((select auth.uid()) = user_id)';
  execute 'drop policy if exists "Users insert own outcomes" on public.outcomes';
  execute 'create policy "Users insert own outcomes" on public.outcomes for insert to authenticated with check ((select auth.uid()) = user_id)';
end
$setup$;
