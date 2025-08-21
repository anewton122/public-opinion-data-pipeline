"""
Pipeline for Automated Public Opinion Data Processing
---------------------------------------------------

This module defines a Prefect flow that performs the extract‑transform‑load
workflow for public opinion survey data. The pipeline reads raw survey data
from the ``data/raw`` directory, computes summary statistics such as the
overall support rate and support rates broken down by demographic
characteristics, and writes a human‑readable report to the ``docs``
directory with a timestamped filename.

The goal of this pipeline is to mirror the kind of automation you used in
professional settings to produce updated analytics without manual
intervention. By scheduling this pipeline to run on a periodic basis (for
example via Prefect Cloud or GitHub Actions), organizations can ensure
their insights stay current as new data arrives.

This file requires Prefect 2.x. To run the flow locally, execute
``python src/pipeline.py`` from the repository root. If you wish to
schedule the flow, you can register it with Prefect Cloud or embed it in
a CI/CD workflow.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import pandas as pd
from prefect import flow, task, get_run_logger


@task
def extract_data() -> pd.DataFrame:
    """Read raw survey CSV files from the data/raw directory and concatenate them.

    Returns
    -------
    pandas.DataFrame
        The concatenated survey responses.
    """
    logger = get_run_logger()
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    csv_files = list(raw_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")
    frames = []
    for csv_file in csv_files:
        logger.info(f"Reading {csv_file}…")
        frames.append(pd.read_csv(csv_file))
    df = pd.concat(frames, ignore_index=True)
    logger.info(f"Loaded {len(df)} rows from {len(csv_files)} file(s)")
    return df


@task
def transform_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute summary statistics from the survey data.

    The returned dictionary contains the overall support rate as well as
    lists of dictionaries summarizing support by each demographic column.

    Parameters
    ----------
    df : pandas.DataFrame
        The survey responses.

    Returns
    -------
    dict
        A dictionary of summary statistics.
    """
    summary: Dict[str, Any] = {}
    summary["overall_support_rate"] = df["policy_support"].mean()
    # Compute support rates by each demographic feature
    demographic_cols = ["gender", "race", "age_group", "education", "income"]
    for col in demographic_cols:
        grouped = df.groupby(col)["policy_support"].agg(["count", "mean"])
        summary[col] = (
            grouped.reset_index()
            .rename(columns={"count": "respondent_count", "mean": "support_rate"})
            .to_dict(orient="records")
        )
    return summary


@task
def load_data(summary: Dict[str, Any]) -> str:
    """Write the summary statistics to a timestamped report in the docs directory.

    Parameters
    ----------
    summary : dict
        The computed summary statistics.

    Returns
    -------
    str
        The path to the written report file.
    """
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = docs_dir / f"report_{ts}.txt"
    lines = []
    lines.append("Public Opinion Data Summary Report")
    lines.append("=" * 36)
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")
    # overall
    overall_rate = summary.get("overall_support_rate", None)
    if overall_rate is not None:
        lines.append(f"Overall support rate: {overall_rate:.3f}")
        lines.append("")
    # by categories
    for col in ["gender", "race", "age_group", "education", "income"]:
        lines.append(f"Support by {col}:")
        for record in summary[col]:
            value = record[col]
            count = record["respondent_count"]
            rate = record["support_rate"]
            lines.append(
                f"  {value:20} — respondents: {count:4d}, support_rate: {rate:.3f}"
            )
        lines.append("")
    # write to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return str(report_path)


@flow(name="public_opinion_data_pipeline")
def pipeline() -> str:
    """Run the full extract‑transform‑load pipeline.

    Returns
    -------
    str
        The path to the generated report file.
    """
    df = extract_data()
    summary = transform_data(df)
    report_path = load_data(summary)
    return report_path


if __name__ == "__main__":
    # Execute the pipeline when run as a script
    report_file = pipeline()
    print(f"Pipeline completed. Report written to: {report_file}")
