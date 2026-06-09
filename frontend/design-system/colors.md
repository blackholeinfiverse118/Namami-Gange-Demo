# BHIV Design System — Sovereign Color Tokens

The Namami Gange Platform adopts an **Operational Calmness & High-Density Obs** style. It is designed to minimize cognitive load, eliminate visual fatigue during extended operational shifts, and draw instant, high-contrast attention to system anomalies and suitability opportunities.

## 1. Core Palette Tokens

| Color Name | Variable Name | HEX Value | Semantic Usage |
| :--- | :--- | :--- | :--- |
| **Deep Space Navy** | `--deep-navy` | `#050a14` | Application canvas backdrop. |
| **Vapor Surface** | `--surface` | `#0a1120` | Primary cards, panels, and sidebars. |
| **Vapor Surface Elevated** | `--surface-2` | `#1e293b` | Floating panels, dropdown overlays, active tabs. |
| **River Flow Blue** | `--river-blue` | `#3b82f6` | Navigable corridors, intermodal networks, normal stats. |
| **River Light Glow** | `--river-light` | `#60a5fa` | Water system trace overlays, path highlights. |
| **Teal Glow** | `--teal` | `#14b8a6` | Healthy telemetry nodes, active synchronizations, validation SUCCESS. |
| **Warning Amber** | `--amber` | `#f59e0b` | Degraded limits, siltation threshold warnings, medium risk zones. |
| **Alert Red** | `--alert-red` | `#ef4444` | Validation breaches, offline nodes, environmental critical alerts. |
| **Eco Corridor Green** | `--eco-green` | `#10b981` | Restored ecological basins, high suitability ratings (score > 80). |

## 2. Text and Typography Contrast

We ensure clear legibility against deep backdrops through structured contrast tokens:

- **Primary Text (`#f8fafc` / `--text-primary`)**: High-contrast display metrics, section headers, critical status text.
- **Secondary Text (`#94a3b8` / `--text-secondary`)**: Standard labels, active descriptions, telemetry table headers.
- **Dimmed Text (`#64748b` / `--text-dim`)**: Static trace codes, coordinates, minor sensor timestamps.

## 3. Glassmorphic Surface Specifications

```css
.glass {
  background: rgba(10, 17, 32, 0.75);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
}
```

These parameters provide depth, establishing a multi-layered hierarchy that separates operational map viewports from floating metric panels.
