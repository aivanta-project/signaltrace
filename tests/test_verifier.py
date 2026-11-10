"""Unit tests for the TraceVerifier engine."""

import unittest
from signaltrace.models import Actor, EventType
from signaltrace.dag import ProvenanceDAG
from signaltrace.verifier import TraceVerifier


class TestTraceVerifier(unittest.TestCase):
    def setUp(self):
        self.actor = Actor(actor_id="agent-007", role="agent")
        self.dag = ProvenanceDAG(session_id="session-xyz")
        self.dag.add_event(EventType.PROMPT, self.actor, {"q": "search"}, timestamp=100.0)
        self.dag.add_event(EventType.RESPONSE, self.actor, {"r": "found"}, timestamp=101.0)
        self.trace_dict = self.dag.export_trace()

    def test_verify_valid_trace(self):
        result = TraceVerifier.verify_trace_dict(self.trace_dict)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.verified_events_count, 2)
        self.assertEqual(len(result.errors), 0)

    def test_verify_tampered_payload(self):
        tampered = dict(self.trace_dict)
        tampered["events"][0]["payload"]["q"] = "injected_malicious_query"

        result = TraceVerifier.verify_trace_dict(tampered)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Content address mismatch" in err for err in result.errors))

    def test_verify_missing_parent(self):
        tampered = dict(self.trace_dict)
        tampered["events"][1]["parent_ids"] = ["non_existent_event_hash_12345"]

        # Note: changing parent_ids changes compute_id, so update event_id to match compute_id
        # to isolate the missing parent check
        event_obj = self.dag.events[1]
        event_obj.parent_ids = ["non_existent_event_hash_12345"]
        event_obj.event_id = event_obj.compute_id()
        tampered["events"][1] = event_obj.to_dict()

        result = TraceVerifier.verify_trace_dict(tampered)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing causal parent" in err for err in result.errors))

    def test_verify_tampered_root_hash(self):
        tampered = dict(self.trace_dict)
        tampered["receipt"]["root_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"

        result = TraceVerifier.verify_trace_dict(tampered)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Merkle root mismatch" in err for err in result.errors))


if __name__ == "__main__":
    unittest.main()
