#!/usr/bin/env python3
"""Small helpers around `gws gmail` for raw payload and attachment work."""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


def run_gws(*args: str) -> Any:
    command = ["gws", *args]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise SystemExit("gws was not found on PATH")
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        stdout = exc.stdout.strip()
        detail = stderr or stdout or f"exit code {exc.returncode}"
        raise SystemExit(f"gws command failed: {' '.join(command)}\n{detail}")

    stdout = completed.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"gws returned non-JSON output: {exc}\n{stdout[:1000]}")


def walk_parts(part: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield part
    for child in part.get("parts") or []:
        if isinstance(child, dict):
            yield from walk_parts(child)


def get_message(message_id: str) -> dict[str, Any]:
    return run_gws(
        "gmail",
        "users",
        "messages",
        "get",
        "--params",
        json.dumps({"userId": "me", "id": message_id, "format": "full"}),
    )


def attachment_records(message: dict[str, Any]) -> list[dict[str, Any]]:
    payload = message.get("payload") or {}
    records: list[dict[str, Any]] = []
    for part in walk_parts(payload):
        filename = part.get("filename") or ""
        body = part.get("body") or {}
        attachment_id = body.get("attachmentId")
        inline_data = body.get("data")
        if filename or attachment_id:
            records.append(
                {
                    "filename": filename,
                    "mimeType": part.get("mimeType") or "",
                    "attachmentId": attachment_id or "",
                    "size": body.get("size") or 0,
                    "hasInlineData": bool(inline_data),
                }
            )
    return records


def decode_base64url(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def fetch_attachment_data(message_id: str, attachment_id: str) -> str:
    body = run_gws(
        "gmail",
        "users",
        "messages",
        "attachments",
        "get",
        "--params",
        json.dumps({"userId": "me", "messageId": message_id, "id": attachment_id}),
    )
    data = body.get("data")
    if not data:
        raise SystemExit("Attachment response did not include a data field")
    return data


def find_part_by_filename(message: dict[str, Any], filename: str) -> dict[str, Any]:
    matches = [
        part
        for part in walk_parts(message.get("payload") or {})
        if (part.get("filename") or "") == filename
    ]
    if not matches:
        available = attachment_records(message)
        raise SystemExit(
            "No attachment matched filename "
            f"{filename!r}. Available: {json.dumps(available, ensure_ascii=False)}"
        )
    if len(matches) > 1:
        raise SystemExit(f"Multiple attachments matched filename {filename!r}; use --attachment-id")
    return matches[0]


def cmd_attachments(args: argparse.Namespace) -> None:
    message = get_message(args.message_id)
    records = attachment_records(message)
    print(json.dumps(records, ensure_ascii=False, indent=2))


def cmd_download_attachment(args: argparse.Namespace) -> None:
    message = get_message(args.message_id) if args.filename or not args.attachment_id else None
    attachment_id = args.attachment_id
    inline_data = None

    if args.filename:
        assert message is not None
        part = find_part_by_filename(message, args.filename)
        body = part.get("body") or {}
        attachment_id = body.get("attachmentId")
        inline_data = body.get("data")

    if attachment_id:
        data = fetch_attachment_data(args.message_id, attachment_id)
    elif inline_data:
        data = inline_data
    else:
        raise SystemExit("Provide --attachment-id or --filename for a part with downloadable data")

    output = Path(args.output).expanduser()
    if output.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(decode_base64url(data))
    print(json.dumps({"output": str(output), "bytes": output.stat().st_size}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    attachments = subparsers.add_parser("attachments", help="List attachments for a Gmail message")
    attachments.add_argument("--message-id", required=True)
    attachments.set_defaults(func=cmd_attachments)

    download = subparsers.add_parser(
        "download-attachment",
        help="Download and decode a Gmail attachment by filename or attachment ID",
    )
    download.add_argument("--message-id", required=True)
    group = download.add_mutually_exclusive_group(required=True)
    group.add_argument("--filename")
    group.add_argument("--attachment-id")
    download.add_argument("--output", required=True)
    download.add_argument("--force", action="store_true")
    download.set_defaults(func=cmd_download_attachment)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
