# SignalTrace Architecture

## 1. High-Level Concept

SignalTrace provides an immutable, cryptographically verifiable trace layer for autonomous systems and AI agent execution.

```
       [ Inbound Runtimes ]
  (LLM Agents, CLI, MCP Hosts, SDKs)
                  │
                  ▼
   ┌──────────────────────────────┐
   │    SignalTrace Ingest Port   │
   └──────────────┬───────────────┘
                  │
                  ▼
   ┌──────────────────────────────┐
   │    Provenance Domain Core    │
   │  - Canonical Event Hashing   │
   │  - Merkle-DAG Constructor    │
   │  - Signature Verification    │
   └──────────────┬───────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Storage Port │    │ Verifier Port│
└───────┬──────┘    └───────┬──────┘
        ▼                   ▼
  (IPFS/S3/Disk)     (Audit CLI/API)
```

## 2. Hexagonal Architecture (Ports and Adapters)

In conformance with sovereign engineering standards:
- **Core Domain:** Implements purely functional cryptographic algorithms: Merkle-tree state aggregation, event canonicalization, and DAG relationship integrity. Has zero external framework or transport dependencies.
- **Inbound Ports:**
  - `TraceIngestionPort`: Ingests raw telemetry events (tool calls, planning iterations, prompt executions).
  - `VerificationRequestPort`: Validates an input trace against root hashes and public signing keys.
- **Outbound Ports:**
  - `TraceStoragePort`: Persists content-addressed blocks and signatures.
  - `CryptographicProviderPort`: Abstracts key storage and signature validation routines.

## 3. Guarantees

1. **Tamper Evidence:** Modifying any historical event or parameter invalidates all downstream hash chains.
2. **Causal Ordering:** Parent-child causal dependencies are preserved via directed acyclic graphs.
3. **Reproducible Hashing:** Canonical serialization ensures deterministic hashes across runtimes and CPU architectures.
