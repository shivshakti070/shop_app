# Backend Summary API

Endpoint: `GET /summary?period={daily|monthly|yearly|lifetime}`

Response schema (`SummaryOut`):
- `sales`: number — total sales amount (excluding returns)
- `net_sales`: number — sales minus returns
- `profit`: number — positive profit amount
- `loss`: number — positive loss amount
- `inventory_value`: number — current inventory valuation (remaining_quantity * purchase_rate)
- `cash_balance`: number — net cash inflows for the period
- `upi_balance`: number — net UPI inflows for the period
- `credit_due`: number — outstanding credit sales for the period
- `expenses`: number — sum of daily and one-time expenses for the period
- `investments`: number — investment amounts for the period
- `returns`: number — total returns amount for the period
- `credit_recovered`: number — credit recovered (if tracked)

Notes:
- `period` defaults to `daily`.
- For `lifetime` period, the API returns totals across all dates.
- `credit_recovered` will be 0 unless your app records dedicated recovery/payments associated with credit sales.

Quick curl example (after running the FastAPI server locally on port 8000):

1. Signup / get token (creates a user):

```bash
curl -s -X POST http://localhost:8000/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"username":"testuser","email":"t@test.com","password":"pass"}' | jq
```

2. Use the `access_token` returned in the previous step:

```bash
TOKEN="<access_token>"
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/summary/?period=daily" | jq
```

If you run into errors, ensure the server is started (e.g. `uvicorn main:app --reload --port 8000` from the `backend/` folder) and that dependencies are installed (`pip install -r requirements.txt`).
