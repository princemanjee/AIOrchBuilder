// File: src/components/dashboard/TelemetryFeed.tsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import { GlassCard } from '../ui/GlassCard';
import { Terminal, Shield, AlertTriangle, Info, Cpu } from 'lucide-react';
import { hubClient } from '@/lib/supabase';

interface LogEntry {
  id: string;
  created_at: string;
  agent_name: string;
  message: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  metadata: any;
}

export const TelemetryFeed: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!hubClient) return;

    // Initial fetch
    const fetchLogs = async () => {
      try {
        const { data, error } = await hubClient
          .from('agent_audit_logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50);
        
        if (data) setLogs(data.reverse());
      } catch (err) {
        console.warn('Telemetry feed failed to connect to Hub:', err);
      }
    };

    fetchLogs();

    // Subscribe to real-time updates
    const subscription = hubClient
      .channel('public:agent_audit_logs')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'agent_audit_logs' }, (payload: { new: LogEntry }) => {
        setLogs(prev => [...prev.slice(-49), payload.new]);
      })
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '#ff4d4d';
      case 'ERROR': return '#ff7675';
      case 'WARNING': return '#fab1a0';
      default: return 'var(--accent-primary)';
    }
  };

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <Shield size={14} color="#ff4d4d" />;
      case 'WARNING': return <AlertTriangle size={14} color="#fab1a0" />;
      case 'INFO': return <Info size={14} color="var(--accent-primary)" />;
      default: return <Cpu size={14} color="var(--accent-secondary)" />;
    }
  };

  return (
    <GlassCard className="telemetry-console">
      <div className="console-header" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.75rem' }}>
        <Terminal size={18} color="var(--accent-primary)" />
        <h3 style={{ margin: 0, fontSize: '1rem', letterSpacing: '0.05em' }}>LIVE TELEMETRY FEED</h3>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#00ff00', boxShadow: '0 0 10px #00ff00' }} />
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        style={{ 
          height: '300px', 
          overflowY: 'auto', 
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '0.85rem',
          lineHeight: '1.6'
        }}
        className="custom-scrollbar"
      >
        {logs.length === 0 ? (
          <div style={{ color: 'rgba(255,255,255,0.3)', textAlign: 'center', marginTop: '4rem' }}>
            Awaiting signal from agent swarm...
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} style={{ marginBottom: '0.5rem', display: 'flex', gap: '0.75rem', borderLeft: `2px solid ${getSeverityColor(log.severity)}`, paddingLeft: '0.75rem' }}>
              <span style={{ color: 'rgba(255,255,255,0.3)', minWidth: '80px' }}>
                {new Date(log.created_at).toLocaleTimeString([], { hour12: false })}
              </span>
              <span style={{ color: 'var(--accent-secondary)', fontWeight: 600, minWidth: '100px' }}>
                [{log.agent_name}]
              </span>
              <span style={{ color: 'rgba(255,255,255,0.8)' }}>{log.message}</span>
            </div>
          ))
        )}
      </div>
    </GlassCard>
  );
};
