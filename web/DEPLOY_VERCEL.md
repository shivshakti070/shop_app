Vercel Deployment Guide

This document explains how to deploy the `web/` Next.js app to Vercel and wire it to Supabase.

1) Push code to GitHub

If you haven't already pushed the repo to GitHub, run:

```bash
cd /Users/shivshakti/Desktop/shop_app
git add .
git commit -m "web: add next + supabase integration and vercel config"
# create repo on GitHub and set remote url
git remote add origin https://github.com/YOUR_USER/shop-app.git
git branch -M main
git push -u origin main
```

2) Create project on Vercel

- Go to https://vercel.com and sign in with GitHub.
- Click "New Project" → Import Git Repository → select `shop-app`.
- When Vercel asks for the root directory, set it to `web` (so Vercel builds the Next app inside `web/`).
- Ensure the framework preset is `Next.js`.

3) Add Environment Variables (Vercel dashboard)

In your Vercel project → Settings → Environment Variables add the following (for Production and Preview):

- `NEXT_PUBLIC_SUPABASE_URL` = `https://slsidvaepcldfzjgfifn.supabase.co`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` = `sb_publishable_6zuL8WGoiOyGvsvsUHe9OA_zAZhCpg1`

Save and Redeploy the project.

4) Build & Test

- After deployment completes, open the provided Vercel URL.
- Test the page that lists `todos` (the server-side Supabase call).
- If the `todos` table is empty, create a record in Supabase Table Editor to confirm data shows up.

5) Notes & Troubleshooting

- If the app returns `401` or `403` on server-side requests, double-check the publishable key and table RLS/policies in Supabase.
- For private server-side actions, use service_role key on secure server endpoints — do NOT expose the service_role key to the client.
- To preview changes, push a branch and Vercel will create a preview deployment.

6) Next steps

- If you want Vercel to refresh user sessions with Supabase cookies, add middleware and enable Vercel Edge functions as needed.
- Once the web app is live, deploy the backend (Railway) and update `mobile/src/config.ts` with the backend production URL so mobile users can use the central backend.
