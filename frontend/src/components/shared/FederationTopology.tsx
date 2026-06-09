'use client';

import React from 'react';
import styles from './FederationTopology.module.css';

export interface ServiceNode {
  id: string;
  label: string;
  status: 'active' | 'processing' | 'recovering' | 'offline' | 'error';
  metric: string;
}

export interface FederationTopologyProps {
  nodes?: ServiceNode[];
  activeStep?: number; // 0: Ingestion, 1: Validation, 2: Replay, 3: Persistence, 4: Federation
  latencyMs?: number;
  activePacketSource?: string;
  activePacketTarget?: string;
}

export default function FederationTopology({
  nodes = [
    { id: 'ingest', label: 'Ingestion Broker', status: 'active', metric: '4.8k msg/s' },
    { id: 'valid', label: 'Schema Contract', status: 'processing', metric: '100% Match' },
    { id: 'replay', label: 'Replay Core', status: 'active', metric: '1.2x Speed' },
    { id: 'persist', label: 'Persistence Store', status: 'active', metric: '4ms Delay' },
    { id: 'federate', label: 'Federation Matrix', status: 'active', metric: '99.9% Sync' }
  ],
  activeStep = 0,
  latencyMs = 8
}: FederationTopologyProps) {
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'var(--teal)';
      case 'processing': return 'var(--river-light)';
      case 'recovering': return 'var(--amber)';
      case 'offline': return 'var(--text-dim)';
      case 'error': return 'var(--alert-red)';
      default: return 'var(--text-dim)';
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <span className={styles.topLabel}>FEDERATION RUNTIME</span>
          <h4 className={styles.title}>NETWORK TOPOLOGY</h4>
        </div>
        <span className={styles.latency}>
          <span className={styles.dot}></span> Live Sync (Δ: {latencyMs}ms)
        </span>
      </div>
      
      <div className={styles.svgWrapper}>
        <svg viewBox="0 0 320 220" className={styles.svg}>
          {/* Connector Paths */}
          {/* Ingest to Valid */}
          <path d="M 60 40 L 160 40" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
          <path d="M 60 40 L 160 40" fill="none" stroke={activeStep >= 1 ? 'var(--river-blue)' : 'rgba(255,255,255,0.1)'} strokeWidth="1.5" />
          
          {/* Valid to Replay */}
          <path d="M 160 40 L 260 40" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
          <path d="M 160 40 L 260 40" fill="none" stroke={activeStep >= 2 ? 'var(--river-blue)' : 'rgba(255,255,255,0.1)'} strokeWidth="1.5" />

          {/* Replay to Persist */}
          <path d="M 260 40 L 260 130 L 160 130" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
          <path d="M 260 40 L 260 130 L 160 130" fill="none" stroke={activeStep >= 3 ? 'var(--river-blue)' : 'rgba(255,255,255,0.1)'} strokeWidth="1.5" />

          {/* Persist to Federate */}
          <path d="M 160 130 L 60 130" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
          <path d="M 160 130 L 60 130" fill="none" stroke={activeStep >= 4 ? 'var(--river-blue)' : 'rgba(255,255,255,0.1)'} strokeWidth="1.5" />

          {/* Federate back to Ingest (Loop) */}
          <path d="M 60 130 L 60 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="2" strokeDasharray="3,3" />

          {/* Active moving packet animation */}
          {activeStep === 0 && (
            <circle cx="60" cy="40" r="3.5" fill="var(--teal)" className={styles.packetPulse}>
              <animate attributeName="cx" from="60" to="160" dur="1s" repeatCount="indefinite" />
            </circle>
          )}
          {activeStep === 1 && (
            <circle cx="160" cy="40" r="3.5" fill="var(--river-light)" className={styles.packetPulse}>
              <animate attributeName="cx" from="160" to="260" dur="1s" repeatCount="indefinite" />
            </circle>
          )}
          {activeStep === 2 && (
            <circle cx="260" cy="40" r="3.5" fill="var(--amber)" className={styles.packetPulse}>
              <animate attributeName="cy" from="40" to="130" dur="0.7s" fill="freeze" id="down" />
              <animate attributeName="cx" from="260" to="160" begin="down.end" dur="0.7s" repeatCount="indefinite" />
            </circle>
          )}
          {activeStep === 3 && (
            <circle cx="160" cy="130" r="3.5" fill="var(--eco-green)" className={styles.packetPulse}>
              <animate attributeName="cx" from="160" to="60" dur="1s" repeatCount="indefinite" />
            </circle>
          )}

          {/* Nodes */}
          {/* Node 1: Ingestion */}
          <g transform="translate(60, 40)">
            <circle r="14" fill="var(--deep-navy)" stroke={getStatusColor(nodes[0].status)} strokeWidth="2" className={activeStep === 0 ? styles.activeNode : ''} />
            <circle r="4" fill={getStatusColor(nodes[0].status)} />
          </g>

          {/* Node 2: Validation */}
          <g transform="translate(160, 40)">
            <circle r="14" fill="var(--deep-navy)" stroke={getStatusColor(nodes[1].status)} strokeWidth="2" className={activeStep === 1 ? styles.activeNode : ''} />
            <circle r="4" fill={getStatusColor(nodes[1].status)} />
          </g>

          {/* Node 3: Replay */}
          <g transform="translate(260, 40)">
            <circle r="14" fill="var(--deep-navy)" stroke={getStatusColor(nodes[2].status)} strokeWidth="2" className={activeStep === 2 ? styles.activeNode : ''} />
            <circle r="4" fill={getStatusColor(nodes[2].status)} />
          </g>

          {/* Node 4: Persistence */}
          <g transform="translate(160, 130)">
            <circle r="14" fill="var(--deep-navy)" stroke={getStatusColor(nodes[3].status)} strokeWidth="2" className={activeStep === 3 ? styles.activeNode : ''} />
            <circle r="4" fill={getStatusColor(nodes[3].status)} />
          </g>

          {/* Node 5: Federation */}
          <g transform="translate(60, 130)">
            <circle r="14" fill="var(--deep-navy)" stroke={getStatusColor(nodes[4].status)} strokeWidth="2" className={activeStep === 4 ? styles.activeNode : ''} />
            <circle r="4" fill={getStatusColor(nodes[4].status)} />
          </g>
          
          {/* Labels for Node details */}
          <text x="60" y="68" fill="var(--text-primary)" fontSize="7.5" fontWeight="bold" textAnchor="middle" fontFamily="var(--font-mono)">INGESTION</text>
          <text x="60" y="78" fill="var(--text-dim)" fontSize="6.5" textAnchor="middle" fontFamily="var(--font-mono)">{nodes[0].metric}</text>

          <text x="160" y="68" fill="var(--text-primary)" fontSize="7.5" fontWeight="bold" textAnchor="middle" fontFamily="var(--font-mono)">VALIDATION</text>
          <text x="160" y="78" fill="var(--text-dim)" fontSize="6.5" textAnchor="middle" fontFamily="var(--font-mono)">{nodes[1].metric}</text>

          <text x="260" y="68" fill="var(--text-primary)" fontSize="7.5" fontWeight="bold" textAnchor="middle" fontFamily="var(--font-mono)">REPLAY CHAIN</text>
          <text x="260" y="78" fill="var(--text-dim)" fontSize="6.5" textAnchor="middle" fontFamily="var(--font-mono)">{nodes[2].metric}</text>

          <text x="160" y="158" fill="var(--text-primary)" fontSize="7.5" fontWeight="bold" textAnchor="middle" fontFamily="var(--font-mono)">PERSISTENCE</text>
          <text x="160" y="168" fill="var(--text-dim)" fontSize="6.5" textAnchor="middle" fontFamily="var(--font-mono)">{nodes[3].metric}</text>

          <text x="60" y="158" fill="var(--text-primary)" fontSize="7.5" fontWeight="bold" textAnchor="middle" fontFamily="var(--font-mono)">FEDERATION</text>
          <text x="60" y="168" fill="var(--text-dim)" fontSize="6.5" textAnchor="middle" fontFamily="var(--font-mono)">{nodes[4].metric}</text>
        </svg>
      </div>

      <div className={styles.matrixGrid}>
        <div className={styles.matrixItem}>
          <span className={styles.matrixLabel}>Uptime</span>
          <span className={styles.matrixVal}>99.98%</span>
        </div>
        <div className={styles.matrixItem}>
          <span className={styles.matrixLabel}>Recovery Status</span>
          <span className={styles.matrixVal} style={{ color: 'var(--teal)' }}>SECURE</span>
        </div>
        <div className={styles.matrixItem}>
          <span className={styles.matrixLabel}>Sync Mode</span>
          <span className={styles.matrixVal} style={{ color: 'var(--eco-green)' }}>DETERMINISTIC</span>
        </div>
      </div>
    </div>
  );
}
