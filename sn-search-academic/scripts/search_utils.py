#!/usr/bin/env python3
"""Shared utilities for sn-search-academic scripts.

Provides: build_parser, get_client, make_item, make_result, print_json
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def build_parser(description: str) -> argparse.ArgumentParser:
    """Build a standard ArgumentParser with query and limit args.

    Adds:
      - query (positional) -- search query string
      - --limit / -n        -- max results (default 10)
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--limit", "-n", type=int, default=10, help="返回结果数量（默认 10）")
    return parser


def get_client(timeout: int = 30, headers: dict[str, str] | None = None) -> Any:
    """Create an httpx Client with sensible defaults.

    Returns a context-manager that yields an httpx.Client.
    Usage::

        with get_client(timeout=30) as client:
            resp = client.get(url, params=params)
    """
    import httpx

    client_headers = {
        "User-Agent": "HermesAgent/1.0 (sn-search-academic; mailto:hermes@nousresearch.com)",
    }
    if headers:
        client_headers.update(headers)

    return httpx.Client(
        timeout=httpx.Timeout(timeout),
        headers=client_headers,
        follow_redirects=True,
    )


def make_item(**kwargs: Any) -> dict[str, Any]:
    """Create a standardized result item dict, dropping None values.

    Only fields with non-None values are included in the output dict.
    """
    return {k: v for k, v in kwargs.items() if v is not None}


def make_result(
    success: bool,
    query: str,
    provider: str,
    items: list[dict[str, Any]],
    error: str | None = None,
) -> dict[str, Any]:
    """Create the envelope JSON result dict."""
    result: dict[str, Any] = {
        "success": success,
        "query": query,
        "provider": provider,
        "items": items,
    }
    if error is not None:
        result["error"] = error
    return result


def print_json(data: Any) -> None:
    """Print data as pretty JSON to stdout."""
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2, default=str)
    print()