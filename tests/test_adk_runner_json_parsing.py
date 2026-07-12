from __future__ import annotations

import unittest

from medtour_ai.services.adk_runner import _parse_json_text


class AdkRunnerJsonParsingTests(unittest.TestCase):
    def test_parses_json_inside_markdown_with_surrounding_text(self) -> None:
        parsed = _parse_json_text(
            """
            Here is the generated report:

            ```json
            {"status": "ready", "city_options": [{"city": "Shanghai"}]}
            ```

            Please verify all estimates.
            """
        )

        self.assertEqual(parsed["status"], "ready")
        self.assertEqual(parsed["city_options"][0]["city"], "Shanghai")

    def test_parses_first_json_object_from_plain_text(self) -> None:
        parsed = _parse_json_text(
            'Planner draft follows:\n{"status": "ready", "city_options": []}\nEnd of response.'
        )

        self.assertEqual(parsed["status"], "ready")
        self.assertEqual(parsed["city_options"], [])

    def test_parses_python_style_dict_as_last_resort(self) -> None:
        parsed = _parse_json_text("{'status': 'ready', 'city_options': []}")

        self.assertEqual(parsed["status"], "ready")


if __name__ == "__main__":
    unittest.main()
