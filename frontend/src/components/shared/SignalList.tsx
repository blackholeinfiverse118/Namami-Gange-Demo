'use client';

import React from 'react';
import styles from './SignalList.module.css';

interface ReplayLog {
  timestamp: string;
  corrId: string;
  block: number;
  status: 'VERIFIED' | 'COMPATIBLE' | 'BREACH' | 'REPLAYING';
  message: string;
}

interface SignalListProps {
  logs?: ReplayLog[];
}

export default function SignalList({ logs }: SignalListProps) {
  const getSeverity = (status: string) => {
    switch (status) {
      case 'BREACH': return 'high';
      case 'REPLAYING': return 'medium';
      case 'COMPATIBLE': return 'low';
      case 'VERIFIED':
      default:
        return 'low';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'BREACH': return 'CRITICAL BREACH';
      case 'COMPATIBLE': return 'COMPATIBLE';
      case 'REPLAYING': return 'REPLAYING';
      case 'VERIFIED':
      default:
        return 'VERIFIED';
    }
  };

  // If logs is undefined, fall back to default historical logs
  const displayLogs = logs === undefined ? [
    { timestamp: '15:14:02', corrId: 'CORR-2026-0528-9941X', block: 1240, status: 'VERIFIED', message: 'Ingestion schema contract match on Varanasi-seaplane' },
    { timestamp: '15:13:48', corrId: 'CORR-2026-0528-9940Y', block: 1239, status: 'COMPATIBLE', message: 'Backward compatibility validated for Patna terminal payload' }
  ] as ReplayLog[] : logs;

  if (displayLogs.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '13px', border: '1px dashed var(--border)', borderRadius: '8px' }}>
        No telemetry events match the active filter criteria.
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {displayLogs.map((log, i) => {
        const severity = getSeverity(log.status);
        return (
          <div key={i} className={styles.item}>
            <div className={`${styles.indicator} ${styles[severity]}`}></div>
            <div className={styles.content}>
              <div className={styles.header}>
                <span className={styles.id}>{log.corrId.split('-').pop()}</span>
                <span className={styles.time}>{log.timestamp}</span>
              </div>
              <div className={styles.text}>{log.message}</div>
              <div className={styles.confidence}>
                <div 
                  className={styles.confBar} 
                  style={{ 
                    width: log.status === 'BREACH' ? '100%' : '94%',
                    backgroundColor: log.status === 'BREACH' ? 'var(--alert-red)' : 'var(--teal)'
                  }}
                ></div>
                <span className={styles.confLabel}>
                  Status: {getStatusText(log.status)} · Block #{log.block}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
