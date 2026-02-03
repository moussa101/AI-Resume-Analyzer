# Deployment Guide

This guide explains how to make your Skillora app accessible to others on the internet, 24/7.

## Option 1: Render (Best Free/Cheap Option)

[Render](https://render.com) offers a comprehensive free tier that can host your Docker containers and PostgreSQL database.

### 1. Unified Dockerfile (Recommended for Free Tier)
To save on costs and complexity, it's often easiest to deploy the **ML Service** (which contains the core logic) and the **Frontend** separately, or orchestrate them. However, since this is a multi-service app (Frontend, Backend, ML, DB), the "Blueprints" feature is best.

**Note on Free Tier Limits:**
*   Render Free Tier spins down web services after inactivity (starts up again when visited).
*   Free PostgreSQL expires after 30 days (good for demos).

#### Step-by-Step for Render:

1.  **Push your code to GitHub**: Make sure your project is in a public or private GitHub repository.
2.  **Sign up for Render**: Go to [dashboard.render.com](https://dashboard.render.com) and log in with GitHub.
3.  **Create a Blueprint**:
    *   Click "New +" -> "Blueprint".
    *   Connect your GitHub repository.
    *   Render will look for a `render.yaml` file (we will create this below).

### 2. Create `render.yaml`
Add this file to the root of your project to tell Render how to build everything.

```yaml
services:
  # 1. Database
  - type: pserv
    name: resume-db
    env: docker
    plan: free
    ipAllowList: [] # Allow all
    envVars:
      - key: POSTGRES_USER
        value: postgres
      - key: POSTGRES_DB
        value: resume_analyzer

  # 2. ML Service (Python)
  - type: web
    name: ml-service
    env: docker
    dockerContext: ./ml_service
    dockerfilePath: ./ml_service/Dockerfile
    plan: free
    envVars:
      - key: PORT
        value: 8000
      - key: GITHUB_TOKEN
        sync: false # You will enter this in Render dashboard

  # 3. Frontend (Next.js)
  - type: web
    name: frontend-client
    env: docker
    dockerContext: .
    dockerfilePath: ./Dockerfile.frontend # You might need a specific frontend Dockerfile
    plan: free
    envVars:
      - key: NEXT_PUBLIC_API_URL
        fromService: ml-service
        property: host
```

## Option 2: Local Sharing (ngrok) - Truly Free & easiest

If you just want to show a friend **right now** and don't care if it goes offline when you close your laptop, use **ngrok**. It creates a secure tunnel to your localhost.

1.  **Install ngrok**: [Download here](https://ngrok.com/download)
2.  **Start your app locally**: Make sure `docker compose up` is running.
3.  **Expose your frontend**:
    ```bash
    ngrok http 3001
    ```
4.  **Share the Link**: ngrok will give you a URL like `https://a1b2-c3d4.ngrok-free.app`. Send this to your friend!
    *   *Note: You might need to configure your frontend to talk to the backend via public URLs if they are separate, but for a simple demo, this often works for viewing the UI.*

## Summary

| Feature | Local + ngrok | Render Free Tier |
| :--- | :--- | :--- |
| **Cost** | Free | Free (limited) |
| **Uptime** | Only when laptop is on | 24/7 (sleeps on inactivity) |
| **Setup** | Exam | Medium |
| **Best For** | Showing a friend for 10 mins | Permanent demo link |
