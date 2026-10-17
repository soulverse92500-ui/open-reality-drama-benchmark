# Open Reality Drama Benchmark (ORDB)

ORDB is a small, offline benchmark for measuring continuity in multi-episode,
AI-generated drama. It checks structured episode output for character drift,
timeline errors, repeated dialogue, and broken scene transitions.

The project ships with synthetic characters and stories. It contains no private
prompts, user conversations, production analytics, or account credentials.

## Why this exists

Long-form generation often looks convincing one scene at a time while quietly
changing a character's age, clothing, relationships, location, or knowledge.
ORDB makes those failures visible with a reproducible JSON format and a local
evaluator that does not require an API key.

## Quick start

Requirements: Python 3.10 or newer.

```bash
python -m ordb.cli evaluate examples/sample_run.json --pretty
python -m unittest discover -s tests -v
```

When running directly from a source checkout on Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m ordb.cli evaluate examples/sample_run.json --pretty
python -m unittest discover -s tests -v
```

## Input format

Each run contains a baseline cast and an ordered list of episodes. Episodes may
report character state, dialogue, and their opening/closing scene state. See
[`examples/sample_run.json`](examples/sample_run.json) for a complete example.
The portable schema is available at [`schemas/run.schema.json`](schemas/run.schema.json).

The evaluator reports:

- character fact consistency;
- chronological ordering;
- continuity between one episode's end state and the next start state;
- exact normalized dialogue repetition;
- an overall score and machine-readable findings.

## Scope

ORDB evaluates structured metadata. It does not claim to measure artistic
quality, truth, morality, or whether a story is commercially successful. The
included dataset is fictional and should not be used to infer facts about real
people.

## Reproducible experiment

1. Select one synthetic seed from `datasets/story_seeds/`.
2. Generate 10–30 episodes with the same baseline cast.
3. Save each model's output in the documented JSON format.
4. Run ORDB and retain the JSON report.
5. Repeat each condition at least three times.
6. Publish aggregate metrics together with model, prompt version, date, and
   generation settings.

Do not publish API keys, private prompts, personal data, or copyrighted scripts.
See [`docs/PRIVACY.md`](docs/PRIVACY.md) before contributing a dataset or result.

## Roadmap

- JSON Schema validation with precise error locations
- fuzzy semantic repetition detection as an optional plugin
- multilingual dialogue normalization
- blinded human-rating templates
- a versioned public results table

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Security reports should follow
[`SECURITY.md`](SECURITY.md).

## License

Code is licensed under MIT. Synthetic datasets and documentation are
licensed under CC BY 4.0 unless a file states otherwise.
