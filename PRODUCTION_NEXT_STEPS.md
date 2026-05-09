# RunEV Production Setup Notes

## Backend

Start the API:

```bash
uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Database Migrations

Alembic is now configured for versioned database migrations.

For a fresh database:

```bash
alembic upgrade head
```

For the current local SQLite database, avoid running the initial migration directly if tables already exist. The app still keeps `create_all` for compatibility with the existing prototype database.

## Razorpay Environment

Local development works without Razorpay keys by creating mock payment orders.

For real Razorpay payments, set:

```bash
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

Payment endpoints:

```text
POST /api/v1/payments/orders
POST /api/v1/payments/verify
POST /api/v1/payments/webhooks/razorpay
```

The webhook endpoint verifies `X-Razorpay-Signature`.

## Tests

Run:

```bash
python -m pytest -q
```

Current focused tests cover geo helpers, pricing helpers, and Razorpay signature verification.
