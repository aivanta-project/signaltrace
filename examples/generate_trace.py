#!/usr/bin/env python3
"""Example script generating valid and tampered SignalTrace traces."""

import json
from pathlib import Path

from signaltrace.models import Actor, EventType
from signaltrace.dag import ProvenanceDAG


def main():
    examples_dir = Path(__file__).parent

    # 1. Build a valid agent session DAG
    user = Actor(actor_id="user-01", role="user")
    agent = Actor(actor_id="agent-01", role="agent")
    tool = Actor(actor_id="weather-api", role="tool_executor")

    dag = ProvenanceDAG(session_id="session-demo-2026-001")

    # Step 1: User prompt
    e1 = dag.add_event(
        event_type=EventType.PROMPT,
        actor=user,
        payload={"query": "What is the weather in Nairobi today?"},
        timestamp=1762758000.0,
    )

    # Step 2: Agent reasoning step
    e2 = dag.add_event(
        event_type=EventType.THOUGHT,
        actor=agent,
        payload={"plan": "User needs weather data for Nairobi. Invoke weather API."},
        parent_ids=[e1.event_id],
        timestamp=1762758001.0,
    )

    # Step 3: Tool invocation
    e3 = dag.add_event(
        event_type=EventType.TOOL_CALL,
        actor=agent,
        payload={"tool": "get_weather", "location": "Nairobi, Kenya"},
        parent_ids=[e2.event_id],
        timestamp=1762758002.0,
    )

    # Step 4: Tool execution result
    e4 = dag.add_event(
        event_type=EventType.TOOL_RESULT,
        actor=tool,
        payload={"temperature_c": 24, "conditions": "Partly Cloudy"},
        parent_ids=[e3.event_id],
        timestamp=1762758003.0,
    )

    # Step 5: Final agent response
    dag.add_event(
        event_type=EventType.RESPONSE,
        actor=agent,
        payload={"text": "It is currently 24°C and partly cloudy in Nairobi."},
        parent_ids=[e4.event_id],
        timestamp=1762758004.0,
    )

    valid_trace = dag.export_trace()
    valid_path = examples_dir / "simple_agent_trace.json"
    with open(valid_path, "w", encoding="utf-8") as f:
        json.dump(valid_trace, f, indent=2)
    print(f"Generated valid trace: {valid_path}")

    # 2. Build a tampered trace (modify event payload without updating hash)
    tampered_trace = json.loads(json.dumps(valid_trace))
    # Malicious injection into event payload
    tampered_trace["events"][3]["payload"]["temperature_c"] = 99  # Tampered temperature

    tampered_path = examples_dir / "tampered_trace.json"
    with open(tampered_path, "w", encoding="utf-8") as f:
        json.dump(tampered_trace, f, indent=2)
    print(f"Generated tampered trace: {tampered_path}")


if __name__ == "__main__":
    main()
