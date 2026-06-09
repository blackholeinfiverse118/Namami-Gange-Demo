'use client';

import React from 'react';
import styles from './TelemetryCard.module.css';

export interface TelemetryCardProps {
  stationName: string;
  metrics: {
    label: string;
    value: string | number;
    fillPercent: number; // 0-100
    color: string;
  }[];
}

export default function TelemetryCard({ stationName, metrics }: TelemetryCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.label}>STATION TELEMETRY</span>
        <h4 className={styles.stationName}>{stationName}</h4>
      </div>
      <div className={styles.metricsStack}>
        {metrics.map((metric, i) => (
          <div key={i} className={styles.metricItem}>
            <div className={styles.labelRow}>
              <span className={styles.metricLabel}>{metric.label}</span>
              <span className={styles.metricVal} style={{ color: metric.color }}>{metric.value}</span>
            </div>
            <div className={styles.gaugeContainer}>
              <div 
                className={styles.gaugeFill} 
                style={{ 
                  width: `${Math.min(100, Math.max(0, metric.fillPercent))}%`,
                  backgroundColor: metric.color
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
