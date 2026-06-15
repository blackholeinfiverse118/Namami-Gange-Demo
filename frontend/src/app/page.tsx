'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';
import IntelligenceCard from '@/components/shared/IntelligenceCard';
import BasinIntelligence from '@/components/views/BasinIntelligence';
import ScenarioSimulation from '@/components/views/ScenarioSimulation';
import RealtimeSignals from '@/components/views/RealtimeSignals';
import LocationIntel from '@/components/views/LocationIntel';
import Collaboration from '@/components/views/Collaboration';
import InfraNetwork from '@/components/views/InfraNetwork';
import DatasetSources from '@/components/views/DatasetSources';
import GovernanceView from '@/components/views/GovernanceView';
import FederationTopology from '@/components/shared/FederationTopology';
import ReplayConsole from '@/components/shared/ReplayConsole';
import MapCard from '@/components/shared/MapCard';
import TelemetryCard from '@/components/shared/TelemetryCard';
import AlertCard from '@/components/shared/AlertCard';
import styles from './page.module.css';
import { fetchResults, fetchSummary, fetchLocationDetails, fetchSignals, mapBackendToFrontend } from '@/services/api';

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

  // CENTRAL SIMULATOR STATE
  const [isSimulating, setIsSimulating] = useState(true);
  const [activeStep, setActiveStep] = useState(0); // 0: Ingestion, 1: Validation, 2: Replay, 3: Persistence, 4: Federation
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
      score: 82,
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
      score: 74,
      level: 'MEDIUM',
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
      score: 88,
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
      score: 38,
      level: 'LOW',
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
      explanation: 'Kanpur stretch is currently classified as Low Suitability due to severe organic pollution (BOD 8.4 mg/L) and extreme siltation coupled with shallow drafts (1.4m average). Major dredging and ecological rehabilitation are mandated before cargo operations.',
      tracerId: 'TRC-KAN-2026-A12',
      confidence: 82,
      lat: '26.4499° N',
      lng: '80.3319° E'
    },
    prayagraj: {
      id: 'prayagraj',
      name: 'Prayagraj Sangam Confluence',
      score: 65,
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

  // 1. Fetch live signals on mount
  useEffect(() => {
    async function loadSignals() {
      try {
        const signalsData = await fetchSignals();
        if (signalsData?.signals && signalsData.signals.length > 0) {
          const mappedLogs: ReplayLog[] = signalsData.signals.map((sig: any, index: number) => ({
            timestamp: new Date(Date.now() - index * 60000).toLocaleTimeString('en-US', { hour12: false }),
            corrId: `CORR-2026-0528-${9941 - index}X`,
            block: 1240 - index,
            status: sig.signal_value < 20 ? 'BREACH' : 'VERIFIED',
            message: `${sig.description || sig.signal_type} value: ${sig.signal_value}`
          }));
          setReplayLogs(mappedLogs.slice(0, 15));
        }
      } catch (err) {
        console.error('Failed to fetch live signals:', err);
      }
    }
    loadSignals();
  }, []);

  // 2. Load summary stats and model results when selectedModel changes
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
              
              // Dynamically construct factors from backend factor_scores
              const mappedFactors = Object.entries(result.factor_scores || {}).map(([key, val]: any) => ({
                label: FACTOR_LABELS[key] || key.replace('_', ' '),
                val: typeof val === 'boolean' ? (val ? 'Yes' : 'No') : `${Math.round(val)}%`,
                fill: `${val}%`,
                color: FACTOR_COLORS[key] || 'var(--river-blue)'
              }));

              // Dynamically construct constraints
              const mappedConstraints = [];
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
                mappedConstraints.push({
                  label: 'No Constraints Triggered',
                  val: 'Clear',
                  fill: '100%',
                  color: 'var(--eco-green)'
                });
              }

              let key = '';
              if (result.location_id.includes('varanasi')) key = 'varanasi';
              else if (result.location_id.includes('patna')) key = 'patna';
              else if (result.location_id.includes('kanpur')) key = 'kanpur';
              else if (result.location_id.includes('allahabad') || result.location_id.includes('prayagraj')) key = 'prayagraj';
              else if (result.location_id.includes('kolkata') || result.location_id.includes('farakka')) key = 'kolkata';
              else if (result.location_id.includes('hajipur')) key = 'kolkata'; // Fallback to Kolkata hub layout

              if (key && updated[key]) {
                updated[key] = {
                  ...updated[key],
                  score: mapped.score,
                  level: mapped.level,
                  explanation: mapped.explanation,
                  confidence: mapped.confidence,
                  factors: mappedFactors,
                  constraints: mappedConstraints
                };
              }
            });

            return updated;
          });
        }
      } catch (err) {
        console.error('Failed to load data for model:', selectedModel, err);
      }
    }

    loadSummaryAndData();
  }, [selectedModel]);

  // Dynamic simulation engine loops in background
  useEffect(() => {
    if (!isSimulating) return;

    const interval = setInterval(() => {
      // 1. Advance steps
      setActiveStep((prev) => (prev + 1) % 5);

      // 2. Fluctuated latency
      setLatencyMs((prev) => {
        const offset = Math.floor(Math.random() * 5) - 2;
        const next = prev + offset;
        return next < 3 ? 4 : next > 18 ? 16 : next;
      });

      // 3. Telemetry updates on the selected location
      setSuitabilityLocations((prev) => {
        const copy = { ...prev };
        const loc = copy[selectedLocationId];
        if (loc && loc.factors && loc.factors.length > 0) {
          const indexToMutate = Math.floor(Math.random() * loc.factors.length);
          const f = loc.factors[indexToMutate];
          if (f && f.label && typeof f.label === 'string' && f.label.includes('Draft')) {
            const currentDraft = parseFloat(f.val.match(/[\d.]+/)?.[0] || '3.0');
            const diff = (Math.random() * 0.2 - 0.1);
            const nextDraft = Math.max(1.0, Math.min(6.0, currentDraft + diff)).toFixed(1);
            
            const updatedFactors = [...loc.factors];
            updatedFactors[indexToMutate] = {
              ...f,
              val: `${nextDraft}m`,
              fill: `${Math.min(100, Math.max(0, Math.round((parseFloat(nextDraft) / 6.0) * 100)))}%`
            };
            
            copy[selectedLocationId] = {
              ...loc,
              factors: updatedFactors
            };
          }
        }
        return copy;
      });

      // 4. If step transitions to block sync, increment block and add log
      setActiveStep((step) => {
        if (step === 3) { // Persistence layer sync
          setCurrentBlock((b) => {
            const nextBlock = b + 1;
            setCorrIdNumber((c) => {
              const nextCorr = c + 1;
              const nextCorrId = `CORR-2026-0528-${nextCorr}${validationBreach ? 'ERR' : 'X'}`;
              
              // Prepend audit log
              setReplayLogs((prevLogs) => {
                const newLog: ReplayLog = validationBreach 
                  ? {
                      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
                      corrId: nextCorrId,
                      block: nextBlock,
                      status: 'BREACH',
                      message: `CRITICAL: Contract schema breach detected on ${selectedLocationId.toUpperCase()} telemetry node.`
                    }
                  : {
                      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
                      corrId: nextCorrId,
                      block: nextBlock,
                      status: 'VERIFIED',
                      message: `Deterministic replay validated successfully for block #${nextBlock}.`
                    };
                return [newLog, ...prevLogs.slice(0, 14)];
              });

              if (validationBreach) {
                // Prepend active recovery event
                setRecoveryEvents((prevEvents) => [
                  {
                    id: `REC-${Math.floor(Math.random()*900)+100}`,
                    time: new Date().toLocaleTimeString('en-US', { hour12: false }),
                    type: 'SCHEMA_FALLBACK',
                    status: 'ACTIVE',
                    corrId: nextCorrId,
                    detail: `Anomalous schema structure on Block #${nextBlock}. Initiated fallback reconciliation buffer.`
                  },
                  ...prevEvents
                ]);
              }

              return nextCorr;
            });
            return nextBlock;
          });
        }
        return step;
      });

    }, 3000);

    return () => clearInterval(interval);
  }, [isSimulating, selectedLocationId, validationBreach]);

  const toggleBreachSimulation = () => {
    setValidationBreach((v) => !v);
  };

  const handleManualRecoveryResolve = (id: string) => {
    setRecoveryEvents((prev) => 
      prev.map(evt => evt.id === id ? { ...evt, status: 'RESOLVED' } : evt)
    );
  };

  const activeLocData = suitabilityLocations[selectedLocationId] || suitabilityLocations.varanasi;

  const renderContent = () => {
    switch (activeTab) {
      case 'global':
        return (
          <div className={styles.dashboard}>
            {/* Executive KPI Zone (Phase 5) */}
            <div className={styles.gridStats}>
              <IntelligenceCard 
                title="COMPOSITE SUITABILITY" 
                value={`${activeLocData.score}%`} 
                delta={activeLocData.level} 
                deltaType={activeLocData.score > 80 ? 'up' : activeLocData.score > 60 ? 'neutral' : 'down'} 
                color={activeLocData.score > 80 ? 'green' : activeLocData.score > 60 ? 'teal' : 'red'} 
              />
              <IntelligenceCard 
                title="FEDERATION STATE" 
                value={validationBreach ? 'ANOMALOUS' : 'DETERMINISTIC'} 
                delta={validationBreach ? 'BREACH ⚠' : '100% SYNC'} 
                deltaType={validationBreach ? 'down' : 'up'} 
                color={validationBreach ? 'red' : 'green'} 
              />
              <IntelligenceCard 
                title="ACTIVE CORRELATIONS" 
                value={`Block #${currentBlock}`} 
                delta="LIVE" 
                deltaType="neutral" 
                color="blue" 
              />
              <IntelligenceCard 
                title="DECISION CONFIDENCE" 
                value={`${activeLocData.confidence}%`} 
                delta="VERIFIED" 
                color="teal" 
              />
            </div>

            {/* Central Three-Column Observability Grid */}
            <div className={styles.mainGrid}>
              
              {/* Left Column: Federation Runtime Observability */}
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
                
                {/* Control Panel: Simulation variables */}
                <div className={styles.controlPanelCard}>
                  <div className={styles.cardHeader}>OPERATIONAL CONTROLS</div>
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
                      {validationBreach ? '✓ DISMISS CONTRACT BREACH' : '⚡ SIMULATE SCHEMA BREACH'}
                    </button>
                  </div>
                  <p className={styles.controlFootnote}>
                    *Simulation actions update internal registers to test schema compatibility fallback mechanisms.
                  </p>
                </div>
              </div>

              {/* Center Column: Geospatial Intelligence & Location scoring */}
              <div className={styles.centerCol}>
                <MapCard 
                  selectedMarkerId={selectedLocationId}
                  onMarkerSelect={setSelectedLocationId}
                  activeLayers={['waterways', 'seaplanes', 'logistics']}
                  activeLocationCoords={{ lat: activeLocData.lat, lng: activeLocData.lng }}
                />

                {/* Local Intelligence Synthesis Card (Nupur Explanation Layer) */}
                <div className={styles.locIntelCard}>
                  <div className={styles.locHeader}>
                    <div>
                      <span className={styles.locLabel}>CURRENTLY INSPECTING</span>
                      <h2 className={styles.locName}>{activeLocData.name}</h2>
                    </div>
                    <div className={styles.scoreBadge} style={{ borderLeftColor: activeLocData.score > 80 ? 'var(--eco-green)' : 'var(--amber)' }}>
                      <span className={styles.scoreVal}>{activeLocData.score}</span>
                      <span className={styles.scoreLevel} style={{ color: activeLocData.score > 80 ? 'var(--eco-green)' : 'var(--amber)' }}>{activeLocData.level} POTENTIAL</span>
                    </div>
                  </div>
                  
                  <div className={styles.locGrid}>
                    <div className={styles.locDetails}>
                      <span className={styles.subTitle}>SUITABILITY FACTORS</span>
                      <div className={styles.factorStack}>
                        {activeLocData.factors.map((f, i) => (
                          <div key={i} className={styles.factorItem}>
                            <div className={styles.factorLabelRow}>
                              <span>{f.label}</span>
                              <span style={{ color: f.color }}>{f.val}</span>
                            </div>
                            <div className={styles.factorProgress}>
                              <div className={styles.factorFill} style={{ width: f.fill, backgroundColor: f.color }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className={styles.locDetails}>
                      <span className={styles.subTitle}>ECOLOGICAL CONSTRAINTS</span>
                      <div className={styles.factorStack}>
                        {activeLocData.constraints.map((c, i) => (
                          <div key={i} className={styles.factorItem}>
                            <div className={styles.factorLabelRow}>
                              <span>{c.label}</span>
                              <span style={{ color: c.color }}>{c.val}</span>
                            </div>
                            <div className={styles.factorProgress}>
                              <div className={styles.factorFill} style={{ width: c.fill, backgroundColor: c.color }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className={styles.explanationSection}>
                    <span className={styles.subTitle}>DETERMINISTIC COGNITION EXPLANATION</span>
                    <p className={styles.explanationText}>{activeLocData.explanation}</p>
                    <div className={styles.infraTagsRow}>
                      {activeLocData.infrastructure.map((inf, i) => (
                        <span key={i} className={styles.infraTag}>⚡ {inf}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Replay Chain Observability & Validation States */}
              <div className={styles.rightCol}>
                <ReplayConsole 
                  currentBlock={currentBlock} 
                  corrId={`CORR-2026-0528-${corrIdNumber}${validationBreach ? 'ERR' : 'X'}`}
                  validationState={validationBreach ? 'VIOLATION' : 'VERIFIED'}
                  replayLogs={replayLogs}
                  isSimulating={isSimulating}
                />
              </div>

            </div>

            {/* Bottom Panel: Network Recovery & Audit Surface */}
            <div className={styles.bottomConsole}>
              <div className={styles.consoleHeader}>
                <span>RUNTIME RECOVERY & FEDERATION EVENT AUDITOR</span>
                <span className={styles.auditIndicator} style={{ color: validationBreach ? 'var(--alert-red)' : 'var(--teal)' }}>
                  {validationBreach ? '⚠ 1 UNRESOLVED ANOMALY IN BUFFER' : '✓ RECOVERY PERSISTENCE: SECURE'}
                </span>
              </div>
              <div className={styles.recoveryGrid}>
                {recoveryEvents.map((evt) => (
                  <div key={evt.id} className={styles.recoveryCard} style={{ borderLeftColor: evt.status === 'ACTIVE' ? 'var(--alert-red)' : 'var(--teal)' }}>
                    <div className={styles.recoveryCardHeader}>
                      <span className={styles.evtType}>{evt.type} ({evt.id})</span>
                      <span className={styles.evtTime}>{evt.time}</span>
                      <span className={evt.status === 'ACTIVE' ? styles.statusActiveBadge : styles.statusResolvedBadge}>
                        {evt.status}
                      </span>
                    </div>
                    <p className={styles.evtDetail}>{evt.detail}</p>
                    <div className={styles.evtFooter}>
                      <span>Corr ID: {evt.corrId}</span>
                      {evt.status === 'ACTIVE' && (
                        <button 
                          className={styles.resolveBtn}
                          onClick={() => handleManualRecoveryResolve(evt.id)}
                        >
                          MANUALLY RECONCILE CONTRACT
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
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
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <Topbar 
        liveFeed={validationBreach ? 'Anomaly Detected' : 'Active'}
        basinAlerts={summaryStats.basin_alerts}
        avgSuitability={summaryStats.avg_suitability}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onSignalMonitorClick={() => setActiveTab('signals')}
      />
      <div className={styles.content}>
        {renderContent()}
      </div>
    </main>
  );
}
