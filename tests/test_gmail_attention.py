from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI = PLUGIN_ROOT / "bin" / "gmail-attention"


def message(message_id: str, received_at: str, *labels: str) -> dict:
    instant = __import__("datetime").datetime.fromisoformat(received_at.replace("Z", "+00:00"))
    return {
        "id": message_id,
        "threadId": f"thread-{message_id}",
        "labelIds": list(labels or ("INBOX",)),
        "internalDate": str(int(instant.timestamp() * 1000)),
    }


class GmailAttentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture.json"
        self.calls = self.root / "calls.jsonl"
        self.fake_gws = self.root / "gws"
        self.fake_gws.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import json, os, sys
                from pathlib import Path
                fixture = json.loads(Path(os.environ["GMAIL_FIXTURE"]).read_text())
                args = sys.argv[1:]
                with Path(os.environ["GMAIL_CALLS"]).open("a") as handle:
                    handle.write(json.dumps(args) + "\\n")
                if args[:3] == ["gmail", "users", "getProfile"]:
                    print(json.dumps({"emailAddress": "owner@example.com"}))
                elif args[:4] == ["gmail", "users", "messages", "list"]:
                    print(json.dumps({"messages": [{"id": item["id"]} for item in fixture]}))
                elif args[:4] == ["gmail", "users", "messages", "get"]:
                    params = json.loads(args[args.index("--params") + 1])
                    print(json.dumps(next(item for item in fixture if item["id"] == params["id"])))
                else:
                    print("unexpected", file=sys.stderr)
                    raise SystemExit(64)
                """
            ),
            encoding="utf-8",
        )
        self.fake_gws.chmod(0o755)
        self.write_fixture([])

    def tearDown(self):
        self.temp.cleanup()

    def write_fixture(self, values):
        self.fixture.write_text(json.dumps(values), encoding="utf-8")

    def run_cli(self, *args, expected=0):
        completed = subprocess.run(
            [str(CLI), "--gws-bin", str(self.fake_gws), "scan", *args],
            env={**os.environ, "GMAIL_FIXTURE": str(self.fixture), "GMAIL_CALLS": str(self.calls)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(expected, completed.returncode, completed.stderr)
        return json.loads(completed.stdout if expected == 0 else completed.stderr)

    def test_omitted_start_defaults_to_previous_24_hours(self):
        self.write_fixture([
            message("inside", "2026-08-11T12:00:00Z"),
            message("too-old", "2026-08-11T11:59:59Z"),
            message("at-end", "2026-08-12T12:00:00Z"),
        ])
        result = self.run_cli("--until", "2026-08-12T12:00:00Z")
        self.assertEqual(["inside"], [item["id"] for item in result["messages"]])
        self.assertEqual("2026-08-11T12:00:00Z", result["window"]["since"])
        self.assertTrue(result["window"]["defaulted_to_previous_24_hours"])

    def test_relative_and_absolute_windows_are_supported(self):
        self.write_fixture([
            message("recent", "2026-08-12T10:30:00Z"),
            message("older", "2026-08-12T09:30:00Z"),
        ])
        relative = self.run_cli("--since", "2h", "--until", "2026-08-12T12:00:00Z")
        absolute = self.run_cli(
            "--since", "2026-08-12T10:00:00Z", "--until", "2026-08-12T12:00:00Z"
        )
        self.assertEqual(relative["messages"], absolute["messages"])
        self.assertFalse(relative["window"]["defaulted_to_previous_24_hours"])

    def test_same_window_is_repeatable_without_checkpoint_state(self):
        self.write_fixture([message("same", "2026-08-12T11:00:00Z")])
        arguments = ("--since", "24h", "--until", "2026-08-12T12:00:00Z")
        first = self.run_cli(*arguments)
        second = self.run_cli(*arguments)
        self.assertEqual(first, second)
        self.assertTrue(first["stateless"])
        self.assertEqual([], list(self.root.glob("*state*")))

    def test_non_inbound_labels_are_excluded(self):
        self.write_fixture([
            message("sent", "2026-08-12T11:00:00Z", "SENT"),
            message("spam", "2026-08-12T11:00:00Z", "SPAM"),
            message("inbound", "2026-08-12T11:00:00Z", "INBOX", "UNREAD"),
        ])
        result = self.run_cli("--until", "2026-08-12T12:00:00Z")
        self.assertEqual(["inbound"], [item["id"] for item in result["messages"]])

    def test_search_is_bounded_before_exact_timestamp_filtering(self):
        self.run_cli("--since", "24h", "--until", "2026-08-12T12:00:00Z")
        calls = [json.loads(line) for line in self.calls.read_text().splitlines()]
        list_call = next(call for call in calls if call[:4] == ["gmail", "users", "messages", "list"])
        query = json.loads(list_call[list_call.index("--params") + 1])["q"]
        self.assertIn("after:", query)
        self.assertIn("before:", query)

    def test_invalid_or_reversed_windows_fail_closed(self):
        missing_zone = self.run_cli("--since", "2026-08-12T10:00:00", expected=1)
        reversed_window = self.run_cli(
            "--since", "2026-08-13T00:00:00Z", "--until", "2026-08-12T00:00:00Z", expected=1
        )
        self.assertEqual("invalid_window", missing_zone["error"]["code"])
        self.assertEqual("invalid_window", reversed_window["error"]["code"])


if __name__ == "__main__":
    unittest.main()
