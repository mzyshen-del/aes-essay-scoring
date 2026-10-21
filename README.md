# Automated Essay Scoring: feature models and LLM comparison

This is a curated public version of a course research project. I completed Part 1 independently: data audit, feature baselines, LLM experiments, evaluation, and analysis. The notebook compares baselines, two linear regression feature sets, and 12 LLM scoring conditions on the public [ELLIPSE Corpus](https://github.com/scrosseye/ELLIPSE-Corpus). The original essay CSV files and row-level predictions are not redistributed here.

## Contents

- [`notebooks/aes_part1.ipynb`](notebooks/aes_part1.ipynb): analysis and experiment code. Saved outputs were removed because some displayed essay text.
- [`scripts/run_feature_models.py`](scripts/run_feature_models.py): reproducible no-API baseline and feature-model run.
- [`results/summary.json`](results/summary.json): selected aggregate results from the saved final configuration.
- [`results/`](results/): selected comparison charts.

## At a glance

**Question.** How do transparent, low-cost feature models compare with rubric-guided LLM scoring for English learner essays?

**Design.** I trained two linear regression variants on all 3,911 official training essays and evaluated them on all 2,571 official test essays. For the API experiment, I tested 3 models × 2 prompts × 2 temperatures on the same stratified sample of 60 official test essays. I selected the LLM condition by highest Pearson correlation, with MSE as a tie-breaker. All 12 conditions returned scores for all 60 essays.

**Finding.** The selected DeepSeek V3.2 condition tracked relative essay quality more closely than the feature models on the matched 60 essays, but its absolute scores were worse: it underpredicted by 0.458 points on average. In particular, for the 10 essays rated 4.0 or 4.5 by humans, its mean error was −1.00 point. This is unsuitable for unsupervised high-stakes scoring without calibration and a larger independent evaluation.

## Results: keep evaluation scopes separate

### Full official test set (2,571 essays)

| Approach | Evaluation set | Pearson r | MSE |
|---|---:|---:|---:|
| Basic feature regression | Official test split | 0.4610 | 0.3056 |
| Expanded feature regression | Official test split | 0.4996 | 0.2918 |

### Matched 60-essay subset of the official test set

| Approach | Pearson r | MSE | MAE | Mean error (prediction − human) |
|---|---:|---:|---:|---:|
| Basic feature regression | 0.4533 | 0.2838 | 0.4346 | −0.0027 |
| Expanded feature regression | 0.5123 | 0.2631 | 0.4144 | −0.0052 |
| DeepSeek V3.2, direct prompt, temperature 0.2 | **0.6616** | 0.4125 | 0.5250 | −0.4583 |

These matched-set figures were recomputed from the saved final predictions. Pearson r measures association after centering and scaling, so a model can preserve essay ordering while systematically shifting scores. MSE penalizes the resulting absolute errors. Here, 43 of 60 LLM scores were below the human score, 13 matched, and 4 were above. The LLM condition was selected on this same 60-essay sample, so its reported performance is exploratory rather than an unbiased estimate on a held-out selection set.

[`results/summary.json`](results/summary.json) records all 12 LLM conditions and both evaluation scopes. The charts show the 12-condition ranking and the matched 60-essay comparison.

## Reproduce the no-API results

Use Python 3.13.6. From a fresh clone of this repository:

```bash
python -m venv .venv
# Activate .venv with your shell's normal command.
python -m pip install -r requirements-core.txt
python scripts/run_feature_models.py --output-dir outputs/feature_models
```

The command downloads the author's official train CSV and password-protected test ZIP, verifies pinned SHA-256 hashes, and reads the test CSV in memory. It writes `feature_metrics.json` and `feature_comparison.png` to the requested output directory. Expected values (rounded) are in the full-test table above. It needs internet access to fetch the corpus, but no API key or paid request.

The script also ran successfully from an otherwise empty directory. Offline API contract checks can be run with `python -m unittest discover -s tests -v`.

## Reproduce the optional LLM experiment

```bash
python -m pip install -r requirements-llm.txt
```

Open [`notebooks/aes_part1.ipynb`](notebooks/aes_part1.ipynb) in a Python notebook environment. Run the analysis cells in order, then explicitly opt in to the OpenRouter section and set `OPENROUTER_API_KEY` as an environment variable. The notebook retrieves the official rubric, constructs two rubric-based prompts, and runs 3 models × 2 prompts × 2 temperatures on a stratified sample of 60 official test essays (random seed 42). Model names and pricing can change at the provider. The planned run sends **720 scoring requests** plus up to **2 retries per failed request**, so the theoretical maximum is 2,160 requests. Check current provider prices and account limits before running; the project does not claim a fixed cost. The historical run is preserved as aggregate metrics in `results/summary.json` and figures, so repeating the paid run is unnecessary to inspect the findings.

## Data and use

The repository's original code and documentation are released under the [MIT License](LICENSE). This does not grant rights to the ELLIPSE corpus, rubric, essay texts, or other third-party material; use those under their respective source terms.

The notebook downloads the public training CSV, password-protected test ZIP, and `ELL_Rubrics.docx` directly from the [corpus authors' repository](https://github.com/scrosseye/ELLIPSE-Corpus). The ZIP password is published in that repository's README. SHA-256 hashes are checked before use. No corpus file or rubric is committed here.

The ELLIPSE authors publish the data under [CC BY-NC-SA 4.0](https://github.com/scrosseye/ELLIPSE-Corpus#readme). Review that license for your intended use. The LLM section uses OpenRouter and needs an `OPENROUTER_API_KEY`; running it can incur API charges. Saved notebook outputs are cleared. The asset-loading cells were verified independently from a clean working directory; the full paid LLM experiment has not been rerun for this public packaging.

## Scope

This repository contains a research workflow and aggregate results, not a trained production scoring service. Human ratings remain the reference; the selected LLM experiment used only a subset of the official test split.
