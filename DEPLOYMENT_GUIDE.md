# Deployment Guide

## Backend

```bash
cd backend/src
python api.py
```

Expected:

```text
Running on http://localhost:5000
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Expected:

```text
http://localhost:3000
```

---

## Validation

Open:

```text
http://localhost:3000
```

Verify backend activity:

```text
GET /results?model=inland_port
HTTP 200
```

appears in backend console.

---

## Success Criteria

* Frontend loads
* Dashboard renders
* Backend returns HTTP 200
* Suitability score visible
* Navigation works without crashes

Deployment complete.
