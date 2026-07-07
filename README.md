# JNAS_OSV2

## Builder V4

Autonomous project generation:

```bash
python build_project.py \
    --project "Hello Project" \
    --output workspace/generated_projects \
    --provider ollama \
    --milestone 1
```

Builder V4 calls the local Ollama HTTP API directly, parses
`===FILE:path=== ... ===END===` blocks, writes files, runs compile
validation, runs pytest, performs one repair cycle when validation
fails, writes `BUILD_REPORT.md`, and returns exit code `0` only on
success.
