"""Offline contract checks for the notebook's OpenRouter request helpers."""
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace

NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "aes_part1.ipynb"
cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
helper = next("".join(c["source"]) for c in cells if "def score_essay_with_llm(" in "".join(c["source"]))
scope = {"ALLOWED_SCORES": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], "re": re}
exec(compile(helper, str(NOTEBOOK), "exec"), scope)
parse = scope["parse_llm_score"]
score = scope["score_essay_with_llm"]

class FakeCompletions:
    def __init__(self, reply="3.5", error=None):
        self.reply = reply
        self.error = error
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.reply))])

class ContractTest(unittest.TestCase):
    def test_parser_rejects_prose_and_out_of_range_scores(self):
        self.assertEqual(parse("3.5"), 3.5)
        for value in ("Score: 3.5", "4.2", "6", "", None, "1 to 5"):
            self.assertIsNone(parse(value))

    def test_request_shape_and_valid_reply(self):
        fake = FakeCompletions()
        client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
        value, reply = score("A sample essay", client, "test-model", "rubric prompt", 0.2, 8)
        self.assertEqual((value, reply), (3.5, "3.5"))
        self.assertEqual(fake.kwargs["model"], "test-model")
        self.assertEqual(fake.kwargs["messages"][0]["content"], "rubric prompt")
        self.assertIn("A sample essay", fake.kwargs["messages"][1]["content"])
        self.assertEqual(fake.kwargs["max_tokens"], 8)
        self.assertFalse(fake.kwargs["stream"])

    def test_bad_reply_and_transport_error_are_failed_scores(self):
        for fake in (FakeCompletions(reply="not a score"), FakeCompletions(error=TimeoutError("timeout"))):
            client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
            value, _ = score("essay", client, "model", "rubric", 0, 8)
            self.assertIsNone(value)

if __name__ == "__main__":
    unittest.main()

