'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';
import IntelligenceCard from '@/components/shared/IntelligenceCard';
import MapCard from '@/components/shared/MapCard';
import FederationTopology from '@/components/shared/FederationTopology';
import ReplayConsole from '@/components/shared/ReplayConsole';
import styles from './page.module.css';
import { fetchResults, fetchSummary, fetchLocationDetails, fetchSignals, mapBackendToFrontend, fetchDatasets, fetchReplayStatus, postReplayTick, postReplayBreach } from '@/services/api';

// Other views imports
import BasinIntelligence from '@/components/views/BasinIntelligence';
import ScenarioSimulation from '@/components/views/ScenarioSimulation';
import RealtimeSignals from '@/components/views/RealtimeSignals';
import LocationIntel from '@/components/views/LocationIntel';
import Collaboration from '@/components/views/Collaboration';
import InfraNetwork from '@/components/views/InfraNetwork';
import DatasetSources from '@/components/views/DatasetSources';
import GovernanceView from '@/components/views/GovernanceView';

// Removed fallback payloads as part of Sprint 1, 5, 10 cleanup

const FACTOR_LABELS: Record<string, string> = {
  river_stability: 'River Stability',
  terminal_proximity: 'Terminal Proximity',
  logistics_access: 'Logistics Access',
  water_quality: 'Water Quality (BOD)',
  traffic_potential: 'Traffic Potential',
  turbulence: 'Turbulence Index',
  traffic_density: 'Traffic Density',
  urban_proximity: 'Urban Proximity',
  env_clearance_adj: 'Environmental Clearance',
  node_proximity: 'Multi-node Proximity',
  logistics_park: 'Logistics Park Quality',
  terminal_density: 'Terminal Density',
  connectivity: 'Connectivity Score',
  market_access: 'Urban Market Access'
};

const FACTOR_COLORS: Record<string, string> = {
  river_stability: 'var(--river-blue)',
  terminal_proximity: 'var(--teal)',
  logistics_access: 'var(--river-blue)',
  water_quality: 'var(--eco-green)',
  traffic_potential: 'var(--river-blue)',
  turbulence: 'var(--amber)',
  traffic_density: 'var(--river-blue)',
  urban_proximity: 'var(--teal)',
  env_clearance_adj: 'var(--eco-green)',
  node_proximity: 'var(--teal)',
  logistics_park: 'var(--river-blue)',
  terminal_density: 'var(--teal)',
  connectivity: 'var(--eco-green)',
  market_access: 'var(--river-blue)'
};

interface SuitabilityLocation {
  id: string;
  name: string;
  score: number;
  level: 'HIGH' | 'MEDIUM' | 'LOW';
  factors: { label: string; val: string; fill: string; color: string }[];
  constraints: { label: string; val: string; fill: string; color: string }[];
  infrastructure: string[];
  explanation: string;
  tracerId: string;
  confidence: number;
  lat: string;
  lng: string;
  factor_scores?: Record<string, number>;
  scoring_model?: any;
  trace?: any;
}

interface ReplayLog {
  timestamp: string;
  corrId: string;
  block: number;
  status: 'VERIFIED' | 'COMPATIBLE' | 'BREACH' | 'REPLAYING';
  message: string;
}

interface RecoveryEvent {
  id: string;
  time: string;
  type: string;
  status: 'RESOLVED' | 'ACTIVE';
  corrId: string;
  detail: string;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('global');
  const [commodoreMode, setCommodoreMode] = useState(false);

  // CENTRAL SIMULATOR STATE
  const [isSimulating, setIsSimulating] = useState(true);
  const [activeStep, setActiveStep] = useState(0); 
  const [currentBlock, setCurrentBlock] = useState(1240);
  const [corrIdNumber, setCorrIdNumber] = useState(9941);
  const [latencyMs, setLatencyMs] = useState(6);
  const [validationBreach, setValidationBreach] = useState(false);
  const [selectedLocationId, setSelectedLocationId] = useState('varanasi');
  const [selectedModel, setSelectedModel] = useState('inland_port');
  
  const [summaryStats, setSummaryStats] = useState({
    avg_suitability: 70.9,
    basin_alerts: 2,
    level_counts: { HIGH: 2, MEDIUM: 2, LOW: 1, REJECTED: 0 }
  });
  
  const [datasetsList, setDatasetsList] = useState<any[]>([]);

  // Dynamic logs
  const [replayLogs, setReplayLogs] = useState<ReplayLog[]>([
    { timestamp: '15:14:02', corrId: 'CORR-2026-0528-9941X', block: 1240, status: 'VERIFIED', message: 'Ingestion schema contract match on Varanasi-seaplane' },
    { timestamp: '15:13:48', corrId: 'CORR-2026-0528-9940Y', block: 1239, status: 'COMPATIBLE', message: 'Backward compatibility validated for Patna terminal payload' },
    { timestamp: '15:13:30', corrId: 'CORR-2026-0528-9939Z', block: 1238, status: 'VERIFIED', message: 'State synchronization check matched (0ms deviation)' }
  ]);

  const [recoveryEvents, setRecoveryEvents] = useState<RecoveryEvent[]>([
    { id: 'REC-082', time: '15:08:12', type: 'DRAFT_RECONCILE', status: 'RESOLVED', corrId: 'CORR-2026-0528-9912A', detail: 'Patna depth variance (Δ-0.4m) resolved via automatic weir sync.' },
    { id: 'REC-081', time: '14:52:45', type: 'SCHEMA_ALIGN', status: 'RESOLVED', corrId: 'CORR-2026-0528-9889B', detail: 'JSON payload mismatch on Kanpur sensor cluster corrected via back-version mapping.' }
  ]);

  // Dynamic values of suitability locations
  const [suitabilityLocations, setSuitabilityLocations] = useState<Record<string, SuitabilityLocation>>({
    varanasi: {
      id: 'varanasi',
      name: 'Varanasi Corridor NW-1',
      score: 92,
      level: 'HIGH',
      factors: [
        { label: 'Water Quality (BOD)', val: 'Good (2.1 mg/L)', fill: '82%', color: 'var(--eco-green)' },
        { label: 'Navigational Draft', val: 'Optimal (3.2m)', fill: '88%', color: 'var(--river-blue)' },
        { label: 'Intermodal Connectivity', val: 'Excellent', fill: '90%', color: 'var(--teal)' },
        { label: 'Economic Potential', val: 'Very High', fill: '85%', color: 'var(--river-blue)' }
      ],
      constraints: [
        { label: 'Siltation Risk', val: 'Low-Mod (32%)', fill: '32%', color: 'var(--eco-green)' },
        { label: 'Flow Volatility', val: 'Moderate', fill: '45%', color: 'var(--amber)' },
        { label: 'Habitat Sensitivity', val: 'Protected Zone', fill: '70%', color: 'var(--alert-red)' }
      ],
      infrastructure: ['Inland Waterway Terminal', 'Railway Link Corridor', 'Multimodal Freight hub'],
      explanation: 'Varanasi features high suitability as an intermodal inland port due to reliable river depth (NW-1 corridor draft > 3m), ready rail alignment, and low siltation risk compared to eastern sections. Eco-constraints are moderate due to dolphin sanctuaries nearby.',
      tracerId: 'TRC-VNS-2026-X88',
      confidence: 94,
      lat: '25.3176° N',
      lng: '82.9739° E'
    },
    patna: {
      id: 'patna',
      name: 'Patna Terminal NW-1',
      score: 80,
      level: 'HIGH',
      factors: [
        { label: 'Water Quality (BOD)', val: 'Mod (3.4 mg/L)', fill: '68%', color: 'var(--amber)' },
        { label: 'Navigational Draft', val: 'Adequate (2.6m)', fill: '72%', color: 'var(--river-blue)' },
        { label: 'Intermodal Connectivity', val: 'Good', fill: '75%', color: 'var(--teal)' },
        { label: 'Economic Potential', val: 'High', fill: '80%', color: 'var(--river-blue)' }
      ],
      constraints: [
        { label: 'Siltation Risk', val: 'High (78%)', fill: '78%', color: 'var(--alert-red)' },
        { label: 'Flow Volatility', val: 'High Seasonal', fill: '65%', color: 'var(--amber)' },
        { label: 'Habitat Sensitivity', val: 'Low Risk', fill: '25%', color: 'var(--eco-green)' }
      ],
      infrastructure: ['IWAI Jetty Terminal', 'National Highway-31 connector'],
      explanation: 'Patna provides robust economic throughput but is limited by heavy seasonal siltation (siltation risk 78%), requiring regular dredging to maintain a safe 2.5m draft. Economic connectivity via NH-31 is excellent.',
      tracerId: 'TRC-PAT-2026-Y41',
      confidence: 89,
      lat: '25.6112° N',
      lng: '85.1444° E'
    },
    kolkata: {
      id: 'kolkata',
      name: 'Haldia-Kolkata Port Grid',
      score: 91,
      level: 'HIGH',
      factors: [
        { label: 'Water Quality (BOD)', val: 'Good (2.5 mg/L)', fill: '80%', color: 'var(--eco-green)' },
        { label: 'Navigational Draft', val: 'High Draft (4.8m)', fill: '95%', color: 'var(--river-blue)' },
        { label: 'Intermodal Connectivity', val: 'Supreme', fill: '98%', color: 'var(--teal)' },
        { label: 'Economic Potential', val: 'Supreme', fill: '96%', color: 'var(--eco-green)' }
      ],
      constraints: [
        { label: 'Siltation Risk', val: 'Moderate (52%)', fill: '52%', color: 'var(--amber)' },
        { label: 'Flow Volatility', val: 'Tidal (Complex)', fill: '58%', color: 'var(--amber)' },
        { label: 'Habitat Sensitivity', val: 'Mangrove Zone', fill: '85%', color: 'var(--alert-red)' }
      ],
      infrastructure: ['Seaplane Terminal Hub', 'International Cargo Port', 'Railway Junction Network'],
      explanation: 'The Haldia-Kolkata sector has supreme suitability for large-scale maritime freight and logistics integration, maintaining a 4.5m+ draft due to marine tides. Tidal fluctuations require active sync with navigation tables.',
      tracerId: 'TRC-KOL-2026-Z02',
      confidence: 96,
      lat: '22.5726° N',
      lng: '88.3639° E'
    },
    kanpur: {
      id: 'kanpur',
      name: 'Kanpur Industrial Reach',
      score: 72,
      level: 'MEDIUM',
      factors: [
        { label: 'Water Quality (BOD)', val: 'Critical (8.4 mg/L)', fill: '25%', color: 'var(--alert-red)' },
        { label: 'Navigational Draft', val: 'Low (1.4m)', fill: '35%', color: 'var(--alert-red)' },
        { label: 'Intermodal Connectivity', val: 'Moderate', fill: '50%', color: 'var(--amber)' },
        { label: 'Economic Potential', val: 'High', fill: '78%', color: 'var(--river-blue)' }
      ],
      constraints: [
        { label: 'Siltation Risk', val: 'High (82%)', fill: '82%', color: 'var(--alert-red)' },
        { label: 'Flow Volatility', val: 'Critical Lows', fill: '85%', color: 'var(--alert-red)' },
        { label: 'Habitat Sensitivity', val: 'Moderate', fill: '40%', color: 'var(--amber)' }
      ],
      infrastructure: ['Local Jetties', 'Industrial Rail spur'],
      explanation: 'Kanpur stretch is currently classified as Medium Suitability due to severe organic pollution (BOD 8.4 mg/L) and extreme siltation coupled with shallow drafts (1.4m average). Major dredging and ecological rehabilitation are mandated before cargo operations.',
      tracerId: 'TRC-KAN-2026-A12',
      confidence: 82,
      lat: '26.4499° N',
      lng: '80.3319° E'
    },
    prayagraj: {
      id: 'prayagraj',
      name: 'Prayagraj Sangam Confluence',
      score: 53,
      level: 'MEDIUM',
      factors: [
        { label: 'Water Quality (BOD)', val: 'Mod (2.8 mg/L)', fill: '75%', color: 'var(--eco-green)' },
        { label: 'Navigational Draft', val: 'Varying (2.1m)', fill: '58%', color: 'var(--amber)' },
        { label: 'Intermodal Connectivity', val: 'Moderate', fill: '60%', color: 'var(--amber)' },
        { label: 'Economic Potential', val: 'Moderate', fill: '65%', color: 'var(--river-blue)' }
      ],
      constraints: [
        { label: 'Siltation Risk', val: 'High (70%)', fill: '70%', color: 'var(--alert-red)' },
        { label: 'Flow Volatility', val: 'High Seasonal', fill: '75%', color: 'var(--alert-red)' },
        { label: 'Habitat Sensitivity', val: 'Religious Confluence', fill: '90%', color: 'var(--alert-red)' }
      ],
      infrastructure: ['Passenger River Terminal', 'National Highway corridor'],
      explanation: 'Prayagraj suitability is graded Medium. Highly variable river flows during summers affect navigation drafts. The Sangam area possesses supreme cultural-religious sensitivity, limiting heavy industrial infrastructure development.',
      tracerId: 'TRC-PRY-2026-M09',
      confidence: 88,
      lat: '25.4358° N',
      lng: '81.8463° E'
    }
  });

  // Try to load schemas & datasets from backend, with graceful fallback (Phase 8 Resilience)
  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetchDatasets(validationBreach, latencyMs, currentBlock);
        if (res && res.status === 'success') {
          setDatasetsList(res.datasets);
        }
      } catch (err) {
        console.warn('Backend datasets endpoint unavailable, using local mock data.', err);
      }
    }
    loadData();
  }, [validationBreach, latencyMs, currentBlock]);

  // Load results from backend
  useEffect(() => {
    async function loadSummaryAndData() {
      try {
        const [summaryData, resultsData] = await Promise.all([
          fetchSummary(selectedModel),
          fetchResults(selectedModel)
        ]);

        if (summaryData && summaryData.status === 'success') {
          setSummaryStats({
            avg_suitability: summaryData.avg_suitability,
            basin_alerts: summaryData.basin_alerts,
            level_counts: summaryData.level_counts || { HIGH: 2, MEDIUM: 2, LOW: 1, REJECTED: 0 }
          });
        }

        if (resultsData?.results) {
          setSuitabilityLocations(prev => {
            const updated = { ...prev };
            resultsData.results.forEach((result: any) => {
              const mapped = mapBackendToFrontend(result);
              
              let key = '';
              if (result.location_id.includes('varanasi')) key = 'varanasi';
              else if (result.location_id.includes('patna')) key = 'patna';
              else if (result.location_id.includes('kanpur')) key = 'kanpur';
              else if (result.location_id.includes('allahabad') || result.location_id.includes('prayagraj')) key = 'prayagraj';
              else if (result.location_id.includes('kolkata') || result.location_id.includes('farakka')) key = 'kolkata';
              else if (result.location_id.includes('hajipur')) key = 'kolkata';

              // Dynamically construct factors from backend factor_scores if present, otherwise keep existing
              const mappedFactors = (result.factor_scores && Object.keys(result.factor_scores).length > 0)
                ? Object.entries(result.factor_scores).map(([fKey, val]: any) => ({
                    label: FACTOR_LABELS[fKey] || fKey.replace('_', ' '),
                    val: typeof val === 'boolean' ? (val ? 'Yes' : 'No') : `${Math.round(val)}%`,
                    fill: `${val}%`,
                    color: FACTOR_COLORS[fKey] || 'var(--river-blue)'
                  }))
                : (updated[key]?.factors || []);

              // Dynamically construct constraints
              let mappedConstraints: any[] = [];
              if (result.constraints?.hard) {
                result.constraints.hard.forEach((c: string) => {
                  mappedConstraints.push({
                    label: c.replace('_', ' ').toUpperCase() + ' (HARD)',
                    val: 'TRIGGERED',
                    fill: '100%',
                    color: 'var(--alert-red)'
                  });
                });
              }
              if (result.constraints?.soft) {
                result.constraints.soft.forEach((c: string) => {
                  mappedConstraints.push({
                    label: c.replace('_', ' ').toUpperCase() + ' (SOFT)',
                    val: 'PENALTY',
                    fill: '50%',
                    color: 'var(--amber)'
                  });
                });
              }
              if (mappedConstraints.length === 0) {
                mappedConstraints = (updated[key]?.constraints || []);
              }

              if (key && updated[key]) {
                updated[key] = {
                  ...updated[key],
                  score: mapped.score,
                  level: mapped.level,
                  explanation: mapped.explanation,
                  confidence: mapped.confidence,
                  factors: mappedFactors,
                  constraints: mappedConstraints,
                  factor_scores: mapped.factor_scores,
                  scoring_model: mapped.scoring_model,
                  trace: mapped.trace
                };
              }
            });

            return updated;
          });
        }
      } catch (err) {
        console.warn('Backend API results endpoint unavailable. Showing last known telemetry package.', err);
      }
    }

    loadSummaryAndData();
  }, [selectedModel]);

  // Simulation engine loop - Centralized Backend Driven
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    async function pollReplayStatus() {
      if (!isSimulating) return;
      try {
        const status = await fetchReplayStatus();
        if (status) {
          setCurrentBlock(status.current_block);
          setLatencyMs(status.last_tick_latency_ms);
          setValidationBreach(status.validation_breach_active);
          
          if (status.logs) {
            setReplayLogs(status.logs);
          }
          if (status.recovery_events) {
            setRecoveryEvents(status.recovery_events);
          }
          setActiveStep((prev) => (prev + 1) % 5);
        }
      } catch (e) {
        console.warn('Simulation backend unavailable', e);
      }
    }

    if (isSimulating) {
      interval = setInterval(() => {
        postReplayTick().then(() => pollReplayStatus());
      }, 3000);
    }

    return () => clearInterval(interval);
  }, [isSimulating]);

  const toggleBreachSimulation = async () => {
    try {
      await postReplayBreach();
      setValidationBreach((v) => !v);
    } catch (e) {
      console.error('Failed to toggle breach on backend', e);
    }
  };

  const handleManualRecoveryResolve = (id: string) => {
    setRecoveryEvents((prev) => 
      prev.map(evt => evt.id === id ? { ...evt, status: 'RESOLVED' } : evt)
    );
  };

  const activeLocData = suitabilityLocations[selectedLocationId] || suitabilityLocations.varanasi;
  // We use activeLocData directly now, as it is populated from the backend.

  // Active opportunities and constraints count for KPIs
  const activeOppsCount = activeLocData.factors.length;
  const activeConstsCount = activeLocData.constraints.length;

  const renderContent = () => {
    switch (activeTab) {
      case 'global':
        return (
          <div className={styles.dashboard}>
            {/* Header Controls & Commodore Mode Toggle */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '8px', marginBottom: '8px' }}>
              <div>
                <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '800', fontFamily: 'var(--font-display)', color: 'var(--text-primary)' }}>
                  {commodoreMode ? 'COMMODORE PRESENTATION BRIDGE' : 'EXECUTIVE COMMAND CENTER'}
                </h2>
                <p style={{ margin: 0, fontSize: '10px', color: 'var(--text-dim)' }}>Ganga Maritime & Logistics Suitability Spine</p>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button 
                  onClick={() => setCommodoreMode(!commodoreMode)}
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    border: '1px solid var(--teal)',
                    background: commodoreMode ? 'var(--teal)' : 'transparent',
                    color: commodoreMode ? 'var(--deep-navy)' : 'var(--teal)',
                    boxShadow: commodoreMode ? '0 0 12px var(--teal-glow)' : 'none',
                    transition: 'all 0.2s ease'
                  }}
                >
                  ⚓ {commodoreMode ? 'EXIT COMMODORE MODE' : 'ENTER COMMODORE MODE'}
                </button>
              </div>
            </div>

            {/* Top Zone - Executive KPIs (Phase 1) */}
            <div className={styles.gridStats}>
              <IntelligenceCard 
                title="LOCATIONS ANALYZED" 
                value="5 Sites" 
                delta="Active Core" 
                deltaType="neutral"
                color="blue" 
              />
              <IntelligenceCard 
                title="DATASET COUNT" 
                value="5 Sources" 
                delta="Real DB Connections" 
                deltaType="up"
                color="teal" 
              />
              <IntelligenceCard 
                title="INTELLIGENCE CONFIDENCE" 
                value={`${activeLocData.confidence}%`} 
                delta="NICAI Layered" 
                deltaType="up"
                color="green" 
              />
              <IntelligenceCard 
                title="ACTIVE OPPORTUNITIES" 
                value={`${activeOppsCount} Detected`} 
                delta="Ranked Factors" 
                deltaType="neutral"
                color="teal" 
              />
              <IntelligenceCard 
                title="ACTIVE CONSTRAINTS" 
                value={`${activeConstsCount} Triggered`} 
                delta="Strict Enforcement" 
                deltaType="down"
                color="red" 
              />
              <IntelligenceCard 
                title="RUNTIME STATUS" 
                value={validationBreach ? 'ANOMALOUS' : 'OPERATIONAL'} 
                delta={validationBreach ? 'Breach Flagged' : '100% Deterministic'} 
                deltaType={validationBreach ? 'down' : 'up'} 
                color={validationBreach ? 'red' : 'green'} 
              />
            </div>

            {/* Middle & Right Command Center Layout (Phase 1, 2, 3, 4, 5, 6, 7) */}
            <div 
              className={styles.mainGrid} 
              style={{ 
                gridTemplateColumns: '320px 1fr 340px',
                transition: 'grid-template-columns 0.3s ease-in-out'
              }}
            >
              {/* Column 1 (Left): Runtime Observability Surface (Phase 6) */}
              <div className={styles.leftCol}>
                <FederationTopology 
                  activeStep={activeStep} 
                  latencyMs={latencyMs}
                  nodes={[
                    { id: 'ingest', label: 'Ingestion Broker', status: 'active', metric: '4.8k msg/s' },
                    { id: 'valid', label: 'Schema Contract', status: validationBreach ? 'error' : 'processing', metric: validationBreach ? 'MISMATCH' : '100% Match' },
                    { id: 'replay', label: 'Replay Core', status: validationBreach ? 'recovering' : 'active', metric: '1.2x Speed' },
                    { id: 'persist', label: 'Persistence Store', status: 'active', metric: '4ms Delay' },
                    { id: 'federate', label: 'Federation Matrix', status: validationBreach ? 'recovering' : 'active', metric: validationBreach ? '92.4% Sync' : '99.9% Sync' }
                  ]}
                />
                
                {/* Control Panels hidden in Commodore Mode */}
                {!commodoreMode && (
                  <>
                    {/* Control Panel: Simulation variables */}
                    <div className={styles.controlPanelCard}>
                      <div className={styles.cardHeader}>DEMO CONTROLS</div>
                      <div className={styles.controlButtons}>
                        <button 
                          className={isSimulating ? styles.pauseBtn : styles.playBtn}
                          onClick={() => setIsSimulating(!isSimulating)}
                        >
                          {isSimulating ? '⏸ PAUSE RUNTIME SIM' : '▶ RESUME RUNTIME SIM'}
                        </button>
                        <button 
                          className={validationBreach ? styles.clearBreachBtn : styles.triggerBreachBtn}
                          onClick={toggleBreachSimulation}
                        >
                          {validationBreach ? '✓ RESOLVE SCHEMA BREACH' : '⚡ SIMULATE SCHEMA BREACH'}
                        </button>
                      </div>
                    </div>

                    <div className={styles.controlPanelCard} style={{ backgroundColor: 'var(--surface)' }}>
                      <div className={styles.cardHeader} style={{ color: 'var(--teal)' }}>RUNTIME METADATA</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '10px', fontFamily: 'var(--font-mono)' }}>
                        <div>• Message Ingestion Rate: 4.8k msg/s</div>
                        <div>• Validation Rate: 99.85%</div>
                        <div>• Replay Queue Length: 0 pending</div>
                        <div>• Demo Mode Indicator: active</div>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* Column 2 (Center): Map, Location Intel, & Score Breakdown (Phase 1, 2, 4) */}
              <div className={styles.centerCol}>
                {/* Middle Zone: Interactive Ganga Map */}
                <MapCard 
                  selectedMarkerId={selectedLocationId}
                  onMarkerSelect={setSelectedLocationId}
                  activeLayers={['waterways', 'seaplanes', 'logistics']}
                  activeLocationCoords={{ lat: activeLocData.lat, lng: activeLocData.lng }}
                />

                {/* Location Intelligence Surface (Phase 2) */}
                <div className={styles.locIntelCard} style={{ borderLeft: `3px solid ${activeLocData.score > 80 ? 'var(--eco-green)' : 'var(--amber)'}` }}>
                  <div className={styles.locHeader}>
                    <div>
                      <span className={styles.locLabel}>SELECTED LOCATION</span>
                      <h3 className={styles.locName} style={{ margin: 0 }}>{activeLocData.name} ({activeLocData.id.toUpperCase()})</h3>
                    </div>
                    <div className={styles.scoreBadge} style={{ borderLeftColor: activeLocData.score > 80 ? 'var(--eco-green)' : 'var(--amber)' }}>
                      <span className={styles.scoreVal}>{activeLocData.score}%</span>
                      <span className={styles.scoreLevel} style={{ color: activeLocData.score > 80 ? 'var(--eco-green)' : 'var(--amber)' }}>{activeLocData.level} SUITABILITY</span>
                    </div>
                  </div>

                  <div className={styles.explanationSection} style={{ borderTop: 'none', paddingTop: 0 }}>
                    <span className={styles.subTitle}>OPERATIONAL SUMMARY & DECISION COGNITION</span>
                    <p className={styles.explanationText} style={{ margin: '4px 0 8px 0' }}>
                      {activeLocData.explanation}
                    </p>
                    <div className={styles.infraTagsRow}>
                      {activeLocData.infrastructure.map((inf, i) => (
                        <span key={i} className={styles.infraTag}>⚡ {inf}</span>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border)', paddingTop: '8px', fontSize: '9.5px', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                    <span>Tracer ID: {activeLocData.tracerId}</span>
                    <span>Confidence: {activeLocData.confidence}% VERIFIED</span>
                  </div>
                </div>

                {/* Score Breakdown Panel (Phase 4) */}
                <div className={styles.locIntelCard}>
                  <div className={styles.cardHeader}>
                    <span>SCORE PILLAR BREAKDOWN</span>
                    <span style={{ color: 'var(--teal)', fontFamily: 'var(--font-mono)' }}>Weighted Composite</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {activeLocData.scoring_model && activeLocData.factor_scores && Object.entries(activeLocData.scoring_model.weights).map(([pillar, weight]: any) => {
                      const fScore = activeLocData.factor_scores?.[pillar] || 0;
                      const displayScore = Math.min(100, Math.max(0, Math.round(fScore)));
                      const isHigh = displayScore > 80;
                      const isMed = displayScore > 60;
                      return (
                        <div key={pillar} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                            <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{pillar} (Weight: {weight * 100}%)</span>
                            <span style={{ fontFamily: 'var(--font-mono)', color: isHigh ? 'var(--eco-green)' : isMed ? 'var(--amber)' : 'var(--alert-red)' }}>{displayScore}/100</span>
                          </div>
                          <div style={{ height: '4px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                            <div style={{ width: `${displayScore}%`, height: '100%', backgroundColor: isHigh ? 'var(--eco-green)' : isMed ? 'var(--amber)' : 'var(--alert-red)' }}></div>
                          </div>
                          <span style={{ fontSize: '9.5px', color: 'var(--text-dim)', fontStyle: 'italic' }}>Contribution: {Math.round(fScore * weight)} points</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Column 3 (Right): Dataset Transparency & Lineage Evidence (Phase 3, 5) */}
              <div className={styles.rightCol}>
                {/* Dataset Transparency Panel (Phase 3) */}
                <div className={styles.locIntelCard}>
                  <div className={styles.cardHeader}>
                    <span>DATASET TRANSPARENCY REGISTER</span>
                    <span style={{ color: 'var(--eco-green)', fontFamily: 'var(--font-mono)' }}>PROVENANCE PROOF</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {[
                      { name: "CPCB Water Quality", source: "Central Pollution Control Board", coverage: "25 Stations", purpose: "Environmental Assessment", contribution: "Checks BOD/DO biological limits" },
                      { name: "IWAI NW1 Terminal Registry", source: "Inland Waterways Authority", coverage: "NW1 Terminals", purpose: "Infrastructure Readiness", contribution: "Validates active terminal spurs" },
                      { name: "CWC River Gauge Stations", source: "Central Water Commission", coverage: "Ganga Basin", purpose: "Hydrological Stability", contribution: "Calculates lean draft safety margins" },
                      { name: "Logistics Parks Ganga Belt", source: "MoPSW Registry", coverage: "Regional Ring", purpose: "Intermodal Connectivity", contribution: "Computes rail-highway distance indices" }
                    ].map((ds, i) => (
                      <div key={i} style={{ padding: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)', borderRadius: '6px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                          <span>{ds.name}</span>
                          <span style={{ fontSize: '9px', color: 'var(--teal)', fontFamily: 'var(--font-mono)' }}>{ds.source}</span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '6px', fontSize: '9.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                          <div>Coverage: {ds.coverage}</div>
                          <div>Purpose: {ds.purpose}</div>
                        </div>
                        <div style={{ fontSize: '9px', color: 'var(--text-dim)', fontStyle: 'italic', marginTop: '3px' }}>
                          Contrib: {ds.contribution}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Lineage & Evidence Panel (Phase 5) */}
                <div className={styles.locIntelCard} style={{ borderTop: '2px solid var(--teal)' }}>
                  <div className={styles.cardHeader}>
                    <span>LINEAGE & EVIDENCE AUDIT</span>
                    <span style={{ color: 'var(--teal)', fontFamily: 'var(--font-mono)' }}>{activeLocData.name.split(' ')[0]}</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {activeLocData.trace && activeLocData.trace.source_signals && Object.entries(activeLocData.trace.source_signals).map(([source, ids]: any, i: number) => (
                      <div key={i} style={{ padding: '8px', background: 'rgba(20, 184, 166, 0.02)', border: '1px solid rgba(20, 184, 166, 0.08)', borderRadius: '6px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--teal)', textTransform: 'uppercase' }}>
                          {source} SIGNALS
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                          <strong>Signals Used:</strong> <code style={{ fontFamily: 'var(--font-mono)', fontSize: '9.5px', color: 'var(--text-primary)' }}>{ids.join(', ')}</code>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

            </div>

            {/* Bottom Zone: Runtime Observability Event Log */}
            {!commodoreMode && (
              <div className={styles.bottomConsole}>
                <div className={styles.consoleHeader}>
                  <span>REPLAY LEDGER & FEDERATION EVENT AUDITOR</span>
                  <span className={styles.auditIndicator} style={{ color: validationBreach ? 'var(--alert-red)' : 'var(--teal)' }}>
                    {validationBreach ? '⚠ 1 UNRESOLVED ANOMALY IN BUFFER' : '✓ RECOVERY PERSISTENCE: SECURE'}
                  </span>
                </div>
                <div className={styles.recoveryGrid}>
                  {recoveryEvents.map((evt) => (
                    <div key={evt.id} className={styles.recoveryCard} style={{ borderLeftColor: evt.status === 'ACTIVE' ? 'var(--alert-red)' : 'var(--teal)' }}>
                      <div className={styles.recoveryCardHeader}>
                        <span className={styles.evtType}>{evt.type} ({evt.id})</span>
                        <span className={evt.status === 'ACTIVE' ? styles.statusActiveBadge : styles.statusResolvedBadge}>
                          {evt.status}
                        </span>
                      </div>
                      <p className={evt.detail}>{evt.detail}</p>
                    <div className={styles.evtFooter}>
                      <span>Corr ID: {evt.corrId}</span>
                      {evt.status === 'ACTIVE' && (
                        <button 
                          className={styles.resolveBtn}
                          onClick={() => handleManualRecoveryResolve(evt.id)}
                        >
                          MANUALLY RECONCILE
                        </button>
                      )}
                    </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      case 'basin':
        return (
          <BasinIntelligence 
            selectedLocationId={selectedLocationId}
            onLocationSelect={setSelectedLocationId}
            validationBreach={validationBreach}
            suitabilityLocations={suitabilityLocations}
          />
        );
      case 'location':
        return (
          <LocationIntel 
            selectedLocationId={selectedLocationId}
            activeLocation={activeLocData}
          />
        );
      case 'simulation':
        return (
          <ScenarioSimulation 
            selectedLocationId={selectedLocationId}
            activeLocation={activeLocData}
            onLocationSelect={setSelectedLocationId}
            selectedModel={selectedModel}
          />
        );
      case 'signals':
        return (
          <RealtimeSignals 
            replayLogs={replayLogs}
            validationBreach={validationBreach}
            selectedLocationId={selectedLocationId}
            suitabilityLocations={suitabilityLocations}
            onLocationSelect={setSelectedLocationId}
          />
        );
      case 'infra':
        return (
          <InfraNetwork 
            selectedLocationId={selectedLocationId}
            activeLocation={activeLocData}
            validationBreach={validationBreach}
          />
        );
      case 'collab':
        return (
          <Collaboration 
            recoveryEvents={recoveryEvents}
            onResolve={handleManualRecoveryResolve}
            validationBreach={validationBreach}
          />
        );
      case 'governance':
        return (
          <GovernanceView 
            selectedLocationId={selectedLocationId}
            validationBreach={validationBreach}
            currentBlock={currentBlock}
            onLocationSelect={setSelectedLocationId}
            levelCounts={summaryStats.level_counts}
            suitabilityLocations={suitabilityLocations}
          />
        );
      case 'datasets':
        return (
          <DatasetSources 
            latencyMs={latencyMs}
            currentBlock={currentBlock}
            validationBreach={validationBreach}
          />
        );
      default:
        return (
          <div className={styles.placeholder}>
            <h2 className={styles.title}>{activeTab.toUpperCase()} View</h2>
            <p>Intelligence surface initialization in progress...</p>
          </div>
        );
    }
  };

  return (
    <main className={styles.main}>
      {!commodoreMode && <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />}
      <div 
        className={styles.content}
        style={{
          marginLeft: commodoreMode ? '0' : 'var(--sidebar-w)',
          paddingTop: commodoreMode ? '0' : 'var(--topbar-h)',
          height: '100vh',
          transition: 'all 0.3s ease-in-out'
        }}
      >
        {!commodoreMode && (
          <Topbar 
            liveFeed={validationBreach ? 'Anomaly Detected' : 'Active'}
            basinAlerts={summaryStats.basin_alerts}
            avgSuitability={summaryStats.avg_suitability}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
            onSignalMonitorClick={() => setActiveTab('signals')}
          />
        )}

        {renderContent()}
      </div>
    </main>
  );
}
