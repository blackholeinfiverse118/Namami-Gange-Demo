# 🌊 Namami Gange Platform — Sovereign Operational Intelligence

Welcome to the **Namami Gange Platform**, a decision-friendly geospatial intelligence surface designed for civilian administrators, logistics managers, and ministry leadership. Engineered for **Operational Calmness**, this platform projects sovereign authority, scientific precision, and environmental readiness.

---

## 🏛️ Design Philosophy & Core Aesthetic

Unlike high-contrast consumer panels or gaming dashboards, the Namami Gange Platform prioritizes readability and calm decision-making during long shifts:
* **Civilizational Calmness**: Deep, vast color palette inspired by Indian river basins and scientific telemetry displays.
* **Map-Centric Layering**: The geospatial map represents the core source of truth, with panels, details, and telemetry cards emerging as non-obtrusive, layered overlays.
* **Non-Militarized Authority**: Luminous accents and clean structure that present serious telemetry data (BOD, DO levels, tracer codes) with absolute clarity.

### Primary Color Tokens
* **Deep Space Navy** (`#050a14`): Primary application canvas.
* **Vapor Surface Blue** (`#0a1120`): Cards, side panels, and elevated containers.
* **River Flow Blue** (`#1e88e5`): Hydrographic flow tracing and waterways.
* **Teal Glow** (`#00bfa5`): Safe limits and normal telemetry signals.
* **Alert Orange / Red** (`#ff9100` / `#ef4444`): Warnings, degraded states, and anomalies.

---

## 📂 Repository Structure

The workspace is organized into a modular hierarchy:

```
Namami Gange/
├── Namami Gange.html      # High-performance static HTML/CSS concept prototype
├── REVIEW_PACKET.md       # Strategic visual directives, layout specs, and UX requirements
├── .gitignore             # Root-level Git exclusions
└── namami-gange-ui/       # Decoupled React & Next.js frontend application
    ├── src/
    │   ├── app/           # Core Next.js routing, global styles, and Shell
    │   ├── components/    # Reusable structural and map-centric elements
    │   └── views/         # 9 dedicated operational control boards
    ├── public/            # System SVGs, icons, and static assets
    └── package.json       # App configuration and dependencies
```

---

## ⚡ The 9 Operational Views (UI Flow)

Inside `namami-gange-ui`, the application features a dynamic tab-routed sidebar to traverse these dedicated surfaces:

1. **Global Operations Dashboard**: Macro-level interactive SVG map of India tracking waterway signals (NW-1 to NW-111).
2. **Ganga Basin Intelligence**: High-resolution hydrography overlay with active telemetry points (BOD, DO, flow rate, silt).
3. **Location Intelligence**: Granular Varanasi/Kanpur hub compatibility gauges, historical tracer trails, and risk matrices.
4. **Scenario Simulation Engine**: Side-by-side comparative maps projecting Baseline vs. Optimized constraints with delta feedback.
5. **Realtime Signal Center**: Audit ledger stream recording incoming sensor alerts and confidence ratings.
6. **Infrastructure Network**: Intermodal transit health tracing connectivity over waterways, railways, and highways.
7. **Internal Collaboration Layer**: Command channels and crisis active calling overlays.
8. **Dataset & Sources**: Trust registries verifying CWC, ISRO Bhuvan, IWAI, and IMD ingestion health.
9. **CM Governance View**: High-level opportunity maps, connectivity gap finders, and executive metrics.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed (v18+ recommended).

### Running the Next.js UI
1. Navigate into the frontend directory:
   ```bash
   cd namami-gange-ui
   ```
2. Install the workspace dependencies:
   ```bash
   npm install
   ```
3. Run the local development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:3000`.

---

## 🛠️ Technology Stack
* **Core**: Next.js (App Router), React, TypeScript
* **Styling**: Vanilla CSS Modules (high flexibility, zero utility clutter)
* **Graphics**: Vector SVGs for scalable, performant maps and indicators without external GIS overhead.
