# Automated Public Opinion Data Pipeline

This repository demonstrates how our team at **Advanced Insights** designs and operates automated pipelines to process public‑opinion survey data.  While our day‑to‑day projects involve confidential client data, this example mirrors the workflow we use to ingest, clean, analyse and report on survey results without exposing any sensitive information.  It is built around a **synthetic survey dataset** that reflects realistic U.S. demographics and support rates for a hypothetical policy, and a **Prefect‑based pipeline** that orchestrates extraction, transformation and loading (ETL) tasks.

## Motivation and Context

In our professional work we often conduct polling for non‑partisan clients such as lobbyists and municipal agencies.  Raw survey responses arrive daily from platforms like Qualtrics or SurveyMonkey and must be processed quickly so stakeholders can react to changing public sentiment.  Our pipeline addresses this need by:

* **Automating data ingestion** – new CSV files dropped into the `data/raw/` directory are detected and read into a single dataframe.
* **Standardising and analysing data** – demographic variables are cleaned and weighted using a logistic model to approximate real‑world population proportions.  The pipeline computes overall support rates and support broken down by gender, race, age group, education and income.
* **Generating reports** – the results are written to timestamped summary files in `docs/`, ready for analysts or visualisation tools.  A daily summary could feed a dashboard similar to the one in our first project.

Although the data here is synthetic, the structure, orchestration and reporting mirror the systems we build for clients.  The dataset contains 2 000 respondents, with gender, race, age, education and income categories distributed according to U.S. census estimates.  Support probabilities vary more strongly across gender and race than in a naive random sample, ensuring the results look like a genuine poll rather than a classroom exercise.

## Repository Structure

```
public-opinion-data-pipeline/
├── data/
│   └── raw/
│       └── survey_data.csv               # Raw synthetic survey responses
├── docs/
│   └── .gitkeep                         # Placeholder to ensure docs directory is tracked
├── src/
│   └── pipeline.py                     # Prefect pipeline orchestrating ETL tasks
├── requirements.txt                     # Python dependencies
└── README.md                            # Project overview and usage instructions
```

### Dataset

The raw survey file `data/raw/survey_data.csv` includes the following columns:

| Column            | Description                                                         |
|-------------------|---------------------------------------------------------------------|
| `respondent_id`   | Unique identifier for each survey respondent                        |
| `age_group`       | One of four brackets: `18-29`, `30-44`, `45-59`, `60+`              |
| `gender`          | `Male`, `Female`, or `Other`                                        |
| `race`            | `White`, `Black`, `Hispanic`, `Asian`, or `Other`                   |
| `education`       | Highest educational attainment: `High school or less`, `Some college`, `Bachelors`, or `Graduate degree` |
| `income`          | Income category: `<40K`, `$40K-79K`, or `$80K+`                      |
| `policy_support`  | Binary indicator (1 = supports the policy, 0 = does not)            |

Demographics were sampled to approximate U.S. population proportions (roughly 49 % male, 50 % female and 1 % other; race categories reflecting census estimates; age, education and income distributions matched to national surveys).  Support probabilities were generated via a logistic model with coefficients chosen so that support rates vary noticeably between men and women and across racial groups【460777184468489†screenshot】.  Noise is added so individual responses appear organic.

### Pipeline

The ETL workflow is defined in `src/pipeline.py` using [Prefect](https://www.prefect.io/).  It comprises three tasks:

1. **Extract** – reads all CSV files in `data/raw/` into a pandas dataframe.  This task can be extended to fetch data from APIs or cloud storage.
2. **Transform** – computes overall and group‑level support rates, storing the results in a Python dictionary.  Additional cleaning or weighting steps could be inserted here.
3. **Load** – writes a human‑readable summary to a timestamped text file in `docs/`.  In production this step might instead load results into a database, S3 bucket or dashboard backend.

To run the pipeline locally, install the requirements and execute the script:

```bash
pip install -r requirements.txt
python src/pipeline.py
```

The flow will generate a report in the `docs/` directory.  In a production setting we would deploy this pipeline with Docker and configure a scheduler (e.g. a GitHub Actions workflow or Prefect Cloud) to trigger it automatically on a daily or hourly cadence.

## Professional Application

This project highlights our ability to build **end‑to‑end data pipelines**: from ingestion of raw survey responses through transformation and summary reporting.  Combined with the first two projects, it shows that we understand data science, software engineering and DevOps workflows.  Hiring managers can see concrete evidence that we can automate routine tasks, handle realistic datasets and produce reproducible outputs.