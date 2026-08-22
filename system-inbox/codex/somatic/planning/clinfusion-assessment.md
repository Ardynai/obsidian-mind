# ClinFusion — reuse assessment for Somatic (2026-08-17)

**Repo:** [`alibaba-damo-academy/ClinFusion`](https://github.com/alibaba-damo-academy/ClinFusion) · Apache-2.0 · Python · 176★ · default branch `master`.

## What it is
A **vision-centric multimodal LLM system for radiology** — "holistic medical understanding" over 2D medical images (X-ray/CT/MRI/ultrasound, JPG/PNG) **and** 3D volumes (NIfTI `.nii.gz`). Built on **Qwen3-VL 8B/32B** + **DINOv2** + **OpenCLIP ConvNeXt** vision encoders, with a custom multi-encoder fusion ("Cascade Spatial-Aware Locality Fusion"), a medical ViT (MAE/RoPE/positional encodings), and an evaluation stack (`eval/` — evaluators, aggregators, an inference engine, a clinical tagging taxonomy in `eval/tagging/constants.py`, MedIF-Bench-style instruction-following eval, radiologist-validated). Tech stack: **PyTorch, Transformers ≥4.57, Flash-Attention 2.8 (GPU-only), Python 3.11**; multi-GB eval datasets committed in-repo. It does medical VQA, report generation, and instruction-following, with agentic tool use for retrieval-augmented clinical workflows.

## Verdict: do NOT pull any ClinFusion code into Somatic
Three hard incompatibilities, each disqualifying on its own:
1. **Stack collision.** Every module imports torch/transformers/flash-attn and assumes a GPU. Somatic's load-bearing invariant is **stdlib-only, `pyproject` `dependencies == []`**. Importing anything from ClinFusion detonates that invariant and the whole local-first/no-heavy-runtime promise.
2. **Wrong modality.** ClinFusion reasons over **radiology images/volumes**. Somatic reasons over a single user's **numeric/text health data** (labs, wearable series) with **no invented population normals**. There is no data-model overlap — not even the JSONL schemas (theirs carry image/volume paths + radiology tags).
3. **Wrong safety posture.** ClinFusion generates diagnostic radiology assessments; Somatic's entire design **refuses diagnosis** and frames everything informational. Its outputs are the opposite of what `frame_advisory` permits.

## Two conceptual takeaways (reference only — no code, no dependency)
1. **Clinician-aligned evaluation methodology.** ClinFusion's headline idea is that evaluation should match how a clinician actually assesses — factual, fine-grained, region-grounded, validated against board-certified reviewers (MedIF-Bench, ROI-grounded report scoring). That philosophy is a good north star for Somatic's **clinician-facing evaluation of the `share` output** (the clinician simulation scored today's `share` 3.0/5; see F14). Borrow the *principle* — grade the clinician doc the way a real clinician would (dates, units, actual values, provenance, drill-down) — not the code.
2. **Far-future optional imaging Evidence-Source.** The Apache-2.0 license would *permit* wrapping ClinFusion as an optional `VisionReasoner` / imaging `EvidenceSource` **if** Somatic ever grows the heavy, opt-in, sandbox-only imaging lane the master plan already reserves behind the Evidence-Source boundary (`video3d`/imaging). That is aspirational, GPU-gated, an optional-dep lane (like the existing `video`/`csi` extras), **never in the stdlib core**, and **not on the current roadmap**. Note only.

## Bottom line
Nothing to adopt now. Keep the assessment as a documented "considered and declined, here's why" so future sessions (and the autonomous agent) don't try to wire a GPU radiology MLLM into a stdlib personal-health engine. The one durable value is the clinician-aligned-evaluation principle, already captured as F14 in the backlog.
