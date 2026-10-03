-- FDE Course schema. Run once in the Supabase SQL editor (or `supabase db push`).

-- One row per completed Stripe Checkout. Written only by the server (secret key),
-- from the Stripe webhook or the post-checkout success page.
create table if not exists public.purchases (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  stripe_session_id text not null unique,
  stripe_payment_intent text,
  amount_total integer,
  currency text,
  status text not null default 'paid' check (status in ('paid', 'refunded')),
  created_at timestamptz not null default now()
);

create index if not exists purchases_user_id_idx on public.purchases (user_id);
create index if not exists purchases_payment_intent_idx on public.purchases (stripe_payment_intent);

alter table public.purchases enable row level security;

-- Learners can see their own purchases. No insert/update policy: only the secret key writes.
drop policy if exists "Users read own purchases" on public.purchases;
create policy "Users read own purchases" on public.purchases
  for select to authenticated
  using ((select auth.uid()) = user_id);


-- Per-lesson progress and the learner's last saved code.
create table if not exists public.lesson_progress (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  lesson_id text not null check (char_length(lesson_id) <= 200),
  completed_at timestamptz,
  code text check (char_length(code) <= 100000),
  updated_at timestamptz not null default now(),
  primary key (user_id, lesson_id)
);

alter table public.lesson_progress enable row level security;

drop policy if exists "Users read own progress" on public.lesson_progress;
create policy "Users read own progress" on public.lesson_progress
  for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users insert own progress" on public.lesson_progress;
create policy "Users insert own progress" on public.lesson_progress
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users update own progress" on public.lesson_progress;
create policy "Users update own progress" on public.lesson_progress
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
