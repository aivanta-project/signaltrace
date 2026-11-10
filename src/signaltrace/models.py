"""Data models representing canonical SignalTrace events and Merkle DAG nodes."""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time

from signaltrace.canonical import hash_canonical_payload


class EventType(str, Enum):
    PROMPT = "prompt"
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STATE_MUTATION = "state_mutation"
    RESPONSE = "response"


@dataclass
class Actor:
    """Represents an active entity within the execution environment."""
    actor_id: str
    role: str  # e.g., "user", "agent", "tool_executor", "host_runtime"
    public_key: Optional[str] = None


@dataclass
class TraceEvent:
    """An atomic content-addressed node in a SignalTrace execution DAG."""
    event_type: str
    actor: Actor
    payload: Dict[str, Any]
    parent_ids: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default="")
    attestation: Optional[str] = None  # Signature of event_id by actor

    def compute_id(self) -> str:
        """Computes the deterministic content address of this event."""
        envelope = {
            "event_type": self.event_type,
            "actor": asdict(self.actor),
            "payload": self.payload,
            "parent_ids": sorted(self.parent_ids),
            "timestamp": round(self.timestamp, 6),
        }
        return hash_canonical_payload(envelope)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes to a dictionary suitable for JSON transport."""
        return {
            "event_id": self.event_id or self.compute_id(),
            "event_type": self.event_type,
            "actor": asdict(self.actor),
            "payload": self.payload,
            "parent_ids": self.parent_ids,
            "timestamp": self.timestamp,
            "attestation": self.attestation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TraceEvent":
        """Reconstitutes a TraceEvent from a dictionary."""
        actor_data = data.get("actor", {})
        actor = Actor(
            actor_id=actor_data.get("actor_id", "unknown"),
            role=actor_data.get("role", "unknown"),
            public_key=actor_data.get("public_key"),
        )
        event = cls(
            event_type=data.get("event_type", ""),
            actor=actor,
            payload=data.get("payload", {}),
            parent_ids=data.get("parent_ids", []),
            timestamp=data.get("timestamp", 0.0),
            event_id=data.get("event_id", ""),
            attestation=data.get("attestation"),
        )
        if not event.event_id:
            event.event_id = event.compute_id()
        return event


@dataclass
class TraceReceipt:
    """Aggregated cryptographic receipt for an execution session."""
    session_id: str
    root_hash: str
    event_count: int
    leaf_ids: List[str]
    root_signature: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "root_hash": self.root_hash,
            "event_count": self.event_count,
            "leaf_ids": self.leaf_ids,
            "root_signature": self.root_signature,
            "created_at": self.created_at,
        }
