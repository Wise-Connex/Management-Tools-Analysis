# Management-Tools-Analysis

Statistical Analysis tool, of Management Tools best ranked

- Author: Diomar Anez

- Python Coder Assistant: Dimar Anez

This tools are used to analyze the best ranked management tools in the market. They were created to support the Doctoral Thesis of Diomar Anez "Ontological Dichotomy in 'Management Fads'" (c) 2024, about the Managerial Fads.

## Apps

- mta.py (Management-Tools-Analysis): This app is used to analyze the best ranked management tools in the market. Create a report in PDF format with the analysis of the tool.
- crossref.py: This app create CSV files with the data of published works about specific management tools. Create a CSV file with the data of the tool, and a index file with the tool name and the csv filename.
- correlation.py: This app analyze the correlation of a management tool between several sources databases
- dashboard.py: This app create a dashboard to visualize the data analyzed

## Install the Application and Dependencies

1. Clone the repository

```bash
git clone https://github.com/Wise-Connex/Management-Tools-Analysis.git
```

2. Create a Virtual Environment

```bash
cd Management-Tools-Analysis
python -m venv .venv
```

3. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

4. Install the dependencies

```bash
pip install -r requirements.txt
```

> Note: To deactivate the virtual environment

```bash
cd Management-Tools-Analysis
deactivate
```

5. Copy WV-VSCODE-Private.key to Management-Tool_analysis folder

```bash
cp WV-VSCODE-Private.key .
```

> Remember activate the virtual environment when run the app for the first time:

```bash
cd Management-Tools-Analysis
source .venv/bin/activate
```

6. Run the application

```bash
python3 mta.py
```

7. Update local repository

```bash
git pull
```

## Config Files

- tools.py: This file contains the list of tools to be analyzed. including Keywords and filenames to the different sources databases.
- tools.txt: this file include the list of search keywords to be used in the crossref.py app to search for the tools in the different sources databases.
- prompts.py: This file contains the prompts used in the mta.py app to generate the report.

## Databases

- dbase: This folder contains the CSV files with the data of the toll from the different sources databases.
- Each csv use two letter at the beginning to identified the data source:
  - GT: Google Trends
  - GB: Google Books Ngram Viewer
  - CR: Crossref.org
  - BR: Bein Research
