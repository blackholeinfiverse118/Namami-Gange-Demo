'use client';

import React from 'react';
import styles from './AlertCard.module.css';

export interface AlertCardProps {
  id: string;
  text: string;
  severity: 'low' | 'medium' | 'high';
  time: string;
  confidence: number;
  traceId?: string;
  onResolve?: (id: string) => void;
  status?: string;
}

export default function AlertCard({
  id,
  text,
  severity,
  time,
  confidence,
  traceId,
  onResolve,
  status = 'ACTIVE'
}: AlertCardProps) {
  const getSeverityClass = (sev: string) => {
    switch (sev) {
      case 'high':
        return styles.high;
      case 'medium':
        return styles.medium;
      case 'low':
      default:
        return styles.low;
    }
  };

  return (
    <div className={`${styles.card} ${getSeverityClass(severity)}`}>
      <div className={styles.header}>
        <span className={styles.alertId}>{id}</span>
        <span className={styles.time}>{time}</span>
        <span className={status === 'ACTIVE' ? styles.statusActive : styles.statusResolved}>
          {status}
        </span>
      </div>
      <p className={styles.text}>{text}</p>
      <div className={styles.footer}>
        <div className={styles.footerCol}>
          <span className={styles.label}>Confidence</span>
          <span className={styles.val}>{confidence}%</span>
        </div>
        {traceId && (
          <div className={styles.footerCol}>
            <span className={styles.label}>Trace ID</span>
            <span className={`${styles.val} ${styles.mono}`}>{traceId}</span>
          </div>
        )}
        {status === 'ACTIVE' && onResolve && (
          <button className={styles.actionBtn} onClick={() => onResolve(id)}>
            Reconcile
          </button>
        )}
      </div>
    </div>
  );
}
