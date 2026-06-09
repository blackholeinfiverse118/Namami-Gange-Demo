# BHIV Design System — Dashboard Layout Patterns

To deliver comprehensive and immediate operational clarity, we establish three primary **dashboard layout patterns** built on strict CSS Grid layouts and flexbox partitions.

## 1. The Three-Column Command Grid (Recommended)

This layout forms the structural backbone of the sovereign operations dashboard. It organizes macro parameters, geospatial viewports, and streaming events into a single, cohesive view.

```css
.commandCenterGrid {
  display: grid;
  grid-template-columns: 340px 1fr 360px;
  grid-template-rows: 64px 80px 1fr 180px;
  gap: 16px;
  height: 100vh;
  padding: 16px;
  box-sizing: border-box;
}
```

### Component Placement Architecture:
1. **Topbar (Row 1, Columns 1-3)**: Strategic system statuses, ticking executive alarms, and the global clock.
2. **KPI Deck (Row 2, Columns 1-3)**: High-density, horizontal metric cards visualizing overall suitability, runtime health, and active validation queues.
3. **Left Column (Row 3, Column 1)**: Federation Runtime Observability (Interactive topology stream, service matrices).
4. **Center Column (Row 3, Column 2)**: Geospatial Intelligence Corridor (SVG map overlaid with live suitability locations and seaplane routes).
5. **Right Column (Row 3, Column 3)**: Replay Pipeline & Determinism Console (Linear correlation tracks, contract verification flags).
6. **Bottom Console (Row 4, Columns 1-3)**: Network Recovery Ledger & Contract Schema details.

---

## 2. The Split-Simulation Grid

Used when comparing simulated basin models (e.g., baseline status vs. target eco-preservation weights).

```css
.simulationGrid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  height: calc(100vh - 80px);
}

.visualSide {
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 16px;
}

.comparisonCanvas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
```

- **Controls Column**: Side-docked sliders and priority switches to manipulate variables.
- **Comparison Canvas**: Side-by-side geographic profiles that dynamically render the environmental differences resulting from control weight adjustments.

---

## 3. High-Density Layout Rules

- **Zero Overlaps**: Avoid absolute floating cards that obscure dynamic content. All overlays must sit within dedicated container blocks.
- **Scroll Containment**: Use `overflow-y: auto` with styled, 4px-wide scrollbars on panels containing lists to prevent layout shifting.
- **Adaptive Layout Scale**:
  - `> 1600px`: Three-column layout renders side-by-side with full content visibility.
  - `< 1400px`: Left and Right columns adapt to `300px` width; center map grows to occupy remaining space.
  - `< 1024px`: Adapts automatically to stacked scrolls for portable tablets.
