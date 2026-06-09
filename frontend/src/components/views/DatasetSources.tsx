'use client';

import React from 'react';
import styles from './View.module.css';

interface DatasetSourcesProps {
  latencyMs?: number;
  currentBlock?: number;
  validationBreach?: boolean;
}

export default function DatasetSources({
  latencyMs = 6,
  currentBlock = 1240,
  validationBreach = false
}: DatasetSourcesProps) {
  
  const datasets = [
    { name: 'ISRO Bhuvan Satellite Imagery', source: 'ISRO', status: 'Good', updated: '6 Hrs', reliability: 98, version: 'v3.2', coverage: 'Basin-wide' },
    { name: 'CWC River Gauge Network', source: 'CWC', status: 'Good', updated: 'Real-time', reliability: 98, version: 'v3.2', coverage: 'National' },
    { name: 'MoPSW Inland Vessels API', source: 'MoPSW', status: validationBreach ? 'Syncing' : 'Good', updated: `${latencyMs}ms Delay`, reliability: validationBreach ? 85 : 98, version: 'v2.1', coverage: 'National' },
    { name: 'UP PCB Water Quality Sensors', source: 'UP PCB', status: validationBreach ? 'Breach ⚠' : 'Good', updated: 'Real-time', reliability: validationBreach ? 62 : 95, version: 'v1.4', coverage: 'UP State' },
    { name: 'IWAI IWT Terminals', source: 'IWAI', status: 'Good', updated: `Block #${currentBlock}`, reliability: 96, version: 'v2.3', coverage: 'NW-1 to NW-111' },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Dataset & Source Management</h1>
          <p className={styles.subtitle}>Active datasets · Source reliability · Ingestion status · Schema versions</p>
        </div>
        <div className={styles.actions}>
          <button className={styles.primaryBtn} onClick={() => alert('Datasets registry refreshed successfully.')}>Refresh All Sources</button>
        </div>
      </div>

      <div className={styles.statsRow} style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className={styles.listCard}>
          <div className={styles.cardTitle}>Total Datasets</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--river-blue)' }}>24</div>
        </div>
        <div className={styles.listCard}>
          <div className={styles.cardTitle}>Active</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--eco-green)' }}>{validationBreach ? '21' : '23'}</div>
        </div>
        <div className={styles.listCard}>
          <div className={styles.cardTitle}>Degraded</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: validationBreach ? 'var(--alert-red)' : 'var(--alert-orange)' }}>{validationBreach ? '3' : '1'}</div>
        </div>
        <div className={styles.listCard}>
          <div className={styles.cardTitle}>Avg Reliability</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--teal)' }}>{validationBreach ? '91%' : '96%'}</div>
        </div>
      </div>

      <div className={styles.listCard} style={{ padding: 0 }}>
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border)' }}>
          <div className={styles.cardTitle} style={{ margin: 0 }}>Source Registry</div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontWeight: '500' }}>SOURCE NAME</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontWeight: '500' }}>REFRESH DATA / LATENCY</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontWeight: '500' }}>HEALTH STATUS</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontWeight: '500' }}>COVERAGE</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((ds, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                  <td style={{ padding: '12px 16px', color: 'var(--text-primary)', fontWeight: '500' }}>{ds.name}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{ds.updated}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ 
                      display: 'inline-flex', 
                      alignItems: 'center', 
                      gap: '6px', 
                      fontSize: '11px', 
                      color: ds.status === 'Good' ? 'var(--eco-green)' : ds.status === 'Syncing' ? 'var(--river-blue)' : ds.status === 'Breach ⚠' ? 'var(--alert-red)' : 'var(--alert-orange)'
                    }}>
                      <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: ds.status === 'Good' ? 'var(--eco-green)' : ds.status === 'Syncing' ? 'var(--river-blue)' : ds.status === 'Breach ⚠' ? 'var(--alert-red)' : 'var(--alert-orange)' }}></div>
                      {ds.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-dim)' }}>{ds.coverage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
