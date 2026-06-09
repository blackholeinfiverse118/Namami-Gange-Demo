'use client';

import React from 'react';
import styles from './ReplayCard.module.css';

export interface ReplayCardProps {
  currentBlock: number;
  totalBlocks: number;
  correlationId: string;
  lineagePath: string[];
  validationState: 'VERIFIED' | 'BREACH' | 'PENDING';
  isSimulating?: boolean;
}

export default function ReplayCard({
  currentBlock,
  totalBlocks = 2400,
  correlationId,
  lineagePath = ['INGEST', 'VALIDATE', 'REPLAY', 'PERSIST', 'FEDERATE'],
  validationState,
  isSimulating = true
}: ReplayCardProps) {
  const getOverallStateColor = (state: string) => {
    switch (state) {
      case 'VERIFIED':
        return 'var(--teal)';
      case 'BREACH':
        return 'var(--alert-red)';
      case 'PENDING':
      default:
        return 'var(--amber)';
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <span className={styles.label}>OBSERVABILITY DECK</span>
          <h4 className={styles.title}>DETERMINISTIC REPLAY</h4>
        </div>
        <div className={styles.badge}>
          <span className={styles.badgePulse}></span>
          <span>OBSERVER</span>
        </div>
      </div>

      <div className={styles.stats}>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Correlation ID</span>
          <span className={styles.monoValue}>{correlationId}</span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Validation Registry</span>
          <span className={styles.monoValue} style={{ color: getOverallStateColor(validationState) }}>
            {validationState === 'VERIFIED' ? 'SHA-256 MATCHED' : validationState === 'BREACH' ? 'CONTRACT BREACH' : 'PENDING SECURE'}
          </span>
        </div>
      </div>

      <div className={styles.pipeline}>
        <span className={styles.sectionTitle}>REPLAY LINEAGE PATH</span>
        <div className={styles.lineageRow}>
          {lineagePath.map((step, idx) => (
            <div key={idx} className={styles.lineageStep}>
              <div 
                className={`${styles.stepDot} ${
                  validationState === 'BREACH' && idx === 1 ? styles.stepBreach : styles.stepActive
                }`}
              >
                {idx + 1}
              </div>
              <span className={styles.stepLabel}>{step}</span>
              {idx < lineagePath.length - 1 && <div className={styles.stepConnector}></div>}
            </div>
          ))}
        </div>
      </div>

      <div className={styles.progressSection}>
        <div className={styles.progressInfo}>
          <span>Deterministic Block: <strong className={styles.monoValue}>{currentBlock} / {totalBlocks}</strong></span>
          <span className={styles.monoValue}>{isSimulating ? '1.2x Speed' : 'PAUSED'}</span>
        </div>
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill} 
            style={{ width: `${Math.min(100, (currentBlock / totalBlocks) * 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
