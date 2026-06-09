import React, { useState, useEffect } from 'react';
import styles from './Topbar.module.css';

export default function Topbar() {
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
          <span className={`${styles.value} ${styles.good}`}>Active</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.label}>Basin Alert:</span>
          <span className={`${styles.value} ${styles.warning}`}>02 Elevated</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.label}>Avg Suitability:</span>
          <span className={`${styles.value} ${styles.blue}`}>84%</span>
        </div>
      </div>
      
      <div className={styles.actions}>
        <div className={styles.time}>{time || '--:--:-- IST'}</div>
        <button className={styles.actionBtn}>📡 Signal Monitor</button>
      </div>
    </header>
  );
}
