import React from 'react';
import styles from './SimulationControls.module.css';

interface SimulationControlsProps {
  weights: {
    eco: number;
    infra: number;
    connect: number;
    econ: number;
  };
  constraints: {
    flood: boolean;
    eco: boolean;
    lowflow: boolean;
    protected: boolean;
  };
  onWeightChange: (key: 'eco' | 'infra' | 'connect' | 'econ', value: number) => void;
  onConstraintChange: (key: 'flood' | 'eco' | 'lowflow' | 'protected', value: boolean) => void;
  onRunSimulation: () => void;
  isLoading: boolean;
}

export default function SimulationControls({
  weights,
  constraints,
  onWeightChange,
  onConstraintChange,
  onRunSimulation,
  isLoading
}: SimulationControlsProps) {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Scenario Parameters</h3>
      
      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Environmental</label>
          <span className={styles.value}>{weights.eco}%</span>
        </div>
        <input 
          type="range" 
          className={styles.slider} 
          min="0" 
          max="100" 
          value={weights.eco} 
          onChange={(e) => onWeightChange('eco', parseInt(e.target.value, 10))}
        />
      </div>

      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Infrastructure</label>
          <span className={styles.value}>{weights.infra}%</span>
        </div>
        <input 
          type="range" 
          className={styles.slider} 
          min="0" 
          max="100" 
          value={weights.infra} 
          onChange={(e) => onWeightChange('infra', parseInt(e.target.value, 10))}
        />
      </div>

      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Connectivity</label>
          <span className={styles.value}>{weights.connect}%</span>
        </div>
        <input 
          type="range" 
          className={styles.slider} 
          min="0" 
          max="100" 
          value={weights.connect} 
          onChange={(e) => onWeightChange('connect', parseInt(e.target.value, 10))}
        />
      </div>

      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Economic</label>
          <span className={styles.value}>{weights.econ}%</span>
        </div>
        <input 
          type="range" 
          className={styles.slider} 
          min="0" 
          max="100" 
          value={weights.econ} 
          onChange={(e) => onWeightChange('econ', parseInt(e.target.value, 10))}
        />
      </div>

      <div className={styles.constraints}>
        <h4 className={styles.subTitle}>Constraints</h4>
        <div className={styles.checkbox}>
          <input 
            type="checkbox" 
            id="flood" 
            checked={constraints.flood} 
            onChange={(e) => onConstraintChange('flood', e.target.checked)}
          />
          <label htmlFor="flood">Flood Risk</label>
        </div>
        <div className={styles.checkbox}>
          <input 
            type="checkbox" 
            id="eco" 
            checked={constraints.eco} 
            onChange={(e) => onConstraintChange('eco', e.target.checked)}
          />
          <label htmlFor="eco">Eco Sensitive Zone</label>
        </div>
        <div className={styles.checkbox}>
          <input 
            type="checkbox" 
            id="lowflow" 
            checked={constraints.lowflow} 
            onChange={(e) => onConstraintChange('lowflow', e.target.checked)}
          />
          <label htmlFor="lowflow">Low Flow Areas</label>
        </div>
        <div className={styles.checkbox}>
          <input 
            type="checkbox" 
            id="protected" 
            checked={constraints.protected} 
            onChange={(e) => onConstraintChange('protected', e.target.checked)}
          />
          <label htmlFor="protected">Protected Areas</label>
        </div>
      </div>

      <button className={styles.runBtn} onClick={onRunSimulation} disabled={isLoading}>
        <span>{isLoading ? 'Simulating...' : 'Run Simulation'}</span>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 3l14 9-14 9V3z" />
        </svg>
      </button>
    </div>
  );
}
