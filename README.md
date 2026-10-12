# Georges-Patrick Brou — Portfolio

Three things: video breakdown (Wyscout match/set-piece analysis), the NFL carousel deck, and the
real analysis repos behind both on GitHub. Built for linking directly from a CV.

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
  push. They show up in the Video Breakdown section automatically.
- **Carousel slides**: drop image files into `portfolio_app/assets/carousel/`, commit and push. They
  show up in the Carousel section automatically, in alphabetical order, with prev/next navigation.

## Structure

```
portfolio_app/app.py          the portfolio itself
projects/nfl-analytics/       full NFL analytics pipeline + Streamlit dashboards (real source)
```
