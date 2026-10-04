"use client";

// Progress is cached in localStorage so it works for anonymous learners and offline.
// When the learner is signed in, enableServerSync() merges it with their account
// and every later change is also saved to the server.

import { useSyncExternalStore } from "react";

const KEY = "fde-progress-v1";
const CODE_SAVE_DELAY_MS = 1500;

export interface Progress {
  completed: Record<string, string>; // lessonId -> ISO date completed
  code: Record<string, string>; // lessonId -> last saved code
}

const empty: Progress = { completed: {}, code: {} };
let cache: Progress | null = null;
const listeners = new Set<() => void>();

let serverSync = false;
let syncPromise: Promise<void> | null = null;
const pendingCode = new Map<string, ReturnType<typeof setTimeout>>();

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

interface Upload {
  lessonId: string;
  completedAt?: string;
  code?: string;
}

async function upload(items: Upload[]) {
  for (let i = 0; i < items.length; i += 200) {
    try {
      await fetch("/api/progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: items.slice(i, i + 200) }),
        keepalive: true,
      });
    } catch {
      // Offline: the local copy is kept and re-uploaded on the next sync.
    }
  }
}

/**
 * Call once the learner is known to be signed in. Pulls their saved progress,
 * merges it with this browser's, and pushes anything the server is missing.
 */
export function enableServerSync(): Promise<void> {
  syncPromise ??= (async () => {
    let remote: { lesson_id: string; completed_at: string | null; code: string | null }[] = [];
    try {
      const res = await fetch("/api/progress", { cache: "no-store" });
      if (!res.ok) {
        syncPromise = null;
        return;
      }
      remote = (await res.json()).items ?? [];
    } catch {
      syncPromise = null;
      return;
    }

    const local = load();
    const merged: Progress = { completed: { ...local.completed }, code: { ...local.code } };
    const remoteDone = new Set<string>();
    const remoteCode = new Set<string>();
    for (const r of remote) {
      if (r.completed_at) {
        remoteDone.add(r.lesson_id);
        const mine = merged.completed[r.lesson_id];
        if (!mine || r.completed_at < mine) merged.completed[r.lesson_id] = r.completed_at;
      }
      if (r.code != null) {
        remoteCode.add(r.lesson_id);
        // Code typed in this browser wins; otherwise restore the account's copy.
        if (merged.code[r.lesson_id] === undefined) merged.code[r.lesson_id] = r.code;
      }
    }
    save(merged);
    serverSync = true;

    const missing: Upload[] = [];
    for (const [id, at] of Object.entries(local.completed)) if (!remoteDone.has(id)) missing.push({ lessonId: id, completedAt: at });
    for (const [id, code] of Object.entries(local.code)) if (!remoteCode.has(id)) missing.push({ lessonId: id, code });
    if (missing.length) await upload(missing);
  })();
  return syncPromise;
}

export function markComplete(id: string) {
  const p = load();
  if (p.completed[id]) return;
  const at = new Date().toISOString();
  save({ ...p, completed: { ...p.completed, [id]: at } });
  if (serverSync) void upload([{ lessonId: id, completedAt: at }]);
}

export function saveCode(id: string, code: string) {
  const p = load();
  save({ ...p, code: { ...p.code, [id]: code } });
  if (!serverSync) return;
  clearTimeout(pendingCode.get(id));
  pendingCode.set(
    id,
    setTimeout(() => {
      pendingCode.delete(id);
      void upload([{ lessonId: id, code: load().code[id] ?? "" }]);
    }, CODE_SAVE_DELAY_MS),
  );
}

export function getSavedCode(id: string): string | undefined {
  return load().code[id];
}

/** Clears progress stored in this browser only. */
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
