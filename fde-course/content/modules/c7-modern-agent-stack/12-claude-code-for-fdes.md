---
title: "Claude Code for FDEs: Your Tool, and Your Customer's Rollout"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Set up Claude Code in a customer repository with CLAUDE.md, permissions, hooks, MCP servers, subagents and Skills.
> - Use hooks as approval gates and choose a permission mode.
> - Plan a rollout to a customer's engineering org with managed settings.

Claude Code shows up twice in FDE work. It is your own tool, the fastest way to get productive in an unfamiliar customer codebase. And it is a product customers want rolled out to their engineering org, where your job is governance as much as enthusiasm. The facts below come from Claude Code's settings reference; check the current documentation before quoting exact paths to a customer.

## In a customer repo: the pieces

- **CLAUDE.md** is project memory, loaded at the start of a session: how to build, test and run the project, conventions, and what not to touch. Write it the first day on site.
- **Settings files** set permissions, hooks, environment variables and MCP approvals. They layer: user (`~/.claude/settings.json`), project (`.claude/settings.json`, committed and shared), local (`.claude/settings.local.json`, personal, gitignored), command-line flags, then managed policy on top. Later layers override earlier ones; managed policy wins.
- **MCP servers** are declared in a project `.mcp.json` (or added from the CLI) and need approval before they connect.
- **Subagents** are separate agents Claude Code can hand a self-contained task to, each with its own context, tools and model.
- **Skills** live under `.claude/skills/<name>/` and load on demand, exactly like the Skills lesson.

## Permissions and modes

Permission rules come in three lists: `allow`, `ask` and `deny`, using patterns such as `Bash(npm run test)` (exact), `Bash(git *)` (prefix wildcard) or `Edit(src/**)` (file paths). Deny takes precedence. The default mode is set with `permissions.defaultMode`; the documented modes are `default`, `acceptEdits`, `plan`, `auto`, `dontAsk` and `bypassPermissions`. In a customer repo, start in `default` or `plan`, allow the read-only and test commands you trust, and deny anything that touches production or secrets.

## Hooks as approval gates

Hooks run your code at points in Claude Code's lifecycle: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `Stop`, `PreCompact` and more. A `PreToolUse` hook receives the pending tool call as JSON and can block it: exiting with code 2, or returning a `permissionDecision` of `deny`. That makes it the place to enforce a customer rule deterministically ("never run migrations against the prod database URL") instead of hoping the model remembers it. `PostToolUse` hooks are good for formatters and test runs after edits.

## Rolling it out to a customer's engineering org

The rollout conversation is governance. Managed settings are the lever: a `managed-settings.json` placed by IT (for example `/etc/claude-code/` on Linux, `C:\Program Files\ClaudeCode\` on Windows), through MDM, or delivered from the admin console. Managed settings sit above every user and project file. Useful controls:

| Concern | Managed setting |
|---|---|
| Which MCP servers are allowed | `allowedMcpServers`, `deniedMcpServers` (deny wins); `managedMcpServers` to provide servers to everyone |
| Only org-approved permission rules | `allowManagedPermissionRulesOnly` |
| Only org-approved hooks | `allowManagedHooksOnly` |
| No bypass mode | `permissions.disableBypassPermissionsMode` |
| Which models and providers | `availableModels`, `allowedProviders` |
| Org-wide instructions | `claudeMd` (managed memory) |
| Version floor | `requiredMinimumVersion` |

A sensible 90-day shape: a pilot team with a committed project `.claude/settings.json` and CLAUDE.md, managed settings that pin providers and deny unapproved MCP servers, a shared Skills folder for the org's own patterns, then wider rollout once the pilot's metrics (time to first PR, review findings) hold. Measure before and after; don't promise a productivity number you haven't measured.

> **Key takeaways**
> - CLAUDE.md, layered settings, MCP config, subagents and Skills are the pieces you set up in a customer repo.
> - Permission rules are allow, ask and deny (deny wins); pick a conservative mode in a customer codebase.
> - A `PreToolUse` hook can block a tool call deterministically: use it for hard customer rules.
> - Managed settings sit above everything and are how an org governs MCP servers, permissions, hooks, models and providers.
> - Pilot, measure, then widen the rollout; check current docs before quoting exact paths.
