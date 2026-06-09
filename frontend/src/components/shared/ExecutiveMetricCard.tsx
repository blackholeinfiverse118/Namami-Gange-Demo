'use client';

import React from 'react';
import styles from './ExecutiveMetricCard.module.css';

export interface ExecutiveMetricCardProps {
  title: string;
  value: string | number;
  description: string;
  insights: { text: string; status: 'healthy' | 'warning' | 'critical' }[];
  borderAccent?: 'green' | 'blue' | 'amber' | 'red';
}

export default function ExecutiveMetricCard({
  title,
  value,
  description,
  insights,
  borderAccent = 'blue'
}: ExecutiveMetricCardProps) {
  const getAccentClass = (accent: string) => {
    switch (accent) {
      case 'green': return styles.green;
      case 'amber': return styles.amber;
      case 'red': return styles.red;
      case 'blue':
      default:
        return styles.blue;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'var(--eco-green)';
      case 'warning': return 'var(--amber)';
      case 'critical': return 'var(--alert-red)';
      default: return 'var(--text-dim)';
    }
  };

  return (
    <div className={`${styles.card} ${getAccentClass(borderAccent)}`}>
      <div className={styles.header}>
        <span className={styles.label}>EXECUTIVE BRIEF</span>
        <h4 className={styles.title}>{title}</h4>
      </div>
      
      <div className={styles.valueRow}>
        <div className={styles.value}>{value}</div>
        <p className={styles.description}>{description}</p>
      </div>

      <div className={styles.insightsSection}>
        <span className={styles.insightsTitle}>OPERATIONAL SYNTHESIS</span>
        <div className={styles.insightsStack}>
          {insights.map((insight, i) => (
            <div key={i} className={styles.insightItem}>
              <span className={styles.dot} style={{ backgroundColor: getStatusColor(insight.status) }}></span>
              <span className={styles.insightText}>{insight.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
