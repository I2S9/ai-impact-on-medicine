<h1 align="center">AI at the Doctor's</h1>

<p align="center">
  <img src="assets/polygon-logo.svg" alt="Polygon logo: an atom with three orbiting electrons" width="120" height="120">
</p>

<p align="center">
  <strong>Where is AI actually entering medicine?</strong><br>
  Data Visualization course, Università degli Studi di Genova, 2026/27
</p>

<p align="center">
  <a href="https://i2s9.github.io/ai-impact-on-medicine/"><strong>Visit the website</strong></a>
</p>

---

## About the project

<p align="justify">
Headlines regularly announce that artificial intelligence will “revolutionize medicine”, yet few people know which AI tools are actually approved, in which specialties and on what evidence. This project follows the measurable trace that AI leaves in healthcare: before an AI tool can be used on patients in the United States, the Food and Drug Administration (FDA) has to authorize it, and every authorization is recorded with a date, a medical specialty and a regulatory pathway.
</p>

<p align="justify">
The website compares the 1,524 AI-enabled medical devices on the FDA list across years, specialties and regulatory pathways, and shows the gap between the narrative around AI in medicine and the authorized reality.
</p>

## Team

<p align="justify">
<strong>Group Polygon:</strong> Inès Gbadamassi, Maryse Goeh-Akue, James Fosting Tahku and Illia.
</p>

## Research questions

<p align="justify">
<strong>Main question:</strong> <em>“Despite the narrative that AI ‘will revolutionize medicine’, in which medical fields is AI actually authorized and used?”</em>
</p>

| | Supporting question |
| :---: | --- |
| **Q1** | How has the number of authorized AI medical devices evolved? |
| **Q2** | Why does radiology dominate? |
| **Q3** | How large is the gap between published research, clinical trials and authorized products? |
| **Q4** | Which incidents or failures have been recorded? |

## Intended audience

| Audience | What they want to know |
| --- | --- |
| **Primary:** health students and professionals | Which AI tools are really authorized in their field, and how solid is the evidence behind them? |
| **Secondary:** general public interested in health | What does “AI in medicine” actually mean today, beyond the headlines? |

## Website structure

| Section | Content |
| --- | --- |
| **Home** | Title, subtitle and a 3D sphere (three.js) with one point per authorized device, coloured by specialty |
| **Inspiration** | Why we chose this topic |
| **Behind the hype** | Key figures, definition of the FDA and sources |
| **Our questions** | Main question and the four supporting questions |
| **Comparing where AI is authorized** | Six interactive charts (see below) |
| **Who we are telling this story to** | Intended audience |
| **Data at hand** | Datasets and known limits |

## Charts

<p align="justify">
Every chart is drawn with D3.js, animates when it scrolls into view, shows a tooltip on hover and includes a data table for accessibility (“Show the data”).
</p>

| Chart | Type | What it shows | Question |
| --- | --- | --- | :---: |
| Every dot is one authorized device | Radial dot chart (extra) | One dot per device, by year and day of decision, with filters by specialty | Q1, Q2 |
| Authorizations have almost tripled since 2020 | Bar chart | Number of authorizations per year, from 2012 to 2026 | Q1 |
| Radiology grows faster than everything else combined | Grouped bar chart | Top five specialties in 2023, 2024 and 2025 | Q1, Q2 |
| A decade of AI, specialty by specialty | Heatmap | Authorizations by specialty and year, 2016 to 2026 | Q1, Q2 |
| Almost every device takes the shortest route | 100% stacked bar chart | Share of the 510(k), De Novo and PMA pathways by specialty | Q3 |
| Out of 100 AI devices, 76 are in radiology | Waffle chart | Distribution of 100 devices across specialties | Q2 |

## Data

| Dataset | What it contributes | Questions |
| --- | --- | :---: |
| [FDA: AI-Enabled Medical Devices list](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices) | 1,524 devices with decision date, specialty, company and clearance pathway (snapshot of 29 June 2026) | Q1, Q2 |
| [openFDA: 510(k) API](https://open.fda.gov/apis/device/510k) | Applicant country and city, joined by submission number | Q1, Q2 |
| [ClinicalTrials.gov: API v2](https://clinicaltrials.gov/data-api/api) | AI and machine-learning trials by year, phase, condition and country | Q3 |
| [PubMed: E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Number of “AI + specialty” publications per year | Q3 |
| [openFDA: device recalls and MAUDE](https://open.fda.gov/apis/device) | Recalls and adverse-event reports for AI devices | Q4 |
| [AI Incident Database](https://incidentdatabase.ai) | Documented AI failures, filterable for healthcare | Q4 |

<p align="justify">
The FDA list used in the charts comes from the versioned release of Wang et al. (2026), <em>Clinical-function annotations for 1524 US artificial intelligence medical-device authorizations</em>, v1.3.0, licensed CC BY 4.0: <a href="https://github.com/wang177777/fda-ai-clinical-function-annotations">github.com/wang177777/fda-ai-clinical-function-annotations</a>.
</p>

### Known limits

- The FDA list covers the United States only and is updated retroactively, so yearly counts differ between sources.
- The June 2026 snapshot contains decisions up to 30 March 2026, so 2026 is a partial year.
- Europe has no complete public equivalent yet, as EUDAMED is still incomplete.
- An authorization does not tell us whether a device is actually used in hospitals.
- MAUDE under-reports AI-specific failures, so we cross-check it with recalls and incident reports.

## Built with

| Tool | Use |
| --- | --- |
| HTML, CSS and JavaScript | Static single-page website, hosted on GitHub Pages |
| [D3.js](https://d3js.org) v7 | Interactive charts |
| [three.js](https://threejs.org) | 3D sphere on the homepage |
| Python and pandas | Data preparation |
| Montserrat (Google Fonts) | Typography |

## Repository structure

```
ai-impact-on-medicine/
├── index.html                  Single page of the website
├── css/style.css               Styles (Montserrat, sky-blue palette, responsive layout)
├── js/main.js                  Mobile menu, scroll animations and animated key figures
├── js/charts.js                The six D3 charts (animations, tooltips, data tables)
├── js/hero3d.js                three.js sphere of the homepage
├── assets/polygon-logo.svg     Animated Polygon logo
├── scripts/prepare_data.py     Turns the raw FDA list into the chart data
└── data/
    ├── raw/fda_ai_devices_2026-06-29.csv   Raw FDA list (1,524 devices)
    └── chart-data.js                      Chart data generated by the Python script
```

## Run locally

Open `index.html` in a browser, or start a small local server:

```sh
python -m http.server 8000
```

then go to <http://localhost:8000>.

To regenerate the chart data from the raw FDA list:

```sh
pip install pandas
python scripts/prepare_data.py
```

---

<p align="center">
  <sub>Group Polygon · Data Visualization course · Università degli Studi di Genova · 2026/27</sub>
</p>
