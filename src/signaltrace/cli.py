"""Command-line interface for the SignalTrace audit and verification tool."""

import argparse
import json
import sys

from signaltrace.verifier import TraceVerifier


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="signaltrace",
        description="Audits and verifies cryptographic execution traces for AI systems.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: verify
    verify_parser = subparsers.add_parser("verify", help="Verify a trace JSON file")
    verify_parser.add_argument("file", help="Path to the SignalTrace JSON file")
    verify_parser.add_argument(
        "--json", action="store_true", help="Output verification result in JSON format"
    )

    args = parser.parse_args()

    if args.command == "verify":
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                trace_data = json.load(f)
        except Exception as e:
            print(f"Error opening or reading '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)

        result = TraceVerifier.verify_trace_dict(trace_data)

        if args.json:
            out = {
                "is_valid": result.is_valid,
                "session_id": result.session_id,
                "events_count": result.verified_events_count,
                "merkle_root": result.computed_root_hash,
                "errors": result.errors,
            }
            print(json.dumps(out, indent=2))
        else:
            print(result.summary())

        sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
