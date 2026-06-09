import React from 'react';
import styles from './Sidebar.module.css';

const navItems = [
  { id: 'global', label: 'Global Operations', icon: '🌐' },
  { id: 'basin', label: 'Ganga Basin Intel', icon: '🌊' },
  { id: 'location', label: 'Location Intel', icon: '📍' },
  { id: 'simulation', label: 'Scenario Simulation', icon: '🔮' },
  { id: 'signals', label: 'Realtime Signals', icon: '📡' },
  { id: 'infra', label: 'Infra Network', icon: '🏗️' },
  { id: 'collab', label: 'Collaboration', icon: '💬' },
  { id: 'governance', label: 'Governance View', icon: '🏛️' },
  { id: 'datasets', label: 'Dataset Management', icon: '📊' },
];

export default function Sidebar({ activeTab, onTabChange }: { activeTab: string, onTabChange: (id: string) => void }) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <div className={styles.logoIcon}>NG</div>
        <div className={styles.logoText}>
          <span className={styles.brand}>NAMAMI GANGE</span>
          <span className={styles.sub}>Intel Surface</span>
        </div>
      </div>
      
      <nav className={styles.nav}>
        <div className={styles.sectionLabel}>Operational Domains</div>
        {navItems.map(item => (
          <div 
            key={item.id} 
            className={`${styles.navItem} ${activeTab === item.id ? styles.active : ''}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className={styles.icon}>{item.icon}</span>
            <span className={styles.label}>{item.label}</span>
          </div>
        ))}
      </nav>
      
      <div className={styles.footer}>
        <div className={styles.user}>
          <div className={styles.avatar}>JD</div>
          <div className={styles.userInfo}>
            <div className={styles.userName}>J. Dosanjh</div>
            <div className={styles.userRole}>Chief Ops Officer</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
