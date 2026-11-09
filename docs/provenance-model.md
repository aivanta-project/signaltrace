# SignalTrace Provenance Data Model

## 1. Graph Structure (Merkle-DAG)

SignalTrace represents execution histories as an acyclic directed graph where each node represents an atomic execution event.

```
       [Prompt Event E₀]
          │          │
          ▼          ▼
   [Tool Call E₁]  [Thought Step E₂]
          │          │
          ▼          ▼
       [Tool Output E₃]
              │
              ▼
       [Agent Output E₄]
              │
         (Root Hash)
```

## 2. Event Node Definition

Each trace node contains:
- `event_id`: Content-addressed SHA-256 hash of the canonical serialized node.
- `parent_ids`: List of parent event hashes (causal dependencies).
- `timestamp`: UTC ISO-8601 timestamp with microsecond resolution.
- `actor`: Identity / public key of the entity issuing the action (Agent, User, Tool Provider).
- `event_type`: Categorical discriminator (`prompt`, `thought`, `tool_call`, `tool_result`, `state_mutation`, `final_response`).
- `payload`: Canonical JSON or Protobuf payload containing inputs, outputs, and parameters.
- `attestation`: Cryptographic signature (Ed25519) of `event_id` signed by the actor.

## 3. Merkle Root Attestation

Upon completion of an execution cycle, a trace root record aggregates all leaf nodes into a Merkle root. The executing host or agent signs the root hash, producing a verifiable receipt that can be published or submitted to third-party auditors.
