# Production Deployment Guide: Spotify Discovery Feedback Dashboard

This document provides a step-by-step procedure to deploy the Phase 1 Review Discovery Engine & Dashboard to a live production environment.

---

## 🚀 Option A: Deploy on Streamlit Community Cloud (Recommended & Free)
Streamlit Community Cloud is the easiest, zero-cost method to deploy and host Streamlit apps directly from your GitHub repository.

### Step 1: Initialize Git and Push to GitHub
1.  Create a new repository on [GitHub](https://github.com) (e.g., `spotify-discovery-engine`).
2.  In your local workspace terminal, initialize git and push the code:
    ```bash
    git init
    git add .
    git commit -m "feat: initial release of spotify review discovery engine"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/spotify-discovery-engine.git
    git push -u origin main
    ```
    > [!IMPORTANT]
    > **Do NOT commit your `.env` file** to GitHub. Make sure `.env` is listed in your `.gitignore`.

### Step 2: Sign Up and Connect to Streamlit
1.  Go to [share.streamlit.io](https://share.streamlit.io).
2.  Log in using your GitHub account and authorize Streamlit.

### Step 3: Deploy the Dashboard
1.  On the Streamlit Cloud dashboard, click the **"New app"** button.
2.  Fill in the deployment details:
    *   **Repository:** Select your `spotify-discovery-engine` repository.
    *   **Branch:** `main`
    *   **Main file path:** `review_engine/src/dashboard.py` (This is the entry point file).
3.  Click **"Deploy!"**

### Step 4: Configure Production API Keys & Secrets
Streamlit Cloud has a built-in secrets manager so you don't commit credentials to Git.
1.  On your deployed app page, click the **"Settings"** icon in the bottom-right corner.
2.  Select **"Secrets"**.
3.  Paste your environment variables matching this format:
    ```toml
    LLM_PROVIDER = "openai"
    OPENAI_API_KEY = "sk-proj-..."
    OPENAI_MODEL = "gpt-4o-mini"
    
    # Optional Reddit credentials
    REDDIT_CLIENT_ID = "..."
    REDDIT_CLIENT_SECRET = "..."
    REDDIT_USER_AGENT = "spotify-pm-project:v1.0"
    ```
4.  Click **Save**. The app will automatically reboot and load the secret keys securely.

---

## 🐳 Option B: Deploy on Render.com (Web Service via Docker)
Render is a cloud hosting platform that supports hosting Docker containers for free. This is highly useful if you want to deploy to general cloud platforms.

### Step 1: Push Code to GitHub
Ensure your repository is pushed to GitHub (following **Step 1** from Option A above). Render will automatically detect the [Dockerfile](file:///Users/satyampandey/NL_Graduation_Project/review_engine/Dockerfile) inside your repository.

### Step 2: Connect GitHub to Render
1.  Create a free account on [Render.com](https://render.com).
2.  On the dashboard, click **"New +"** and select **"Web Service"**.
3.  Connect your GitHub account and select your `spotify-discovery-engine` repository.

### Step 3: Configure Deployment Settings
1.  Give your service a name (e.g. `spotify-discovery-dashboard`).
2.  **Region:** Choose a region close to your target users (e.g., Oregon or Frankfurt).
3.  **Branch:** `main`
4.  **Runtime:** Select **"Docker"** (Do not choose Python. The Docker runtime is much cleaner and utilizes the predefined packages inside the container).
5.  **Build Filter / Root Directory:** Leave blank (Render will build from the root directory and find `review_engine/Dockerfile` automatically).
6.  **Instance Type:** Select the **Free Tier**.

### Step 4: Add Environment Variables
Before deploying, configure your credentials:
1.  Scroll down to the **"Environment Variables"** section.
2.  Add the following key-value pairs:
    *   `LLM_PROVIDER`: `openai`
    *   `OPENAI_API_KEY`: `your-live-openai-key`
    *   `OPENAI_MODEL`: `gpt-4o-mini`
    *   `PORT`: `8501` (Render automatically routes web traffic to the exposed port).

### Step 5: Deploy
1.  Click **"Deploy Web Service"**.
2.  Render will pull the code, build the Docker container image, and start the Streamlit server.
3.  Once the logs show `Streamlit Server started on port 8501`, your dashboard is live at the public URL provided at the top of the Render page (e.g., `https://spotify-discovery-dashboard.onrender.com`).

---

## 💾 Production Data Persistence Note
Both Streamlit Cloud and Render Free Tier utilize **ephemeral filesystems**. This means that if you click "Sync Feedback Data" inside the live dashboard, the newly scraped data will be saved locally on the container disk, but **it will disappear next time the server restarts or redeploys**.

For a graduation project/demonstration, this is perfectly fine. The dashboard will load the pre-scraped data from your Git repository by default. 

If you want **permanent live updates** that persist forever:
1.  Update the data save functions in [scrapers.py](file:///Users/satyampandey/NL_Graduation_Project/review_engine/src/scrapers.py) to write to a free cloud database (such as MongoDB Atlas or Supabase PostgreSQL) instead of local JSON files.
2.  Configure the dashboard to read from that database.
