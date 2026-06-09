import React from 'react';
import styles from './SimulationControls.module.css';

export default function SimulationControls() {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Scenario Parameters</h3>
      
      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Environmental</label>
          <span className={styles.value}>30%</span>
        </div>
        <input type="range" className={styles.slider} min="0" max="100" defaultValue="30" />
      </div>

      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Infrastructure</label>
          <span className={styles.value}>25%</span>
        </div>
        <input type="range" className={styles.slider} min="0" max="100" defaultValue="25" />
      </div>

      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Connectivity</label>
          <span className={styles.value}>25%</span>
        </div>
        <input type="range" className={styles.slider} min="0" max="100" defaultValue="25" />
      </div>

      <div className={styles.controlGroup}>
        <div className={styles.labelRow}>
          <label className={styles.label}>Economic</label>
          <span className={styles.value}>20%</span>
        </div>
        <input type="range" className={styles.slider} min="0" max="100" defaultValue="20" />
      </div>

      <div className={styles.constraints}>
        <h4 className={styles.subTitle}>Constraints</h4>
        <div className={styles.checkbox}>
          <input type="checkbox" id="flood" defaultChecked />
          <label htmlFor="flood">Flood Risk</label>
        </div>
        <div className={styles.checkbox}>
          <input type="checkbox" id="eco" defaultChecked />
          <label htmlFor="eco">Eco Sensitive Zone</label>
        </div>
        <div className={styles.checkbox}>
          <input type="checkbox" id="lowflow" />
          <label htmlFor="lowflow">Low Flow Areas</label>
        </div>
        <div className={styles.checkbox}>
          <input type="checkbox" id="protected" />
          <label htmlFor="protected">Protected Areas</label>
        </div>
      </div>

      <button className={styles.runBtn}>
        <span>Run Simulation</span>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 3l14 9-14 9V3z" />
        </svg>
      </button>
    </div>
  );
}
