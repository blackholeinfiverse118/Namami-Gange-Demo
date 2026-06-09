# BHIV Design System — Component Library Primitives

This document establishes the technical specifications, CSS styles, and interface properties (Props) for the seven core reusable components designed to industrialize dashboard construction across the Namami Gange Platform.

---

## 1. KPI Card
Visualizes high-level system states, counts, and percentages.
- **Props Interface**:
  ```typescript
  interface KPICardProps {
    title: string;
    value: string | number;
    delta?: string;
    deltaType?: 'up' | 'down' | 'neutral';
    color?: 'blue' | 'red' | 'green' | 'teal' | 'amber';
  }
  ```
- **UX Behavior**: Delivers instant, macro-level system updates. Positive/negative deltas display custom-colored, micro-indicators (e.g., green up-arrows, red down-arrows).

---

## 2. Alert Card
Highlights chronological anomalies, event triggers, and sensor spikes.
- **Props Interface**:
  ```typescript
  interface AlertCardProps {
    id: string;
    text: string;
    severity: 'low' | 'medium' | 'high';
    time: string;
    confidence: number;
    traceId?: string;
  }
  ```
- **UX Behavior**: Emits a soft, pulsing alert glow matching the severity level (red for high, amber for medium, blue for low). Renders a corresponding status trace code for quick operational lookup.

---

## 3. Telemetry Card
Visualizes dense arrays of multi-sensor environmental indicators.
- **Props Interface**:
  ```typescript
  interface TelemetryCardProps {
    stationName: string;
    metrics: {
      label: string;
      value: string | number;
      fillPercent: number; // 0-100
      color: string;
    }[];
  }
  ```
- **UX Behavior**: Renders compact, vertical telemetry bars with horizontal fill gauges, offering a space-efficient view of complex environmental data.

---

## 4. Replay Card
Visualizes the historical data replay stream and deterministic validation status.
- **Props Interface**:
  ```typescript
  interface ReplayCardProps {
    currentBlock: number;
    totalBlocks: number;
    correlationId: string;
    lineagePath: string[];
    validationState: 'VERIFIED' | 'BREACH' | 'PENDING';
  }
  ```
- **UX Behavior**: Renders linear pipeline stages, color-coded by contract validation status, with clear read-only labeling to prevent operator confusion.

---

## 5. Topology Card
Visualizes real-time, inter-service network health and pipeline data flow.
- **Props Interface**:
  ```typescript
  interface ServiceNode {
    id: string;
    label: string;
    status: 'active' | 'processing' | 'recovering' | 'offline';
  }
  interface TopologyCardProps {
    nodes: ServiceNode[];
    activePacketSource?: string;
    activePacketTarget?: string;
  }
  ```
- **UX Behavior**: Visualizes the active data packet stream via subtle glowing particle paths traveling along SVG connectors, helping operators quickly isolate bottleneck locations.

---

## 6. Map Card
Integrates the geographic viewport of truth, displaying waterway segments, suitability scoring overlays, and seaplane routes.
- **Props Interface**:
  ```typescript
  interface LocationMarker {
    id: string;
    name: string;
    lat: number;
    lng: number;
    suitabilityScore: number;
    type: 'port' | 'seaplane' | 'monitoring' | 'logistics';
  }
  interface MapCardProps {
    markers: LocationMarker[];
    selectedMarkerId?: string;
    onMarkerSelect: (id: string) => void;
    activeLayers: string[]; // e.g. ['waterways', 'seaplanes', 'logistics']
  }
  ```
- **UX Behavior**: Supports interactive, hoverable node highlighting and smooth layer filtering overlays, serving as the central coordinator for localized intelligence.

---

## 7. Executive Metric Card
Synthesizes composite indicators, opportunities, and risk profiles for rapid decision-making.
- **Props Interface**:
  ```typescript
  interface ExecutiveMetricCardProps {
    title: string;
    value: string;
    description: string;
    insights: { text: string; status: 'healthy' | 'warning' | 'critical' }[];
    borderAccent?: string;
  }
  ```
- **UX Behavior**: Synthesizes administrative metrics (e.g., investment potential, infrastructural bottlenecks) at a glance, featuring left-side colored accents to categorize priority fields.
