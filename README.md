# Georges-Patrick Brou — Portfolio

Real, deployable portfolio showing match analysis (Wyscout), NFL performance analytics, and the
tools built to produce both. Built for linking directly from a CV.

## Run locally

```bash
pip install -r requirements.txt
streamlit run portfolio_app/app.py
```

## Deploy for a public link

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub (same account this
   repo is on).
2. Click **New app**, pick this repo, branch `main`, and set the main file path to
   `portfolio_app/app.py`.
3. Click **Deploy**. Streamlit Cloud gives a permanent public URL like
   `https://gp-portfolio.streamlit.app`.

Every push to `main` redeploys automatically — no need to repeat the steps above after the first time.

## Adding content

- **Video clips**: drop `.mp4`/`.mov`/`.webm` files into `portfolio_app/assets/videos/`, commit and
  push. They show up in the Match & Set-Piece Analysis section automatically.
- **CV**: add a PDF at `portfolio_app/assets/CV.pdf` and a download button appears in the header
  automatically.
- **New carousel/project images**: drop images into `portfolio_app/assets/` and reference them in
  `portfolio_app/app.py`.

## Structure

```
portfolio_app/app.py          the portfolio itself
projects/nfl-analytics/       full NFL analytics pipeline + Streamlit dashboards (real source)
projects/job-application-tailor/   the sports job application tailor tool (real source)
```
