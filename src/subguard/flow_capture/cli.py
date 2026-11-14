"""Command-line entry point for public flow capture."""

from __future__ import annotations

import argparse

from .capturer import FlowCapturer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a public SubGuard flow.")
    parser.add_argument("--url", required=True, help="Public flow start URL.")
    parser.add_argument(
        "--flow-type",
        required=True,
        choices=("sign-up", "cancellation"),
        help="Flow type being captured.",
    )
    parser.add_argument(
        "--next-selector",
        action="append",
        default=[],
        help="Visible selector to click for the next screen; repeat in screen order.",
    )
    parser.add_argument("--output-dir", default="captures/flow", help="Evidence output directory.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    flow = FlowCapturer(args.output_dir).capture(
        args.url,
        args.flow_type,
        args.next_selector,
    )
    print(f"Captured {len(flow.screens)} screen(s) in {flow.output_dir}")

