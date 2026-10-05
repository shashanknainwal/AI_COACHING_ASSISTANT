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
      theme="playbook-night"
      beforeMount={(monaco) => {
        monaco.editor.defineTheme("playbook-night", {
          base: "vs-dark",
          inherit: true,
          rules: [
            { token: "comment", foreground: "7d8590", fontStyle: "italic" },
            { token: "keyword", foreground: "ff7b72" },
            { token: "string", foreground: "a5d6ff" },
            { token: "number", foreground: "79c0ff" },
          ],
          colors: {
            "editor.background": "#0d1117",
            "editor.lineHighlightBackground": "#161b22",
            "editorLineNumber.foreground": "#3b434e",
            "editorLineNumber.activeForeground": "#8b949e",
            "editorCursor.foreground": "#6ee7b7",
            "editor.selectionBackground": "#264f78",
          },
        });
      }}
      value={value}
      onChange={(v) => onChange(v ?? "")}
      onMount={(editor, monaco) => {
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, onRun);
        if (onSubmit) editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, onSubmit);
      }}
      options={{
        fontSize: 14,
        fontFamily: '"JetBrains Mono", ui-monospace, Menlo, monospace',
        fontLigatures: true,
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
