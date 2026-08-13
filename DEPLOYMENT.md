# Deployment Guide

## 1. Local verification

Before publishing, run:

```bash
python -m pytest -q
streamlit run app.py
```

Use **Included sample CSV** in the interface to confirm that the app works even if the public market-data provider is temporarily unavailable.

## 2. Publish the source to GitHub

1. Create a new GitHub repository named `A-Share-OTC-Option-Pricer`.
2. Keep the repository public if the interviewers should view it without access permissions; otherwise grant them collaborator access.
3. From this project directory, run:

   ```bash
   git init
   git add .
   git commit -m "Initial interview submission"
   git branch -M main
   git remote add origin https://github.com/<YOUR-USERNAME>/A-Share-OTC-Option-Pricer.git
   git push -u origin main
   ```

4. Confirm that the repository contains `app.py`, `requirements.txt`, `README.md`, `src/`, `tests/`, `data/sample_prices.csv`, and `DEPLOYMENT.md`.

Never commit passwords, API keys, `.env` files, virtual environments, or cache folders. The supplied `.gitignore` excludes these common non-deliverable files.

## 3. Deploy with Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Select **Create app** and choose the GitHub repository and `main` branch.
3. Set the entry point to `app.py`.
4. Deploy. Streamlit installs dependencies from `requirements.txt`.
5. Open the generated `https://<app-name>.streamlit.app` link and test the **Included sample CSV** flow.
6. Add the live-demo URL to the GitHub repository description and the interview submission email.

## 4. Suggested submission package

- **Live demo:** your Streamlit URL
- **Source code:** your GitHub repository URL
- **Methodology:** `README.md` in the repository
- **Backup:** the clean ZIP archive delivered alongside the source

