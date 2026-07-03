# Shop App React Native Deployment Guide

This project is an inventory management shop app with:

- Mobile app: React Native with Expo
- API client: shared `fetch()` service in `mobile/src/services/api.ts`
- Backend: FastAPI
- Database: Supabase Postgres
- Backend hosting: Render
- Mobile build: Expo / EAS APK

## Project Structure

```text
shop_app/
  backend/              FastAPI server, database models, API routes
  mobile/               Expo React Native app
  web/                  Web app files, if used later
  Electronic_Shop_final/ CSV source/reference files
```

Important mobile files:

- `mobile/App.tsx`: app root, Redux provider, navigation provider
- `mobile/index.ts`: Expo entry file
- `mobile/app.json`: Expo build config, app icon, Android package
- `mobile/.env`: mobile environment variables
- `mobile/src/config.ts`: API URL config
- `mobile/src/services/api.ts`: reusable fetch API service
- `mobile/src/screens/*`: app screens

Important backend files:

- `backend/main.py`: FastAPI app and router registration
- `backend/database.py`: database connection
- `backend/models.py`: SQLAlchemy database tables
- `backend/schemas.py`: API request/response schemas
- `backend/routers/*.py`: API routes

## How The App Connects

The mobile app does not call Supabase directly. It calls your FastAPI backend on Render.

```text
Expo app -> fetch API service -> Render FastAPI -> Supabase Postgres
```

This is a good production pattern because:

- Database credentials stay on the backend.
- Authentication and business logic stay centralized.
- Mobile screens do not duplicate networking code.
- Backend rules can be changed without rebuilding every screen.

## Environment Variables

Mobile uses:

```text
EXPO_PUBLIC_API_URL=https://shop-app-qs90.onrender.com
```

This is loaded from `mobile/.env`.

The app reads it in:

```ts
mobile/src/config.ts
```

Expo only exposes variables to the mobile app if they start with `EXPO_PUBLIC_`.

## API Service Pattern

All mobile screens should call the shared API service:

```ts
import { api } from '../services/api';

const inventory = await api.getInventory(token);
await api.createInventory(token, payload);
```

Avoid calling `fetch()` directly inside every screen unless there is a special reason. Also avoid mixing axios and fetch in the same app, because it creates different error handling and different base URL behavior.

The shared service handles:

- Base URL
- JSON headers
- Bearer token auth
- Parsing JSON responses
- Backend error messages
- 401 logout/session reset

## Authentication Flow

Login screen calls:

```text
POST /auth/token
```

Signup screen calls:

```text
POST /auth/signup
```

After login/signup, the token is stored in Redux:

```text
mobile/src/store/authSlice.ts
```

Protected screens send:

```text
Authorization: Bearer <token>
```

## Inventory Logic

Inventory now works like this:

- Item + brand is the unique stock identity.
- Adding the same item and same brand again merges into the existing stock.
- Example: 10 Panasonic bulbs + 10 more Panasonic bulbs = one Panasonic bulb record with 20 purchased quantity.
- The user enters only `Quantity`, not `Remaining Quantity`.
- Available stock is calculated internally.
- Sales reduce available stock.
- Deleting a sale restores available stock.

The database still keeps `remaining_quantity` internally because the backend needs it to prevent overselling. The mobile UI calls this `Available` instead of asking the user to manually enter it.

## Backend Deployment On Render

Typical Render setup:

1. Create a new Web Service.
2. Connect your GitHub repo.
3. Root directory:

```text
backend
```

4. Build command:

```bash
pip install -r requirements.txt
```

5. Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

6. Add environment variables for database connection and auth secret.

After deployment, test:

```text
https://your-render-service.onrender.com/health
```

Expected response:

```json
{"status":"ok"}
```

## Supabase Database Notes

Supabase gives you a hosted Postgres database. Your backend should use the Supabase Postgres connection string.

Keep these values only on the backend:

- Database URL
- Supabase password
- JWT secret
- Any service role keys

Do not put private database credentials in Expo `.env`, because mobile app environment variables are bundled into the app.

## Running Locally

Backend:

```bash
cd backend
uvicorn main:app --reload
```

Mobile:

```bash
cd mobile
npm install
npm start
```

If testing against local backend on a physical phone, your phone cannot use `localhost` for your laptop. Use your laptop LAN IP:

```text
EXPO_PUBLIC_API_URL=http://192.168.x.x:8000
```

For production APK builds, use the Render URL.

## Expo APK Build

Install EAS CLI:

```bash
npm install -g eas-cli
```

Login:

```bash
eas login
```

Check config:

```bash
cd mobile
cat eas.json
```

Build Android APK:

```bash
eas build -p android --profile preview
```

If your `eas.json` profile builds an AAB instead of APK, set the Android build type:

```json
{
  "build": {
    "preview": {
      "android": {
        "buildType": "apk"
      }
    }
  }
}
```

## App Icon

Expo uses these files:

- `mobile/assets/icon.png`
- `mobile/assets/adaptive-icon.png`
- `mobile/assets/splash-icon.png`
- `mobile/assets/favicon.png`

They are referenced in:

```text
mobile/app.json
```

After changing icons, rebuild the APK. Installed app icons do not reliably update from only refreshing Expo Go.

## Useful Verification Commands

TypeScript check:

```bash
cd mobile
npx tsc --noEmit
```

Search for old networking code:

```bash
rg "axios|fetch\\(" mobile/src
```

Backend health:

```bash
curl https://shop-app-qs90.onrender.com/health
```

## Common Problems

### Login works, other screens do not load data

Check that every screen uses:

```ts
api.someEndpoint(token)
```

Also confirm the token exists:

```ts
const token = useSelector((state: RootState) => state.auth.token);
```

### App works in browser but not on phone

If using local backend, replace `localhost` with your laptop IP. If using Render, confirm the Render service is awake and `/health` works.

### Render is slow on first request

Free Render services may sleep. The first request can take time. Open `/health` once before testing the mobile app.

### APK still shows old icon

Uninstall the old app from the phone, rebuild the APK, and install the new APK. Android may cache app icons.

### Inventory duplicates appear

The backend merge rule is based on same item name and same brand name, case-insensitive. `Bulb + Panasonic` and `bulb + panasonic` merge, but `Bulb + Philips` is a different stock record.

## Recommended Workflow

1. Make backend change.
2. Test backend locally.
3. Deploy backend to Render.
4. Test Render `/health`.
5. Update mobile `.env` if backend URL changed.
6. Run `npx tsc --noEmit`.
7. Test in Expo Go.
8. Build APK with EAS.

This keeps the app predictable and avoids mixing local and production URLs by accident.
