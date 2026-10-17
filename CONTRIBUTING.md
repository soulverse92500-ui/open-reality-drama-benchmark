# Contributing

Thank you for helping improve ORDB.

1. Open an issue describing the continuity failure or metric change.
2. Use only fictional or properly licensed test data.
3. Do not submit personal data, private prompts, API keys, or copyrighted scripts.
4. Add or update a focused unit test.
5. Run `python -m unittest discover -s tests -v` before opening a pull request.

Metric changes should explain what failure they measure, how false positives are
controlled, and whether scores remain comparable with earlier benchmark versions.
