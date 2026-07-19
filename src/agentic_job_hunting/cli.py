from __future__ import annotations

import argparse
import json

from .pipeline import build_pack


def main() -> None:
    parser = argparse.ArgumentParser(prog="agentic-job-hunting")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--profile", required=True)
    build.add_argument("--jd", required=True)
    build.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "build":
        print(json.dumps(build_pack(args.profile, args.jd, args.output), indent=2))
