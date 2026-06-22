# National Waterways Geospatial Command Layer Specification
## Namami Gange Marine Operations Command Center (MOCC)

This document specifies the multi-layered geospatial architecture, GIS feature layers, map symbols, and GeoJSON data schemas required to support tactical mapping of the National Waterways network (NW-1 to NW-111) in the Geospatial Command Layer.

---

## 1. Geospatial Layer Stack Architecture

The command center map operates on a five-layer GIS composition designed to remain responsive under dense telemetry updates. Operators can toggle individual layers depending on their task (e.g., traffic control vs. infrastructure planning):

```
+--------------------------------------------------------+
| [Layer 5] Vessel Tracking (Real-Time AIS Nodes)        |  --> Dynamic (GPS/AIS)
+--------------------------------------------------------+
| [Layer 4] Hydrology & Sensors (CWC Gauges, WQ Points)  |  --> Dynamic (IoT)
+--------------------------------------------------------+
| [Layer 3] Ports, Jetties, & Logistics (Static Nodes)   |  --> Static (MasterDB)
+--------------------------------------------------------+
| [Layer 2] Navigation Fairways & Channels (Corridors)   |  --> Static (IWAI Bathymetry)
+--------------------------------------------------------+
| [Layer 1] Base Topographic Map (Dark-Mode Terrain)    |  --> Vector Tile Server
+--------------------------------------------------------+
```

---

## 2. Waterway Network Mappings

While the current deployment focuses on **NW-1 (Ganga-Bhagirathi-Hooghly system, 1620 km)**, the geospatial engine supports the broader Indian Inland Waterways network:

* **National Waterway 1 (NW-1)**: Ganga-Bhagirathi-Hooghly River System (Haldia to Prayagraj). Primary industrial freight corridor.
* **National Waterway 2 (NW-2)**: Brahmaputra River (Dhubri to Sadiya). Critical cargo pipeline to Northeast India.
* **National Waterway 3 (NW-3)**: West Coast Canal (Kottapuram to Kollam). Core barge transport link for Kerala's ports.
* **National Waterway 4 (NW-4)**: Kakinada-Puducherry canals along Godavari and Krishna rivers. Serving Southern industrial hubs.
* **National Waterways 5–111**: Secondary feeders, tidal channels, and regional tributaries mapped for future expansion.

---

## 3. Geospatial Node Classifications

The map layers feature distinct visual representations for maritime infrastructure:

### A. Multimodal Inland Ports
* *Icons*: Bold teal anchors with glowing rings.
* *Attributes*: Crane capacity, rail links, container berths, fuel bunkering facilities.
* *Key Sites*: Haldia MMT, Sahibganj MMT, Varanasi MMT.

### B. Floating & Permanent Jetties
* *Icons*: Smaller teal squares.
* *Attributes*: Draft capacity, barge length limits, cargo categories handled.
* *Key Sites*: Gaighat (Patna), Jajmau (Kanpur), Garden Reach (Kolkata).

### C. Multi-modal Logistics Parks
* *Icons*: Cyan hexagons with warehouse glyphs.
* *Attributes*: Road linkages, warehouse volume, cargo consolidation areas.

### D. Seaplane Candidate Locations (Water Aerodromes)
* *Icons*: Glowing purple wings.
* *Attributes*: Splashdown runway length, passenger lounge status, water depth limits.
* *Key Sites*: Prayagraj Sangam, Varanasi (Ravidas Ghat), Patna Sahib.

---

## 4. GeoJSON Data Payload Schemas

To render these layers, the frontend consumes standardized GeoJSON feeds from the geospatial backends:

### A. Vessel AIS Node GeoJSON Feed
**Endpoint**: `GET /api/geospatial/layers/vessels`  
**JSON Payload**:
```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" }
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [84.1205, 25.4521]
      },
      "properties": {
        "vessel_id": "VES-NW1-088",
        "name": "MV Ganga-Vahini",
        "class": "Class III",
        "sog_kts": 8.2,
        "cog_deg": 112.5,
        "draft_m": 1.6,
        "heading": 110.0,
        "alert_status": "NORMAL"
      }
    }
  ]
}
```

### B. Navigational Fairway Channel GeoJSON Feed
**Endpoint**: `GET /api/geospatial/layers/fairways`  
**JSON Payload**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [82.9739, 25.3176],
          [83.2144, 25.5123],
          [84.1205, 25.4521],
          [85.1444, 25.6112]
        ]
      },
      "properties": {
        "corridor_id": "CORR-NW1-SECT-01",
        "name": "Varanasi-Patna Fairway Channel",
        "maintained_depth_m": 3.0,
        "shoaling_hazard": "LOW",
        "speed_limit_knots": 8.0
      }
    }
  ]
}
```
