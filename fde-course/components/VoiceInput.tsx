"use client";

// Voice mode for role-plays, built only on browser APIs (no external services):
//   input   SpeechRecognition / webkitSpeechRecognition dictates into the answer box, which stays editable
//   output  speechSynthesis reads the persona's replies aloud
// The toggle is off by default and remembered in localStorage. Browsers without speech
// recognition don't see the toggle; they get a one-line note instead.

import { useCallback, useEffect, useRef, useState } from "react";
import { clock, useLocalFlag } from "./practice-shared";

// Minimal typings: SpeechRecognition isn't in every TypeScript DOM lib.
interface RecognitionAlternative {
  transcript: string;
}
interface RecognitionResult {
  isFinal: boolean;
  0: RecognitionAlternative;
}
interface RecognitionEvent {
  resultIndex: number;
  results: { length: number; [i: number]: RecognitionResult };
}
interface Recognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: RecognitionEvent) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}
type RecognitionCtor = new () => Recognition;

function recognitionCtor(): RecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export interface SpeechSupport {
  recognition: boolean;
  synthesis: boolean;
}

/** null until mounted (so server and first client render match). */
export function useSpeechSupport(): SpeechSupport | null {
  const [s, setS] = useState<SpeechSupport | null>(null);
  useEffect(() => {
    setS({ recognition: recognitionCtor() !== null, synthesis: typeof window !== "undefined" && "speechSynthesis" in window });
  }, []);
  return s;
}

export const useVoiceMode = () => useLocalFlag("fde-voice-mode-v1");

export function speak(text: string, onEnd?: () => void) {
  try {
    const synth = window.speechSynthesis;
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.02;
    if (onEnd) {
      u.onend = onEnd;
      u.onerror = onEnd;
    }
    synth.speak(u);
  } catch {
    onEnd?.();
  }
}

export function stopSpeaking() {
  try {
    window.speechSynthesis.cancel();
  } catch {
    // No synthesis.
  }
}

const ERRORS: Record<string, string> = {
  "not-allowed": "Microphone access was blocked. Allow it in your browser's site settings, or type instead.",
  "service-not-allowed": "This browser doesn't allow speech recognition here. Type instead.",
  "audio-capture": "No microphone was found.",
  network: "Speech recognition needs a network connection in this browser. Type instead.",
};

/** Dictation: final phrases go to onFinal (appended to the editable draft); interim text is shown live. */
export function useDictation(onFinal: (text: string) => void) {
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [error, setError] = useState<string | null>(null);
  const rec = useRef<Recognition | null>(null);
  const finalRef = useRef(onFinal);
  useEffect(() => {
    finalRef.current = onFinal;
  }, [onFinal]);

  const stop = useCallback(() => {
    rec.current?.stop();
    setListening(false);
    setInterim("");
  }, []);

  const start = useCallback(() => {
    const Ctor = recognitionCtor();
    if (!Ctor) return;
    stopSpeaking();
    setError(null);
    try {
      const r = new Ctor();
      r.lang = navigator.language || "en-US";
      r.continuous = true;
      r.interimResults = true;
      r.onresult = (e) => {
        let live = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const res = e.results[i];
          if (res.isFinal) finalRef.current(res[0].transcript.trim());
          else live += res[0].transcript;
        }
        setInterim(live);
      };
      r.onerror = (e) => {
        if (e.error !== "no-speech" && e.error !== "aborted") setError(ERRORS[e.error] ?? `Speech recognition stopped (${e.error}).`);
      };
      r.onend = () => {
        setListening(false);
        setInterim("");
      };
      rec.current = r;
      r.start();
      setListening(true);
    } catch {
      setError("Speech recognition couldn't start. Type instead.");
      setListening(false);
    }
  }, []);

  useEffect(() => () => rec.current?.abort(), []);

  return { listening, interim, error, start, stop };
}

/** The voice toggle, or the unsupported note. */
export function VoiceToggle({ support, on, onChange }: { support: SpeechSupport | null; on: boolean; onChange: (v: boolean) => void }) {
  if (!support) return null;
  if (!support.recognition) return null;
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      onClick={() => onChange(!on)}
      className={`flex items-center gap-1.5 rounded-md px-2 py-1 text-xs ${on ? "bg-sky-400/15 text-sky-200" : "text-console-muted hover:bg-console-2 hover:text-gray-200"}`}
      title="Answer out loud; the persona's replies are read aloud"
    >
      <span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full ${on ? "bg-sky-300" : "bg-gray-500"}`} />
      Voice {on ? "on" : "off"}
    </button>
  );
}

export function VoiceUnsupportedNote({ support }: { support: SpeechSupport | null }) {
  if (!support || support.recognition) return null;
  return <p className="px-4 pt-2 text-xs text-console-muted">Voice mode needs a browser with speech recognition (Chrome, Edge or Safari). You can type your answers here.</p>;
}

const OVER_MS = 2 * 60_000;

/** Per-answer timer: counts from when the question landed until the answer is sent; flags answers over 2 minutes. */
export function AnswerTimer({ since, now }: { since: number | null; now: number }) {
  if (since === null) return null;
  const ms = Math.max(0, now - since);
  const over = ms > OVER_MS;
  return (
    <span
      className={`font-mono text-[11px] tabular-nums ${over ? "rounded bg-amber-400/15 px-1.5 py-0.5 text-amber-200" : "text-console-muted"}`}
      title="Time on this answer. Spoken answers in real rounds usually run 60 to 90 seconds."
    >
      answer {clock(ms)}
      {over ? " · over 2 min, tighten it" : ""}
    </span>
  );
}
