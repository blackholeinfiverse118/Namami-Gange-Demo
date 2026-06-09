'use client';

import React, { useState } from 'react';
import styles from './View.module.css';
import MapCard from '../shared/MapCard';
import SimulationControls from '../shared/SimulationControls';
import IntelligenceCard from '../shared/IntelligenceCard';

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
}

export default function ScenarioSimulation({
  selectedLocationId = 'varanasi',
  activeLocation,
  onLocationSelect
}: ScenarioSimulationProps) {
  const [simulationWeights, setSimulationWeights] = useState({
    eco: 30,
    infra: 25,
    connect: 25,
    econ: 20
  });

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

  // Let's compute a projected score based on slider weights (purely deterministic)
  const baseScore = loc.score;
  const ecoOffset = (simulationWeights.eco - 30) * 0.15;
  const infraOffset = (simulationWeights.infra - 25) * 0.25;
  const projectedScore = Math.max(15, Math.min(99, Math.round(baseScore + ecoOffset + infraOffset)));

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Scenario Simulation Engine · {loc.name.split(' ')[0]}</h1>
          <p className={styles.subtitle}>Predictive Modeling & "What-If" Analysis for Basin Development</p>
        </div>
      </div>

      <div className={styles.simulationGrid}>
        <div className={styles.controlsSide}>
          <SimulationControls />
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
                value={`${projectedScore > baseScore ? '+' : ''}${projectedScore - baseScore}%`} 
                delta="Projected" 
                color={projectedScore >= baseScore ? 'teal' : 'red'} 
              />
              <IntelligenceCard 
                title="Risk Delta" 
                value={projectedScore > baseScore ? '-8%' : '+15%'} 
                delta="Ecology Check" 
                color={projectedScore > baseScore ? 'green' : 'amber'} 
              />
              <IntelligenceCard 
                title="Econ Opportunity" 
                value={projectedScore > baseScore ? '+14%' : '-6%'} 
                delta="Projected Gain" 
                color="blue" 
              />
              <IntelligenceCard 
                title="Silt Buffer" 
                value="VERIFIED" 
                delta="Safe Limit" 
                color="teal" 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
