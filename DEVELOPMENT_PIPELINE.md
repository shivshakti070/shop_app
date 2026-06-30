# Development Pipeline & Workflow

This document outlines the complete pipeline for developing, testing, and deploying new code to the Shop App (backend + mobile).

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Development Environment                    │
│  (Local Machine: Backend + Mobile Emulator/Device)          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   Git Repository (GitHub)   │
        │  (main + feature branches)  │
        └────────────┬────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   ┌─────────────┐          ┌──────────────┐
   │  Staging    │          │  Production  │
   │   Server    │          │    Server    │
   │ (test URLs) │          │ (public URLs)│
   └─────────────┘          └──────────────┘
        │                         │
        ▼                         ▼
   [Staging DB]           [Production DB]
   (Postgres)             (Postgres)
```

---

## 2. Development Stages

### Stage 1: Local Development

**What happens here:**
- Backend: `backend/main.py`, routers, models, schemas are developed locally.
- Mobile: `mobile/src/screens/`, store logic, navigation are developed.
- Database: Local SQLite (`backend/sql_app.db`) or local Postgres.
- Testing: Unit tests, manual testing on emulator/device.

**Key files to modify:**
- Backend: `backend/routers/*.py`, `backend/models.py`, `backend/schemas.py`, `backend/auth.py`
- Mobile: `mobile/src/screens/*.tsx`, `mobile/src/store/*.ts`

**Commands to run:**
```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Mobile (in another terminal)
cd mobile
npm install
npx expo start -c
# Or: npx expo start --lan (for device testing)
```

**Verification checklist:**
- ✅ Backend starts without errors (`/health` endpoint responds)
- ✅ Mobile app loads in Expo Go
- ✅ API calls (login, inventory, sales) work locally
- ✅ New feature flows are testable end-to-end

---

### Stage 2: Code Review & Branch Protection

**What happens here:**
- Create a feature branch: `git checkout -b feature/my-feature`
- Push to GitHub and create a Pull Request (PR)
- Code review by team lead or peer
- Automated checks run (linting, basic tests if available)

**Branch naming convention:**
```
feature/add-inventory-dropdown
feature/fix-network-error
feature/add-hindi-labels
bugfix/duplicate-sale-check
```

**PR Checklist:**
- ✅ Branch is up-to-date with `main`
- ✅ New code follows existing style (Python PEP8, TypeScript/React conventions)
- ✅ No console.error or unhandled promises left behind
- ✅ Database migrations (if any) are documented
- ✅ Mobile screenshots/videos attached (if UI changes)
- ✅ Test evidence provided (local test results, logs)

---

### Stage 3: Automated Testing (CI/CD Pipeline)

**What happens here:**
- GitHub Actions (or similar CI tool) runs automated checks on PR
- Linting, type checking, unit tests run
- Docker build is tested to ensure Dockerfile works
- Database migrations are validated

**Example GitHub Actions workflow** (`.github/workflows/ci.yml`):
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Lint with flake8
        run: |
          flake8 backend --count --select=E9,F63,F7,F82 --show-source --statistics
      - name: Type check with mypy (optional)
        run: |
          pip install mypy
          mypy backend || true
      - name: Build Docker image
        run: |
          docker build -t shop-app-backend:latest backend/
```

**Automated checks:**
- ✅ Python syntax & imports valid
- ✅ Docker image builds without errors
- ✅ Database schema migrations are valid
- ✅ API endpoints respond (basic smoke test)

---

### Stage 4: Staging Deployment

**What happens here:**
- After PR approval, merge feature branch into `develop` or a `staging` branch
- CI/CD automatically deploys to staging server
- Staging uses a separate Postgres database (copy of production data or fresh schema)
- QA and team can test on a public URL (not production)

**Staging environment setup:**
```
Staging Server: https://staging.shop-app.com (or Railway staging URL)
Database: Supabase Postgres (staging project)
Environment Variables:
  DATABASE_URL=postgres://staging-db-url
  SECRET_KEY=staging-secret-key-long-random-string
  ENVIRONMENT=staging
```

**Staging deployment checklist:**
- ✅ Docker image pushed to staging server
- ✅ Database migrations applied
- ✅ Environment variables loaded
- ✅ `/health` endpoint responds
- ✅ Mobile app can connect (update config.ts API_URL to staging)
- ✅ Full manual test flow:
  - Create account
  - Add inventory
  - Add sales
  - Add expenses
  - View summary
- ✅ No error logs in backend console

**Commands (manual staging test):**
```bash
# Update mobile to point to staging
# In mobile/src/config.ts:
export const API_URL = "https://staging.shop-app.com";

# Or override at runtime:
global.__API_HOST__ = "staging.shop-app.com";

# Then test in Expo Go
```

---

### Stage 5: Production Deployment

**What happens here:**
- After successful staging validation, merge `develop` → `main`
- CI/CD automatically builds and deploys to production server
- Production uses the main Postgres database
- Public users can access the app

**Production environment setup:**
```
Production Server: https://shop-app.com (or Railway production URL)
Database: Supabase Postgres (production project)
Environment Variables:
  DATABASE_URL=postgres://production-db-url
  SECRET_KEY=production-secret-key-long-random-string
  ENVIRONMENT=production
  ACCESS_TOKEN_EXPIRE_MINUTES=120
```

**Production deployment checklist:**
- ✅ All staging tests passed
- ✅ Release notes prepared
- ✅ Backup of production database taken
- ✅ Rollback plan ready (see Stage 6)
- ✅ Docker image deployed
- ✅ Database migrations applied
- ✅ `/health` endpoint responds
- ✅ Sample user account created for testing
- ✅ Monitoring alerts configured
- ✅ Users notified of deployment (if major feature)

**Production deployment command (example with Railway):**
```bash
# After PR merged to main, Railway auto-deploys
# Or manual trigger:
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# Railway CI triggers and deploys to production
```

---

### Stage 6: Monitoring & Rollback

**What happens here:**
- Monitor production logs, error rates, and user feedback
- If critical bugs are found, quickly rollback to previous version
- If minor issues, create hotfix branch and redeploy

**Monitoring checklist:**
- ✅ Backend logs (Uvicorn startup, request logs)
- ✅ Database health (connection pool, query performance)
- ✅ User error reports (Metro logs, app crashes)
- ✅ API response times (especially `/daily-sales`, `/inventory`)

**Rollback procedure:**
```bash
# If production deployment has critical bugs:
# 1. Identify last stable commit/tag
git tag -a v1.0.0 -m "Last stable"

# 2. Revert to that version
git revert <commit-hash>
git push origin main

# 3. CI/CD auto-redeploys production from reverted code
# 4. Verify /health endpoint and critical flows
curl https://shop-app.com/health

# 5. Once stable, create a hotfix branch
git checkout -b hotfix/critical-bug main
# Fix the bug, test locally, PR, merge to main, deploy
```

---

## 3. Feature Development Workflow (Step-by-step)

### Example: Adding a new feature "Customer Credit Ledger"

#### Step 1: Create feature branch locally
```bash
git checkout -b feature/customer-credit-ledger
```

#### Step 2: Develop on backend
```python
# backend/models.py - add new model
class CustomerCredit(Base):
    __tablename__ = "customer_credits"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, index=True)
    total_credit = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

# backend/schemas.py - add schema
class CustomerCreditOut(BaseModel):
    id: int
    customer_name: str
    total_credit: float
    owner_id: int
    class Config:
        from_attributes = True

# backend/routers/customer_credit.py - add router
from fastapi import APIRouter
router = APIRouter(prefix="/customer-credit", tags=["customer_credit"])

@router.get("/", response_model=List[CustomerCreditOut])
def get_customer_credits(current_user = Depends(get_current_user), db = Depends(get_db)):
    return db.query(models.CustomerCredit).filter(models.CustomerCredit.owner_id == current_user.id).all()

# backend/main.py - include router
app.include_router(customer_credit.router)
```

#### Step 3: Test locally
```bash
# Backend
uvicorn main:app --reload

# Test endpoint
curl -H "Authorization: Bearer <token>" http://localhost:8000/customer-credit/
```

#### Step 4: Develop on mobile
```typescript
// mobile/src/screens/CustomerCreditScreen.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CustomerCreditScreen: React.FC<Props> = ({ navigation }) => {
  const [credits, setCredits] = useState([]);
  
  useEffect(() => {
    fetchCredits();
  }, []);
  
  const fetchCredits = async () => {
    try {
      const base = axios.defaults.baseURL || API_URL;
      const response = await axios.get(`${base.replace(/\/$/, '')}/customer-credit/`);
      setCredits(response.data);
    } catch (error) {
      console.error('Failed to fetch credits', error);
    }
  };
  
  return (
    <View style={styles.container}>
      <Text>Customer Credit Ledger (ग्राहक क्रेडिट खाता)</Text>
      {/* Render credits list */}
    </View>
  );
};
export default CustomerCreditScreen;

// mobile/src/navigation/AppNavigator.tsx - add route
<Stack.Screen name="CustomerCredit" component={CustomerCreditScreen} />

// mobile/src/screens/HomeScreen.tsx - add card
<TouchableOpacity onPress={() => navigation.navigate('CustomerCredit')}>
  <Text>Customer Credit\nग्राहक क्रेडिट</Text>
</TouchableOpacity>
```

#### Step 5: Test end-to-end locally
```bash
# Metro
npx expo start --lan

# Open on device, test "Customer Credit" flow
# Verify data loads from backend
```

#### Step 6: Push and create PR
```bash
git add .
git commit -m "feat: add customer credit ledger"
git push origin feature/customer-credit-ledger
# Go to GitHub, create PR, add description & screenshots
```

#### Step 7: Code review + CI checks
- Peer reviews code
- CI runs linting, Docker build test
- Address feedback, push new commits

#### Step 8: Merge to develop
- PR approved
- Merge to `develop` branch
- CI auto-deploys to staging

#### Step 9: Staging validation
- Test on staging server: `https://staging.shop-app.com`
- Update mobile `API_URL` to staging and re-test
- Verify no error logs

#### Step 10: Merge to main & deploy to production
```bash
# After staging green-lit
git checkout main
git merge develop
git push origin main
# CI auto-deploys to production
```

#### Step 11: Monitor production
- Check logs for errors
- Watch for user feedback
- If critical bug found, rollback (see Stage 6)

---

## 4. Database Migration Strategy

### For schema changes (adding tables/columns)

#### Local development
```bash
# Make model changes in backend/models.py
# Restart app — SQLAlchemy auto-creates tables for local SQLite
uvicorn main:app --reload
```

#### For production (manual approach for now)
```bash
# 1. Make model change
# 2. Test locally
# 3. Push to GitHub, merge to main
# 4. Trigger production deployment
# 5. Main.py runs Base.metadata.create_all() → new tables created on Postgres

# For data backfill (if needed):
# Connect to production Postgres and run SQL
# Example: psql -h <host> -U <user> -d <db> -c "ALTER TABLE inventory_items ADD COLUMN new_col TEXT;"
```

#### For data migrations (moving/transforming existing data)
```python
# backend/migrations/001_add_customer_credit.py (example for future Alembic setup)
def upgrade():
    # Add new column to daily_sales
    op.add_column('daily_sales', Column('customer_id', Integer, ForeignKey('customer_credits.id')))

def downgrade():
    op.drop_column('daily_sales', 'customer_id')
```

---

## 5. Testing Strategy

### Unit Tests (backend)
```python
# backend/test_auth.py
import pytest
from auth import get_password_hash, verify_password

def test_password_hashing():
    plain = "test123"
    hashed = get_password_hash(plain)
    assert verify_password(plain, hashed)
    assert not verify_password("wrong", hashed)

# Run tests
pytest backend/test_auth.py
```

### Integration Tests (backend + DB)
```python
# backend/test_inventory.py
def test_create_inventory_item(test_db_session, test_user):
    from models import InventoryItem
    item = InventoryItem(item="Test Item", owner_id=test_user.id)
    test_db_session.add(item)
    test_db_session.commit()
    assert item.id is not None
```

### Manual Testing (mobile + backend)
```
Checklist for each feature:
- [ ] Create account
- [ ] Login
- [ ] Add inventory item
- [ ] Edit inventory item
- [ ] Delete inventory item
- [ ] Add daily sale (using inventory dropdown)
- [ ] Verify quantity validation
- [ ] Verify duplicate prevention
- [ ] Add daily expense (using inventory dropdown)
- [ ] View summary
- [ ] Test on Android device (Expo Go)
- [ ] Test on another Wi-Fi (different network)
```

---

## 6. Environment Configuration

### Development (local)
```bash
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=dev-secret-not-secure
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### Staging
```bash
DATABASE_URL=postgres://user:pass@staging-db:5432/staging_db
SECRET_KEY=staging-secret-random-string-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=120
ENVIRONMENT=staging
```

### Production
```bash
DATABASE_URL=postgres://user:pass@prod-db:5432/prod_db
SECRET_KEY=prod-secret-random-string-32-chars-very-secure
ACCESS_TOKEN_EXPIRE_MINUTES=120
ENVIRONMENT=production
CORS_ORIGINS=https://shop-app.com  # (future: tighten from "*")
```

---

## 7. Deployment Checklist

### Before any deployment
- [ ] All local tests pass
- [ ] Code follows style guide
- [ ] No console.error or unhandled exceptions
- [ ] Database schema is valid
- [ ] Environment variables are documented

### Before production deployment
- [ ] Staging deployment successful
- [ ] Full manual flow tested on staging
- [ ] Database backup taken
- [ ] Rollback plan prepared
- [ ] Team notified of planned downtime (if any)
- [ ] Release notes prepared

### Post-deployment validation
- [ ] `/health` endpoint responds
- [ ] `/auth/login` works
- [ ] `/inventory/` returns data
- [ ] `/daily-sales/` works
- [ ] Mobile app connects successfully
- [ ] No errors in backend logs
- [ ] Database queries complete in reasonable time

---

## 8. Troubleshooting

### Deployment fails
```bash
# 1. Check logs
# Railway/Fly: check deployment logs in dashboard
# 2. Verify environment variables
# 3. Check database connectivity
curl -v https://your-app.com/health
# 4. Rollback if critical
git revert <commit>
```

### Mobile app can't connect
```bash
# 1. Verify API_URL in mobile/src/config.ts
console.log('API_URL:', API_URL);
console.log('axios.defaults.baseURL:', axios.defaults.baseURL);
# 2. Test backend endpoint directly
curl https://your-app.com/health
# 3. Check network (Wi-Fi, VPN, firewall)
# 4. Restart Metro with cache clear
npx expo start -c
```

### Database migration issues
```bash
# 1. Verify DATABASE_URL is correct
psql -c 'SELECT version();'
# 2. Check tables exist
psql -c 'SELECT * FROM information_schema.tables;'
# 3. Re-run migration script
DATABASE_URL="..." python migrate_sqlite_to_postgres.py
```

---

## 9. Quick Reference Commands

```bash
# Development
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
cd mobile && npx expo start -c

# Testing
pytest backend/
curl -v http://localhost:8000/health

# Git workflow
git checkout -b feature/my-feature
git add .
git commit -m "feat: description"
git push origin feature/my-feature
# PR → Review → Merge to develop → Staging → Merge to main → Production

# Database migration (staging/production)
export DATABASE_URL="postgres://..."
python backend/migrate_sqlite_to_postgres.py

# Docker build & run (local test)
docker build -t shop-app-backend:latest backend/
docker run -e DATABASE_URL="..." -p 8000:8000 shop-app-backend:latest
```

---

## 10. Future Enhancements

- [ ] Add unit tests with pytest & mocking
- [ ] Set up Alembic for database migrations
- [ ] Add logging to all routers (structured JSON logs)
- [ ] Implement rate limiting on login/signup
- [ ] Add Sentry for error tracking
- [ ] Set up automated database backups
- [ ] Add mobile CI (EAS Build for Expo)
- [ ] Implement push notifications
- [ ] Add user analytics & crash reporting
- [ ] Switch CORS to specific origins (not "*")
- [ ] Add API versioning (e.g., /api/v1/...)
- [ ] Implement refresh token rotation

---

**Version:** 1.0  
**Last Updated:** June 2026  
**Owner:** Development Team
