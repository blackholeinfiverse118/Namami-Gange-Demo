'use client';

import React, { useState } from 'react';
import styles from './View.module.css';
import SignalList from '../shared/SignalList';
import ReasoningPanel from '../shared/ReasoningPanel';
import MapCard from '../shared/MapCard';

interface ReplayLog {
  timestamp: string;
  corrId: string;
  block: number;
  status: 'VERIFIED' | 'COMPATIBLE' | 'BREACH' | 'REPLAYING';
  message: string;
}

interface RealtimeSignalsProps {
  replayLogs?: ReplayLog[];
  validationBreach?: boolean;
  selectedLocationId?: string;
  suitabilityLocations?: Record<string, any>;
  onLocationSelect?: (id: string) => void;
}

export default function RealtimeSignals({
  replayLogs = [],
  validationBreach = false,
  selectedLocationId = 'varanasi',
  suitabilityLocations,
  onLocationSelect
}: RealtimeSignalsProps) {
  const [activeFilter, setActiveFilter] = useState<'all' | 'alerts' | 'anomalies' | 'observations'>('all');
  const activeLocation = suitabilityLocations?.[selectedLocationId];

  // Filter logs dynamically based on the selected tab
  const filteredLogs = replayLogs.filter(log => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'alerts') return log.status === 'BREACH';
    if (activeFilter === 'anomalies') return log.status === 'BREACH' || log.status === 'REPLAYING';
    if (activeFilter === 'observations') return log.status === 'VERIFIED' || log.status === 'COMPATIBLE';
    return true;
  });

  // Chronological order for the timeline chart (oldest left, newest right)
  const displayLogs = [...replayLogs].reverse();
  const points = displayLogs.map((log, i) => {
    const totalPoints = displayLogs.length || 1;
    const x = i * (400 / Math.max(1, totalPoints - 1));
    let y = 70; // Default verified low stress
    if (log.status === 'BREACH') y = 15;
    else if (log.status === 'REPLAYING') y = 35;
    else if (log.status === 'COMPATIBLE') y = 55;
    
    // Add some deterministic deviation based on index/block to look like a smooth waveform
    const waveOffset = Math.sin(i * 1.5) * 4;
    y = Math.max(10, Math.min(85, y + waveOffset));
    
    return { x, y, status: log.status };
  });

  const chartPoints = points.length > 0 ? points : [
    { x: 0, y: 70, status: 'VERIFIED' },
    { x: 100, y: 40, status: 'VERIFIED' },
    { x: 200, y: 20, status: 'VERIFIED' },
    { x: 300, y: 50, status: 'VERIFIED' },
    { x: 400, y: 60, status: 'VERIFIED' }
  ];

  const pathD = chartPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
  const fillD = `${pathD} L 400 80 L 0 80 Z`;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Realtime Signal Center</h1>
          <p className={styles.subtitle}>Unified Event Stream, Telemetry & AI Synthesis</p>
        </div>
      </div>

      <div className={styles.signalsGrid}>
        <div className={styles.signalsListSide}>
          <div style={{ display: 'flex', gap: '20px', marginBottom: '16px', borderBottom: '1px solid var(--border)' }}>
            <button 
              onClick={() => setActiveFilter('all')}
              style={{ 
                background: 'none', 
                border: 'none', 
                borderBottom: activeFilter === 'all' ? '2px solid var(--river-blue)' : '2px solid transparent', 
                color: activeFilter === 'all' ? 'var(--river-blue)' : 'var(--text-secondary)', 
                paddingBottom: '10px', 
                fontSize: '13px', 
                fontWeight: '600', 
                cursor: 'pointer' 
              }}
            >
              All Events
            </button>
            <button 
              onClick={() => setActiveFilter('alerts')}
              style={{ 
                background: 'none', 
                border: 'none', 
                borderBottom: activeFilter === 'alerts' ? '2px solid var(--river-blue)' : '2px solid transparent', 
                color: activeFilter === 'alerts' ? 'var(--river-blue)' : 'var(--text-secondary)', 
                paddingBottom: '10px', 
                fontSize: '13px', 
                fontWeight: '600', 
                cursor: 'pointer' 
              }}
            >
              Alerts
            </button>
            <button 
              onClick={() => setActiveFilter('anomalies')}
              style={{ 
                background: 'none', 
                border: 'none', 
                borderBottom: activeFilter === 'anomalies' ? '2px solid var(--river-blue)' : '2px solid transparent', 
                color: activeFilter === 'anomalies' ? 'var(--river-blue)' : 'var(--text-secondary)', 
                paddingBottom: '10px', 
                fontSize: '13px', 
                fontWeight: '600', 
                cursor: 'pointer' 
              }}
            >
              Anomalies
            </button>
            <button 
              onClick={() => setActiveFilter('observations')}
              style={{ 
                background: 'none', 
                border: 'none', 
                borderBottom: activeFilter === 'observations' ? '2px solid var(--river-blue)' : '2px solid transparent', 
                color: activeFilter === 'observations' ? 'var(--river-blue)' : 'var(--text-secondary)', 
                paddingBottom: '10px', 
                fontSize: '13px', 
                fontWeight: '600', 
                cursor: 'pointer' 
              }}
            >
              Observations
            </button>
          </div>
          <SignalList logs={filteredLogs} />
        </div>
        
        <div className={styles.signalsDetailSide}>
          <div className={styles.mapSmall}>
            <MapCard 
              selectedMarkerId={selectedLocationId} 
              onMarkerSelect={onLocationSelect} 
              activeLayers={['waterways']}
            />
          </div>
          <ReasoningPanel activeLocation={activeLocation} />
          
          <div className={styles.listCard} style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3 className={styles.cardTitle} style={{ margin: 0 }}>Event Timeline (Last 24 Hours)</h3>
            </div>
            <div style={{ position: 'relative', height: '140px', width: '100%' }}>
              <svg viewBox="0 0 400 100" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                {/* Axes */}
                <line x1="0" y1="80" x2="400" y2="80" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="40" y1="0" x2="40" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="2,2" />
                <line x1="120" y1="0" x2="120" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="2,2" />
                <line x1="200" y1="0" x2="200" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="2,2" />
                <line x1="280" y1="0" x2="280" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="2,2" />
                <line x1="360" y1="0" x2="360" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="2,2" />
                
                {/* Labels */}
                <text x="40" y="95" fill="var(--text-dim)" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">00:00</text>
                <text x="120" y="95" fill="var(--text-dim)" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">06:00</text>
                <text x="200" y="95" fill="var(--text-dim)" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">12:00</text>
                <text x="280" y="95" fill="var(--text-dim)" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">18:00</text>
                <text x="360" y="95" fill="var(--text-dim)" fontSize="9" textAnchor="middle" fontFamily="var(--font-mono)">24:00</text>

                {/* Line chart */}
                <path 
                  d={pathD} 
                  fill="none" 
                  stroke={validationBreach ? 'var(--alert-red)' : 'var(--river-blue)'} 
                  strokeWidth="2.5" 
                />
                
                {/* Area fill */}
                <path 
                  d={fillD} 
                  fill={validationBreach ? 'rgba(239, 68, 68, 0.1)' : 'rgba(30,136,229,0.1)'} 
                />

                {/* Data points */}
                {chartPoints.map((p, i) => (
                  <g key={i}>
                    <circle 
                      cx={p.x} 
                      cy={p.y} 
                      r={p.status === 'BREACH' ? 4.5 : 3.5} 
                      fill={p.status === 'BREACH' ? 'var(--alert-red)' : p.status === 'COMPATIBLE' ? 'var(--amber)' : 'var(--river-blue)'} 
                      className={p.status === 'BREACH' ? styles.mapRipple : undefined}
                    />
                    {p.status === 'BREACH' && (
                      <circle 
                        cx={p.x} 
                        cy={p.y} 
                        r={7.5} 
                        fill="none" 
                        stroke="var(--alert-red)" 
                        strokeWidth="1"
                        style={{ opacity: 0.5 }}
                      />
                    )}
                  </g>
                ))}
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
