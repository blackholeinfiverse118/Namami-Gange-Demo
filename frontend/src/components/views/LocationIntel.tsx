'use client';

import React from 'react';
import styles from './View.module.css';
import TelemetryCard from '../shared/TelemetryCard';

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

interface LocationIntelProps {
  selectedLocationId?: string;
  activeLocation?: SuitabilityLocation;
}

export default function LocationIntel({ selectedLocationId = 'varanasi', activeLocation }: LocationIntelProps) {
  // Default fallback details in case parent is loading or empty
  const defaultLocs: Record<string, SuitabilityLocation> = {
    varanasi: {
      id: 'varanasi',
      name: 'Varanasi Corridor NW-1',
      score: 82,
      level: 'HIGH',
      factors: [
        { label: 'Water Quality (BOD)', val: 'Good (2.1 mg/L)', fill: '82%', color: 'var(--eco-green)' },
        { label: 'Navigational Draft', val: 'Optimal (3.2m)', fill: '88%', color: 'var(--river-blue)' },
        { label: 'Intermodal Connectivity', val: 'Excellent', fill: '90%', color: 'var(--teal)' },
        { label: 'Economic Potential', val: 'Very High', fill: '85%', color: 'var(--river-blue)' }
      ],
      constraints: [
        { label: 'Siltation Risk', val: 'Low-Mod (32%)', fill: '32%', color: 'var(--eco-green)' },
        { label: 'Flow Volatility', val: 'Moderate', fill: '45%', color: 'var(--amber)' },
        { label: 'Habitat Sensitivity', val: 'Protected Zone', fill: '70%', color: 'var(--alert-red)' }
      ],
      infrastructure: ['Inland Waterway Terminal', 'Railway Link Corridor', 'Multimodal Freight hub'],
      explanation: 'Varanasi features high suitability as an intermodal inland port due to reliable river depth (NW-1 corridor draft > 3m), ready rail alignment, and low siltation risk compared to eastern sections. Eco-constraints are moderate due to dolphin sanctuaries nearby.',
      tracerId: 'TRC-VNS-2026-X88',
      confidence: 94,
      lat: '25.3176° N',
      lng: '82.9739° E'
    }
  };

  const loc = activeLocation || defaultLocs[selectedLocationId] || defaultLocs.varanasi;

  // Map markers depending on coordinates
  const mapCX = loc.id === 'kanpur' ? 100 : loc.id === 'prayagraj' ? 210 : loc.id === 'varanasi' ? 280 : loc.id === 'patna' ? 410 : 510;
  const mapCY = loc.id === 'kanpur' ? 115 : loc.id === 'prayagraj' ? 125 : loc.id === 'varanasi' ? 160 : loc.id === 'patna' ? 175 : 205;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Location Intelligence · {loc.name.split(' ')[0]}</h1>
          <p className={styles.subtitle}>Strategic inland corridor candidate · NW-1 Corridor</p>
        </div>
        <div className={styles.actions}>
          <button className={styles.primaryBtn} onClick={() => alert(`Exporting intelligence packet for ${loc.name}...`)}>Export Location Report</button>
        </div>
      </div>

      <div className={styles.basinGrid}>
        <div className={styles.mapLarge} style={{ height: '100%', minHeight: '650px' }}>
          <div className={styles.placeholderMap} style={{ backgroundImage: 'radial-gradient(ellipse at center, #0f172a 0%, #050a14 100%)' }}>
             <svg viewBox="0 0 600 460" style={{ width: '100%', height: '100%', opacity: 0.8 }}>
                {/* Simulated river map */}
                <path d="M 50 120 Q 180 90 280 160 T 450 180 T 560 210" fill="none" stroke="var(--river-blue)" strokeWidth="12" opacity="0.15" />
                <path d="M 50 120 Q 180 90 280 160 T 450 180 T 560 210" fill="none" stroke="var(--river-light)" strokeWidth="2.5" />
                
                <circle cx={mapCX} cy={mapCY} r="16" fill="rgba(20, 184, 166, 0.2)" stroke="var(--teal)" strokeWidth="2" className={styles.mapRipple} />
                <circle cx={mapCX} cy={mapCY} r="5" fill="var(--teal)" />
                <path d={`M ${mapCX} ${mapCY} L ${mapCX + 60} ${mapCY - 60}`} fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="1" strokeDasharray="3,3" />
                <circle cx={mapCX + 60} cy={mapCY - 60} r="3" fill="var(--text-primary)" />
                <text x={mapCX + 70} y={mapCY - 57} fill="var(--text-primary)" fontSize="10" fontWeight="bold" fontFamily="var(--font-mono)">INSPECTION VECTOR</text>
                
                <text x={mapCX} y={mapCY + 25} fill="var(--teal)" fontSize="11" fontWeight="bold" fontFamily="var(--font-mono)" textAnchor="middle">{loc.name.toUpperCase()}</text>
             </svg>
             <div className={styles.mapLabel} style={{ position: 'absolute', bottom: '20px', left: '20px' }}>COGNITIVE COORDINATE ENGINE — LIVE</div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className={styles.listCard}>
            <div className={styles.cardTitle} style={{ marginBottom: '8px' }}>Suitability Score</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ position: 'relative', width: '60px', height: '60px' }}>
                <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="3" />
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={loc.score > 80 ? 'var(--eco-green)' : loc.score > 60 ? 'var(--amber)' : 'var(--alert-red)'} strokeWidth="3" strokeDasharray={`${loc.score}, 100`} />
                </svg>
                <div style={{ 
                  position: 'absolute', 
                  inset: 0, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  fontSize: '18px', 
                  fontWeight: '800', 
                  fontFamily: 'var(--font-display)', 
                  color: loc.score > 80 ? 'var(--eco-green)' : loc.score > 60 ? 'var(--amber)' : 'var(--alert-red)' 
                }}>{loc.score}</div>
              </div>
              <div>
                <div style={{ 
                  fontSize: '16px', 
                  fontWeight: '700', 
                  color: loc.score > 80 ? 'var(--eco-green)' : loc.score > 60 ? 'var(--amber)' : 'var(--alert-red)' 
                }}>{loc.level} POTENTIAL</div>
              </div>
            </div>
          </div>

          <TelemetryCard 
            stationName={loc.name} 
            metrics={loc.factors.map(f => ({
              label: f.label,
              value: f.val,
              fillPercent: parseFloat(f.fill),
              color: f.color
            }))} 
          />

          <div className={styles.listCard}>
            <div className={styles.cardTitle}>Infrastructure opportunities</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {loc.infrastructure.map((inf, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>⚡ {inf}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--eco-green)' }}>READY</span>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.listCard}>
            <div className={styles.cardTitle}>ECO-CONSTRAINTS & Silts</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {loc.constraints.map((c, i) => (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{c.label}</span>
                    <span style={{ color: c.color }}>{c.val}</span>
                  </div>
                  <div style={{ height: '4px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                    <div style={{ width: c.fill, height: '100%', backgroundColor: c.color }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.listCard}>
            <div className={styles.cardTitle}>Sources & deterministic Trace</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Tracer ID</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{loc.tracerId}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Confidence Registry</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--eco-green)' }}>{loc.confidence}% VERIFIED</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Geospatial coordinates</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{loc.lat} · {loc.lng}</span>
              </div>
            </div>
            <button className={styles.primaryBtn} style={{ width: '100%' }} onClick={() => alert(`Deterministic logic explanation: ${loc.explanation}`)}>View Reasoning Chain</button>
          </div>
        </div>
      </div>
    </div>
  );
}
