"""SignalTrace — Cryptographic Provenance & Trace Verification for Autonomous AI Systems."""

from signaltrace.canonical import canonical_json_bytes, hash_canonical_payload, sha256_digest
from signaltrace.models import Actor, EventType, TraceEvent, TraceReceipt
from signaltrace.dag import ProvenanceDAG
from signaltrace.verifier import TraceVerifier, VerificationResult

__version__ = "0.1.0-alpha.1"

__all__ = [
    "canonical_json_bytes",
    "hash_canonical_payload",
    "sha256_digest",
    "Actor",
    "EventType",
    "TraceEvent",
    "TraceReceipt",
    "ProvenanceDAG",
    "TraceVerifier",
    "VerificationResult",
]
