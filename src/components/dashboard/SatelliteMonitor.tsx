// File: src/components/dashboard/SatelliteMonitor.tsx
'use client';

import React from 'react';
import { GlassCard } from '../ui/GlassCard';
import { Server, Globe, ShieldCheck, Activity } from 'lucide-react';

interface SatelliteInstance {
  id: string;
  name: string;
  url: string;
  status: 'ONLINE' | 'OFFLINE' | 'SYNCING';
  lastPing: string;
}

export const SatelliteMonitor: React.FC<{ instances: SatelliteInstance[] }> = ({ instances }) => {
  return (
    <div className="satellite-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
      {instances.map((instance) => (
        <GlassCard key={instance.id} className="satellite-node">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div className={`status-indicator ${instance.status.toLowerCase()}`} 
                style={{ 
                  width: 10, 
                  height: 10, 
                  borderRadius: '50%', 
                  background: instance.status === 'ONLINE' ? '#00ff00' : instance.status === 'OFFLINE' ? '#ff4d4d' : '#f1c40f',
                  boxShadow: `0 0 10px ${instance.status === 'ONLINE' ? '#00ff00' : '#ff4d4d'}`
                }} 
              />
              <h4 style={{ margin: 0, fontSize: '1rem' }}>{instance.name}</h4>
            </div>
            <Server size={18} color="rgba(255,255,255,0.2)" />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.5)' }}>
              <Globe size={14} />
              <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{instance.url}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.5)' }}>
              <ShieldCheck size={14} color="var(--accent-primary)" />
              <span>RBAC Policy: Active</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.5)' }}>
              <Activity size={14} color="var(--accent-secondary)" />
              <span>Last Heartbeat: {instance.lastPing}</span>
            </div>
          </div>

          <div className="mini-chart" style={{ height: '40px', background: 'rgba(255,255,255,0.02)', marginTop: '1rem', borderRadius: '4px', overflow: 'hidden', display: 'flex', alignItems: 'flex-end', gap: '2px', padding: '0 4px' }}>
            {/* Fake Sparkline */}
            {[40, 70, 45, 90, 65, 80, 50, 85, 95, 60, 75].map((h, i) => (
              <div key={i} style={{ flex: 1, height: `${h}%`, background: 'var(--accent-primary)', opacity: 0.3 + (h/150), borderRadius: '1px' }} />
            ))}
          </div>
        </GlassCard>
      ))}
    </div>
  );
};
