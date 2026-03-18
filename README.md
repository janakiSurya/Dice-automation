# Dice Job Application Automation

This repo automates applying to jobs on Dice.com using Selenium.

High-level flow:
1. Search for jobs by keyword/location
2. Open postings and click the **Apply** entry point
3. Use **Google Gemini** to answer application questions using your profile in `src/data.yaml`
4. Click through the application wizard (Next/Submit) until final submit

## Important Notes

- This is an automation tool. Use it responsibly and make sure it complies with Dice’s terms and your local policies.
- Dice’s UI changes can break selectors. If it stops applying, check `application.log` and we can update locators.

## Prerequisites

- Python 3.9+
- Google Chrome
- A matching `chromedriver` available on your system `PATH` (Selenium uses the system driver configuration)

## Setup

1) Create a venv and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Configure secrets via `.env`

```bash
cp .env.example .env
```

Edit `.env`:
- `GEMINI_API_KEY`: your Google Gemini API key
- `DICE_USERNAME`: Dice login email/username
- `DICE_PASSWORD`: Dice password

3) Configure what to apply for

Edit `src/config.yaml`:

```yaml
search_params:
  keyword: "Gen AI"
  location: "United States"
  days_posted: 1
```

`days_posted` is mapped internally:
- `1` => `ONE`
- `3` => `THREE`
- `7` => `SEVEN`

4) Configure your profile answers

Copy `src/data.example.yaml` to `src/data.yaml` and fill in your details:

```bash
cp src/data.example.yaml src/data.yaml
```

Then edit `src/data.yaml` with your personal information, education, experience, skills, and preferences. The bot uses this data to answer the questions on the Dice application form.

## Run

```bash
python3 src/app.py
```

Logs:
- `application.log`

## Troubleshooting

- No jobs found: job-card selector may need updating.
- Apply clicked but no fields filled: textarea/radio selectors may need adjustment.
- Submit not clicked: Next/Submit button selectors may need updates; check the button HTML and update `src/job_search.py`.

