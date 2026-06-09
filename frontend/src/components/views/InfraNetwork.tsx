'use client';

import React from 'react';
import styles from './View.module.css';

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

interface InfraNetworkProps {
  selectedLocationId?: string;
  activeLocation?: SuitabilityLocation;
  validationBreach?: boolean;
}

export default function InfraNetwork({
  selectedLocationId = 'varanasi',
  activeLocation,
  validationBreach = false
}: InfraNetworkProps) {
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
  const healthValue = validationBreach ? '91.8% DEGRADED' : '99.9% SECURE';

  // Map markers coordinates
  const mapCX = loc.id === 'kanpur' ? 100 : loc.id === 'prayagraj' ? 200 : loc.id === 'varanasi' ? 290 : loc.id === 'patna' ? 390 : 470;
  const mapCY = loc.id === 'kanpur' ? 98 : loc.id === 'prayagraj' ? 120 : loc.id === 'varanasi' ? 140 : loc.id === 'patna' ? 180 : 210;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Infrastructure Network View</h1>
          <p className={styles.subtitle}>Ports · IWT Terminals · Logistics Parks · Corridor Connectivity</p>
        </div>
        <div className={styles.actions}>
          <button className={styles.primaryBtn} onClick={() => alert('Infrastructure map exported.')}>Export Network Map</button>
        </div>
      </div>

      <div className={styles.infoGrid} style={{ gridTemplateColumns: '1fr 300px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className={styles.mapLarge} style={{ height: '450px' }}>
            <div className={styles.placeholderMap} style={{ backgroundImage: 'radial-gradient(ellipse at center, #0a1730 0%, #030815 100%)' }}>
              <svg viewBox="0 0 540 360" style={{ width: '100%', height: '100%' }}>
                <rect width="540" height="360" fill="transparent" />
                {/* Rail corridors */}
                <path d="M 60 50 L 135 80 L 220 90 L 285 100 L 360 110 L 420 130 L 480 150" fill="none" stroke="rgba(136,153,170,0.2)" strokeWidth="2" />
                <path d="M 80 280 L 140 250 L 200 230 L 270 210 L 340 200 L 400 195 L 460 200" fill="none" stroke="rgba(136,153,170,0.2)" strokeWidth="2" />
                {/* Waterways */}
                <path d="M 55 90 Q 120 82 180 88 Q 240 92 300 96 Q 350 100 395 105 Q 430 110 465 118" fill="none" stroke="var(--river-blue)" strokeWidth="2.5" strokeDasharray="6,4" opacity="0.6" />
                
                {/* Active node highlight */}
                <circle cx={mapCX} cy={mapCY} r="18" fill="rgba(20, 184, 166, 0.15)" stroke="var(--teal)" strokeWidth="1.5" className={styles.mapRipple} />
                <circle cx={mapCX} cy={mapCY} r="6" fill="var(--teal)" />
                <text x={mapCX + 12} y={mapCY + 4} fill="var(--text-primary)" fontSize="9" fontWeight="bold" fontFamily="var(--font-mono)">{loc.name.split(' ')[0].toUpperCase()}</text>

                {/* Other Static Infrastructure Nodes */}
                <circle cx="85" cy="250" r="4" fill="var(--river-blue)" opacity="0.6" />
                <circle cx="455" cy="210" r="4" fill="var(--river-blue)" opacity="0.6" />
                <circle cx="310" cy="98" r="3" fill="var(--eco-green)" opacity="0.6" />
              </svg>
              <div className={styles.mapLabel}>INFRASTRUCTURE CONNECTIVITY NETWORK — ACTIVE</div>
            </div>
          </div>

          <div className={styles.statsRow} style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
            {[
              { label: 'Total Ports', value: '40', color: 'var(--river-blue)' },
              { label: 'IWT Terminals', value: '20', color: 'var(--teal)' },
              { label: 'Logistics Parks', value: '10', color: 'var(--amber)' },
              { label: 'Major Corridors', value: '7', color: 'var(--eco-green)' }
            ].map((stat, i) => (
              <div key={i} className={styles.listCard} style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '24px', 
                  fontWeight: '800', 
                  color: stat.color,
                  fontFamily: 'var(--font-display)'
                }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {stat.label}
                </div>
              </div>
            ))}
            <div className={styles.listCard} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)', fontFamily: 'var(--font-display)' }}>High</div>
              <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', marginTop: '4px', letterSpacing: '0.05em' }}>Density</div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className={styles.listCard}>
            <div className={styles.cardTitle}>Infrastructure Layers</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { label: 'Ports', color: 'var(--river-blue)', active: true },
                { label: 'IWT Terminals', color: 'var(--teal)', active: true },
                { label: 'Logistics Parks', color: 'var(--amber)', active: true },
                { label: 'Railways', color: '#8899AA', active: true },
                { label: 'National Highways', color: '#556677', active: true },
                { label: 'Waterways', color: 'var(--river-blue)', active: true },
              ].map((layer, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: layer.color }}></div>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{layer.label}</span>
                  </div>
                  <div style={{ 
                    width: '32px', 
                    height: '16px', 
                    borderRadius: '8px', 
                    backgroundColor: layer.active ? 'var(--teal)' : 'var(--surface-2)',
                    position: 'relative',
                    cursor: 'pointer',
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}>
                    <div style={{ 
                      position: 'absolute', 
                      width: '12px', 
                      height: '12px', 
                      backgroundColor: 'white', 
                      borderRadius: '50%', 
                      top: '1px', 
                      left: layer.active ? '17px' : '1px',
                      transition: 'left 0.2s'
                    }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.listCard} style={{ background: 'rgba(20,184,166,0.03)', borderColor: 'rgba(20,184,166,0.15)' }}>
            <div className={styles.cardTitle} style={{ color: 'var(--teal)' }}>Network Health</div>
            <div style={{ fontSize: '20px', fontWeight: '700', color: validationBreach ? 'var(--alert-red)' : 'var(--text-primary)' }}>{healthValue}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '4px' }}>
              {validationBreach ? 'Anomalous validation breach in buffer' : 'All corridors fully secure & operational'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
