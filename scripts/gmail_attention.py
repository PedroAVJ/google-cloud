#!/usr/bin/env python3
"""Read a stateless, source-time-bounded Gmail attention window."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Mapping, Optional, Sequence


DEFAULT_WINDOW = dt.timedelta(hours=24)
DEFAULT_PAGE_SIZE = 500
EXCLUDED_LABELS = {"SENT", "DRAFT", "CHAT", "SPAM", "TRASH"}
_DURATION = re.compile(r"^(?P<amount>\d+(?:\.\d+)?)(?P<unit>[mhdw])$")


class GmailAttentionError(RuntimeError):
    def __init__(self, code: str, message: str, details: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(details or {})


def emit(value: Mapping[str, Any], stream: Any = sys.stdout) -> None:
    json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
    stream.write("\n")


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _absolute_time(value: str, option: str) -> dt.datetime:
    raw = value.strip()
    try:
        parsed = dt.datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
    except ValueError as exc:
        raise GmailAttentionError("invalid_window", f"{option} must be an ISO-8601 timestamp with a timezone.") from exc
    if parsed.tzinfo is None:
        raise GmailAttentionError("invalid_window", f"{option} must include a timezone.")
    return parsed.astimezone(dt.timezone.utc)


def _duration(value: str) -> Optional[dt.timedelta]:
    match = _DURATION.fullmatch(value.strip().casefold())
    if not match:
        return None
    amount = float(match.group("amount"))
    seconds = amount * {"m": 60, "h": 3600, "d": 86400, "w": 604800}[match.group("unit")]
    if seconds <= 0:
        return None
    return dt.timedelta(seconds=seconds)


def resolve_window(
    since: Optional[str],
    until: Optional[str],
    *,
    now: Optional[dt.datetime] = None,
) -> tuple[dt.datetime, dt.datetime, bool]:
    end = _absolute_time(until, "--until") if until else (now or dt.datetime.now(dt.timezone.utc))
    end = end.astimezone(dt.timezone.utc)
    defaulted = since is None
    if since is None:
        start = end - DEFAULT_WINDOW
    else:
        relative = _duration(since)
        start = end - relative if relative else _absolute_time(since, "--since")
    if start >= end:
        raise GmailAttentionError("invalid_window", "--since must be earlier than --until.")
    return start, end, defaulted


def gws_binary(raw: Optional[str]) -> str:
    return raw or os.environ.get("GMAIL_ATTENTION_GWS_BIN") or "gws"


def parse_json_output(raw: str, command_name: str) -> Mapping[str, Any]:
    decoder = json.JSONDecoder()
    for index, character in enumerate(raw):
        if character not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(raw[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise GmailAttentionError(
        "invalid_gws_json",
        "The Google Workspace CLI returned an unexpected response.",
        {"command": command_name},
    )


def run_gws(binary: str, *args: str) -> Mapping[str, Any]:
    executable = shutil.which(binary) if "/" not in binary else binary
    if not executable:
        raise GmailAttentionError("gws_missing", "The Google Workspace CLI was not found.", {"binary": binary})
    try:
        process = subprocess.run(
            [executable, *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise GmailAttentionError("gws_timeout", "The Gmail read timed out.") from exc
    if process.returncode != 0:
        raise GmailAttentionError(
            "gws_failed",
            "The Google Workspace CLI could not read Gmail.",
            {"exit_code": process.returncode, "stderr": process.stderr.strip()[-2000:]},
        )
    return parse_json_output(process.stdout, " ".join(args[:4]))


def get_account(binary: str) -> str:
    profile = run_gws(
        binary,
        "gmail",
        "users",
        "getProfile",
        "--params",
        json.dumps({"userId": "me"}, separators=(",", ":")),
    )
    email = profile.get("emailAddress")
    if not isinstance(email, str) or not email:
        raise GmailAttentionError("invalid_gmail_profile", "Gmail profile omitted emailAddress.")
    return email


def _message_details(binary: str, message_id: str) -> Mapping[str, Any]:
    return run_gws(
        binary,
        "gmail",
        "users",
        "messages",
        "get",
        "--params",
        json.dumps(
            {"userId": "me", "id": message_id, "format": "metadata", "metadataHeaders": []},
            separators=(",", ":"),
        ),
    )


def _normalize_message(raw: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    message_id = raw.get("id")
    if not isinstance(message_id, str) or not message_id:
        return None
    labels = sorted({str(value).upper() for value in raw.get("labelIds") or []})
    if EXCLUDED_LABELS.intersection(labels):
        return None
    raw_time = raw.get("internalDate")
    try:
        received = dt.datetime.fromtimestamp(int(str(raw_time)) / 1000, tz=dt.timezone.utc)
    except (TypeError, ValueError, OSError) as exc:
        raise GmailAttentionError(
            "invalid_gmail_message",
            f"Gmail message {message_id} omitted a valid internalDate.",
        ) from exc
    thread_id = raw.get("threadId")
    return {
        "id": message_id,
        "thread_id": thread_id if isinstance(thread_id, str) and thread_id else message_id,
        "label_ids": labels,
        "received_at": _iso(received),
        "_received": received,
    }


def fetch_messages(
    binary: str,
    start: dt.datetime,
    end: dt.datetime,
    page_size: int,
) -> list[dict[str, Any]]:
    if not 1 <= page_size <= 500:
        raise GmailAttentionError("invalid_page_size", "--page-size must be between 1 and 500.")
    # Gmail's search syntax is second-granular, so query a one-second halo and
    # enforce the exact half-open interval against internalDate below.
    query = (
        f"after:{math.floor(start.timestamp()) - 1} "
        f"before:{math.ceil(end.timestamp()) + 1} "
        "-in:sent -in:drafts -in:spam -in:trash"
    )
    page_token: Optional[str] = None
    seen_tokens: set[str] = set()
    refs: dict[str, None] = {}
    while True:
        params: dict[str, Any] = {
            "userId": "me",
            "maxResults": page_size,
            "includeSpamTrash": False,
            "q": query,
        }
        if page_token:
            params["pageToken"] = page_token
        page = run_gws(
            binary,
            "gmail",
            "users",
            "messages",
            "list",
            "--params",
            json.dumps(params, separators=(",", ":")),
        )
        for raw in page.get("messages") or []:
            if isinstance(raw, dict) and isinstance(raw.get("id"), str) and raw["id"]:
                refs[raw["id"]] = None
        next_token = page.get("nextPageToken")
        if not isinstance(next_token, str) or not next_token:
            break
        if next_token in seen_tokens:
            raise GmailAttentionError("invalid_gmail_pagination", "Gmail repeated a messages page token.")
        seen_tokens.add(next_token)
        page_token = next_token

    messages: list[dict[str, Any]] = []
    for message_id in refs:
        message = _normalize_message(_message_details(binary, message_id))
        if message and start <= message["_received"] < end:
            message.pop("_received")
            messages.append(message)
    return sorted(messages, key=lambda item: (item["received_at"], item["id"]))


def scan(args: argparse.Namespace) -> Mapping[str, Any]:
    start, end, defaulted = resolve_window(args.since, args.until)
    executable = gws_binary(args.gws_bin)
    messages = fetch_messages(executable, start, end, args.page_size)
    return {
        "source": "gmail",
        "account": get_account(executable),
        "window": {
            "field": "internalDate",
            "since": _iso(start),
            "until": _iso(end),
            "bounds": "[since, until)",
            "defaulted_to_previous_24_hours": defaulted,
        },
        "count": len(messages),
        "messages": messages,
        "stateless": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read a bounded inbound Gmail attention window.")
    parser.add_argument("--gws-bin")
    commands = parser.add_subparsers(dest="command", required=True)
    scan_parser = commands.add_parser("scan", help="read messages received in a source-time window")
    scan_parser.add_argument(
        "--since",
        help="ISO-8601 start time, or a duration such as 24h relative to --until/current time",
    )
    scan_parser.add_argument("--until", help="ISO-8601 exclusive end time; defaults to now")
    scan_parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        emit(scan(args))
        return 0
    except GmailAttentionError as exc:
        emit(
            {"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
            stream=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
