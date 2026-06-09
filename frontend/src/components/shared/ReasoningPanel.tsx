'use client';

import React from 'react';
import styles from './ReasoningPanel.module.css';

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

interface ReasoningPanelProps {
  activeLocation?: SuitabilityLocation;
  target?: string;
  reasoning?: string;
  confidence?: number;
  tracerId?: string;
}

export default function ReasoningPanel({ 
  activeLocation,
  target,
  reasoning,
  confidence,
  tracerId
}: ReasoningPanelProps) {
  
  const displayTarget = target || (activeLocation 
    ? `${activeLocation.name} · Analysis Vector`
    : "Varanasi Sector — Anomaly SIG-0941");
    
  const displayReasoning = reasoning || (activeLocation 
    ? activeLocation.explanation 
    : "Anomaly detected due to sudden variance in water turbidity (Δ+15%) coupled with localized vessel congregation. Cross-referencing suggests unauthorized sand mining.");
    
  const displayConfidence = confidence || (activeLocation ? activeLocation.confidence : 94);
  const displayTracer = tracerId || (activeLocation ? activeLocation.tracerId : 'TRC-8829-X');

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.icon}>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <span className={styles.title}>AI Reasoning Engine</span>
      </div>
      
      <div className={styles.content}>
        <div className={styles.target}>{displayTarget}</div>
        <p className={styles.reasoning}>{displayReasoning}</p>
        
        <div className={styles.footer}>
          <div className={styles.stat}>
            <span className={styles.statLabel}>Confidence</span>
            <span className={styles.statValue} style={{ color: 'var(--teal)' }}>{displayConfidence}%</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statLabel}>Tracer Registry</span>
            <span className={styles.statValue}>{displayTracer}</span>
          </div>
        </div>
      </div>
      
      <div className={styles.actions}>
        <button className={styles.actionBtn} onClick={() => alert('Onsite monitoring unit deployed.')}>Deploy Onsite Unit</button>
        <button className={styles.secondaryBtn} onClick={() => alert('Anomaly dismissed from buffer.')}>Dismiss Signal</button>
      </div>
    </div>
  );
}
