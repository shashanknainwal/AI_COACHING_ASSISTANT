"use client";

import Editor, { loader } from "@monaco-editor/react";

// Served from public/monaco (copied by scripts/prepare-runtime.mjs).
loader.config({ paths: { vs: "/monaco/vs" } });

export default function CodeEditor({
  value,
  onChange,
  onRun,
  onSubmit,
}: {
  value: string;
  onChange: (v: string) => void;
  onRun: () => void;
  onSubmit?: () => void;
}) {
  return (
    <Editor
      height="100%"
      language="python"
      theme="vs-dark"
      value={value}
      onChange={(v) => onChange(v ?? "")}
      onMount={(editor, monaco) => {
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, onRun);
        if (onSubmit) editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, onSubmit);
      }}
      options={{
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        tabSize: 4,
        insertSpaces: true,
        wordWrap: "on",
        automaticLayout: true,
        padding: { top: 12 },
      }}
      loading={<div className="p-4 text-sm text-gray-400">Loading editor…</div>}
    />
  );
}
