import React, { useState, useEffect } from 'react';
import styles from './Topbar.module.css';

interface TopbarProps {
  liveFeed?: string;
  basinAlerts?: number;
  avgSuitability?: number;
  selectedModel?: string;
  onModelChange?: (model: string) => void;
  onSignalMonitorClick?: () => void;
}

export default function Topbar({
  liveFeed = 'Active',
  basinAlerts = 2,
  avgSuitability = 70.9,
  selectedModel = 'inland_port',
  onModelChange,
  onSignalMonitorClick
}: TopbarProps) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const options: Intl.DateTimeFormatOptions = { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit', 
        hour12: false,
        timeZone: 'Asia/Kolkata' 
      };
      setTime(now.toLocaleTimeString('en-IN', options) + ' IST');
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className={styles.topbar}>
      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.label}>Live Feed:</span>
          <span className={`${styles.value} ${liveFeed === 'Active' ? styles.good : styles.warning}`}>{liveFeed}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.label}>Basin Alert:</span>
          <span className={`${styles.value} ${basinAlerts > 0 ? styles.warning : styles.good}`}>
            {basinAlerts < 10 ? `0${basinAlerts}` : basinAlerts} Elevated
          </span>
        </div>
        <div className={styles.stat}>
          <span className={styles.label}>Avg Suitability:</span>
          <span className={`${styles.value} ${styles.blue}`}>{avgSuitability}%</span>
        </div>
      </div>
      
      <div className={styles.actions}>
        <div className={styles.modelSelector}>
          <span className={styles.label}>Model:</span>
          <select 
            className={styles.select} 
            value={selectedModel} 
            onChange={(e) => onModelChange?.(e.target.value)}
          >
            <option value="inland_port">Inland Port</option>
            <option value="seaplane">Seaplane Landing</option>
            <option value="hub_spoke">Hub-Spoke Logistics</option>
          </select>
        </div>
        <div className={styles.time}>{time || '--:--:-- IST'}</div>
        <button className={styles.actionBtn} onClick={onSignalMonitorClick}>📡 Signal Monitor</button>
      </div>
    </header>
  );
}
