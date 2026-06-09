# Namami Gange Demo

Integrated demonstration repository containing:

* Namami Gange Frontend
* Suitability Intelligence Backend
* Frontend–Backend Integration Layer

## Repository Structure

```text
Namami-Gange-Demo/
├── backend/
└── frontend/
```

## Prerequisites

### Backend

* Python 3.10+
* pip

### Frontend

* Node.js 18+
* npm

---

## Backend Setup

```bash
cd backend/src
pip install -r requirements.txt
python api.py
```

Backend starts on:

```text
http://localhost:5000
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend starts on:

```text
http://localhost:3000
```

---

## Integration Endpoint

Frontend consumes:

```text
GET /results?model=inland_port
```

Example:

```text
http://localhost:5000/results?model=inland_port
```

---

## Validation Checklist

* Backend starts successfully
* Frontend starts successfully
* CORS enabled
* API requests return HTTP 200
* Dashboard loads successfully
* Navigation validated across all views
* Backend suitability values visible in UI

---

## Current Demo Scope

The suitability intelligence pipeline is connected to the backend.

Some visualization screens continue to use static demonstration content and are not yet fully API-driven.

This repository is intended for demonstration and evaluation purposes.
