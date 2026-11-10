"""Canonical serialization and content-addressed hashing for SignalTrace."""

import hashlib
import json
from typing import Any


def canonical_json_bytes(data: Any) -> bytes:
    """Serializes data into deterministic canonical UTF-8 bytes (RFC 8785 subset).

    - Keys are sorted lexicographically.
    - No insignificant whitespace (separators=(',', ':')).
    - UTF-8 encoded.
    - Floats are rendered without trailing zeroes where possible.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_digest(data: bytes) -> str:
    """Computes a SHA-256 hexadecimal digest of input bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_canonical_payload(data: Any) -> str:
    """Serializes payload canonically and computes its SHA-256 content-address."""
    return sha256_digest(canonical_json_bytes(data))
