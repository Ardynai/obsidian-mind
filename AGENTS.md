# Obsidian Mind

This vault is built for [Claude Code](https://claude.ai/code) with a full operating manual in `CLAUDE.md`.

**Read `CLAUDE.md` for all vault conventions** — structure, note types, linking rules, frontmatter schemas, indexes, and workflows. Most of the content is agent-agnostic.

## Hooks

The hook scripts in `.claude/scripts/` are agent-agnostic TypeScript and shell, executed natively by Node via `--experimental-strip-types` — no build step, no runtime dependencies, no Claude SDK. Hook configs are provided for three agents:

| Agent | Config | Status |
|-------|--------|--------|
| Claude Code | `.claude/settings.json` | Full support |
| Codex CLI | `.codex/hooks.json` | Shared hook scripts |
| Gemini CLI | `.gemini/settings.json` | Shared hook scripts |

| Script | Purpose | Claude event | Codex event | Gemini event |
|--------|---------|--------------|-------------|--------------|
| `session-start.ts` | Inject vault context at startup | SessionStart | SessionStart | SessionStart |
| `classify-message.ts` | Classify messages, inject routing hints | UserPromptSubmit | UserPromptSubmit | BeforeAgent |
| `validate-write.ts` | Validate frontmatter and wikilinks | PostToolUse | PostToolUse | AfterTool |
| `pre-compact.ts` | Back up transcript before compaction | PreCompact | — | PreCompress |

## Commands

18 commands in `.claude/commands/` — agent-agnostic markdown with YAML frontmatter.

- **Claude Code / Gemini CLI**: invoke as `/om-standup`, `/om-dump`, etc.
- **Codex CLI**: type the command name as a regular prompt without the `/` prefix (e.g. `om-standup`). Codex will find and execute the command file.

## Memory

The vault's memory lives in `brain/` — `Memories.md`, `Patterns.md`, `Key Decisions.md`, `Gotchas.md`. These are plain markdown files that any agent can read and write. When you learn something worth remembering, write it to the relevant `brain/` topic note with a wikilink to context.

The `~/.claude/` auto-loaded memory index is Claude Code-specific — skip that section in `CLAUDE.md`. The vault-side `brain/` notes are the source of truth.

## Subagents

9 subagents in `.claude/agents/` handle isolated tasks (brag spotting, vault auditing, cross-linking, etc.). The prompt content is agent-agnostic markdown. Codex CLI (`.codex/agents/`) and Gemini CLI (`.gemini/agents/`) support the same pattern — copy the files and adapt the YAML frontmatter fields to your agent's schema.

## What's Claude Code-specific

Only the `~/.claude/` auto-memory loader is truly Claude Code-specific. Everything else — hooks, commands, subagent prompts, vault memory — is portable.

## Setup

**Codex CLI**: Reads `AGENTS.md` natively. For direct access to `CLAUDE.md`, add to `~/.codex/config.toml`:
```toml
project_doc_fallback_filenames = ["CLAUDE.md"]
```

**Gemini CLI**: Reads `GEMINI.md` natively. For direct access to `CLAUDE.md`, add to `~/.gemini/settings.json`:
```json
{ "context": { "fileName": ["GEMINI.md", "CLAUDE.md"] } }
```

**Other agents** (Cursor, Windsurf, Copilot): Read `AGENTS.md` for vault conventions. Hook support varies by agent.

For more information, see the [README](README.md).

## Ponytail — minimal-code discipline

Ruleset copied from `DietrichGebert/ponytail` at `c4d1925ae9b76a1b641877328209ad25cfeb5ef2`; agent-specific copies live in `.cursor/rules/ponytail.mdc`, `.windsurf/rules/ponytail.md`, `.clinerules/ponytail.md`, and `.github/copilot-instructions.md`.

This section applies to every AI agent working in this repository, including Codex, Jules, Hermes, Copilot, Cursor, Cline, Windsurf, Gemini, and Claude.

### Ponytail, lazy senior dev mode

You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written.

Before writing any code, stop at the first rung that holds:

1. Does this need to be built at all? (YAGNI)
2. Does it already exist in this codebase? Reuse the helper, util, or pattern that's already here, don't re-write it.
3. Does the standard library already do this? Use it.
4. Does a native platform feature cover it? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can this be one line? Make it one line.
7. Only then: write the minimum code that works.

The ladder runs after you understand the problem, not instead of it: read the task and the code it touches, trace the real flow end to end, then climb.

Bug fix = root cause, not symptom: a report names a symptom. Grep every caller of the function you touch and fix the shared function once — one guard there is a smaller diff than one per caller, and patching only the path the ticket names leaves a sibling caller still broken.

Rules:

- No abstractions that weren't explicitly requested.
- No new dependency if it can be avoided.
- No boilerplate nobody asked for.
- Deletion over addition. Boring over clever. Fewest files possible.
- Shortest working diff wins, but only once you understand the problem. The smallest change in the wrong place isn't lazy, it's a second bug.
- Question complex requests: "Do you actually need X, or does Y cover it?"
- Pick the edge-case-correct option when two stdlib approaches are the same size, lazy means less code, not the flimsier algorithm.
- Mark intentional simplifications with a `ponytail:` comment. If the shortcut has a known ceiling (global lock, O(n²) scan, naive heuristic), the comment names the ceiling and the upgrade path.

Not lazy about: understanding the problem (read it fully and trace the real flow before picking a rung, a small diff you don't understand is just laziness dressed up as efficiency), input validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs (the platform is never the spec ideal, a clock drifts, a sensor reads off), anything explicitly requested. Lazy code without its check is unfinished: non-trivial logic leaves ONE runnable check behind, the smallest thing that fails if the logic breaks (an assert-based demo/self-check or one small test file; no frameworks, no fixtures). Trivial one-liners need no test.
