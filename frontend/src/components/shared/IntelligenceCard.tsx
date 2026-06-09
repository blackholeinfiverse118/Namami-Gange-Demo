import React from 'react';
import styles from './IntelligenceCard.module.css';

interface Props {
  title: string;
  value: string | number;
  delta?: string;
  deltaType?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'teal' | 'amber' | 'red' | 'green';
}

export default function IntelligenceCard({ title, value, delta, deltaType, color = 'blue' }: Props) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.title}>{title}</span>
        <span className={styles.icon}>🔍</span>
      </div>
      <div className={`${styles.value} ${styles[color]}`}>{value}</div>
      {delta && (
        <div className={`${styles.delta} ${deltaType ? styles[deltaType] : ''}`}>
          {delta} <span className={styles.deltaLabel}>from baseline</span>
        </div>
      )}
    </div>
  );
}
