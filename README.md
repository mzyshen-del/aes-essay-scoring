# Automated Essay Scoring: feature models and LLM comparison

This is a curated public version of a course research project. The notebook compares baselines, two linear regression feature sets, and 12 LLM scoring conditions on the public [ELLIPSE Corpus](https://github.com/scrosseye/ELLIPSE-Corpus). The original essay CSV files and row-level predictions are not redistributed here.

## Contents

- [`notebooks/aes_part1.ipynb`](notebooks/aes_part1.ipynb): analysis and experiment code. Saved outputs were removed because some displayed essay text.
- [`results/summary.json`](results/summary.json): selected aggregate results from the saved final configuration.
- [`results/`](results/): selected comparison charts.

## Selected results

| Approach | Evaluation set | Pearson r | MSE |
|---|---:|---:|---:|
| Expanded feature regression | Official test split | 0.4996 | 0.2918 |
| Selected LLM condition, DeepSeek V3.2 | 60 essay subset | 0.6616 | 0.4125 |

The two rows use different evaluation sizes. The metrics should not be interpreted as a direct matched-set ranking. The notebook contains the experiment workflow and the saved summary records 12 tested LLM conditions.

## Run

Open the notebook in Python 3 and run cells in order. It downloads the public training CSV, the password-protected test ZIP, and `ELL_Rubrics.docx` directly from the [corpus authors' repository](https://github.com/scrosseye/ELLIPSE-Corpus). The ZIP password is published in that repository's README. The notebook checks SHA-256 hashes before using these files, then extracts the test CSV in memory. No corpus file or rubric is committed here.

The ELLIPSE authors publish the data under [CC BY-NC-SA 4.0](https://github.com/scrosseye/ELLIPSE-Corpus#readme). Review that license for your intended use. The LLM section uses OpenRouter and needs an `OPENROUTER_API_KEY`; running it can incur API charges. Saved notebook outputs are cleared. The asset-loading cells were verified independently from a clean working directory; the full paid LLM experiment has not been rerun for this public packaging.

## Scope

This repository contains a research workflow and aggregate results, not a trained production scoring service. Human ratings remain the reference; the selected LLM experiment used only a subset of the official test split.
