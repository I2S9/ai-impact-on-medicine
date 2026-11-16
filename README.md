# AI at the Doctor's — Where is AI actually entering medicine?

Interactive data visualization website for the Data Visualization course, Università di Genova (2026/27).
Part of the course theme **Mapping the Impact of AI through Data**.

**Live site:** https://i2s9.github.io/mapping-the-impact-of-ai/

**Group Polygon:** Inès Gbadamassi, Maryse Goeh-Akue, James Fosting Tahku, Illia

## Main question

Despite the narrative that AI "will revolutionize medicine", in which medical fields is AI actually authorized and used?

### Supporting questions

1. How has the number of authorized AI medical devices evolved?
2. Why does radiology dominate?
3. How large is the gap between published research, clinical trials and authorized products?
4. Which incidents or failures have been recorded?

## Intended audience

- **Health students and professionals:** which AI tools are really authorized in their field?
- **General public interested in health:** what does "AI in medicine" actually mean today?

## Datasets

| Dataset | What it contributes | Questions |
| --- | --- | --- |
| [FDA — AI-Enabled Medical Devices list](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices) | ~1,600 devices with decision date, specialty, company and clearance pathway | Q1, Q2 |
| [openFDA — 510(k) API](https://open.fda.gov/apis/device/510k) | Applicant country and city, joined by submission number | Q1, Q2 |
| [ClinicalTrials.gov — API v2](https://clinicaltrials.gov/data-api/api) | AI and machine-learning trials by year, phase, condition and country | Q3 |
| [PubMed — E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Number of "AI + specialty" publications per year | Q3 |
| [openFDA — device recalls and MAUDE](https://open.fda.gov/apis/device) | Recalls and adverse-event reports for AI devices | Q4 |
| [AI Incident Database](https://incidentdatabase.ai) | Documented AI failures, filterable for healthcare | Q4 |

## Planned visualizations

- **Stacked area chart:** authorizations by specialty over time (Q1)
- **Treemap:** radiology's share of all AI devices (Q2)
- **Network graph:** companies linked to the specialties they build for (Q2)
- **World map:** where devices are made and where AI trials take place (Q1, Q3)
- **Funnel:** publications → clinical trials → authorized devices (Q3)
- **Timeline:** recalls and incidents after authorization (Q4)

## Known data limits

- The FDA list covers the United States only and is updated retroactively, so yearly counts differ between sources.
- Europe has no complete public equivalent yet (EUDAMED is still incomplete).
- An authorization does not tell us whether a device is actually used in hospitals.
- MAUDE under-reports AI-specific failures; we cross-check with recalls and incident reports.

## Repository structure

- `index.html` — main page
- `css/style.css` — all styles (Arial everywhere, sky-blue palette)
- `data/` — cleaned datasets used by the visualizations
