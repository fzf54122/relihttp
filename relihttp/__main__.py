# -*- coding: utf-8 -*-
# @Time    : 2026/2/3 16:10
# @Author  : fzf
# @FileName: __main__.py
# @Software: PyCharm
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Optional, Tuple

from .client import SyncClient


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid int value: {value}") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be > 0")
    return parsed


def _parse_headers(values: Optional[Iterable[str]]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if not values:
        return headers
    for raw in values:
        if ":" not in raw:
            raise ValueError(f"invalid header format: {raw}. expected 'Key: Value'")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"invalid header key: {raw}")
        headers[key] = value
    return headers


def _parse_json_payload(raw: Optional[str]) -> Optional[object]:
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid json payload: {exc}") from exc


def _build_client(timeout: Optional[float], max_retries: Optional[int]) -> SyncClient:
    kwargs = {}
    if timeout is not None:
        kwargs["timeout"] = float(timeout)
    if max_retries is not None:
        kwargs["max_retries"] = int(max_retries)
    return SyncClient(**kwargs)


def _handle_test(args: argparse.Namespace) -> int:
    try:
        headers = _parse_headers(args.header)
        payload_json = _parse_json_payload(args.json)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    client = _build_client(args.timeout, args.max_retries)
    try:
        response = client.request(
            args.method.upper(),
            args.url,
            headers=headers or None,
            data=args.data,
            json=payload_json,
            timeout=args.timeout,
            max_retries=args.max_retries,
        )
    except Exception as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1

    if response is None:
        print("no response", file=sys.stderr)
        return 1

    print(f"status={response.status_code} elapsed_ms={response.elapsed_ms} url={response.url}")
    print(response.text)
    return 0


def _bench_request(
    url: str,
    timeout: Optional[float],
    max_retries: Optional[int],
) -> Tuple[bool, Optional[int], Optional[int], Optional[str]]:
    client = _build_client(timeout, max_retries)
    try:
        response = client.get(url, timeout=timeout, max_retries=max_retries)
    except Exception as exc:
        return False, None, None, str(exc)
    if response is None:
        return False, None, None, "no response"
    return True, int(response.elapsed_ms), int(response.status_code), None


def _handle_bench(args: argparse.Namespace) -> int:
    start = time.perf_counter()
    durations: List[int] = []
    failures: List[str] = []

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(_bench_request, args.url, args.timeout, args.max_retries)
            for _ in range(args.requests)
        ]
        for future in as_completed(futures):
            ok, elapsed_ms, _status, error = future.result()
            if ok and elapsed_ms is not None:
                durations.append(elapsed_ms)
            else:
                failures.append(error or "unknown error")

    total_time_ms = int((time.perf_counter() - start) * 1000)
    success = len(durations)
    failed = len(failures)

    print(
        f"total={args.requests} success={success} failed={failed} "
        f"concurrency={args.concurrency} total_time_ms={total_time_ms}"
    )
    if durations:
        durations.sort()
        avg_ms = sum(durations) / len(durations)
        print(
            f"min_ms={durations[0]} avg_ms={avg_ms:.2f} "
            f"max_ms={durations[-1]}"
        )
    else:
        print("no successful responses")

    if failures:
        sample = "; ".join(failures[:3])
        print(f"sample_errors={sample}")
    return 0 if failed == 0 else 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="relihttp",
        description="relihttp command line tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    test_parser = subparsers.add_parser("test", help="send a single request")
    test_parser.add_argument(
        "method",
        choices=["get", "post", "put", "delete", "patch", "head", "options"],
        help="HTTP method",
    )
    test_parser.add_argument("url", help="request url")
    test_parser.add_argument("--timeout", type=float, help="request timeout in seconds")
    test_parser.add_argument("--max-retries", type=int, help="max retries (including first try)")
    test_parser.add_argument("--json", help="json payload string")
    test_parser.add_argument("--data", help="raw body")
    test_parser.add_argument(
        "-H",
        "--header",
        action="append",
        help="custom header, repeatable, format: 'Key: Value'",
    )
    test_parser.set_defaults(func=_handle_test)

    bench_parser = subparsers.add_parser("bench", help="basic benchmark")
    bench_parser.add_argument("url", help="request url")
    bench_parser.add_argument(
        "--concurrency",
        type=_positive_int,
        default=10,
        help="number of concurrent workers",
    )
    bench_parser.add_argument(
        "--requests",
        type=_positive_int,
        default=100,
        help="total requests",
    )
    bench_parser.add_argument("--timeout", type=float, help="request timeout in seconds")
    bench_parser.add_argument("--max-retries", type=int, help="max retries (including first try)")
    bench_parser.set_defaults(func=_handle_bench)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
