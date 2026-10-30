# SmartHire AI — Resume Screening and Recruitment Decision Support

SmartHire AI is a local Streamlit application that helps recruiters compare PDF and DOCX resumes against a job description and a configurable list of required skills. It presents evidence and ranking indicators to support **human review**; it does not make hiring decisions.

## Features

- Upload multiple PDF and DOCX resumes in one analysis.
- Extract selectable text from PDF files and text from DOCX paragraphs and tables.
- Match configured required skills using keyword matching and recognized aliases.
- Display matched skills, missing skills, and text evidence for detected matches.
- Calculate a weighted skill-match score.
- Optionally compare the job description with resume text chunks using a local Sentence Transformers model.
- Show candidate comparisons, critical-skill review flags, and a CSV report.
- Keep the skill score and semantic similarity visible as separate metrics.

## Scoring methodology

### Weighted skill-match score

- Each configured critical skill earns **2 points** when detected.
- Each other required skill earns **1 point** when detected.
- The weighted skill-match percentage is earned points divided by total possible points, multiplied by 100.

### Semantic similarity

The application uses `sentence-transformers/all-MiniLM-L6-v2` to compare the job description with overlapping chunks of resume text. The app averages up to the three highest cosine-similarity values.

**Semantic similarity is a cosine-similarity measure, not a probability of suitability.**

### Combined ranking score

When semantic similarity is available, the application calculates:

`Combined ranking score = 80% × weighted skill-match score + 20% × (clamped semantic similarity × 100)`

If semantic analysis is unavailable, the application falls back to the weighted skill-match score. Candidates missing configured critical skills are placed after candidates without those missing critical skills and are flagged for human review. This is a configurable prototype scoring approach, not a validated hiring or performance prediction model.

## Requirements

- Windows, macOS, or Linux
- Python compatible with the pinned package versions in `requirements.txt`
- Internet access the first time the Sentence Transformers model must be downloaded, unless it is already cached
- Sufficient disk space and memory for PyTorch and the embedding model

The current development environment used these direct dependencies:

- Streamlit 1.66.0
- NumPy 2.5.4
- pypdf 6.21.1
- python-docx 1.2.0
- sentence-transformers 6.1.0
- PyTorch 2.14.1

## Setup on Windows (PowerShell)

Open PowerShell in the project directory.

1. Create a virtual environment if you do not already have one:

   ```powershell
   py -m venv .venv
   ```

2. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   python -m streamlit run .\app_day6.py --server.fileWatcherType none
   ```

5. Open the local URL shown in the terminal, usually `http://localhost:8501`.

If the project already has a working `.venv`, do not recreate it unnecessarily. Install from `requirements.txt` in a separate clean environment before claiming the project has been verified on a fresh setup.

## How to use

1. Enter a job title.
2. Enter required skills as comma-separated values.
3. Enter critical skills. Every critical skill must also appear in the required-skills list.
4. Enter the job description.
5. Upload one or more PDF or DOCX resumes.
6. Select **Analyze candidates**.
7. Review the overview, compare candidates, inspect skill evidence, and export the CSV report.

## Limitations and responsible use

- Scanned/image-only PDFs are not processed by OCR in this version; they may produce no extractable text.
- Keyword matching detects text mentions. A detected mention does not prove proficiency, and a missing keyword does not prove that a candidate lacks a skill.
- Resume formatting, abbreviations, unusual skill names, and aliases can affect extraction and matching.
- Semantic similarity measures text relatedness and must not be interpreted as a probability or a validated candidate-quality score.
- Combined ranking weights are configurable prototype choices and have not been established as predictive of job performance.
- Review the source evidence and assess candidates consistently. Do not use this tool as the sole basis for employment decisions.
- Resume documents can contain personal information. Use authorized data, limit access, and follow applicable privacy and retention policies. The CSV export intentionally omits full extracted resume text.

## Project files

- `app_day6.py` — main Streamlit application.
- `skill_matcher.py` — text normalization, skill-alias matching, evidence extraction, and weighted score calculation.
- `requirements.txt` — direct Python dependencies for the application.
- `README.md` — project overview and setup instructions.
- `README.txt` — existing notes for the separate Day 7.5 synthetic evaluation pack; retained as a separate document.

The project directory may contain experimental scripts and reports from development. They are not all required to launch the main application. Before distributing the project, identify and include the files imported or needed by the selected application version, and do not delete development artifacts until that dependency check is complete.

## Verification status

This README describes the intended behavior of the current `app_day6.py` implementation. Syntax checks and a local demo are useful but do not prove all features are correct. Before submission, run an end-to-end smoke test with authorized sample resumes and verify uploads, scoring, candidate selection, semantic-analysis fallback, and CSV export.
