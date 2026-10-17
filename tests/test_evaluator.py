import unittest

from ordb.evaluator import evaluate_run


def clean_run():
    return {
        "run_name": "test",
        "characters": [{"id": "a", "facts": {"age": 30, "coat": "blue"}}],
        "episodes": [
            {
                "index": 1,
                "character_states": {"a": {"age": 30, "coat": "blue"}},
                "start_state": {"location": "hall"},
                "end_state": {"location": "desk"},
                "dialogue": [{"speaker": "a", "text": "請等一下"}],
            },
            {
                "index": 2,
                "character_states": {"a": {"age": 30, "coat": "blue"}},
                "start_state": {"location": "desk"},
                "end_state": {"location": "desk"},
                "dialogue": [{"speaker": "a", "text": "我看到了"}],
            },
        ],
    }


class EvaluatorTests(unittest.TestCase):
    def test_clean_run_scores_100(self):
        report = evaluate_run(clean_run())
        self.assertEqual(report["scores"]["overall"], 100.0)
        self.assertEqual(report["findings"], [])

    def test_detects_character_drift(self):
        run = clean_run()
        run["episodes"][1]["character_states"]["a"]["age"] = 41
        report = evaluate_run(run)
        self.assertTrue(any(item["code"] == "CHARACTER_DRIFT" for item in report["findings"]))
        self.assertLess(report["scores"]["character_consistency"], 100.0)

    def test_detects_broken_transition_and_repetition(self):
        run = clean_run()
        run["episodes"][1]["start_state"]["location"] = "street"
        run["episodes"][1]["dialogue"][0]["text"] = "請，等一下！"
        report = evaluate_run(run)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("BROKEN_TRANSITION", codes)
        self.assertIn("REPEATED_DIALOGUE", codes)

    def test_rejects_duplicate_character_ids(self):
        run = clean_run()
        run["characters"].append({"id": "a", "facts": {}})
        with self.assertRaises(ValueError):
            evaluate_run(run)


if __name__ == "__main__":
    unittest.main()
