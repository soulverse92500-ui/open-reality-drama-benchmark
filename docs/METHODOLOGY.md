# Methodology

ORDB evaluates metadata exported by a generation workflow. A fair comparison
uses the same synthetic seed, baseline cast, episode count, and output schema for
every model or prompting condition.

## Recommended protocol

- Generate 20 episodes per run.
- Repeat each condition three times with recorded random seeds when available.
- Keep temperature and other sampling settings in the result manifest.
- Report every run, including failures.
- Publish aggregate scores and raw structured metadata, after checking that it
  contains no personal or confidential information.

## Current weights

- character consistency: 40%
- scene transition continuity: 25%
- timeline order: 20%
- dialogue uniqueness: 15%

The weights are versioned benchmark policy, not universal measures of artistic
quality. Changes require a benchmark version bump and an explanation.
