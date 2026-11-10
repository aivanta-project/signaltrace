"""Unit tests for ProvenanceDAG construction and Merkle tree generation."""

import unittest
from signaltrace.models import Actor, EventType
from signaltrace.dag import ProvenanceDAG


class TestProvenanceDAG(unittest.TestCase):
    def setUp(self):
        self.actor = Actor(actor_id="test-agent", role="agent")
        self.dag = ProvenanceDAG(session_id="test-sess")

    def test_add_event_linking(self):
        e1 = self.dag.add_event(
            event_type=EventType.PROMPT,
            actor=self.actor,
            payload={"prompt": "hello"},
            timestamp=1000.0,
        )
        self.assertEqual(e1.parent_ids, [])
        self.assertEqual(self.dag.leaf_ids, [e1.event_id])

        e2 = self.dag.add_event(
            event_type=EventType.RESPONSE,
            actor=self.actor,
            payload={"text": "world"},
            timestamp=1001.0,
        )
        self.assertEqual(e2.parent_ids, [e1.event_id])
        self.assertEqual(self.dag.leaf_ids, [e2.event_id])

    def test_merkle_root_determinism(self):
        dag1 = ProvenanceDAG(session_id="sess-1")
        dag1.add_event(EventType.PROMPT, self.actor, {"q": 1}, timestamp=10.0)
        dag1.add_event(EventType.RESPONSE, self.actor, {"a": 2}, timestamp=11.0)

        dag2 = ProvenanceDAG(session_id="sess-2")
        dag2.add_event(EventType.PROMPT, self.actor, {"q": 1}, timestamp=10.0)
        dag2.add_event(EventType.RESPONSE, self.actor, {"a": 2}, timestamp=11.0)

        self.assertEqual(dag1.compute_merkle_root(), dag2.compute_merkle_root())

    def test_mutation_changes_merkle_root(self):
        dag1 = ProvenanceDAG(session_id="sess-1")
        dag1.add_event(EventType.PROMPT, self.actor, {"q": 1}, timestamp=10.0)

        dag2 = ProvenanceDAG(session_id="sess-1")
        dag2.add_event(EventType.PROMPT, self.actor, {"q": 2}, timestamp=10.0)

        self.assertNotEqual(dag1.compute_merkle_root(), dag2.compute_merkle_root())


if __name__ == "__main__":
    unittest.main()
