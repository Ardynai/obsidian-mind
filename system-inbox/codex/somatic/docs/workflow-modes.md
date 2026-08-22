# Workflow Modes

Somatic workflows are declared as manifests. Each mode should define inputs, adapters, evidence expectations, safety gates, and report outputs before implementation.

## Literature Only

Reviews papers, notes evidence, extracts claims, and produces research summaries. It does not plan real-world experiments or make clinical recommendations.

## Hypothesis Tournament

Runs Co-Scientist-style proposal, critique, ranking, and refinement loops. Outputs candidate hypotheses with evidence, assumptions, uncertainty, and next-step suggestions for human review.

## Robin Loop

Models a Crow/Falcon/Finch-style loop:

- Crow gathers literature and prior evidence.
- Falcon proposes research plans or experiment designs.
- Finch analyzes results and updates hypotheses.

## In-Silico Screening

Coordinates biomodel and cheminformatics adapters such as Boltz, ESM, Chai, AlphaFold-optional, and RDKit. Outputs are research artifacts and must include model assumptions and provenance.

## Wet Lab Manual

Prepares human-readable lab plans, checklists, and observation forms. It must not trigger equipment or order materials automatically.

## Sandbox Lab

Runs simulated experiments for education, planning, and dry runs where users do not have lab access.

## WiFi CSI Observation

Coordinates WiFi channel state information and other sensor-observation planning adapters for research metadata. It must follow consent, privacy, and local law requirements.

Phase 7B treats WiFi CSI examples as fake-backed planning metadata only. It
does not run live CSI capture, access WiFi hardware, use ESP32 or RTL8812AU
devices, use routers or drivers, enter monitor mode, perform packet capture,
probe WiFi devices, collect raw RF/CSI data, call networks, or make clinical
claims. RuView is conditional reference-only and must not be copied, imported,
executed, depended on, or treated as a Somatic implementation source.

## N-of-1

Uses fake-backed sandbox sensor features and a local baseline placeholder for
single-subject planning. It is research-only and sandbox-only: no hardware,
camera, microphone, audio, wearable, BLE, WiFi, CSI, thermal, environmental,
or network access; no real monitoring; and no diagnosis, treatment, or
emergency triage.

## Hybrid Clinical

Combines literature, patient baseline graphs, sensor observations, and safety-gated decision-support reports. It requires human review and must not claim diagnosis, treatment, cure, emergency triage, or clinician replacement.

## Fabric Pack Ingest

Verifies and catalogs datasets, documents, model weights, workflows, and plugin packs before use. Code packs must remain quarantined until explicitly enabled.
