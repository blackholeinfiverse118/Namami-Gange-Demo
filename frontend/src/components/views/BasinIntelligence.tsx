'use client';

import React, { useState, useEffect } from 'react';
import styles from './View.module.css';
import { fetchDigitalDepthSummary } from '@/services/api';

interface BasinIntelligenceProps {
  selectedLocationId?: string;
  onLocationSelect?: (id: string) => void;
  validationBreach?: boolean;
  suitabilityLocations?: Record<string, any>;
}

export default function BasinIntelligence({
  selectedLocationId = 'varanasi',
  onLocationSelect,
  validationBreach = false,
  suitabilityLocations
}: BasinIntelligenceProps) {
  
  // Layer Switch States
  const [activeLayers, setActiveLayers] = useState<Record<string, boolean>>({
    'River Network': true,
    'Monitoring Stations': true,
    'Barrages & Dams': true,
    'IWT Terminals': true,
    'Ports & Jetties': true,
    'Logistics Parks': true,
    'Environmental Zones': true,
    'Suitability Heatmap': true,
  });

  // Live Layer Counts from /digital-depth summary
  const [layerCounts, setLayerCounts] = useState<Record<string, number>>({
    'River Network': 3,
    'Environmental Zones': 3,
    'Barrages & Dams': 2,
    'IWT Terminals': 3,
    'Ports & Jetties': 3
  });

  useEffect(() => {
    async function loadDepthSummary() {
      try {
        const depthData = await fetchDigitalDepthSummary();
        if (depthData?.layers) {
          setLayerCounts({
            'River Network': depthData.layers.physical?.feature_count || 3,
            'Environmental Zones': depthData.layers.ecological?.feature_count || 3,
            'Barrages & Dams': depthData.layers.policy?.feature_count || 2,
            'IWT Terminals': depthData.layers.infrastructure?.feature_count || 3,
            'Ports & Jetties': depthData.layers.economic?.feature_count || 3
          });
        }
      } catch (err) {
        console.error('Failed to load depth summary:', err);
      }
    }
    loadDepthSummary();
  }, []);

  const handleNodeClick = (id: string) => {
    if (onLocationSelect) {
      onLocationSelect(id);
    }
  };

  const getMarkerColor = (id: string) => {
    const loc = suitabilityLocations?.[id];
    if (!loc) {
      if (id === 'kanpur') return 'var(--alert-red)';
      if (id === selectedLocationId) return 'var(--teal)';
      return '#FFB300';
    }
    if (id === selectedLocationId) return 'var(--teal)';
    if (loc.level === 'HIGH') return 'var(--eco-green)';
    if (loc.level === 'MEDIUM') return 'var(--amber)';
    return 'var(--alert-red)';
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Ganga Basin Intelligence</h1>
          <p className={styles.subtitle}>Detailed River System, Infrastructure & Environmental Metrics</p>
        </div>
      </div>

      <div className={styles.basinGrid}>
        <div className={styles.mapLarge} style={{ height: '650px' }}>
          <div className={styles.placeholderMap} style={{ background: '#040e1c' }}>
            <svg viewBox="0 0 600 460" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
              <rect width="600" height="460" fill="transparent" />
              {/* Basin region highlighted */}
              <path
                d="M 130 60 Q 160 55 200 65 Q 240 58 280 62 Q 320 56 360 68 Q 390 72 415 85 Q 420 100 415 118 Q 408 130 400 145 Q 390 158 375 168 Q 358 175 338 180 Q 316 184 294 182 Q 272 180 252 175 Q 230 168 210 158 Q 190 148 172 135 Q 155 122 142 105 Q 132 88 130 72 Z"
                fill="rgba(30,136,229,0.07)" stroke="rgba(30,136,229,0.2)" strokeWidth="1"
                strokeDasharray="4,4" 
              />

              {/* Suitability Heatmap Glow */}
              {activeLayers['Suitability Heatmap'] && (
                <ellipse cx="280" cy="110" rx="140" ry="40" fill="rgba(20,184,166,0.04)" filter="blur(8px)" pointerEvents="none" />
              )}

              {/* River Network Layer */}
              {activeLayers['River Network'] && (
                <>
                  {/* Main Ganga with suitability coloring */}
                  <path
                    d="M 128 92 Q 155 88 185 90 Q 210 92 235 94 Q 258 96 280 100 Q 302 103 322 108 Q 340 112 358 116 Q 372 120 385 125"
                    fill="none" stroke="var(--river-blue)" strokeWidth="3.5" strokeLinecap="round" 
                  />
                  {/* Tributaries */}
                  <path d="M 195 58 Q 200 72 205 86 Q 210 96 215 106 Q 218 115 218 125 Q 216 138 212 148 Q 208 158 203 168" fill="none" stroke="#42A5F5" strokeWidth="2" opacity="0.7" />
                  <path d="M 270 58 Q 275 72 278 86 Q 280 98 278 112 Q 275 124 272 136" fill="none" stroke="#42A5F5" strokeWidth="2" opacity="0.6" />
                  <path d="M 318 140 Q 312 152 305 162 Q 298 172 290 182" fill="none" stroke="#42A5F5" strokeWidth="1.5" opacity="0.5" />
                </>
              )}

              {/* Monitoring Stations Layer */}
              {activeLayers['Monitoring Stations'] && (
                <>
                  {/* Kanpur node */}
                  <g onClick={() => handleNodeClick('kanpur')} style={{ cursor: 'pointer' }}>
                    <circle cx="260" cy="97" r={selectedLocationId === 'kanpur' ? 12 : 7} fill="rgba(229,57,53,0.2)" stroke="var(--alert-red)" strokeWidth="1.5" className={selectedLocationId === 'kanpur' ? styles.mapRipple : ''} />
                    <circle cx="260" cy="97" r="4" fill="var(--alert-red)" />
                  </g>

                  {/* Prayagraj node */}
                  <g onClick={() => handleNodeClick('prayagraj')} style={{ cursor: 'pointer' }}>
                    <circle cx="185" cy="90" r={selectedLocationId === 'prayagraj' ? 12 : 7} fill="rgba(255,179,0,0.2)" stroke={getMarkerColor('prayagraj')} strokeWidth="1.5" className={selectedLocationId === 'prayagraj' ? styles.mapRipple : ''} />
                    <circle cx="185" cy="90" r="3" fill={getMarkerColor('prayagraj')} />
                  </g>

                  {/* Varanasi node */}
                  <g onClick={() => handleNodeClick('varanasi')} style={{ cursor: 'pointer' }}>
                    <circle cx="296" cy="100" r={selectedLocationId === 'varanasi' ? 12 : 7} fill="rgba(16,185,129,0.2)" stroke={getMarkerColor('varanasi')} strokeWidth="1.5" className={selectedLocationId === 'varanasi' ? styles.mapRipple : ''} />
                    <circle cx="296" cy="100" r="3" fill={getMarkerColor('varanasi')} />
                  </g>

                  {/* Patna node */}
                  <g onClick={() => handleNodeClick('patna')} style={{ cursor: 'pointer' }}>
                    <circle cx="318" cy="120" r={selectedLocationId === 'patna' ? 12 : 7} fill="rgba(20,184,166,0.2)" stroke={getMarkerColor('patna')} strokeWidth="1.5" className={selectedLocationId === 'patna' ? styles.mapRipple : ''} />
                    <circle cx="318" cy="120" r="3" fill={getMarkerColor('patna')} />
                  </g>

                  {/* Kolkata node */}
                  <g onClick={() => handleNodeClick('kolkata')} style={{ cursor: 'pointer' }}>
                    <circle cx="358" cy="125" r={selectedLocationId === 'kolkata' ? 12 : 7} fill="rgba(16,185,129,0.2)" stroke={getMarkerColor('kolkata')} strokeWidth="1.5" className={selectedLocationId === 'kolkata' ? styles.mapRipple : ''} />
                    <circle cx="358" cy="125" r="3" fill={getMarkerColor('kolkata')} />
                  </g>
                </>
              )}

              {/* Ports & Jetties (Economic Layer) */}
              {activeLayers['Ports & Jetties'] && (
                <>
                  <rect x="190" y="96" width="6" height="6" rx="1" fill="#42A5F5" opacity="0.8" transform="rotate(45,193,99)" />
                  <rect x="298" y="104" width="6" height="6" rx="1" fill="#42A5F5" opacity="0.8" transform="rotate(45,301,107)" />
                </>
              )}

              {/* Barrages & Dams (Policy Layer) */}
              {activeLayers['Barrages & Dams'] && (
                <>
                  <rect x="168" y="88" width="8" height="4" rx="1" fill="#FFB300" opacity="0.9" />
                  <rect x="310" y="104" width="8" height="4" rx="1" fill="#FFB300" opacity="0.9" />
                </>
              )}

              {/* Environmental Zones Layer */}
              {activeLayers['Environmental Zones'] && (
                <>
                  <ellipse cx="215" cy="155" rx="28" ry="20" fill="rgba(76,175,80,0.08)" stroke="rgba(76,175,80,0.4)" strokeWidth="0.8" strokeDasharray="3,3" />
                  <ellipse cx="350" cy="140" rx="22" ry="16" fill="rgba(76,175,80,0.08)" stroke="rgba(76,175,80,0.4)" strokeWidth="0.8" strokeDasharray="3,3" />
                </>
              )}

              {/* Labels */}
              <text x="170" y="82" fontSize="7" fill="#90CAF9" fontFamily="var(--font-mono)">HARIDWAR</text>
              <text x="185" y="105" fontSize="7" fill={selectedLocationId === 'prayagraj' ? 'var(--teal)' : '#90CAF9'} fontFamily="var(--font-mono)" fontWeight={selectedLocationId === 'prayagraj' ? 'bold' : 'normal'}>PRAYAGRAJ</text>
              <text x="255" y="108" fontSize="7" fill={selectedLocationId === 'kanpur' ? 'var(--teal)' : 'var(--alert-red)'} fontFamily="var(--font-mono)" fontWeight="bold">KANPUR ⚠</text>
              <text x="296" y="90" fontSize="7" fill={selectedLocationId === 'varanasi' ? 'var(--teal)' : '#90CAF9'} fontFamily="var(--font-mono)" fontWeight={selectedLocationId === 'varanasi' ? 'bold' : 'normal'}>VARANASI</text>
              <text x="318" y="132" fontSize="7" fill={selectedLocationId === 'patna' ? 'var(--teal)' : '#90CAF9'} fontFamily="var(--font-mono)" fontWeight={selectedLocationId === 'patna' ? 'bold' : 'normal'}>PATNA</text>
              <text x="358" y="117" fontSize="7" fill={selectedLocationId === 'kolkata' ? 'var(--teal)' : '#90CAF9'} fontFamily="var(--font-mono)" fontWeight={selectedLocationId === 'kolkata' ? 'bold' : 'normal'}>KOLKATA</text>

              {/* Suitability Legend */}
              <rect x="430" y="50" width="140" height="50" rx="4" fill="rgba(8,18,32,0.8)" stroke="rgba(255,255,255,0.06)" />
              <text x="445" y="65" fontSize="8" fill="#8899AA" fontFamily="Inter" fontWeight="600">SUITABILITY</text>
              <defs>
                <linearGradient id="suitGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="var(--alert-red)" />
                  <stop offset="50%" stopColor="var(--amber)" />
                  <stop offset="100%" stopColor="var(--eco-green)" />
                </linearGradient>
              </defs>
              <rect x="445" y="72" width="110" height="6" rx="2" fill="url(#suitGrad)" />
              <text x="445" y="90" fontSize="7" fill="#556070" fontFamily="Inter">Low</text>
              <text x="555" y="90" fontSize="7" fill="var(--eco-green)" fontFamily="Inter" textAnchor="end">High</text>
            </svg>
            <p className={styles.mapLabel}>
              RIVER BASIN MAPPING ENGINE — {validationBreach ? 'DEGRADED REGISTER' : 'ACTIVE'}
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className={styles.listCard}>
            <div className={styles.cardTitle}>Ganga Basin Overview</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Length</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>2,525 km</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Active Channels</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--river-light)' }}>NW-1 Corridor</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Federation State</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: validationBreach ? 'var(--alert-red)' : 'var(--teal)', fontWeight: 'bold' }}>
                  {validationBreach ? 'BREACH STATE ⚠' : 'Deterministic'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-dim)' }}>Currently Inspecting</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--teal)', fontWeight: 'bold' }}>
                  {selectedLocationId.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <div className={styles.listCard}>
            <div className={styles.cardTitle}>Layer Controls</div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {[
                { label: 'River Network', icon: '〰️' },
                { label: 'Monitoring Stations', icon: '📡' },
                { label: 'Barrages & Dams', icon: '🚧' },
                { label: 'IWT Terminals', icon: '⚓' },
                { label: 'Ports & Jetties', icon: '🚢' },
                { label: 'Logistics Parks', icon: '🏭' },
                { label: 'Environmental Zones', icon: '🌿' },
                { label: 'Suitability Heatmap', icon: '🔥' },
              ].map((layer, i) => {
                const isActive = activeLayers[layer.label] ?? false;
                const count = layerCounts[layer.label];
                const displayName = count !== undefined ? `${layer.label} (${count})` : layer.label;

                return (
                  <div 
                    key={i} 
                    className={styles.layerToggle} 
                    onClick={() => setActiveLayers(prev => ({ ...prev, [layer.label]: !prev[layer.label] }))} 
                    style={{ cursor: 'pointer' }}
                  >
                    <div className={styles.layerLabel}>
                      <span style={{ width: '16px', textAlign: 'center' }}>{layer.icon}</span>
                      <span>{displayName}</span>
                    </div>
                    <div 
                      className={styles.toggleSwitch} 
                      style={{ 
                        backgroundColor: isActive ? 'var(--teal)' : 'var(--surface-2)', 
                        borderColor: isActive ? 'transparent' : 'rgba(255,255,255,0.1)' 
                      }}
                    >
                      <div 
                        className={styles.toggleKnob} 
                        style={{ 
                          left: isActive ? '17px' : '1px',
                          transition: 'left 0.2s'
                        }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
