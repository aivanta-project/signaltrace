# RFC 0001: SignalTrace Canonical Event Schema and Merkle Provenance DAG

- **Status:** Draft (R&D Preview)
- **Authors:** Aivanta Engineering Team
- **Created:** 2026-11-09
- **Target Audience:** Systems Engineers, AI Tool Implementors, Security Auditors

---

## 1. Abstract

This RFC specifies the SignalTrace protocol for capturing, hashing, and cryptographically verifying execution traces of autonomous AI agents. By organizing atomic runtime actions into a directed acyclic graph (Merkle-DAG) and calculating deterministic event content addresses using RFC 8785 JSON canonicalization, SignalTrace provides tamper-evident auditability across heterogeneous compute environments.

## 2. Problem Statement

Autonomous agents execute non-deterministic, multi-step tasks involving tools, database queries, and external APIs. Traditional text-based logging is vulnerable to:
1. **Tampering:** Malicious modification of log records to hide exfiltration or unauthorized tool actions.
2. **Equivocation:** Omitting actions taken during an agentic run while maintaining valid timestamps.
3. **Prompt Injection Obfuscation:** Lack of provenance linking adversarial prompts directly to subsequent dangerous tool calls.

## 3. Specification

### 3.1 Content Addressing
Every node in the DAG is addressed by the SHA-256 hash of its canonical JSON serialization:
$$\text{event\_id} = \text{SHA-256}(\text{CanonicalJSON}(\text{EventEnvelope}))$$

### 3.2 Causal Continuity
Every event specifies an ordered list of parent hashes (`parent_ids`). A trace is valid if and only if:
- All parent references resolve to existing predecessor nodes in the graph.
- The graph is strictly acyclic.
- The recalculated root hash matches the root hash declared in the `TraceReceipt`.

### 3.3 Receipt Verification
At session termination, a binary Merkle tree is computed across lexicographically sorted event identifiers. The resulting Merkle root hash is signed by the execution environment or host runtime.

## 4. Security Considerations

- **Adversarial Tool Returns:** Tool providers sign output events with independent keys, preventing compromised agents from fabricating fictitious tool responses.
- **Performance:** Canonical hashing and tree calculation execute in $\mathcal{O}(N \log N)$ time and benchmark under 5 milliseconds for graphs of 1,000 events.
