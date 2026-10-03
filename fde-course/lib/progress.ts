"use client";

// Progress lives in the browser for now. When Supabase is added, swap these
// functions for API calls and keep the same signatures.

import { useSyncExternalStore } from "react";

const KEY = "fde-progress-v1";

export interface Progress {
  completed: Record<string, string>; // lessonId -> ISO date completed
  code: Record<string, string>; // lessonId -> last saved code
}

const empty: Progress = { completed: {}, code: {} };
let cache: Progress | null = null;
const listeners = new Set<() => void>();

export function lessonId(moduleSlug: string, lessonSlug: string) {
  return `${moduleSlug}/${lessonSlug}`;
}

function load(): Progress {
  if (cache) return cache;
  try {
    const raw = window.localStorage.getItem(KEY);
    cache = raw ? { ...empty, ...JSON.parse(raw) } : { ...empty };
  } catch {
    cache = { ...empty };
  }
  return cache!;
}

function save(next: Progress) {
  cache = next;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    // Storage blocked (private mode); progress lasts for this tab only.
  }
  listeners.forEach((l) => l());
}

export function markComplete(id: string) {
  const p = load();
  if (p.completed[id]) return;
  save({ ...p, completed: { ...p.completed, [id]: new Date().toISOString() } });
}

export function saveCode(id: string, code: string) {
  const p = load();
  save({ ...p, code: { ...p.code, [id]: code } });
}

export function getSavedCode(id: string): string | undefined {
  return load().code[id];
}

export function resetProgress() {
  save({ completed: {}, code: {} });
}

function subscribe(l: () => void) {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function useProgress(): Progress {
  return useSyncExternalStore(subscribe, load, () => empty);
}
