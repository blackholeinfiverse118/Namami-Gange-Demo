'use client';

import React from 'react';
import styles from './MapCard.module.css';

export interface LocationMarker {
  id: string;
  name: string;
  lat: string;
  lng: string;
  suitabilityScore: number;
  type: 'port' | 'seaplane' | 'monitoring' | 'logistics';
  level: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface MapCardProps {
  markers?: LocationMarker[];
  selectedMarkerId?: string;
  onMarkerSelect?: (id: string) => void;
  activeLayers?: string[]; // e.g. ['waterways', 'seaplanes', 'logistics']
  activeLocationCoords?: { lat: string; lng: string };
}

export default function MapCard({
  markers = [
    { id: 'kanpur', name: 'KANPUR ⚠', lat: '26.4499° N', lng: '80.3319° E', suitabilityScore: 38, type: 'monitoring', level: 'LOW' },
    { id: 'prayagraj', name: 'PRAYAGRAJ', lat: '25.4358° N', lng: '81.8463° E', suitabilityScore: 65, type: 'monitoring', level: 'MEDIUM' },
    { id: 'varanasi', name: 'VARANASI', lat: '25.3176° N', lng: '82.9739° E', suitabilityScore: 82, type: 'port', level: 'HIGH' },
    { id: 'patna', name: 'PATNA', lat: '25.6112° N', lng: '85.1444° E', suitabilityScore: 74, type: 'port', level: 'MEDIUM' },
    { id: 'kolkata', name: 'KOLKATA HUB', lat: '22.5726° N', lng: '88.3639° E', suitabilityScore: 88, type: 'logistics', level: 'HIGH' }
  ],
  selectedMarkerId = 'varanasi',
  onMarkerSelect,
  activeLayers = ['waterways', 'seaplanes', 'logistics'],
  activeLocationCoords
}: MapCardProps) {
  
  const getMarkerColor = (level: string) => {
    switch (level) {
      case 'HIGH': return 'var(--eco-green)';
      case 'MEDIUM': return 'var(--amber)';
      case 'LOW':
      default:
        return 'var(--alert-red)';
    }
  };

  const selectedLoc = markers.find(m => m.id === selectedMarkerId) || markers[2];
  const displayLat = activeLocationCoords?.lat || selectedLoc.lat;
  const displayLng = activeLocationCoords?.lng || selectedLoc.lng;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <span className={styles.label}>NW-1 GEOSPATIAL INTELLIGENCE MAP</span>
          <h4 className={styles.title}>WATERWAY DECK</h4>
        </div>
        <div className={styles.coordinates}>
          <span>{displayLat}</span>
          <span className={styles.divider}>·</span>
          <span>{displayLng}</span>
        </div>
      </div>

      <div className={styles.mapViewport}>
        <svg viewBox="0 0 600 340" className={styles.svg}>
          <defs>
            <pattern id="dotGrid" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="0.8" fill="rgba(255,255,255,0.06)" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dotGrid)" />

          {/* Waterway Layer */}
          {activeLayers.includes('waterways') && (
            <>
              <path 
                d="M 80 120 Q 180 90 280 160 T 450 180 T 560 210" 
                fill="none" 
                stroke="var(--river-blue)" 
                strokeWidth="6" 
                opacity="0.15" 
              />
              <path 
                d="M 80 120 Q 180 90 280 160 T 450 180 T 560 210" 
                fill="none" 
                stroke="var(--river-light)" 
                strokeWidth="2.5" 
                strokeLinecap="round"
              />
            </>
          )}

          {/* Seaplane Route Layer */}
          {activeLayers.includes('seaplanes') && (
            <path
              d="M 280 160 Q 380 100 480 200"
              fill="none"
              stroke="var(--amber)"
              strokeWidth="1.2"
              strokeDasharray="4,4"
              opacity="0.6"
            />
          )}

          {/* Interactive Marker Groups */}
          {/* Kanpur */}
          <g className={styles.markerGroup} onClick={() => onMarkerSelect?.('kanpur')}>
            <circle cx="100" cy="115" r={selectedMarkerId === 'kanpur' ? 12 : 7} fill="rgba(239, 68, 68, 0.2)" stroke={getMarkerColor('LOW')} strokeWidth="1.5" />
            <circle cx="100" cy="115" r="4" fill={getMarkerColor('LOW')} />
            <text x="100" y="98" className={styles.markerText}>KANPUR ⚠</text>
          </g>

          {/* Prayagraj */}
          <g className={styles.markerGroup} onClick={() => onMarkerSelect?.('prayagraj')}>
            <circle cx="210" cy="125" r={selectedMarkerId === 'prayagraj' ? 12 : 7} fill="rgba(245, 158, 11, 0.2)" stroke={getMarkerColor('MEDIUM')} strokeWidth="1.5" />
            <circle cx="210" cy="125" r="4" fill={getMarkerColor('MEDIUM')} />
            <text x="210" y="142" className={styles.markerText}>PRAYAGRAJ</text>
          </g>

          {/* Varanasi */}
          <g className={styles.markerGroup} onClick={() => onMarkerSelect?.('varanasi')}>
            <circle 
              cx="280" 
              cy="160" 
              r={selectedMarkerId === 'varanasi' ? 14 : 9} 
              fill="rgba(16, 185, 129, 0.2)" 
              stroke={getMarkerColor('HIGH')} 
              strokeWidth="2" 
              className={selectedMarkerId === 'varanasi' ? styles.markerGlow : ''} 
            />
            <circle cx="280" cy="160" r="5" fill={getMarkerColor('HIGH')} />
            <text x="315" y="164" className={styles.markerVaranasiText}>VARANASI</text>
          </g>

          {/* Patna */}
          <g className={styles.markerGroup} onClick={() => onMarkerSelect?.('patna')}>
            <circle cx="410" cy="175" r={selectedMarkerId === 'patna' ? 12 : 7} fill="rgba(20, 184, 166, 0.2)" stroke={getMarkerColor('MEDIUM')} strokeWidth="1.5" />
            <circle cx="410" cy="175" r="4" fill={getMarkerColor('MEDIUM')} />
            <text x="410" y="192" className={styles.markerText}>PATNA</text>
          </g>

          {/* Kolkata */}
          <g className={styles.markerGroup} onClick={() => onMarkerSelect?.('kolkata')}>
            <circle cx="510" cy="205" r={selectedMarkerId === 'kolkata' ? 12 : 7} fill="rgba(16, 185, 129, 0.2)" stroke={getMarkerColor('HIGH')} strokeWidth="1.5" />
            <circle cx="510" cy="205" r="4" fill={getMarkerColor('HIGH')} />
            <text x="510" y="222" className={styles.markerText}>KOLKATA HUB</text>
          </g>
        </svg>
      </div>
      
      <div className={styles.footer}>
        <div className={styles.feedStatus}>
          <span className={styles.dot}></span>
          <span>GEOSPATIAL FEED: ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
