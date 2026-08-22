# User and AI Install Guidance Workflow

This workflow records the requirement that users, and AI assistants helping users, must know what to install, why to install it, what it costs, and which workflow it unlocks.

## Purpose

Ardynai repos and tools should be installable through guided workflows instead of tribal knowledge.

Locus Evolution Lab should help produce:

- repo/tool purpose summaries
- install prerequisites
- cost/compute expectations
- local vs cloud options
- recommended model/API/provider choices
- safety boundaries
- verification checks
- uninstall/rollback notes
- workflow templates for best results

## Product stance

Some workflows will cost users more than normal use. That is acceptable if the result quality is materially better and the user understands the cost/benefit tradeoff.

The system should support:

- cheap/default mode
- best-results mode
- local-only mode
- cloud-enhanced mode
- expert/manual mode
- AI-assisted install mode

## Required install guidance fields

Each tool/repo guidance page should include:

| Field | Meaning |
| --- | --- |
| What it does | Plain-language purpose. |
| Best for | The workflows where it helps. |
| Not for | When users should not install it. |
| Cost profile | Free/local/API/cloud/GPU/storage costs. |
| Compute profile | CPU/GPU/RAM/disk/model size expectations. |
| Install mode | Manual, guided, OpenClaw-assisted, or unsupported. |
| Required accounts/API keys | Provider requirements without exposing secrets. |
| Verification | How to confirm it works. |
| Rollback | How to undo or disable it. |
| Content Fabric role | Whether it publishes, consumes, verifies, or installs packs. |

## First workflow families

| Family | Repos/tools | Install guidance goal |
| --- | --- | --- |
| Kortex Audio | `kortex-audio`, audio tools, sample/beat packs | Help users build audio/studio/marketplace workflows and use best-result templates. |
| Content Creation | ComfyUI, Remotion, Blender, OpenUSD, video/audio/image tools | Help users pick local/cloud pipelines and understand quality/cost tradeoffs. |
| Somatic | `somatic` and related embodied-agent tools | Explain installation once architecture is inspected. |
| Financial repo | future Ardynai financial repo plus data tools | Separate research/paper-trading/live-trading modes with strict gates. |
| Multiverse | `multiverse`, citizen adapters, Content Fabric | Let users install/connect harnesses and content packs safely. |

## Locus role

Locus should generate and evolve install guidance as part of each repo workflow. Install docs are not afterthoughts; they are part of the product surface.

## Initial prompt template

```text
Create install guidance for this repo/tool. Do not install anything. Read README/docs first, then produce: purpose, best workflows, not-for cases, cost profile, compute profile, install mode, required accounts/API keys, verification, rollback, and Content Fabric role. Keep guidance user-facing and AI-assistant-friendly.
```
