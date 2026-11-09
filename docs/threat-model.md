# SignalTrace Threat Model

## 1. Scope & Security Objectives

The objective of SignalTrace is to provide reliable, tamper-evident audit trails for agentic operations. The threat model evaluates threats against:
- **Trace Integrity:** Preventing post-hoc alteration or deletion of intermediate agent decisions or tool executions.
- **Trace Authenticity:** Ensuring that recorded actions were genuinely initiated by the declared agent or tool actor.
- **Causal Lineage:** Preventing injection of fabricated intermediary events that alter causal perception.

## 2. Threat Actors & Scenarios

### T1: Compromised Agent Runtime
- **Threat:** An agent instance hijacked by malicious prompt injection attempts to forge benign execution logs.
- **Mitigation:** Tool responses and host boundaries sign their respective events independently. An agent cannot forge a tool provider's cryptographic attestation.

### T2: Selective Event Omission (Equivocation)
- **Threat:** An adversary records only favorable events while omitting dangerous actions before generating a root receipt.
- **Mitigation:** Inbound tool ports require referencing pre-signed parent tokens; missing links break DAG continuity and fail verification.

### T3: Replay Attacks
- **Threat:** Replaying previously signed valid traces from another session to prove compliance in a new context.
- **Mitigation:** Every trace root is bound to an ephemeral session nonce and context timestamp anchored to the host runtime.

## 3. Assumptions & Out-of-Scope Items

- **Hardware Compromise:** If the host execution environment itself is completely compromised, hardware-level TPM / enclave attestations (e.g., Intel SGX / AMD SEV) would be required; this is considered an advanced future extension.
- **Confidentiality:** SignalTrace focuses primarily on integrity and provenance. Selective disclosure and zero-knowledge redaction of sensitive data are addressed via commitment schemes.
