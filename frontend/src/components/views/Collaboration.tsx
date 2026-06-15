'use client';

import React, { useState, useEffect } from 'react';
import styles from './View.module.css';

interface RecoveryEvent {
  id: string;
  time: string;
  type: string;
  status: 'RESOLVED' | 'ACTIVE';
  corrId: string;
  detail: string;
}

interface CollaborationProps {
  recoveryEvents?: RecoveryEvent[];
  onResolve?: (id: string) => void;
  validationBreach?: boolean;
}

export default function Collaboration({
  recoveryEvents = [],
  onResolve,
  validationBreach = false
}: CollaborationProps) {
  const [activeChannel, setActiveChannel] = useState<'ganga-intelligence' | 'federation-audit' | 'env-monitoring'>('ganga-intelligence');
  const [inputText, setInputText] = useState('');
  
  const [channelsMessages, setChannelsMessages] = useState<Record<string, any[]>>({
    'ganga-intelligence': [
      { user: 'Amit Kumar', initial: 'AK', time: '10:14 AM', text: 'Water quality anomaly detected near Kanpur. BOD at 12.4 mg/L. Cross-checking with upstream stations now.', color: '#1E3A6E' },
      { user: 'Priya Sharma', initial: 'PS', time: '10:31 AM', text: 'Potential industrial discharge source identified near Jajmau CETP. Flagging for CPCB notification.', color: '#1B5E20' },
      { user: 'Ravi Verma', initial: 'RV', time: '10:42 AM', text: 'Increasing sampling frequency at G-047 and G-052. Will update in 2 hours.', color: '#4A148C' },
    ],
    'federation-audit': [
      { user: 'System Audit', initial: 'SA', time: '11:02 AM', text: 'Deterministic replay core initialized on port 5000. Integrity: guaranteed.', color: '#E65100' },
      { user: 'Auditor Bot', initial: 'AB', time: '11:15 AM', text: 'Verification transaction completed for Block #1240. Block hash is verified.', color: '#006064' }
    ],
    'env-monitoring': [
      { user: 'Eco Sensor Hub', initial: 'ES', time: '09:15 AM', text: 'CPCB sensor cluster online. Monitoring parameters: WQI, BOD, DO, Turbidity.', color: '#004D40' },
      { user: 'Nirmal Ganga Monitor', initial: 'NG', time: '09:45 AM', text: 'Kanpur Reach exceeds ecological stress safe limits. WQI is critically low.', color: '#3E2723' }
    ]
  });

  const [callTime, setCallTime] = useState({ minutes: 4, seconds: 32 });

  useEffect(() => {
    const timer = setInterval(() => {
      setCallTime(prev => {
        let sec = prev.seconds + 1;
        let min = prev.minutes;
        if (sec >= 60) {
          sec = 0;
          min += 1;
        }
        return { minutes: min, seconds: sec };
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatCallTime = () => {
    const mins = callTime.minutes.toString().padStart(2, '0');
    const secs = callTime.seconds.toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  const handleSend = () => {
    if (!inputText.trim()) return;
    const newMessage = {
      user: 'J. Dosanjh',
      initial: 'JD',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: inputText,
      color: 'var(--river-blue)'
    };
    setChannelsMessages(prev => ({
      ...prev,
      [activeChannel]: [...prev[activeChannel], newMessage]
    }));
    setInputText('');
  };

  const currentMessages = channelsMessages[activeChannel] || [];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Internal Collaboration Layer</h1>
          <p className={styles.subtitle}>Intelligence discussion · Operational coordination · Live Annotations</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr 320px', gap: '16px', height: '620px' }}>
        {/* Channels */}
        <div className={styles.listCard} style={{ overflowY: 'auto' }}>
          <div className={styles.cardTitle}>Channels</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { id: 'ganga-intelligence', name: '# ganga-intelligence', count: 0 },
              { id: 'federation-audit', name: '# federation-audit', count: validationBreach ? 1 : 0 },
              { id: 'env-monitoring', name: '# env-monitoring', count: 0 }
            ].map((channel) => (
              <div 
                key={channel.id} 
                onClick={() => setActiveChannel(channel.id as any)}
                style={{ 
                  padding: '10px', 
                  borderRadius: '8px', 
                  backgroundColor: activeChannel === channel.id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                  border: activeChannel === channel.id ? '1px solid rgba(59, 130, 246, 0.2)' : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
              >
                <div style={{ 
                  fontSize: '13px', 
                  color: activeChannel === channel.id ? 'var(--river-light)' : 'var(--text-secondary)', 
                  fontWeight: activeChannel === channel.id ? '600' : '400' 
                }}>
                  {channel.name}
                </div>
                {channel.count > 0 && (
                  <div style={{ fontSize: '10px', color: 'var(--alert-red)', marginTop: '2px', fontWeight: 'bold' }}>
                    {channel.count} ACTIVE ANOMALY
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className={styles.listCard} style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ paddingBottom: '12px', borderBottom: '1px solid var(--border)', marginBottom: '16px', fontWeight: '600', display: 'flex', justifyContent: 'space-between' }}>
            <span>#{activeChannel}</span>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>12 members online</span>
          </div>
          
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', paddingRight: '8px' }}>
            {currentMessages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', gap: '12px' }}>
                <div style={{ 
                  width: '32px', 
                  height: '32px', 
                  borderRadius: '8px', 
                  backgroundColor: msg.color, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '11px',
                  fontWeight: '700',
                  color: 'white',
                  flexShrink: 0
                }}>
                  {msg.initial}
                </div>
                <div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'baseline', marginBottom: '4px' }}>
                    <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>{msg.user}</span>
                    <span style={{ fontSize: '10px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{msg.time}</span>
                  </div>
                  <div style={{ 
                    padding: '10px 12px', 
                    backgroundColor: 'var(--surface-2)', 
                    border: '1px solid var(--border)', 
                    borderRadius: '0 12px 12px 12px',
                    fontSize: '13px',
                    lineHeight: '1.5',
                    color: 'var(--text-secondary)'
                  }}>
                    {msg.text}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border)', display: 'flex', gap: '12px' }}>
            <input 
              type="text" 
              placeholder="Type a message..." 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              style={{ 
                flex: 1, 
                backgroundColor: 'var(--surface-2)', 
                border: '1px solid var(--border)', 
                borderRadius: '8px', 
                padding: '10px 16px',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            />
            <button 
              onClick={handleSend}
              className={styles.primaryBtn} 
              style={{ padding: '0 20px' }}
            >
              Send
            </button>
          </div>
        </div>

        {/* Dynamic Recovery Panel Integration */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className={styles.listCard} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div className={styles.cardTitle}>Live recovery queue</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', flex: 1, paddingRight: '4px' }}>
              {recoveryEvents.length === 0 ? (
                <div style={{ fontSize: '12px', color: 'var(--text-dim)', padding: '10px', textAlign: 'center' }}>No active anomalies in reconciliation queue.</div>
              ) : (
                recoveryEvents.map((evt) => (
                  <div key={evt.id} style={{ 
                    padding: '10px', 
                    backgroundColor: 'rgba(0,0,0,0.15)', 
                    borderRadius: '8px', 
                    border: '1px solid var(--border)', 
                    borderLeft: `3px solid ${evt.status === 'ACTIVE' ? 'var(--alert-red)' : 'var(--eco-green)'}` 
                  }}>
                    <div style={{ display: 'flex', justifySelf: 'stretch', justifyContent: 'space-between', fontSize: '11px', marginBottom: '4px' }}>
                      <strong style={{ color: 'var(--text-primary)' }}>{evt.id}</strong>
                      <span style={{ color: 'var(--text-dim)', fontSize: '9px', fontFamily: 'var(--font-mono)' }}>{evt.time}</span>
                    </div>
                    <p style={{ fontSize: '10.5px', color: 'var(--text-secondary)', margin: '0 0 6px 0', lineHeight: '1.3' }}>{evt.detail}</p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '8px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>Block #{evt.corrId.split('-').pop()}</span>
                      {evt.status === 'ACTIVE' && onResolve && (
                        <button 
                          onClick={() => onResolve(evt.id)}
                          style={{
                            fontSize: '8px',
                            fontWeight: 'bold',
                            fontFamily: 'var(--font-mono)',
                            backgroundColor: 'var(--teal)',
                            color: 'var(--deep-navy)',
                            border: 'none',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            cursor: 'pointer'
                          }}
                        >
                          RECONCILE
                        </button>
                      )}
                      {evt.status === 'RESOLVED' && (
                        <span style={{ fontSize: '8.5px', color: 'var(--eco-green)', fontWeight: 'bold' }}>✓ RESOLVED</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className={styles.listCard} style={{ textAlign: 'center' }}>
            <div className={styles.cardTitle}>Active Ops Call</div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', margin: '16px 0' }}>
              {['AK', 'PS', 'RV'].map((init, i) => (
                <div key={i} style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: i === 0 ? '#1E3A6E' : i === 1 ? '#1B5E20' : '#4A148C', border: '2px solid var(--deep-navy)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', color: 'white', fontWeight: '700' }}>{init}</div>
              ))}
            </div>
            <div style={{ fontSize: '20px', fontFamily: 'var(--font-mono)', color: 'var(--teal)', marginBottom: '16px' }}>{formatCallTime()}</div>
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
              <button style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'var(--surface-2)', border: '1px solid var(--border)', cursor: 'pointer' }}>🎤</button>
              <button style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'var(--surface-2)', border: '1px solid var(--border)', cursor: 'pointer' }}>📷</button>
              <button style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'var(--alert-red)', border: 'none', cursor: 'pointer' }}>📞</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
