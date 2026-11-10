"""Unit tests for canonical serialization and hashing."""

import unittest
from signaltrace.canonical import canonical_json_bytes, hash_canonical_payload, sha256_digest


class TestCanonical(unittest.TestCase):
    def test_key_sorting_determinism(self):
        d1 = {"b": 2, "a": 1, "c": {"y": 2, "x": 1}}
        d2 = {"c": {"x": 1, "y": 2}, "a": 1, "b": 2}

        bytes1 = canonical_json_bytes(d1)
        bytes2 = canonical_json_bytes(d2)

        self.assertEqual(bytes1, bytes2)
        self.assertEqual(hash_canonical_payload(d1), hash_canonical_payload(d2))

    def test_whitespace_omission(self):
        data = {"hello": "world", "list": [1, 2, 3]}
        raw_bytes = canonical_json_bytes(data)
        # Should not contain spaces after separators
        self.assertNotIn(b": ", raw_bytes)
        self.assertNotIn(b", ", raw_bytes)

    def test_sha256_digest(self):
        digest = sha256_digest(b"aivanta")
        self.assertEqual(len(digest), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in digest))


if __name__ == "__main__":
    unittest.main()
