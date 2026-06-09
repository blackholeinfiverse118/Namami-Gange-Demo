import React from 'react';
import styles from './MapContainer.module.css';

interface MapContainerProps {
  type?: 'global' | 'basin';
}

export default function MapContainer({ type = 'global' }: MapContainerProps) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.background}>
        <svg viewBox="0 0 800 400" className={styles.svg}>
          {/* Stylized Grid */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Stylized Basin Path */}
          {type === 'basin' ? (
            <path
              d="M 50 100 Q 150 80 250 150 T 450 180 T 650 250 T 750 300"
              fill="none"
              stroke="var(--river-blue)"
              strokeWidth="3"
              className={styles.riverPath}
            />
          ) : (
            <g className={styles.globalArt}>
               <path d="M 100 200 Q 200 150 300 200 T 500 250 T 700 200" fill="none" stroke="var(--river-blue)" strokeWidth="1" opacity="0.2" />
               <path d="M 120 220 Q 220 170 320 220 T 520 270 T 720 220" fill="none" stroke="var(--river-blue)" strokeWidth="1" opacity="0.1" />
            </g>
          )}

          {/* Interactive Nodes */}
          <g className={styles.nodes}>
            <circle cx="250" cy="150" r="4" className={styles.node} />
            <circle cx="450" cy="180" r="4" className={styles.node} />
            <circle cx="650" cy="250" r="4" className={styles.nodeAlert} />
          </g>
        </svg>
      </div>
      
      <div className={styles.overlay}>
        <div className={styles.coordinates}>
          <span>LAT: 25.3176° N</span>
          <span>LON: 82.9739° E</span>
        </div>
        <div className={styles.status}>
          <div className={styles.pulse}></div>
          <span>GEOSPATIAL FEED: ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
