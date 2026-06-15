'use client';

import React, { useState, useEffect, useCallback } from 'react';
import styles from './View.module.css';
import MapCard from '../shared/MapCard';
import SimulationControls from '../shared/SimulationControls';
import IntelligenceCard from '../shared/IntelligenceCard';
import { runSimulation } from '@/services/api';

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

interface ScenarioSimulationProps {
  selectedLocationId?: string;
  activeLocation?: SuitabilityLocation;
  onLocationSelect?: (id: string) => void;
  selectedModel?: string;
}

export default function ScenarioSimulation({
  selectedLocationId = 'varanasi',
  activeLocation,
  onLocationSelect,
  selectedModel = 'inland_port'
}: ScenarioSimulationProps) {
  const [weights, setWeights] = useState({
    eco: 30,
    infra: 25,
    connect: 25,
    econ: 20
  });

  const [constraints, setConstraints] = useState({
    flood: true,
    eco: true,
    lowflow: false,
    protected: false
  });

  const [simulationResults, setSimulationResults] = useState<{
    baseline: any[];
    scenario: any[];
    delta: any[];
  } | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const defaultLocs: Record<string, SuitabilityLocation> = {
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
    }
  };

  const loc = activeLocation || defaultLocs[selectedLocationId] || defaultLocs.varanasi;

  const triggerSimulation = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const sum = weights.eco + weights.infra + weights.connect + weights.econ;
      const wEco = sum > 0 ? weights.eco / sum : 0;
      const wInfra = sum > 0 ? weights.infra / sum : 0;
      const wConnect = sum > 0 ? weights.connect / sum : 0;
      const wEcon = sum > 0 ? weights.econ / sum : 0;

      let priorityWeights: Record<string, number> = {};
      const model = selectedModel || 'inland_port';

      if (model === 'inland_port') {
        priorityWeights = {
          river_stability: parseFloat((wEco * 0.5).toFixed(4)),
          terminal_proximity: parseFloat(wInfra.toFixed(4)),
          logistics_access: parseFloat(wConnect.toFixed(4)),
          water_quality: parseFloat((wEco * 0.5).toFixed(4)),
          traffic_potential: parseFloat(wEcon.toFixed(4))
        };
      } else if (model === 'seaplane') {
        priorityWeights = {
          water_quality: parseFloat((wEco * (0.25 / 0.35)).toFixed(4)),
          env_clearance_adj: parseFloat((wEco * (0.10 / 0.35)).toFixed(4)),
          turbulence: parseFloat(wInfra.toFixed(4)),
          urban_proximity: parseFloat(wConnect.toFixed(4)),
          traffic_density: parseFloat(wEcon.toFixed(4))
        };
      } else if (model === 'hub_spoke') {
        priorityWeights = {
          node_proximity: parseFloat(wEco.toFixed(4)),
          terminal_density: parseFloat(wInfra.toFixed(4)),
          connectivity: parseFloat(wConnect.toFixed(4)),
          logistics_park: parseFloat((wEcon * (0.25 / 0.40)).toFixed(4)),
          market_access: parseFloat((wEcon * (0.15 / 0.40)).toFixed(4))
        };
      }

      // Check sum of priorityWeights and adjust rounding discrepancies to ensure exactly 1.0
      const weightKeys = Object.keys(priorityWeights);
      if (weightKeys.length > 0) {
        const weightSum = Object.values(priorityWeights).reduce((a, b) => a + b, 0);
        const diff = 1.0 - weightSum;
        if (Math.abs(diff) > 0.0001) {
          priorityWeights[weightKeys[0]] = parseFloat((priorityWeights[weightKeys[0]] + diff).toFixed(4));
        }
      }

      const excludeZones: string[] = [];
      if (!constraints.flood) excludeZones.push('flood_zone');
      if (!constraints.eco) excludeZones.push('wetland_zone');
      if (!constraints.lowflow) excludeZones.push('critical_depth');
      if (!constraints.protected) excludeZones.push('no_env_clearance');

      const body = {
        dataset_id: 'ganga_basin_reference',
        scenario: {
          scenario_id: 'custom',
          description: 'User modified weights',
          modifications: {
            priority_weights: priorityWeights,
            exclude_zones: excludeZones
          }
        },
        model_type: model
      };

      const res = await runSimulation(body);
      if (res && res.status === 'success') {
        setSimulationResults(res);
      } else {
        throw new Error('Simulation failed to return success status');
      }
    } catch (err: any) {
      console.error('Simulation error:', err);
      setError(err.message || 'An error occurred during simulation');
    } finally {
      setIsLoading(false);
    }
  }, [weights, constraints, selectedModel]);

  // Run simulation on mount and when selectedModel/selectedLocationId changes
  useEffect(() => {
    triggerSimulation();
  }, [selectedLocationId, selectedModel]);

  const handleWeightChange = (key: 'eco' | 'infra' | 'connect' | 'econ', val: number) => {
    setWeights(prev => ({
      ...prev,
      [key]: val
    }));
  };

  const handleConstraintChange = (key: 'flood' | 'eco' | 'lowflow' | 'protected', val: boolean) => {
    setConstraints(prev => ({
      ...prev,
      [key]: val
    }));
  };

  // Helper to extract baseline & scenario results for active location
  const getSelectedResult = (list: any[]) => {
    if (!list) return null;
    return list.find((r: any) => {
      const locId = r.location_id.toLowerCase();
      const targetId = selectedLocationId.toLowerCase();
      if (targetId === 'varanasi') return locId.includes('varanasi');
      if (targetId === 'patna') return locId.includes('patna');
      if (targetId === 'kanpur') return locId.includes('kanpur');
      if (targetId === 'prayagraj') return locId.includes('prayagraj') || locId.includes('allahabad');
      if (targetId === 'kolkata') return locId.includes('kolkata') || locId.includes('farakka') || locId.includes('hajipur');
      return locId.includes(targetId);
    });
  };

  const baselineResult = simulationResults ? getSelectedResult(simulationResults.baseline) : null;
  const scenarioResult = simulationResults ? getSelectedResult(simulationResults.scenario) : null;

  const baseScore = baselineResult ? Math.round(baselineResult.score) : loc.score;
  const projectedScore = scenarioResult ? Math.round(scenarioResult.score) : baseScore;

  // Calculate dynamic summary metrics
  const suitabilityShift = projectedScore - baseScore;
  const shiftText = `${suitabilityShift > 0 ? '+' : ''}${suitabilityShift}%`;
  const shiftColor: 'blue' | 'teal' | 'amber' | 'red' | 'green' = suitabilityShift > 0 ? 'teal' : suitabilityShift < 0 ? 'red' : 'blue';

  let riskVal = 'VERIFIED';
  let riskColor: 'blue' | 'teal' | 'amber' | 'red' | 'green' = 'green';
  if (scenarioResult?.level === 'REJECTED') {
    riskVal = 'REJECTED';
    riskColor = 'red';
  } else if (baselineResult?.level === 'REJECTED' && scenarioResult?.level !== 'REJECTED') {
    riskVal = 'RESOLVED';
    riskColor = 'green';
  } else if (baselineResult && scenarioResult) {
    const bCount = (baselineResult.constraints?.hard?.length || 0) + (baselineResult.constraints?.soft?.length || 0);
    const sCount = (scenarioResult.constraints?.hard?.length || 0) + (scenarioResult.constraints?.soft?.length || 0);
    const diff = sCount - bCount;
    if (diff < 0) {
      riskVal = `${diff} Constraint${Math.abs(diff) > 1 ? 's' : ''}`;
      riskColor = 'green';
    } else if (diff > 0) {
      riskVal = `+${diff} Constraint${diff > 1 ? 's' : ''}`;
      riskColor = 'amber';
    } else {
      riskVal = 'UNALTERED';
      riskColor = 'teal';
    }
  }

  let econKey = 'traffic_potential';
  if (selectedModel === 'seaplane') econKey = 'traffic_density';
  if (selectedModel === 'hub_spoke') econKey = 'market_access';

  const bEcon = baselineResult?.factor_scores?.[econKey] ?? 0;
  const sEcon = scenarioResult?.factor_scores?.[econKey] ?? 0;
  const econDiff = Math.round(sEcon - bEcon);
  const econVal = econDiff === 0 ? 'STABLE' : `${econDiff > 0 ? '+' : ''}${econDiff}%`;
  const econColor: 'blue' | 'teal' | 'amber' | 'red' | 'green' = econDiff >= 0 ? 'blue' : 'red';

  let siltVal = 'VERIFIED';
  let siltColor: 'blue' | 'teal' | 'amber' | 'red' | 'green' = 'teal';
  if (scenarioResult?.constraints?.overridden?.length > 0) {
    siltVal = 'BYPASSED';
    siltColor = 'amber';
  } else if (scenarioResult?.constraints?.hard?.length > 0 || scenarioResult?.constraints?.soft?.length > 0) {
    siltVal = 'CONSTRAINED';
    siltColor = 'amber';
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Scenario Simulation Engine · {loc.name.split(' ')[0]}</h1>
          <p className={styles.subtitle}>Predictive Modeling & "What-If" Analysis for Basin Development</p>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'var(--alert-red-transparent, rgba(239, 83, 80, 0.1))', border: '1px dashed var(--alert-red)', color: 'var(--alert-red)', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '13px' }}>
          <strong>Simulation Error:</strong> {error}
        </div>
      )}

      <div className={styles.simulationGrid}>
        <div className={styles.controlsSide}>
          <SimulationControls 
            weights={weights}
            constraints={constraints}
            onWeightChange={handleWeightChange}
            onConstraintChange={handleConstraintChange}
            onRunSimulation={triggerSimulation}
            isLoading={isLoading}
          />
        </div>
        
        <div className={styles.visualSide}>
          <div className={styles.comparisonGrid}>
            <div className={styles.compareItem}>
              <div className={styles.compareLabel}>Baseline (A) · {loc.name.split(' ')[0]} (Score: {baseScore}%)</div>
              <div className={styles.miniMap}>
                <MapCard 
                  selectedMarkerId={selectedLocationId}
                  onMarkerSelect={onLocationSelect}
                  activeLayers={['waterways']}
                />
              </div>
            </div>
            <div className={styles.compareItem}>
              <div className={styles.compareLabel}>Projected (B) · {loc.name.split(' ')[0]} (Score: {projectedScore}%)</div>
              <div className={styles.miniMap}>
                <MapCard 
                  selectedMarkerId={selectedLocationId}
                  onMarkerSelect={onLocationSelect}
                  activeLayers={['waterways', 'seaplanes', 'logistics']}
                />
              </div>
            </div>
          </div>

          <div className={styles.deltaAnalysis}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 className={styles.analysisTitle} style={{ margin: 0 }}>Model delta summary</h3>
            </div>
            <div className={styles.statsRow} style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
              <IntelligenceCard 
                title="Suitability Shift" 
                value={shiftText} 
                delta="Projected" 
                color={shiftColor} 
              />
              <IntelligenceCard 
                title="Risk Delta" 
                value={riskVal} 
                delta="Ecology Check" 
                color={riskColor} 
              />
              <IntelligenceCard 
                title="Econ Opportunity" 
                value={econVal} 
                delta="Projected Gain" 
                color={econColor} 
              />
              <IntelligenceCard 
                title="Silt Buffer" 
                value={siltVal} 
                delta="Safe Limit" 
                color={siltColor} 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
