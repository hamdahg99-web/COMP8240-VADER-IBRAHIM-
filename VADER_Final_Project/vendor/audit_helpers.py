"""Load VADER, evaluate the released corpora and export results."""
from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import sys
import tarfile
import time
import urllib.request

COMMIT = "44fc044cd877310ee8278a0eadf34bcd50d41d06"
RAW = f"https://raw.githubusercontent.com/cjhutto/vaderSentiment/{COMMIT}/"
ARCHIVE_SHA = "d5bb07d87474b3eb8d30b4deccbc23f19d742a6c5718fbacc65485b70b95c5fa"
PORT_SHA = "31c5b97ab8295e3517a22c561f97cf7f909843ecb4b9264f54f974ce861033d7"
MAINTAINED_FILES = {
    "vaderSentiment.py": "c9aac2ce0260a64d1d8493eeba4f31216b479f3d90269d1fe5719959a6083bf0",
    "vader_lexicon.txt": "ec636f884f36b5de6a4d681b2f61c08c2ec90eeb440472033f3307d0d6fa8bc9",
    "emoji_utf8_lexicon.txt": "25b217601fb59d4ed8f89360b719ddb4f352a40df0743f1cfb6f8150d02eb83a",
}
CORPORA = {
    "tweets": ("Tweet-like texts", "tweets_GroundTruth.txt", 4200, .881),
    "movie_reviews": ("Movie snippets", "movieReviewSnippets_GroundTruth.txt", 10605, .451),
    "product_reviews": ("Product snippets", "amazonReviewSnippets_GroundTruth.txt", 3708, .565),
    "nyt_editorials": ("Editorial snippets", "nytEditorialSnippets_GroundTruth.txt", 5190, .492),
}
INPUT_SHA = {
    "tweets_GroundTruth.txt": "dfbe7102e2f92579ed8b19df9a3822491880697c67adf712fb66e520cc05102f",
    "movieReviewSnippets_GroundTruth.txt": "c8293b0d942e90e223ea2c0955d969040d1a1be514a978b9af0698940bd13350",
    "amazonReviewSnippets_GroundTruth.txt": "11a9807a0974a2506a2d3b4851eaf69b3d6d20688ce4923adda2312a4f6dd6c2",
    "nytEditorialSnippets_GroundTruth.txt": "7d8fbcce7dde5d716da53e78f4ef4be6b706e9ef1e1d51887e6d0ad4b69cc27e",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download(url, destination, expected_sha):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and digest(destination) == expected_sha:
        return
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "COMP8240-VADER-audit"})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != expected_sha:
                raise ValueError("Source checksum differs from the recorded project revision.")
            destination.write_bytes(data)
            return
        except (OSError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("Source download failed after three attempts.")
            time.sleep(attempt + 1)


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prepare(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    original = root / "original"
    current = root / "maintained"
    original.mkdir(exist_ok=True)
    current.mkdir(exist_ok=True)
    archive_path = root / "hutto_ICWSM_2014.tar.gz"
    print("Downloading and checking the author's original data...")
    download(RAW + "additional_resources/hutto_ICWSM_2014.tar.gz", archive_path, ARCHIVE_SHA)
    wanted = {"vader_sentiment_lexicon.txt", "vaderSentiment.py", *INPUT_SHA}
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            name = Path(member.name).name
            if member.isfile() and name in wanted:
                with archive.extractfile(member) as source:
                    (original / name).write_bytes(source.read())
    for name, expected in INPUT_SHA.items():
        if digest(original / name) != expected:
            raise ValueError(f"Original input checksum mismatch: {name}")
    port = root / "vader2014_py3.py"
    if digest(port) != PORT_SHA:
        raise ValueError("The archived Python 3 compatibility port has changed.")
    print("Downloading and checking the author's maintained comparison code...")
    for name, expected in MAINTAINED_FILES.items():
        download(RAW + "vaderSentiment/" + name, current / name, expected)
    previous = Path.cwd()
    try:
        os.chdir(original)
        archived = import_file("vader2014_colab", port)
    finally:
        os.chdir(previous)
    maintained = import_file("vader_maintained_colab", current / "vaderSentiment.py")
    analyser = maintained.SentimentIntensityAnalyzer()
    print("READY: both VADER versions loaded. All four original data files verified.")
    print("Python:", platform.python_version(), "| Source revision:", COMMIT[:8])
    return archived, analyser


def polarity(score):
    return 1 if score >= .05 else -1 if score <= -.05 else 0


def label(score):
    return {-1: "Negative", 0: "Neutral", 1: "Positive"}[polarity(score)]


def pearson(x, y):
    n = len(x)
    xm, ym = math.fsum(x) / n, math.fsum(y) / n
    dx, dy = [v - xm for v in x], [v - ym for v in y]
    denominator = math.sqrt(math.fsum(v * v for v in dx) * math.fsum(v * v for v in dy))
    return math.fsum(a * b for a, b in zip(dx, dy)) / denominator


def macro_f1(gold, predictions):
    f1 = []
    for cls in (-1, 0, 1):
        tp = sum(g == cls and p == cls for g, p in zip(gold, predictions))
        fp = sum(g != cls and p == cls for g, p in zip(gold, predictions))
        fn = sum(g == cls and p != cls for g, p in zip(gold, predictions))
        denominator = 2 * tp + fp + fn
        f1.append(2 * tp / denominator if denominator else 0.0)
    return math.fsum(f1) / 3


def show_table(headers, rows):
    try:
        from IPython.display import HTML, display
    except ImportError:
        print(" | ".join(map(str, headers)))
        for row in rows:
            print(" | ".join(map(str, row)))
        return
    head = "".join(f"<th>{html.escape(str(v))}</th>" for v in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>" for row in rows)
    display(HTML("<style>.vader-output{border-collapse:collapse;width:100%;max-width:1100px}"
                 ".vader-output th,.vader-output td{border:1px solid #cbd5e1;padding:9px;text-align:left}"
                 ".vader-output th{background:#e8eef5;color:#111}</style>"
                 f"<table class='vader-output'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"))


def demo(texts, archived, maintained):
    rows = []
    for text in texts:
        old = archived.sentiment(text)["compound"]
        new = maintained.polarity_scores(text)["compound"]
        rows.append([text, f"{old:.4f}", f"{new:.4f}", label(old)])
    show_table(["Text", "Archived compound", "Maintained compound", "Archived predicted class"], rows)
    return rows


def full_audit(root, archived, maintained):
    root = Path(root)
    result_dir = root / "results"
    result_dir.mkdir(exist_ok=True)
    summary = []
    total_start = time.perf_counter()
    for key, (name, filename, expected_n, paper_r) in CORPORA.items():
        print(f"Scoring {name}: {expected_n:,} texts...", flush=True)
        path = root / "original" / filename
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                identifier, mean, text = line.split("\t", 2)
                records.append((identifier, float(mean), text))
        assert len(records) == expected_n, f"Unexpected number of records in {filename}"
        start = time.perf_counter()
        old = [archived.sentiment(row[2])["compound"] for row in records]
        new = [maintained.polarity_scores(row[2])["compound"] for row in records]
        human = [row[1] for row in records]
        provisional_gold = [polarity(v / 4.0) for v in human]
        summary.append({
            "domain": key, "corpus": name, "n": len(records), "paper_r": paper_r,
            "archived_r": round(pearson(human, old), 6),
            "maintained_r": round(pearson(human, new), 6),
            "archived_macro_f1_provisional": round(macro_f1(provisional_gold, [polarity(v) for v in old]), 6),
            "maintained_macro_f1_provisional": round(macro_f1(provisional_gold, [polarity(v) for v in new]), 6),
            "seconds": round(time.perf_counter() - start, 3),
        })
        with (result_dir / f"{key}-scores.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "human_mean", "archived_compound", "maintained_compound"])
            writer.writerows((row[0], row[1], a, b) for row, a, b in zip(records, old, new))
    (result_dir / "original-data-results.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (result_dir / "original-data-results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    metadata = {
        "python": platform.python_version(), "platform": platform.platform(),
        "source_commit": COMMIT, "source_url": RAW, "archive_sha256": ARCHIVE_SHA,
        "input_sha256": INPUT_SHA, "archived_compatibility_source_sha256": PORT_SHA,
        "compatibility_changes": ["Python 2 syntax converted with lib2to3 under Python 3.12", "Latin-1 lexicon decoding"],
        "correlation_implementation": "Standard Pearson correlation; Python standard library",
        "classification_policy": "Provisional: gold mean / 4, inclusive +/-0.05, macro-F1 over three classes",
        "paper_f1_protocol_confirmed": False,
        "human_annotation_performed": False, "new_benchmark_scored": False,
        "total_seconds": round(time.perf_counter() - total_start, 3),
    }
    (result_dir / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"DONE: {sum(item['n'] for item in summary):,} original texts scored with both versions.")
    return summary, result_dir
