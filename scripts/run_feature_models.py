"""Reproduce the two feature regressions without an API key.

Run from any directory: python /path/to/scripts/run_feature_models.py --output-dir out
Only aggregate metrics and a chart are written; essay text stays in memory.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


BASE = "https://raw.githubusercontent.com/scrosseye/ELLIPSE-Corpus/main/"
ASSETS = {
    "train": ("ELLIPSE_Final_github_train.csv", "782344e99668a3ff508d7410c0eb6e36da70f3b28f81c96e367f1ca04924b06c"),
    "test": ("ELLIPSE_Final_github_test.zip", "9ecddfcda83f6a99c8a24dda47fb1c30673fedeaf578a0fadac6645fd151a2f8"),
}
BASIC = ["num_words", "num_sent", "TTR", "MTLD", "num_word_div_para"]
EXPANDED = BASIC + ["num_para", "avg_sentence_length", "avg_paragraph_length", "sentences_per_paragraph", "log_num_words", "Type", "Token"]


def fetch_verified(name):
    filename, expected = ASSETS[name]
    with urlopen(BASE + filename, timeout=60) as response:
        payload = response.read()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"Upstream {filename} changed; review it before updating its hash")
    return payload


def add_features(frame):
    frame = frame.copy()
    frame["avg_sentence_length"] = frame["num_words"] / frame["num_sent"].clip(lower=1)
    frame["avg_paragraph_length"] = frame["num_words"] / frame["num_para"].clip(lower=1)
    frame["sentences_per_paragraph"] = frame["num_sent"] / frame["num_para"].clip(lower=1)
    frame["log_num_words"] = np.log1p(frame["num_words"])
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/feature_models"))
    args = parser.parse_args()
    train = pd.read_csv(io.BytesIO(fetch_verified("train")))
    with ZipFile(io.BytesIO(fetch_verified("test"))) as archive:
        test = pd.read_csv(io.BytesIO(archive.read("ELLIPSE_Final_github_test.csv", pwd=b"ellipse_test")))
    if len(train) != 3911 or len(test) != 2571:
        raise ValueError("Unexpected corpus split size")
    train, test = add_features(train), add_features(test)
    y_train = train["Overall"].to_numpy()
    y_test = test["Overall"].to_numpy()
    results = {}
    predictions = {}
    for name, features in (("lr_basic", BASIC), ("lr_expanded", EXPANDED)):
        model = LinearRegression().fit(train[features], y_train)
        predicted = np.clip(model.predict(test[features]), 1.0, 5.0)
        predictions[name] = predicted
        results[name] = {
            "features": features,
            "pearson_r": float(pearsonr(y_test, predicted).statistic),
            "mse": float(mean_squared_error(y_test, predicted)),
        }
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary = {"train_size": len(train), "test_size": len(test), "evaluation_split": "official_test", "models": results}
    (output / "feature_metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    for ax, (name, predicted) in zip(axes, predictions.items()):
        ax.scatter(y_test, predicted, s=5, alpha=0.25)
        ax.plot([1, 5], [1, 5], color="black", linestyle="--", linewidth=1)
        ax.set(title=f"{name}: r={results[name]['pearson_r']:.3f}, MSE={results[name]['mse']:.3f}", xlabel="Human score", ylabel="Predicted score")
    fig.tight_layout()
    fig.savefig(output / "feature_comparison.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))
    print(f"Wrote aggregate results to {output}")


if __name__ == "__main__":
    main()
