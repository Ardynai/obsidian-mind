# Regulatory Notes

Somatic is not positioned as a medical device, clinical service, diagnostic system, treatment system, cure, emergency triage tool, or replacement for clinicians.

This repository is a research harness skeleton. Future users and contributors are responsible for evaluating applicable laws, institutional policies, ethics review requirements, data protection rules, biosafety requirements, lab certifications, and medical device regulations in their jurisdiction.

## Health Research

Health-related workflows should be framed as research and decision support. Outputs should be safety-gated reports with evidence, assumptions, uncertainty, and human review state.

Personal or patient baseline graphs may contain sensitive data. The default design should keep them local-first, minimize export, and require explicit consent for sharing.

Phase 7C baseline artifacts are fake-backed placeholders only. They load no
real health data, perform no real profile storage, use no database or external
memory, export no personal health data, and make no medical advice, diagnosis,
treatment, clinical interpretation, monitoring, or emergency-triage claim.
Future real baseline storage requires explicit local storage consent,
data-locality review, local-first privacy controls, privacy review, safety
review, human review, retention/export controls, and separate opt-in
configuration.

## Lab Research

Manual, wet-lab, and cloud-lab workflows may involve biosafety, chemical safety, sample handling, procurement, equipment access, and institutional oversight. Future adapters must expose human approval gates before real-world actions.

## Sensor Research

WiFi CSI and other sensor workflows may involve privacy, consent, surveillance, radio regulations, and location-specific rules. Workflows should document data capture scope, retention, and consent assumptions. Phase 7B is fake-backed planning metadata only: no WiFi hardware, monitor mode, packet capture, WiFi probing, raw RF/CSI collection/export, or clinical interpretation is enabled.

## Fabric Distribution

Datasets, documents, model weights, and plugin packs may carry license, export, privacy, and safety restrictions. Pack manifests should make these gates explicit before ingestion or use.
