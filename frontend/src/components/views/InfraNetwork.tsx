'use client';

import React, { useState, useEffect } from 'react';
import styles from './View.module.css';
import { fetchInfrastructureOverlay } from '@/services/api';

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
  const [nodes, setNodes] = useState<any[]>([]);
  const [activeLayers, setActiveLayers] = useState<Record<string, boolean>>({
    ports: true,
    terminals: true,
    parks: true,
    railways: true,
    highways: true,
    waterways: true
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadNodes() {
      setIsLoading(true);
      try {
        const data = await fetchInfrastructureOverlay(true);
        if (data && data.features) {
          setNodes(data.features);
        }
      } catch (err) {
        console.error('Failed to fetch infrastructure overlay:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadNodes();
  }, []);

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

  // Map markers coordinates for selected active node
  const mapCX = loc.id === 'kanpur' ? 100 : loc.id === 'prayagraj' ? 200 : loc.id === 'varanasi' ? 290 : loc.id === 'patna' ? 390 : 470;
  const mapCY = loc.id === 'kanpur' ? 98 : loc.id === 'prayagraj' ? 120 : loc.id === 'varanasi' ? 140 : loc.id === 'patna' ? 180 : 210;

  // Custom coordinate mapping function from longitude and latitude to SVG viewport
  const mapCoords = (lng: number, lat: number) => {
    let x = 100;
    if (lng <= 80.33) {
      x = 100;
    } else if (lng <= 81.85) {
      x = 100 + ((lng - 80.33) / (81.85 - 80.33)) * 100;
    } else if (lng <= 82.97) {
      x = 200 + ((lng - 81.85) / (82.97 - 81.85)) * 90;
    } else if (lng <= 85.14) {
      x = 290 + ((lng - 82.97) / (85.14 - 82.97)) * 100;
    } else {
      x = 390 + ((lng - 85.14) / (88.36 - 85.14)) * 80;
    }

    let y = 140;
    if (lat >= 26.45) {
      y = 98;
    } else if (lat >= 25.59) {
      y = 98 + ((26.45 - lat) / (26.45 - 25.59)) * 82;
    } else if (lat >= 25.44) {
      y = 180 - ((lat - 25.44) / (25.59 - 25.44)) * 60;
    } else if (lat >= 25.32) {
      y = 120 + ((25.44 - lat) / (25.44 - 25.32)) * 20;
    } else {
      y = 140 + ((25.32 - lat) / (25.32 - 22.57)) * 70;
    }

    return { x, y };
  };

  const getLayerKey = (nodeType: string): string => {
    const type = nodeType.toLowerCase();
    if (type.includes('port')) return 'ports';
    if (type.includes('terminal') || type.includes('jetty') || type.includes('tourism') || type.includes('enablement')) return 'terminals';
    if (type.includes('logistics') || type.includes('mmlp') || type.includes('hub_spoke') || type.includes('cez')) return 'parks';
    return '';
  };

  const toggleLayer = (layerId: string) => {
    setActiveLayers(prev => ({
      ...prev,
      [layerId]: !prev[layerId]
    }));
  };

  const isNodeVisible = (node: any) => {
    const layer = getLayerKey(node.properties.node_type);
    if (!layer) return true;
    return activeLayers[layer];
  };

  const visibleNodes = nodes.filter(isNodeVisible);

  // Stats programmatically computed
  const totalPorts = nodes.filter(n => getLayerKey(n.properties.node_type) === 'ports').length;
  const totalTerminals = nodes.filter(n => getLayerKey(n.properties.node_type) === 'terminals').length;
  const totalParks = nodes.filter(n => getLayerKey(n.properties.node_type) === 'parks').length;
  const multimodalNodes = nodes.filter(n => n.properties.multimodal === true).length;

  const portsVal = totalPorts > 0 ? totalPorts.toString() : '40';
  const terminalsVal = totalTerminals > 0 ? totalTerminals.toString() : '20';
  const parksVal = totalParks > 0 ? totalParks.toString() : '10';
  const corridorsVal = multimodalNodes > 0 ? multimodalNodes.toString() : '7';
  const densityVal = totalPorts + totalTerminals + totalParks > 8 ? 'High' : 'Medium';

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
                {activeLayers.railways && (
                  <>
                    <path d="M 60 50 L 135 80 L 220 90 L 285 100 L 360 110 L 420 130 L 480 150" fill="none" stroke="rgba(136,153,170,0.2)" strokeWidth="2" />
                    <path d="M 80 280 L 140 250 L 200 230 L 270 210 L 340 200 L 400 195 L 460 200" fill="none" stroke="rgba(136,153,170,0.2)" strokeWidth="2" />
                  </>
                )}

                {/* National Highways */}
                {activeLayers.highways && (
                  <path d="M 70 120 L 150 140 L 240 130 L 320 160 L 410 170 L 490 190" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" strokeDasharray="4,4" />
                )}

                {/* Waterways */}
                {activeLayers.waterways && (
                  <path d="M 55 90 Q 120 82 180 88 Q 240 92 300 96 Q 350 100 395 105 Q 430 110 465 118" fill="none" stroke="var(--river-blue)" strokeWidth="2.5" strokeDasharray="6,4" opacity="0.6" />
                )}
                
                {/* Active node highlight */}
                <circle cx={mapCX} cy={mapCY} r="18" fill="rgba(20, 184, 166, 0.15)" stroke="var(--teal)" strokeWidth="1.5" className={styles.mapRipple} />
                <circle cx={mapCX} cy={mapCY} r="6" fill="var(--teal)" />
                <text x={mapCX + 12} y={mapCY + 4} fill="var(--text-primary)" fontSize="9" fontWeight="bold" fontFamily="var(--font-mono)">{loc.name.split(' ')[0].toUpperCase()}</text>

                {/* Dynamic Candidates and Infrastructure Nodes */}
                {visibleNodes.map((n: any, idx: number) => {
                  const coords = n.geometry?.coordinates || [83.0, 25.5];
                  const { x, y } = mapCoords(coords[0], coords[1]);
                  
                  // Skip drawing if it matches active location
                  if (Math.abs(x - mapCX) < 10 && Math.abs(y - mapCY) < 10) {
                    return null;
                  }

                  const layer = getLayerKey(n.properties.node_type);
                  const color = layer === 'ports' ? 'var(--river-blue)' : layer === 'terminals' ? 'var(--teal)' : 'var(--amber)';
                  
                  return (
                    <g key={n.properties.node_id || idx} style={{ cursor: 'pointer' }} onClick={() => alert(`${n.properties.proposal || n.properties.node_id}`)}>
                      <circle cx={x} cy={y} r="4.5" fill={color} opacity="0.75" />
                      <circle cx={x} cy={y} r="7" fill="none" stroke={color} strokeWidth="0.5" opacity="0.3" />
                    </g>
                  );
                })}
              </svg>
              <div className={styles.mapLabel}>INFRASTRUCTURE CONNECTIVITY NETWORK — ACTIVE</div>
            </div>
          </div>

          <div className={styles.statsRow} style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
            {[
              { label: 'Total Ports', value: portsVal, color: 'var(--river-blue)' },
              { label: 'IWT Terminals', value: terminalsVal, color: 'var(--teal)' },
              { label: 'Logistics Parks', value: parksVal, color: 'var(--amber)' },
              { label: 'Major Corridors', value: corridorsVal, color: 'var(--eco-green)' }
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
              <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)', fontFamily: 'var(--font-display)' }}>{densityVal}</div>
              <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', marginTop: '4px', letterSpacing: '0.05em' }}>Density</div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className={styles.listCard}>
            <div className={styles.cardTitle}>Infrastructure Layers</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { id: 'ports', label: 'Ports', color: 'var(--river-blue)' },
                { id: 'terminals', label: 'IWT Terminals', color: 'var(--teal)' },
                { id: 'parks', label: 'Logistics Parks', color: 'var(--amber)' },
                { id: 'railways', label: 'Railways', color: '#8899AA' },
                { id: 'highways', label: 'National Highways', color: '#556677' },
                { id: 'waterways', label: 'Waterways', color: 'var(--river-blue)' },
              ].map((layer, i) => {
                const isActive = activeLayers[layer.id];
                return (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: layer.color }}></div>
                      <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{layer.label}</span>
                    </div>
                    <div 
                      onClick={() => toggleLayer(layer.id)}
                      style={{ 
                        width: '32px', 
                        height: '16px', 
                        borderRadius: '8px', 
                        backgroundColor: isActive ? 'var(--teal)' : 'var(--surface-2)',
                        position: 'relative',
                        cursor: 'pointer',
                        border: '1px solid rgba(255,255,255,0.1)'
                      }}
                    >
                      <div style={{ 
                        position: 'absolute', 
                        width: '12px', 
                        height: '12px', 
                        backgroundColor: 'white', 
                        borderRadius: '50%', 
                        top: '1px', 
                        left: isActive ? '17px' : '1px',
                        transition: 'left 0.2s'
                      }}></div>
                    </div>
                  </div>
                );
              })}
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
