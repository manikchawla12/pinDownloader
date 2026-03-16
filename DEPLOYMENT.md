# Deployment Instructions for Pinterest Video Downloader

## Backend (Render)
1. Push the `backend` folder to a GitHub repository.
2. Sign up / Log in to [Render](https://render.com).
3. Click "New" > "Web Service".
4. Connect your GitHub repository and select the `backend` folder.
5. Use the settings outlined in `backend/render.yaml`:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Once deployed, note the generated URL (e.g., `https://pinterest-downloader-api.onrender.com`).

## Frontend (Vercel)
1. Before deploying, open `frontend/assets/js/app.js` and replace the `API_BASE_URL` constant with your exact Render URL from the previous step.
2. Push the `frontend` folder to a GitHub repository or subfolder.
3. Sign up / Log in to [Vercel](https://vercel.com).
4. Click "Add New" > "Project".
5. Import your GitHub repository and select the `frontend` folder as the Root Directory.
6. The framework preset should be identified as "Other".
7. Vercel commands:
   - **Build Command:** `npm run build:css`
   - **Install Command:** `npm install`
   - **Output Directory:** `.` or leave default depending on how Vercel detects static files.
8. Click "Deploy". Ensure you configure any custom domains under the Vercel project settings to match the AdSense approvals.
9. Your SEO-optimized, super-fast Pinterest Video Downloader is now live!
