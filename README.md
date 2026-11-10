# SignalTrace

> **Cryptographic Provenance and Verifiable Execution Traces for Autonomous AI Systems**

[![Project Status: Alpha / R&D](https://img.shields.io/badge/status-Alpha%20%2F%20R%26D-blue.svg)](https://aivanta-project.github.io/aivanta-project/projects/signaltrace/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![Python: >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-brightgreen.svg)](pyproject.toml)
[![Architecture: Hexagonal](https://img.shields.io/badge/architecture-hexagonal-purple.svg)](docs/architecture.md)

---

## Overview

Modern software engineering and autonomous agents execute non-deterministic, multi-step actions across tools, APIs, and databases. Standard logging lacks cryptographic immutability, tamper-evident lineage, and cross-boundary verifiability.

**SignalTrace** solves this challenge by introducing:
1. **Cryptographic Provenance DAGs:** Every prompt, tool execution, model inference, and state mutation is recorded as a cryptographically signed, content-addressed node in a directed acyclic graph (DAG).
2. **Deterministic Trace Verification:** Independent auditors can verify execution trajectories, detect prompt injections or tool manipulation, and confirm output authenticity without blind platform trust.
3. **Language-Agnostic Canonical Standards:** Strict RFC 8785 deterministic serialization and JSON Schema specifications suitable for Python, Rust, Go, and TypeScript runtimes.

SignalTrace is developed under **[Aivanta — Independent Open Technology Initiative](https://github.com/aivanta-project)**.
Review the dedicated project page at: **[https://aivanta-project.github.io/aivanta-project/projects/signaltrace/](https://aivanta-project.github.io/aivanta-project/projects/signaltrace/)**.

---

## Core Technical Objectives & Measurable Outcomes

| Objective | Milestone | Measurable Outcome |
| :--- | :--- | :--- |
| **Tamper-Evident Lineage** | Content-addressed DAG with Merkle root receipts | Modifying any event bit invalidates the Merkle root and pinpoints the corrupted node |
| **Deterministic Canonicalization** | RFC 8785 compliant canonical serialization | Identical hash output across Python, Rust, Go, and JavaScript runtimes |
| **Audit Performance** | Lean, zero-overhead verification algorithm | Verifies >1,000 trace events in <5ms on commodity hardware |
| **Runtime Portability** | Language-agnostic specification & Python SDK | Seamless integration with OpenTelemetry and Model Context Protocol (MCP) |

---

## Installation & Quickstart

SignalTrace requires Python $\ge$ 3.11.

```bash
# Clone the repository
git clone https://github.com/aivanta-project/signaltrace.git
cd signaltrace

# Install in editable mode
pip install -e .
```

---

## Usage

### 1. Python SDK — Recording a Verifiable Agent Session

```python
from signaltrace.models import Actor, EventType
from signaltrace.dag import ProvenanceDAG

# Initialize session graph
dag = ProvenanceDAG(session_id="session-prod-001")
user = Actor(actor_id="user-42", role="user")
agent = Actor(actor_id="agent-01", role="agent")
tool = Actor(actor_id="db-query-service", role="tool_executor")

# 1. Record inbound prompt
e1 = dag.add_event(
    event_type=EventType.PROMPT,
    actor=user,
    payload={"query": "Summarize user transactions for October"}
)

# 2. Record tool invocation (linked causally to prompt)
e2 = dag.add_event(
    event_type=EventType.TOOL_CALL,
    actor=agent,
    payload={"tool": "sql_query", "params": "SELECT * FROM tx WHERE month=10"},
    parent_ids=[e1.event_id]
)

# 3. Record tool output
e3 = dag.add_event(
    event_type=EventType.TOOL_RESULT,
    actor=tool,
    payload={"rows_returned": 142},
    parent_ids=[e2.event_id]
)

# 4. Export canonical trace with cryptographic Merkle receipt
trace_envelope = dag.export_trace()
print(f"Merkle Root: {trace_envelope['receipt']['root_hash']}")
```

### 2. CLI Tool — Verifying a Trace

You can independently audit any exported trace using the `signaltrace` CLI:

```bash
# Verify valid execution trace
signaltrace verify examples/simple_agent_trace.json

# Output:
# VALID: Session 'session-demo-2026-001' verified successfully.
#   Events validated: 5
#   Merkle Root: 1386b42ba530829fe907542e3addba2b35928db2fb52579479655c37dc887447
```

If any event, parent reference, or payload parameter has been tampered with:

```bash
signaltrace verify examples/tampered_trace.json

# Output:
# INVALID: Verification failed for session 'session-demo-2026-001'.
#   Errors:
#   - Content address mismatch at event #3: declared='84f17...', computed='3c0b2...'. Possible payload tampering.
```

---

## Repository Structure

```text
signaltrace/
├── README.md               # Overview, quickstart, and technical objectives
├── LICENSE                 # Apache-2.0 open-source license
├── pyproject.toml          # Package metadata and CLI entry points
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md             # Cryptographic vulnerability disclosure policy
├── docs/                   # Architectural blueprints & formal threat models
│   ├── architecture.md     # Hexagonal architecture (Ports and Adapters)
│   ├── provenance-model.md # Merkle-DAG graph structure
│   └── threat-model.md     # Adversarial actors and mitigation strategies
├── specifications/         # Formal JSON Schemas and RFC drafts
│   ├── event-schema-v0.1.json
│   └── provenance-rfc.md
├── examples/               # Reference traces and trace generator
│   ├── generate_trace.py
│   ├── simple_agent_trace.json
│   └── tampered_trace.json
├── src/                    # Python reference implementation
│   └── signaltrace/
│       ├── __init__.py
│       ├── canonical.py    # Deterministic JSON serialization
│       ├── models.py       # Event, Actor, and Receipt dataclasses
│       ├── dag.py          # Merkle-DAG tree constructor
│       ├── verifier.py     # Independent audit engine
│       └── cli.py          # Command-line verifier
├── tests/                  # Unit test suites (canonical, dag, verifier)
└── .github/
    └── workflows/
        └── ci.yml          # Automated test execution & spec verification
```

---

## Running Tests

```bash
python3 -m unittest discover tests
```

---

## Specifications & Documentation Links

- 🌐 **Project Page:** [https://aivanta-project.github.io/aivanta-project/projects/signaltrace/](https://aivanta-project.github.io/aivanta-project/projects/signaltrace/)
- 📄 [Architecture Specification](docs/architecture.md)
- 📐 [Provenance Data Model](docs/provenance-model.md)
- 🛡️ [Threat Model & Security Boundaries](docs/threat-model.md)
- 📋 [RFC 0001 Specification Draft](specifications/provenance-rfc.md)
- 🔍 [Canonical JSON Schema v0.1](specifications/event-schema-v0.1.json)

---

## License

SignalTrace is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright © 2026 Aivanta Contributors.
