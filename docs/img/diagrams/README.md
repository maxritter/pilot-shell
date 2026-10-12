# Diagrams

Images drawn for the QualityLayer workshop deck (Claude Design project `47ffd63a`), exported in
the App's dark and light palettes for reuse in the README, the docs and the website. Each image
comes as `<name>-dark.webp` and `<name>-light.webp`.

| Image | Shows | Source to cite |
|---|---|---|
| `software-factory-2022` | How a team shipped before agents: people decide, an engineer builds, a person reviews | – |
| `software-factory-planning-first` | Planning together first makes review shorter | – |
| `software-factory-agentic` | An agent builds; review becomes the slow part | – |
| `software-factory-lights-off` | Teams that stop reading the code | – |
| `software-factory-lights-on` | People at the plan and the review, mapped to the QualityLayer steps | – |
| `research-700-companies` | More code and pull requests, the same finished features, longer reviews | Fiona Chen and James Stratton, Harvard, "Artificial Intelligence in the Firm: Bottlenecks in Software Production", version of 4 August 2026 ([PDF](https://fion.ac/jellyfish.pdf)); Jellyfish data from 700+ companies, 2021 to March 2026 |
| `slopcodebench-by-release` | Strict pass rate by model release | SlopCodeBench, University of Wisconsin–Madison, May 2026; starred models from HumanLayer's full rerun of the same benchmark, 4 October 2026 snapshot (`humanlayer/advanced-context-engineering-for-coding-agents`, benchmarking-new-models-on-slop-code-bench.md) |
| `codebase-drift` | Drift over time, with the paper's erosion and verbosity figures | SlopCodeBench, University of Wisconsin–Madison, May 2026 |Regenerate after changing the deck: serve the deck's local working folder
(`.open-claude-design/design-scratch/deck/workshop/`, not tracked) on loopback and run
`node tools/export-diagrams.mjs <deck url> <repository>/docs/img/diagrams` from there.
