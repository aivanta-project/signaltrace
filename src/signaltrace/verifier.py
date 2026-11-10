"""Cryptographic verification engine for SignalTrace execution traces."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from signaltrace.models import TraceEvent, TraceReceipt
from signaltrace.dag import ProvenanceDAG


@dataclass
class VerificationResult:
    is_valid: bool
    session_id: str
    verified_events_count: int
    computed_root_hash: str
    declared_root_hash: str
    errors: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.is_valid:
            return (
                f"VALID: Session '{self.session_id}' verified successfully.\n"
                f"  Events validated: {self.verified_events_count}\n"
                f"  Merkle Root: {self.computed_root_hash}"
            )
        error_list = "\n  - ".join(self.errors)
        return (
            f"INVALID: Verification failed for session '{self.session_id}'.\n"
            f"  Errors:\n  - {error_list}"
        )


class TraceVerifier:
    """Audits and validates exported execution traces against tampering or missing nodes."""

    @staticmethod
    def verify_trace_dict(trace_data: dict) -> VerificationResult:
        """Verifies a full trace envelope containing receipt and event array."""
        session_id = trace_data.get("session_id", "unknown")
        receipt_data = trace_data.get("receipt", {})
        declared_root = receipt_data.get("root_hash", "")
        raw_events = trace_data.get("events", [])

        errors: List[str] = []

        if not raw_events:
            errors.append("Trace contains zero events.")
            return VerificationResult(
                is_valid=False,
                session_id=session_id,
                verified_events_count=0,
                computed_root_hash="",
                declared_root_hash=declared_root,
                errors=errors,
            )

        # 1. Reconstruct and verify individual content addresses
        events_by_id: Dict[str, TraceEvent] = {}
        for idx, event_dict in enumerate(raw_events):
            event = TraceEvent.from_dict(event_dict)
            computed_id = event.compute_id()

            if event.event_id != computed_id:
                errors.append(
                    f"Content address mismatch at event #{idx}: "
                    f"declared='{event.event_id}', computed='{computed_id}'. "
                    f"Possible payload tampering."
                )

            events_by_id[event.event_id] = event

        # 2. Check causal graph continuity (all parent_ids must exist in trace)
        for event in events_by_id.values():
            for parent_id in event.parent_ids:
                if parent_id not in events_by_id:
                    errors.append(
                        f"Missing causal parent: Event '{event.event_id}' references "
                        f"parent '{parent_id}' which is not present in the trace."
                    )

        # 3. Check for cycles (DAG verification)
        visited: Set[str] = set()
        visiting: Set[str] = set()

        def has_cycle(node_id: str) -> bool:
            visiting.add(node_id)
            node = events_by_id.get(node_id)
            if node:
                for pid in node.parent_ids:
                    if pid in visiting:
                        return True
                    if pid not in visited:
                        if has_cycle(pid):
                            return True
            visiting.remove(node_id)
            visited.add(node_id)
            return False

        for eid in events_by_id:
            if eid not in visited:
                if has_cycle(eid):
                    errors.append(f"Cycle detected in provenance graph at node '{eid}'.")
                    break

        # 4. Reconstruct DAG and verify Merkle root hash
        dag = ProvenanceDAG(session_id=session_id)
        for event in events_by_id.values():
            dag._events[event.event_id] = event

        computed_root = dag.compute_merkle_root()
        if computed_root != declared_root:
            errors.append(
                f"Merkle root mismatch: declared='{declared_root}', "
                f"computed='{computed_root}'."
            )

        is_valid = len(errors) == 0
        return VerificationResult(
            is_valid=is_valid,
            session_id=session_id,
            verified_events_count=len(events_by_id),
            computed_root_hash=computed_root,
            declared_root_hash=declared_root,
            errors=errors,
        )
