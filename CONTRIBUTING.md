# Contributing to SignalTrace

Thank you for your interest in contributing to SignalTrace! As an independent open-technology research initiative under Aivanta, we welcome thoughtful contributions from developers, researchers, and system designers.

## Research & Development Phase

SignalTrace is currently in the **Research and Development** phase. At this stage, contributions are most valuable in:
- Refining the provenance data model and event schemas.
- Enhancing formal threat models and identifying edge cases in agent trace verification.
- Drafting RFC specifications.

## Code of Conduct

We are committed to providing a welcoming, inclusive, and professional environment for all contributors. Respect, constructive feedback, and intellectual rigor are required.

## Development Principles

When contributing code, architectures, or specifications:
1. **Hexagonal Architecture:** Decouple cryptographic verification logic from concrete runtime frameworks, network transports, or storage backends.
2. **Deterministic Outputs:** All hashing, serialization (e.g., canonical JSON or Protobuf), and verification routines must produce identical outputs across architectures.
3. **Conventional Commits:** Use Conventional Commits (`feat:`, `fix:`, `docs:`, `spec:`, `test:`, `chore:`).
4. **License Compliance:** All contributions must be eligible for release under the [Apache-2.0 License](LICENSE).

## Submitting Pull Requests

1. Fork the repository and create a feature branch (`git checkout -b feat/provenance-spec`).
2. Ensure documentation and tests are updated.
3. Open a Pull Request clearly explaining the rationale, design trade-offs, and verification approach.
