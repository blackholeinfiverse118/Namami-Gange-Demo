# Marine Operations Design System (MODS)
## Namami Gange Marine Operations Command Center (MOCC)

This document establishes the UI styling system, CSS custom properties (design tokens), component structures, and visual interfaces for the 8 primitive cards of the Marine Operations Command Center.

---

## 1. Unified CSS Custom Properties (Design Tokens)

These values represent the core palette for the MOCC. Place them in your global CSS stylesheet (e.g., `global.css` or `page.module.css`):

```css
:root {
  /* Brand & Neutrals */
  --deep-navy: hsl(222, 47%, 7%);
  --surface: hsl(222, 40%, 12%);
  --surface-hover: hsl(222, 35%, 16%);
  --border: hsl(222, 25%, 20%);
  --text-primary: hsl(0, 0%, 96%);
  --text-secondary: hsl(220, 10%, 75%);
  --text-dim: hsl(220, 8%, 55%);

  /* Functional Status Colors (Glowing HSL tokens) */
  --active-cyan: hsl(180, 100%, 45%);
  --active-cyan-glow: hsla(180, 100%, 45%, 0.15);
  
  --eco-green: hsl(145, 80%, 45%);
  --eco-green-glow: hsla(145, 80%, 45%, 0.15);
  
  --warn-amber: hsl(38, 95%, 55%);
  --warn-amber-glow: hsla(38, 95%, 55%, 0.15);
  
  --alert-red: hsl(355, 85%, 55%);
  --alert-red-glow: hsla(355, 85%, 55%, 0.15);
  
  --seaplane-purple: hsl(275, 85%, 65%);
  
  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-display: 'Outfit', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

---

## 2. Reusable Card Primitives (Types & Specs)

### A. Vessel Card
* **Purpose**: Display status, class, and parameters of an active vessel.
* **Component Prop Definition (TypeScript)**:
```typescript
interface VesselCardProps {
  name: string;
  vesselClass: string;
  status: 'UNDERWAY' | 'MOORED' | 'ANCHORED';
  route: string;
  speed: number;
  eta: string;
  alert?: 'DRAFT_WARN' | 'SPEED_VIOL' | 'ROUTE_DEV';
}
```

### B. Cargo Card
* **Purpose**: Display transit metrics and volume details of a cargo shipment.
* **Component Prop Definition**:
```typescript
interface CargoCardProps {
  manifestId: string;
  commodityType: 'FLY_ASH' | 'COAL' | 'CONTAINERS' | 'AGRI_BULK';
  tonnage: number;
  assignedVessel: string;
  destinationTerminal: string;
  loadingProgress: number; // 0 to 100
}
```

### C. Water Level Card
* **Purpose**: Show real-time water levels, trend lines, and draft limits.
* **Component Prop Definition**:
```typescript
interface WaterLevelCardProps {
  stationName: string;
  riverLevelMeters: number;
  safetyMarginMeters: number;
  trend: 'RISING' | 'FALLING' | 'STABLE';
  siltationWarning: boolean;
}
```

### D. Navigation Alert Card
* **Purpose**: Display Notice to Mariners (NtM) safety broadcasts and directives.
* **Component Prop Definition**:
```typescript
interface NavigationAlertCardProps {
  noticeId: string;
  type: 'WATERWAY_BLOCK' | 'WEATHER_WARN' | 'DREDGING' | 'SHALLOW_WATER';
  urgency: 'IMMEDIATE' | 'URGENT' | 'ROUTINE';
  description: string;
  issuedAt: string;
}
```

### E. Terminal Card
* **Purpose**: Render terminal berthing stats, yard saturation, and capacities.
* **Component Prop Definition**:
```typescript
interface TerminalCardProps {
  terminalName: string;
  activeBerths: number;
  totalBerths: number;
  yardUtilizationPercent: number;
  dailyThroughputTons: number;
  congestionStatus: 'LOW' | 'MODERATE' | 'CRITICAL';
}
```

### F. Congestion Card
* **Purpose**: Display wait queues and utilization heatmaps.
* **Component Prop Definition**:
```typescript
interface CongestionCardProps {
  locationId: string;
  currentWaitTimeHours: number;
  averageTurnaroundHours: number;
  queueLength: number;
  hourlyLoadProfile: number[]; // 24 values
}
```

### G. Voyage Card
* **Purpose**: Highlight active route details, alternate choices, and overall risk levels.
* **Component Prop Definition**:
```typescript
interface VoyageCardProps {
  voyageId: string;
  routeTitle: string;
  durationHours: number;
  distanceKm: number;
  constraintsDetected: string[];
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  isRecommended: boolean;
}
```

### H. RIS Card
* **Purpose**: Detail Lock states, river conditions, and electronic reporting packets.
* **Component Prop Definition**:
```typescript
interface RISCardProps {
  lockId: string;
  chamberNumber: number;
  gateState: 'OPEN' | 'CLOSED' | 'OPENING' | 'CLOSING';
  waterDifferentialMeters: number;
  waitingVesselsCount: number;
  systemReplayActive: boolean;
}
```

---

## 3. Reference Component Implementation: VesselCard

Here is a reference React component built to support these HSL custom properties:

```tsx
import React from 'react';
import styles from './VesselCard.module.css';

export const VesselCard: React.FC<VesselCardProps> = ({
  name,
  vesselClass,
  status,
  route,
  speed,
  eta,
  alert
}) => {
  const isAlert = !!alert;

  return (
    <div className={`${styles.card} ${isAlert ? styles.alertCard : ''}`}>
      <div className={styles.header}>
        <div>
          <h4 className={styles.name}>{name}</h4>
          <span className={styles.classLabel}>{vesselClass}</span>
        </div>
        <span className={`${styles.statusBadge} ${styles[status.toLowerCase()]}`}>
          {status}
        </span>
      </div>
      
      <div className={styles.body}>
        <div className={styles.metaRow}>
          <span className={styles.metaLabel}>Route:</span>
          <span className={styles.metaVal}>{route}</span>
        </div>
        <div className={styles.metaRow}>
          <span className={styles.metaLabel}>Speed:</span>
          <span className={styles.metaVal}>{speed} kts</span>
        </div>
        <div className={styles.metaRow}>
          <span className={styles.metaLabel}>ETA:</span>
          <span className={styles.metaVal}>{eta}</span>
        </div>
      </div>

      {isAlert && (
        <div className={styles.alertFooter}>
          <span className={styles.alertIcon}>⚠</span>
          <span className={styles.alertText}>
            {alert === 'DRAFT_WARN' && 'UNDER-KEEL DRAFT BREACH'}
            {alert === 'SPEED_VIOL' && 'SPEED LIMIT EXCEEDED'}
            {alert === 'ROUTE_DEV' && 'OUTSIDE NAVIGATION CHANNEL'}
          </span>
        </div>
      )}
    </div>
  );
};
```
