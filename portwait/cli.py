"""Command-line interface for portwait."""

from __future__ import annotations

import argparse
import sys

from . import wait_for_port


def _host(value: str) -> str:
    if not value.strip():
        raise argparse.ArgumentTypeError("host must be a non-empty string")
    return value


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer from 1 to 65535") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be an integer from 1 to 65535")
    return port


def _nonnegative_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be a finite non-negative number") from exc
    if number < 0 or number == float("inf") or number != number:
        raise argparse.ArgumentTypeError("value must be a finite non-negative number")
    return number


def _positive_float(value: str) -> float:
    number = _nonnegative_float(value)
    if number == 0:
        raise argparse.ArgumentTypeError("value must be a finite positive number")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portwait",
        description="Wait until a TCP host and port accept connections.",
    )
    parser.add_argument("host", type=_host, help="hostname or IP address to check")
    parser.add_argument("port", type=_port, help="TCP port (1-65535)")
    parser.add_argument("--timeout", type=_nonnegative_float, default=30.0, metavar="SECONDS",
                        help="maximum wait time; defaults to 30 seconds")
    parser.add_argument("--interval", type=_positive_float, default=0.5, metavar="SECONDS",
                        help="delay between failed attempts; defaults to 0.5 seconds")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if wait_for_port(args.host, args.port, timeout=args.timeout, interval=args.interval):
        print(f"ready: {args.host}:{args.port}")
        return 0
    print(f"timed out waiting for {args.host}:{args.port} after {args.timeout:g}s", file=sys.stderr)
    return 1
