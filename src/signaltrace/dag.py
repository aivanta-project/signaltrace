"""Merkle-DAG construction and provenance graph management."""

from typing import Dict, List, Optional
import hashlib

from signaltrace.models import Actor, TraceEvent, TraceReceipt
from signaltrace.canonical import sha256_digest


class ProvenanceDAG:
    """Maintains an append-only directed acyclic graph (DAG) of trace events."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._events: Dict[str, TraceEvent] = {}
        self._leaf_ids: set[str] = set()

    def add_event(
        self,
        event_type: str,
        actor: Actor,
        payload: dict,
        parent_ids: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
    ) -> TraceEvent:
        """Adds a new event linked to explicit parents or current active leaves."""
        if parent_ids is None:
            # Default causal parent is current leaves (or empty if root)
            parent_ids = sorted(list(self._leaf_ids))

        event = TraceEvent(
            event_type=event_type,
            actor=actor,
            payload=payload,
            parent_ids=parent_ids,
            timestamp=timestamp if timestamp is not None else TraceEvent().timestamp,
        )
        event.event_id = event.compute_id()

        self._events[event.event_id] = event

        # Update leaves: remove nodes that are now parents of this node
        for pid in parent_ids:
            self._leaf_ids.discard(pid)
        self._leaf_ids.add(event.event_id)

        return event

    def get_event(self, event_id: str) -> Optional[TraceEvent]:
        return self._events.get(event_id)

    @property
    def events(self) -> List[TraceEvent]:
        return list(self._events.values())

    @property
    def leaf_ids(self) -> List[str]:
        return sorted(list(self._leaf_ids))

    def compute_merkle_root(self) -> str:
        """Calculates a deterministic Merkle root combining all node hashes in the DAG.

        Uses binary hashing over the sorted event identifiers to guarantee
        that adding, mutating, or reordering any node alters the root.
        """
        if not self._events:
            return sha256_digest(b"empty_session")

        sorted_ids = sorted(self._events.keys())
        current_layer = [sha256_digest(eid.encode("utf-8")) for eid in sorted_ids]

        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                if i + 1 < len(current_layer):
                    combined = (current_layer[i] + current_layer[i + 1]).encode("utf-8")
                    next_layer.append(sha256_digest(combined))
                else:
                    # Odd node carried over
                    next_layer.append(current_layer[i])
            current_layer = next_layer

        return current_layer[0]

    def generate_receipt(self, root_signature: Optional[str] = None) -> TraceReceipt:
        """Constructs an auditable TraceReceipt for the current graph state."""
        return TraceReceipt(
            session_id=self.session_id,
            root_hash=self.compute_merkle_root(),
            event_count=len(self._events),
            leaf_ids=self.leaf_ids,
            root_signature=root_signature,
        )

    def export_trace(self) -> dict:
        """Exports the full graph and receipt into a canonical exchange format."""
        receipt = self.generate_receipt()
        return {
            "version": "0.1.0-alpha",
            "session_id": self.session_id,
            "receipt": receipt.to_dict(),
            "events": [e.to_dict() for e in self.events],
        }
