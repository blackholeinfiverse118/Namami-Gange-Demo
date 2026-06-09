'use client';

import React from 'react';
import styles from './ReplayConsole.module.css';

interface ReplayLog {
  timestamp: string;
  corrId: string;
  block: number;
  status: 'VERIFIED' | 'COMPATIBLE' | 'BREACH' | 'REPLAYING';
  message: string;
}

interface ReplayConsoleProps {
  currentBlock?: number;
  totalBlocks?: number;
  corrId?: string;
  validationState?: 'VERIFIED' | 'VIOLATION' | 'SYNCING';
  replayLogs?: ReplayLog[];
  isSimulating?: boolean;
}

export default function ReplayConsole({
  currentBlock = 1208,
  totalBlocks = 2400,
  corrId = 'CORR-2026-0528-9941X',
  validationState = 'VERIFIED',
  replayLogs = [
    { timestamp: '15:14:02', corrId: 'CORR-2026-0528-9941X', block: 1208, status: 'VERIFIED', message: 'Ingestion schema contract match on Varanasi-seaplane' },
    { timestamp: '15:13:58', corrId: 'CORR-2026-0528-9940Y', block: 1207, status: 'COMPATIBLE', message: 'Backward compatibility validated for Patna terminal payload' },
    { timestamp: '15:13:50', corrId: 'CORR-2026-0528-9939Z', block: 1206, status: 'VERIFIED', message: 'State synchronization check matched (0ms deviation)' }
  ],
  isSimulating = true
}: ReplayConsoleProps) {
  
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'VERIFIED': return styles.statusVerified;
      case 'COMPATIBLE': return styles.statusCompatible;
      case 'BREACH': return styles.statusBreach;
      case 'REPLAYING': return styles.statusReplaying;
      default: return '';
    }
  };

  const getOverallStateColor = (state: string) => {
    switch (state) {
      case 'VERIFIED': return 'var(--teal)';
      case 'VIOLATION': return 'var(--alert-red)';
      case 'SYNCING': return 'var(--amber)';
      default: return 'var(--text-dim)';
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <span className={styles.title}>DETERMINISTIC REPLAY PIPELINE</span>
          <p className={styles.subtitle}>Read-Only Observability Console</p>
        </div>
        <div className={styles.badge}>
          <span className={styles.badgePulse}></span>
          <span>OBSERVER MODE</span>
        </div>
      </div>

      <div className={styles.trackerGrid}>
        <div className={styles.trackerCard}>
          <span className={styles.label}>Correlation ID</span>
          <span className={styles.valueMono}>{corrId}</span>
        </div>
        <div className={styles.trackerCard}>
          <span className={styles.label}>Validation Hash</span>
          <span className={styles.valueMono} style={{ color: getOverallStateColor(validationState) }}>
            {validationState === 'VERIFIED' ? 'SHA-256 MATCHED' : validationState === 'VIOLATION' ? 'CONTRACT BREACH' : 'CALCULATING'}
          </span>
        </div>
      </div>

      <div className={styles.progressSection}>
        <div className={styles.progressInfo}>
          <span>Deterministic Block: <strong className={styles.valueMono}>{currentBlock} / {totalBlocks}</strong></span>
          <span className={styles.valueMono}>{isSimulating ? '1.2x Speed' : 'PAUSED'}</span>
        </div>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${(currentBlock / totalBlocks) * 100}%` }}></div>
        </div>
      </div>

      {/* Contract & Compatibility Metrics */}
      <div className={styles.contractSection}>
        <span className={styles.sectionHeader}>ANKITA VALIDATION LAYER</span>
        <div className={styles.contractItem}>
          <span>JSON Schema Matcher</span>
          <span className={styles.chipGood}>100% PASS</span>
        </div>
        <div className={styles.contractItem}>
          <span>Backward compatibility contract</span>
          <span className={styles.chipGood}>SECURE</span>
        </div>
        <div className={styles.contractItem}>
          <span>Validation State</span>
          <span style={{ color: getOverallStateColor(validationState), fontWeight: 'bold' }}>{validationState}</span>
        </div>
      </div>

      {/* Chronological Audit Logs */}
      <div className={styles.auditSection}>
        <span className={styles.sectionHeader}>DETERMINISTIC LINEAGE LOGS</span>
        <div className={styles.logList}>
          {replayLogs.map((log, i) => (
            <div key={i} className={styles.logItem}>
              <div className={styles.logHeader}>
                <span className={styles.logTime}>{log.timestamp}</span>
                <span className={`${styles.logStatus} ${getStatusClass(log.status)}`}>{log.status}</span>
                <span className={styles.logBlock}>Block #{log.block}</span>
              </div>
              <p className={styles.logMsg}>{log.message}</p>
              <div className={styles.logFooter}>
                <span>Corr: {log.corrId}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
