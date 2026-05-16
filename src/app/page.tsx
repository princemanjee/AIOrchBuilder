// File: src/app/page.tsx
'use client'

import React, { useState } from 'react'
import {
    LayoutDashboard,
    Settings,
    Users,
    Box,
    Activity,
    Search,
    Bell,
    Cpu,
    Layers,
    Terminal,
    Plus,
    Globe,
    Zap,
    Layout,
    Database,
    Copy,
    Check,
    X,
    FileCode,
    Folder,
    File,
    Download,
    Shield,
    RotateCcw,
    Server,
    Share2
} from 'lucide-react'
import { getSatelliteClient } from '@/lib/supabase'
import { GlassCard } from '@/components/ui/GlassCard'
import { GlassInput } from '@/components/ui/GlassInput'
import { GlassButton } from '@/components/ui/GlassButton'
import { TelemetryFeed } from '@/components/dashboard/TelemetryFeed'


export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('Overview')
    const [isSatelliteModalOpen, setIsSatelliteModalOpen] = useState(false)
    const [satelliteConfig, setSatelliteConfig] = useState({
        url: '',
        key: '',
        projectId: 'POC-1'
    })
    const [isConnected, setIsConnected] = useState(false)
    const [requirement, setRequirement] = useState('')
    const [blueprint, setBlueprint] = useState<any>(null)
    const [tasks, setTasks] = useState<any[]>([])
    const [isParsing, setIsParsing] = useState(false)
    const [viewingArtifact, setViewingArtifact] = useState<{name: string, files: Record<string, string>, activeFile: string} | null>(null)
    const [copied, setCopied] = useState(false)
    const [isDecomposing, setIsDecomposing] = useState(false)
    const [buildStatus, setBuildStatus] = useState<'idle' | 'review' | 'building' | 'complete'>('idle')
    const [userRole, setUserRole] = useState<'admin' | 'user'>('admin')
    const [config, setConfig] = useState<any>({
        revision_limit: 3,
        agent_speed: 'M',
        token_limit: 50000,
        unlimited_admin_tokens: true,
        active_llm_engine: 'Anthropic',
        active_model: 'claude-3-5-sonnet-latest',
        llm_engines: [],
        mcp_tools: []
    })
    const [isSavingConfig, setIsSavingConfig] = useState(false)

    const [satellites, setSatellites] = useState([
        { id: 'hub', name: 'Global Hub', url: 'hub-instance.supabase.co', status: 'ONLINE' as const, lastPing: '2m ago' }
    ])

    // Real-time listener for task updates via audit logs
    React.useEffect(() => {
        const { hubClient } = require('@/lib/supabase')
        if (!hubClient) return

        const channel = hubClient.channel('task-updates')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'agent_audit_logs' }, (payload: any) => {
                const log = payload.new
                if (log.metadata && log.metadata.task_id) {
                    setTasks(prev => prev.map(t => 
                        t.id === log.metadata.task_id ? { ...t, status: log.metadata.status } : t
                    ))
                }
            })
            .subscribe()

        return () => { hubClient.removeChannel(channel) }
    }, [])

    React.useEffect(() => {
        fetchConfig()
    }, [])

    const fetchConfig = async () => {
        try {
            const res = await fetch('http://localhost:8001/admin/config')
            const data = await res.json()
            setConfig(data)
        } catch (err) {
            console.error("Failed to fetch config", err)
        }
    }

    const agents = [
        { name: 'AGENT_UI', status: isConnected ? 'Active' : 'Idle', color: '#00f3ff', icon: <Zap size={16} /> },
        { name: 'AGENT_LOGIC', status: isConnected ? 'Active' : 'Idle', color: '#9d00ff', icon: <Cpu size={16} /> },
        { name: 'AGENT_DATA', status: isConnected ? 'Active' : 'Idle', color: '#00ff88', icon: <Database size={16} /> },
        { name: 'AGENT_API', status: isConnected ? 'Updating' : 'Idle', color: '#6366f1', icon: <Activity size={16} /> },
    ]

    const phases = [
        { id: '01', title: 'Request Analysis', status: 'Complete' },
        { id: '02', title: 'Blueprint Design', status: 'Complete' },
        { id: '03', title: 'Agent Construction', status: 'Complete' },
        { id: '04', title: 'Build Execution', status: 'In Progress' },
        { id: '05', title: 'Validation', status: 'Pending' },
        { id: '06', title: 'Refinement', status: 'Pending' },
    ]

    const connectSatellite = async () => {
        try {
            const response = await fetch('http://localhost:8001/connect-satellite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(satelliteConfig)
            })
            if (!response.ok) throw new Error("Backend connection failed")

            const client = getSatelliteClient(satelliteConfig.projectId, satelliteConfig.url, satelliteConfig.key)
            if (client) {
                setIsConnected(true)
                setIsSatelliteModalOpen(false)
                setSatellites(prev => [...prev, {
                    id: satelliteConfig.projectId,
                    name: `App: ${satelliteConfig.projectId}`,
                    url: satelliteConfig.url,
                    status: 'ONLINE' as const,
                    lastPing: 'Just now'
                }])
            }
        } catch (err) {
            alert("Connection failed. Check credentials.")
        }
    }

    const parseRequirement = async () => {
        setIsParsing(true)
        try {
            const response = await fetch('http://localhost:8001/logic/parse-requirements', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: requirement })
            })
            const data = await response.json()
            setBlueprint(data)
            setBuildStatus('idle')
        } catch (err) {
            console.error("Parsing failed", err)
        } finally {
            setIsParsing(false)
        }
    }

    const decomposeBlueprint = async () => {
        if (!blueprint) return
        setIsDecomposing(true)
        try {
            const response = await fetch('http://localhost:8001/logic/decompose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(blueprint)
            })
            const data = await response.json()
            setTasks(data.tasks)
            setBuildStatus('review')
        } catch (err) {
            console.error("Decomposition failed", err)
        } finally {
            setIsDecomposing(false)
        }
    }

    const approveBuild = async () => {
        try {
            await fetch('http://localhost:8001/logic/approve-build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ blueprint, tasks, approved: true })
            })
            setBuildStatus('building')
            
            // Check for completion every 2 seconds
            const checkCompletion = setInterval(() => {
                setTasks(currentTasks => {
                    const allComplete = currentTasks.length > 0 && currentTasks.every(t => t.status === 'complete')
                    if (allComplete) {
                        setBuildStatus('complete')
                        clearInterval(checkCompletion)
                    }
                    return currentTasks
                })
            }, 2000)
        } catch (err) {
            console.error("Approval failed", err)
        }
    }

    const updateConfig = async (updates: any) => {
        setIsSavingConfig(true)
        try {
            const newConfig = { ...config, ...updates }
            await fetch('http://localhost:8001/admin/config', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Role': userRole
                },
                body: JSON.stringify(updates)
            })
            setConfig(newConfig)
        } catch (err) {
            console.error("Failed to update config", err)
        } finally {
            setIsSavingConfig(false)
        }
    }

    const factoryReset = async () => {
        if (!confirm("Are you sure you want to restore all system settings to factory defaults?")) return
        setIsSavingConfig(true)
        try {
            const res = await fetch('http://localhost:8001/admin/reset', {
                method: 'POST',
                headers: { 'X-Role': userRole }
            })
            const data = await res.json()
            setConfig(data.config)
            alert("System restored to factory defaults.")
        } catch (err) {
            console.error("Reset failed", err)
        } finally {
            setIsSavingConfig(false)
        }
    }

    const renderOverview = () => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            {/* Main Action Call: Build New Project */}
            <GlassCard style={{ 
                padding: '3rem', 
                background: 'linear-gradient(165deg, rgba(0, 243, 255, 0.05) 0%, rgba(157, 0, 255, 0.05) 100%)',
                border: '1px solid rgba(0, 243, 255, 0.15)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <div style={{ position: 'absolute', top: '-10%', right: '-5%', opacity: 0.05 }}>
                    <Zap size={300} color="var(--accent-primary)" />
                </div>
                
                <div style={{ position: 'relative', zIndex: 1, maxWidth: '800px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(0, 243, 255, 0.1)', border: '1px solid rgba(0, 243, 255, 0.2)' }}>
                            <Plus size={24} color="var(--accent-primary)" />
                        </div>
                        <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>BUILD NEW APPLICATION</h2>
                    </div>
                    <p style={{ fontSize: '1.1rem', color: 'rgba(255,255,255,0.6)', marginBottom: '2.5rem', lineHeight: '1.6' }}>
                        Transform your vision into production-ready software. Describe your app's core functionality, data needs, and style preferences. Our specialist swarm handles the rest.
                    </p>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <textarea 
                            className="glass-input" 
                            placeholder="e.g. A premium SaaS platform for real-time crypto portfolio tracking with automated rebalancing and deep audit logs..."
                            style={{ minHeight: '150px', fontSize: '1.1rem', lineHeight: '1.6' }}
                            value={requirement}
                            onChange={(e) => setRequirement(e.target.value)}
                        />
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <GlassButton 
                                variant="primary" 
                                style={{ flex: 2, height: '60px', fontSize: '1rem' }} 
                                onClick={parseRequirement}
                                disabled={isParsing || !requirement}
                            >
                                {isParsing ? (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div className="animate-spin" style={{ width: '20px', height: '20px', border: '3px solid #000', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
                                        <span>ANALYZING INTENT...</span>
                                    </div>
                                ) : (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <Zap size={20} />
                                        <span>INITIATE AUTONOMOUS BUILD</span>
                                    </div>
                                )}
                            </GlassButton>
                            <GlassButton variant="secondary" style={{ flex: 1, height: '60px' }} onClick={() => setRequirement('')}>CLEAR</GlassButton>
                        </div>
                    </div>
                </div>
            </GlassCard>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
                {/* System Status & Admin Controls */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                    <section>
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1rem', color: 'rgba(255,255,255,0.4)' }}>
                            <Settings size={16} /> SYSTEM ORCHESTRATION
                        </h3>
                        <GlassCard style={{ padding: '2rem' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <h4 style={{ fontSize: '0.9rem', margin: '0 0 0.25rem 0' }}>REVISION CACHE</h4>
                                        <p style={{ fontSize: '0.75rem', opacity: 0.5 }}>Stored versions per project</p>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <span style={{ fontWeight: 800, color: 'var(--accent-primary)' }}>{config.revision_limit}</span>
                                        <input type="range" min="1" max="10" value={config.revision_limit} onChange={(e) => updateConfig({ revision_limit: parseInt(e.target.value) })} style={{ width: '80px', accentColor: 'var(--accent-primary)' }} />
                                    </div>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <h4 style={{ fontSize: '0.9rem', margin: '0 0 0.25rem 0' }}>AGENT VELOCITY</h4>
                                        <p style={{ fontSize: '0.75rem', opacity: 0.5 }}>Execution cycle speed</p>
                                    </div>
                                    <div style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', padding: '4px' }}>
                                        {['S', 'M', 'L'].map(size => (
                                            <button 
                                                key={size}
                                                onClick={() => updateConfig({ agent_speed: size })}
                                                style={{ padding: '6px 14px', borderRadius: '8px', fontSize: '0.75rem', border: 'none', background: config.agent_speed === size ? 'var(--accent-primary)' : 'transparent', color: config.agent_speed === size ? '#000' : '#fff', cursor: 'pointer', fontWeight: 700, transition: 'all 0.3s' }}
                                            >
                                                {size}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                        <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>ACTIVE ENGINE</span>
                                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-secondary)' }}>{config.active_llm_engine}</span>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        <div style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
                                            <p style={{ fontSize: '0.6rem', opacity: 0.4, marginBottom: '2px' }}>MCP TOOLS</p>
                                            <p style={{ fontSize: '0.9rem', fontWeight: 800 }}>{config.mcp_tools.length}</p>
                                        </div>
                                        <div style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
                                            <p style={{ fontSize: '0.6rem', opacity: 0.4, marginBottom: '2px' }}>MODELS</p>
                                            <p style={{ fontSize: '0.9rem', fontWeight: 800 }}>{config.llm_engines.length}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </GlassCard>
                    </section>
                </div>

                {/* Swarm & Telemetry Mix */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                    <section>
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1rem', color: 'rgba(255,255,255,0.4)' }}>
                            <Activity size={16} /> LIVE TELEMETRY
                        </h3>
                        <div style={{ height: '365px', overflow: 'hidden' }}>
                            <TelemetryFeed />
                        </div>
                    </section>
                </div>
            </div>
            
            {/* Global Logs Footer section */}
            <section style={{ opacity: 0.8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ height: '1px', flex: 1, background: 'linear-gradient(90deg, transparent, rgba(255,100,0,0.2))' }}></div>
                    <span style={{ fontSize: '0.7rem', fontWeight: 800, letterSpacing: '0.2em', opacity: 0.4 }}>ADVANCED GOVERNANCE ACTIVE</span>
                    <div style={{ height: '1px', flex: 1, background: 'linear-gradient(90deg, rgba(255,100,0,0.2), transparent)' }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '3rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Shield size={14} color="#ff6400" />
                        <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>RBAC ENFORCED</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <RotateCcw size={14} color="#ff6400" />
                        <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>AUDIT TRAIL ACTIVE</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Globe size={14} color="#ff6400" />
                        <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>MULTI-ENGINE ROUTING</span>
                    </div>
                </div>
            </section>
        </div>
    )

    const renderAuditLogs = () => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <GlassCard style={{ padding: '2.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ padding: '0.75rem', borderRadius: '12px', background: 'rgba(0, 243, 255, 0.1)' }}>
                            <Terminal size={24} color="var(--accent-primary)" />
                        </div>
                        <div>
                            <h3 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800 }}>HISTORICAL AUDIT CONSOLE</h3>
                            <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.4 }}>GLOBAL TELEMETRY ARCHIVE</p>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <div className="glass-input" style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0 1.5rem', height: '50px' }}>
                            <Search size={18} opacity={0.3} />
                            <input type="text" placeholder="Filter audit trail..." style={{ background: 'transparent', border: 'none', color: '#fff', fontSize: '0.9rem', outline: 'none', width: '250px' }} />
                        </div>
                        <GlassButton variant="secondary" icon={<Download size={18} />}>EXPORT</GlassButton>
                    </div>
                </div>

                <div style={{ height: '600px', overflowY: 'auto', paddingRight: '1rem' }}>
                    <TelemetryFeed />
                </div>
            </GlassCard>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem' }}>
                <GlassCard style={{ padding: '1.5rem' }}>
                    <p style={{ fontSize: '0.7rem', fontWeight: 800, opacity: 0.4, marginBottom: '1rem', letterSpacing: '0.1em' }}>TOTAL AGENT CYCLES</p>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                        <span style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-primary)' }}>1,482</span>
                        <span style={{ fontSize: '0.8rem', color: '#00ff88', fontWeight: 700 }}>+12%</span>
                    </div>
                </GlassCard>
                <GlassCard style={{ padding: '1.5rem' }}>
                    <p style={{ fontSize: '0.7rem', fontWeight: 800, opacity: 0.4, marginBottom: '1rem', letterSpacing: '0.1em' }}>SYSTEM UPTIME</p>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                        <span style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-secondary)' }}>99.98%</span>
                        <span style={{ fontSize: '0.8rem', opacity: 0.4 }}>STABLE</span>
                    </div>
                </GlassCard>
                <GlassCard style={{ padding: '1.5rem' }}>
                    <p style={{ fontSize: '0.7rem', fontWeight: 800, opacity: 0.4, marginBottom: '1rem', letterSpacing: '0.1em' }}>REVISION DEPTH</p>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                        <span style={{ fontSize: '2rem', fontWeight: 900 }}>48</span>
                        <span style={{ fontSize: '0.8rem', opacity: 0.4 }}>PROJECTS</span>
                    </div>
                </GlassCard>
            </div>
        </div>
    )

    const renderAgentSwarm = () => (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 1fr) 1.5fr', gap: '2.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <GlassCard style={{ padding: '2.5rem' }}>
                    <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.25rem' }}>
                        <Terminal size={22} color="var(--accent-primary)" /> REQUIREMENT INTAKE
                    </h3>
                    <p style={{ fontSize: '1rem', color: 'rgba(255,255,255,0.5)', marginBottom: '2rem', lineHeight: '1.6' }}>
                        Describe the application you want to build. Our specialist swarm will decompose it into a technical blueprint.
                    </p>
                    <textarea 
                        className="glass-input" 
                        placeholder="e.g. Build a healthcare management system with patient records, doctor scheduling, and real-time appointment alerts..."
                        style={{ width: '100%', minHeight: '300px', fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '2rem' }}
                        value={requirement}
                        onChange={(e) => setRequirement(e.target.value)}
                    />
                    <GlassButton 
                        variant="primary"
                        style={{ width: '100%', height: '60px' }} 
                        onClick={parseRequirement}
                        disabled={isParsing || !requirement}
                    >
                        {isParsing ? 'PARSING REQUIREMENTS...' : 'GENERATE ARCHITECTURE BLUEPRINT'}
                    </GlassButton>
                </GlassCard>

                <GlassCard style={{ padding: '2rem' }}>
                    <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1rem', color: 'rgba(255,255,255,0.4)' }}>
                        <Users size={18} /> ACTIVE SWARM
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        {agents.map((agent) => (
                            <div key={agent.name} style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{ padding: '0.5rem', borderRadius: '8px', background: `${agent.color}20`, border: `1px solid ${agent.color}40`, color: agent.color }}>
                                    {agent.icon}
                                </div>
                                <div>
                                    <p style={{ fontSize: '0.75rem', fontWeight: 800, margin: 0 }}>{agent.name}</p>
                                    <p style={{ fontSize: '0.65rem', color: agent.status === 'Active' || agent.status === 'Updating' ? '#00ff88' : 'rgba(255,255,255,0.3)', margin: 0, fontWeight: 600 }}>{agent.status.toUpperCase()}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </GlassCard>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                {blueprint ? (
                    <GlassCard className="animate-fade-in" style={{ padding: '2.5rem', background: 'rgba(255,255,255,0.01)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem' }}>
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.5rem' }}>
                                <Layers size={24} color="var(--accent-secondary)" /> ARCHITECTURE BLUEPRINT
                            </h3>
                            <div style={{ padding: '4px 12px', borderRadius: '20px', background: 'rgba(157, 0, 255, 0.1)', border: '1px solid rgba(157, 0, 255, 0.2)', fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-secondary)' }}>
                                V1.0 DESIGN
                            </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                            <section>
                                <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-primary)', marginBottom: '0.75rem', letterSpacing: '0.1em' }}>PROJECT IDENTITY</p>
                                <p style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>{blueprint.project_name}</p>
                            </section>
                            
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                                <section>
                                    <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-primary)', marginBottom: '1rem', letterSpacing: '0.1em' }}>DATA ARCHITECTURE</p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        {blueprint.data_layer.tables.map((t: any) => (
                                            <div key={t.name} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', padding: '0.75rem 1rem', borderRadius: '8px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                <Database size={14} color="#00ff88" />
                                                <span>{t.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                                
                                <section>
                                    <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-primary)', marginBottom: '1rem', letterSpacing: '0.1em' }}>API INFRASTRUCTURE</p>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        {blueprint.api_layer.endpoints.map((e: any) => (
                                            <div key={e.path} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', padding: '0.75rem 1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                                                <span style={{ color: 'var(--accent-secondary)', fontWeight: 800, marginRight: '0.5rem', fontSize: '0.7rem' }}>{e.method}</span>
                                                <span style={{ opacity: 0.8 }}>{e.path}</span>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            </div>

                            <section style={{ background: 'rgba(157, 0, 255, 0.05)', border: '1px solid rgba(157, 0, 255, 0.1)', padding: '1.5rem', borderRadius: '16px' }}>
                                <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--accent-secondary)', marginBottom: '0.75rem', letterSpacing: '0.1em' }}>AGENT REASONING & STRATEGY</p>
                                <p style={{ fontSize: '0.95rem', color: 'rgba(255,255,255,0.7)', lineHeight: '1.7', fontStyle: 'italic' }}>"{blueprint.reasoning}"</p>
                            </section>
                        </div>

                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', marginTop: '3rem', paddingTop: '2rem' }}>
                            {buildStatus === 'idle' && (
                                <GlassButton variant="primary" style={{ width: '100%', height: '60px' }} onClick={decomposeBlueprint} disabled={isDecomposing}>
                                    {isDecomposing ? 'DECOMPOSING...' : 'DECOMPOSE INTO AGENT TASKS'}
                                </GlassButton>
                            )}

                            {(buildStatus === 'review' || buildStatus === 'building' || buildStatus === 'complete') && (
                                <div className="animate-fade-in">
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                        <h4 style={{ color: 'var(--accent-secondary)', fontSize: '1rem', fontWeight: 700 }}>
                                            {buildStatus === 'review' ? 'PROPOSED TASK GRAPH' : 
                                             buildStatus === 'building' ? 'ACTIVE BUILD PIPELINE' : 'BUILD COMPLETE'}
                                        </h4>
                                        <span style={{ fontSize: '0.75rem', opacity: 0.4 }}>{tasks.length} INDEPENDENT TASKS</span>
                                    </div>
                                    
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2.5rem' }}>
                                        {tasks.map((task: any) => (
                                            <div key={task.id} style={{ 
                                                background: 'rgba(255,255,255,0.02)', 
                                                padding: '1.25rem', 
                                                borderRadius: '12px', 
                                                border: '1px solid rgba(255,255,255,0.05)',
                                                position: 'relative',
                                                borderLeft: `5px solid ${task.status === 'complete' ? '#00ff88' : task.status === 'in_progress' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)'}`,
                                                boxShadow: task.status === 'in_progress' ? '0 0 20px rgba(0, 243, 255, 0.05)' : 'none'
                                            }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                        <span style={{ fontSize: '0.75rem', fontWeight: 900, color: 'var(--accent-primary)', letterSpacing: '0.05em' }}>{task.agent_name}</span>
                                                        <span style={{ height: '4px', width: '4px', borderRadius: '50%', background: 'rgba(255,255,255,0.2)' }}></span>
                                                        <span style={{ fontSize: '0.7rem', opacity: 0.4, fontWeight: 600 }}>TASK_{task.id.split('-')[0].toUpperCase()}</span>
                                                    </div>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                        {task.status === 'complete' && (task.output_artifact || task.artifacts) && (
                                                            <button 
                                                                onClick={() => {
                                                                    const files = task.artifacts || { 'output.txt': task.output_artifact };
                                                                    setViewingArtifact({
                                                                        name: `${task.agent_name} Output`,
                                                                        files,
                                                                        activeFile: Object.keys(files)[0]
                                                                    });
                                                                }}
                                                                className="glass-button secondary"
                                                                style={{ fontSize: '0.65rem', padding: '4px 10px', height: 'auto' }}
                                                            >
                                                                <FileCode size={12} />
                                                                <span>VIEW CODE</span>
                                                            </button>
                                                        )}
                                                        <span style={{ 
                                                            fontSize: '0.65rem', 
                                                            fontWeight: 800, 
                                                            borderRadius: '6px', 
                                                            background: task.status === 'complete' ? 'rgba(0, 255, 136, 0.1)' : task.status === 'in_progress' ? 'rgba(0, 243, 255, 0.1)' : 'rgba(255,255,255,0.05)', 
                                                            padding: '4px 10px', 
                                                            color: task.status === 'complete' ? '#00ff88' : task.status === 'in_progress' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.3)',
                                                            border: `1px solid ${task.status === 'complete' ? 'rgba(0, 255, 136, 0.2)' : task.status === 'in_progress' ? 'rgba(0, 243, 255, 0.2)' : 'transparent'}`
                                                        }}>
                                                            {task.status.toUpperCase()}
                                                        </span>
                                                    </div>
                                                </div>
                                                <p style={{ fontSize: '0.9rem', opacity: 0.8, lineHeight: '1.5', margin: 0 }}>{task.task_description}</p>
                                                {task.dependencies.length > 0 && (
                                                    <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: 0.3 }}>
                                                        <Share2 size={12} />
                                                        <span style={{ fontSize: '0.65rem', fontWeight: 600 }}>DEPENDS ON: {task.dependencies.join(', ')}</span>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>

                                    {buildStatus === 'review' && (
                                        <div style={{ display: 'flex', gap: '1.5rem', position: 'sticky', bottom: '-2rem', background: 'var(--background)', padding: '1.5rem 0', marginTop: '-1rem', zIndex: 10 }}>
                                            <GlassButton variant="secondary" style={{ flex: 1, height: '60px' }} onClick={() => setBuildStatus('idle')}>REVISE BLUEPRINT</GlassButton>
                                            <GlassButton variant="primary" style={{ flex: 2, height: '60px' }} onClick={approveBuild}>COMMENCE PRODUCTION BUILD</GlassButton>
                                        </div>
                                    )}

                                    {buildStatus === 'building' && (
                                        <div style={{ textAlign: 'center', padding: '2rem', background: 'rgba(0,243,255,0.03)', borderRadius: '20px', border: '1px solid rgba(0,243,255,0.1)' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                                <Zap className="animate-pulse" size={20} color="var(--accent-primary)" />
                                                <span style={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '0.05em' }}>SWARM ACTIVE: EXECUTING BUILD PIPELINE...</span>
                                            </div>
                                            <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden', marginBottom: '1rem' }}>
                                                <div style={{ 
                                                    height: '100%', 
                                                    background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))', 
                                                    width: `${(tasks.filter((t: any) => t.status === 'complete').length / tasks.length) * 100}%`,
                                                    transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                                                    boxShadow: '0 0 15px var(--accent-primary)'
                                                }} />
                                            </div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', opacity: 0.4, fontWeight: 800 }}>
                                                <span>{tasks.filter((t: any) => t.status === 'complete').length} COMPLETED</span>
                                                <span>{Math.round((tasks.filter((t: any) => t.status === 'complete').length / tasks.length) * 100)}% TOTAL PROGRESS</span>
                                            </div>
                                        </div>
                                    )}

                                    {buildStatus === 'complete' && (
                                        <div className="animate-fade-in" style={{ textAlign: 'center', padding: '3rem', background: 'rgba(0,255,136,0.03)', borderRadius: '24px', border: '1px solid rgba(0,255,136,0.15)' }}>
                                            <div style={{ width: '64px', height: '64px', background: 'rgba(0,255,136,0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto' }}>
                                                <Check size={32} color="#00ff88" />
                                            </div>
                                            <h4 style={{ color: '#00ff88', fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.75rem' }}>BUILD SUCCESSFUL</h4>
                                            <p style={{ fontSize: '1.1rem', opacity: 0.6, marginBottom: '2.5rem', maxWidth: '400px', margin: '0 auto 2.5rem auto' }}>The specialist swarm has successfully completed the autonomous build cycle.</p>
                                            <GlassButton 
                                                variant="primary" 
                                                style={{ width: '100%', height: '70px', background: '#00ff88', color: '#000', fontSize: '1.1rem' }}
                                                icon={<Download size={22} />}
                                                onClick={() => window.open('http://localhost:8001/logic/download-bundle')}
                                            >
                                                DOWNLOAD PRODUCTION PACKAGE
                                            </GlassButton>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </GlassCard>
                ) : (
                    <div style={{ height: '100%', border: '2px dashed rgba(255,255,255,0.05)', borderRadius: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.15)', background: 'rgba(255,255,255,0.01)', minHeight: '600px' }}>
                        <div style={{ padding: '2rem', borderRadius: '50%', background: 'rgba(255,255,255,0.02)', marginBottom: '2rem' }}>
                            <Layers size={80} opacity={0.2} />
                        </div>
                        <h3 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>BLUEPRINT STACK EMPTY</h3>
                        <p style={{ fontSize: '1rem', opacity: 0.5 }}>Submit architecture requirements to initialize the swarm.</p>
                    </div>
                )}
            </div>
        </div>
    )



    return (
        <div className="premium-gradient-bg" style={{ display: 'flex', minHeight: '100vh', background: 'var(--background)' }}>
            {viewingArtifact && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(15px)', zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
                    <GlassCard style={{ width: '100%', maxWidth: '1200px', height: '85vh', display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
                        <div style={{ padding: '1.5rem 2rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{ padding: '0.5rem', borderRadius: '10px', background: 'rgba(0, 243, 255, 0.1)' }}>
                                    <FileCode size={20} color="var(--accent-primary)" />
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>{viewingArtifact.name}</h3>
                                    <p style={{ fontSize: '0.65rem', letterSpacing: '0.1em', opacity: 0.4 }}>WORKSPACE EXPLORER</p>
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <button className="glass-button secondary" onClick={() => {
                                    navigator.clipboard.writeText(viewingArtifact.files[viewingArtifact.activeFile])
                                    setCopied(true)
                                    setTimeout(() => setCopied(false), 1500)
                                }}>
                                    {copied ? <Check size={16} color="#00ff88" /> : <Copy size={16} />}
                                    <span>{copied ? 'COPIED' : 'COPY'}</span>
                                </button>
                                <button onClick={() => setViewingArtifact(null)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', opacity: 0.5 }}>
                                    <X size={28} />
                                </button>
                            </div>
                        </div>

                        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                            <div style={{ width: '280px', background: 'rgba(0,0,0,0.3)', borderRight: '1px solid var(--glass-border)', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto' }}>
                                <div style={{ fontSize: '0.65rem', fontWeight: 800, opacity: 0.3, marginBottom: '1rem', letterSpacing: '0.1em' }}>PROJECT STRUCTURE</div>
                                {Object.keys(viewingArtifact.files).map(filePath => (
                                    <div 
                                        key={filePath}
                                        onClick={() => setViewingArtifact({ ...viewingArtifact, activeFile: filePath })}
                                        className={`nav-link ${viewingArtifact.activeFile === filePath ? 'active' : ''}`}
                                        style={{ padding: '10px 14px', fontSize: '0.85rem' }}
                                    >
                                        <File size={16} />
                                        <span>{filePath.split('/').pop()}</span>
                                    </div>
                                ))}
                            </div>
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#08080c' }}>
                                <div style={{ flex: 1, overflow: 'auto', padding: '2.5rem' }}>
                                    <pre style={{ margin: 0, fontFamily: "'JetBrains Mono', monospace", fontSize: '0.95rem', lineHeight: '1.7', color: 'rgba(255,255,255,0.8)' }}>
                                        {viewingArtifact.files[viewingArtifact.activeFile]}
                                    </pre>
                                </div>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            )}

            <div className="sidebar">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '3.5rem' }}>
                    <div style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(0, 243, 255, 0.3)' }}>
                        <Zap size={24} color="#000" />
                    </div>
                    <span style={{ fontWeight: 800, fontSize: '1.4rem', letterSpacing: '0.05em' }}>AI<span style={{ color: 'var(--accent-primary)' }}>ORCH</span></span>
                </div>
                
                <nav style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.65rem', fontWeight: 800, opacity: 0.3, marginBottom: '1.5rem', letterSpacing: '0.2em' }}>MAIN WORKSPACE</div>
                    {[
                        { id: 'Overview', icon: <LayoutDashboard size={22} /> },
                        { id: 'Build Stack', icon: <Layers size={22} />, badge: tasks.length > 0 ? tasks.length : null },
                        { id: 'Audit Hub', icon: <Terminal size={22} /> },
                    ].map(item => (
                        <div 
                            key={item.id} 
                            onClick={() => setActiveTab(item.id)} 
                            className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
                            style={{ marginBottom: '0.75rem' }}
                        >
                            {item.icon}
                            <span style={{ flex: 1 }}>{item.id}</span>
                            {item.badge && <span style={{ background: 'var(--accent-primary)', color: '#000', fontSize: '0.65rem', fontWeight: 800, padding: '2px 8px', borderRadius: '20px' }}>{item.badge}</span>}
                        </div>
                    ))}
                    
                    <div style={{ fontSize: '0.65rem', fontWeight: 800, opacity: 0.3, margin: '2.5rem 0 1.5rem 0', letterSpacing: '0.2em' }}>GOVERNANCE</div>
                    <div 
                        onClick={() => setActiveTab('Settings')} 
                        className={`nav-link ${activeTab === 'Settings' ? 'active' : ''}`}
                    >
                        <Settings size={22} />
                        <span>System Config</span>
                    </div>
                </nav>
                
                <GlassCard style={{ padding: '1.5rem', marginTop: 'auto' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                        <div style={{ width: 10, height: 10, borderRadius: '50%', background: isConnected ? 'var(--accent-success)' : 'rgba(255,255,255,0.1)', boxShadow: isConnected ? '0 0 10px var(--accent-success)' : 'none' }}></div>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>{isConnected ? 'NODE_ACTIVE' : 'STANDBY'}</span>
                    </div>
                    <p style={{ fontSize: '0.7rem', opacity: 0.4, fontStyle: 'italic' }}>
                        Connected to {isConnected ? satelliteConfig.projectId : 'LOCAL_HUB'}
                    </p>
                </GlassCard>
            </div>

            <main className="main-content">
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4rem' }}>
                    <div>
                        <h1 style={{ fontSize: '3rem', fontWeight: 800, letterSpacing: '-0.04em', marginBottom: '0.5rem' }}>{activeTab === 'Overview' ? 'ORCHESTRATION' : activeTab.toUpperCase()}</h1>
                        <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '1.2rem', fontWeight: 400 }}>
                            {activeTab === 'Overview' ? 'The autonomous multi-agent software factory.' : `Configure and manage the ${activeTab.toLowerCase()} layer.`}
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: '1.5rem' }}>
                        <div style={{ position: 'relative', width: '48px', height: '48px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                            <Bell size={22} opacity={0.5} />
                            <div style={{ position: 'absolute', top: 12, right: 12, width: 8, height: 8, borderRadius: '50%', background: 'var(--accent-primary)', boxShadow: '0 0 10px var(--accent-primary)' }} />
                        </div>
                        <div style={{ width: '48px', height: '48px', borderRadius: '16px', border: '2px solid var(--accent-primary)', padding: '2px' }}>
                            <div style={{ width: '100%', height: '100%', borderRadius: '12px', background: 'rgba(255,255,255,0.1)', overflow: 'hidden' }}>
                                <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=Admin`} alt="User" />
                            </div>
                        </div>
                    </div>
                </header>

                <div className="animate-fade-in">
                    {activeTab === 'Overview' && renderOverview()}
                    {activeTab === 'Build Stack' && renderAgentSwarm()}
                    {activeTab === 'Audit Hub' && renderAuditLogs()}
                    {activeTab === 'Settings' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '3rem' }}>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                                    {/* LLM Engine Configuration */}
                                    <section>
                                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 700 }}>
                                            <Cpu size={22} color="var(--accent-primary)" /> LLM ENGINE ORCHESTRATION
                                        </h3>
                                        <GlassCard style={{ padding: '2.5rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                        <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>ACTIVE PROVIDER</label>
                                                        <select 
                                                            className="glass-input" 
                                                            style={{ height: '50px', appearance: 'none' }}
                                                            value={config.active_llm_engine}
                                                            onChange={(e) => updateConfig({ active_llm_engine: e.target.value })}
                                                        >
                                                            {config.llm_engines.map((eng: any) => (
                                                                <option key={eng.name} value={eng.name} style={{ background: '#111' }}>{eng.name}</option>
                                                            ))}
                                                        </select>
                                                    </div>
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                        <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>PRIMARY MODEL</label>
                                                        <select 
                                                            className="glass-input" 
                                                            style={{ height: '50px', appearance: 'none' }}
                                                            value={config.active_model}
                                                            onChange={(e) => updateConfig({ active_model: e.target.value })}
                                                        >
                                                            {config.llm_engines.find((e: any) => e.name === config.active_llm_engine)?.models.map((m: string) => (
                                                                <option key={m} value={m} style={{ background: '#111' }}>{m}</option>
                                                            ))}
                                                        </select>
                                                    </div>
                                                </div>

                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                                                        <div>
                                                            <p style={{ margin: 0, fontWeight: 700, fontSize: '0.95rem' }}>Multi-Engine Routing</p>
                                                            <p style={{ margin: 0, fontSize: '0.75rem', opacity: 0.4 }}>Automatically switch engines based on task complexity</p>
                                                        </div>
                                                        <div 
                                                            onClick={() => updateConfig({ multi_llm_orchestration: !config.multi_llm_orchestration })}
                                                            style={{ width: '50px', height: '26px', borderRadius: '13px', background: config.multi_llm_orchestration ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)', cursor: 'pointer', position: 'relative', transition: 'all 0.3s' }}
                                                        >
                                                            <div style={{ position: 'absolute', top: '3px', left: config.multi_llm_orchestration ? '27px' : '3px', width: '20px', height: '20px', borderRadius: '50%', background: config.multi_llm_orchestration ? '#000' : '#fff', transition: 'all 0.3s' }}></div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                            <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>OLLAMA URL</label>
                                                            <GlassInput 
                                                                type="text" 
                                                                value={config.ollama_url || ''} 
                                                                onChange={(e) => updateConfig({ ollama_url: e.target.value })}
                                                                placeholder="http://localhost:11434"
                                                            />
                                                        </div>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                            <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>LMSTUDIO URL</label>
                                                            <GlassInput 
                                                                type="text" 
                                                                value={config.lmstudio_url || ''} 
                                                                onChange={(e) => updateConfig({ lmstudio_url: e.target.value })}
                                                                placeholder="http://localhost:1234"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                            <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>GPT4ALL URL</label>
                                                            <GlassInput 
                                                                type="text" 
                                                                value={config.gpt4all_url || ''} 
                                                                onChange={(e) => updateConfig({ gpt4all_url: e.target.value })}
                                                                placeholder="http://localhost:4891"
                                                            />
                                                        </div>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                            <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>VLLM URL</label>
                                                            <GlassInput 
                                                                type="text" 
                                                                value={config.vllm_url || ''} 
                                                                onChange={(e) => updateConfig({ vllm_url: e.target.value })}
                                                                placeholder="http://localhost:8000"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                        <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>PERPLEXITY API KEY</label>
                                                        <GlassInput 
                                                            type="password" 
                                                            value={config.perplexity_api_key || ''} 
                                                            onChange={(e) => updateConfig({ perplexity_api_key: e.target.value })}
                                                            placeholder="pplx-..."
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        </GlassCard>
                                    </section>

                                    {/* Webhook & Integration */}
                                    <section>
                                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 700 }}>
                                            <Share2 size={22} color="var(--accent-secondary)" /> INTEGRATIONS & WEBHOOKS
                                        </h3>
                                        <GlassCard style={{ padding: '2.5rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                    <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>SYSTEM ALERT WEBHOOK</label>
                                                    <div style={{ display: 'flex', gap: '1rem' }}>
                                                        <GlassInput 
                                                            type="text" 
                                                            style={{ flex: 1 }}
                                                            value={config.webhook_url || ''} 
                                                            onChange={(e) => updateConfig({ webhook_url: e.target.value })}
                                                            placeholder="https://hooks.slack.com/services/..."
                                                        />
                                                        <GlassButton variant="secondary">TEST</GlassButton>
                                                    </div>
                                                    <p style={{ fontSize: '0.7rem', opacity: 0.3, marginTop: '0.5rem' }}>Triggers on critical provider failures or build completion.</p>
                                                </div>
                                            </div>
                                        </GlassCard>
                                    </section>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                                    {/* Security & Access */}
                                    <section>
                                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 700 }}>
                                            <Shield size={22} color="#ff6400" /> GOVERNANCE & ACCESS
                                        </h3>
                                        <GlassCard style={{ padding: '2rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                    <div>
                                                        <p style={{ margin: 0, fontWeight: 700 }}>Active Role</p>
                                                        <p style={{ margin: 0, fontSize: '0.75rem', opacity: 0.4 }}>Current user permissions</p>
                                                    </div>
                                                    <span style={{ padding: '4px 12px', borderRadius: '6px', background: userRole === 'admin' ? 'rgba(255, 100, 0, 0.1)' : 'rgba(255,255,255,0.05)', color: userRole === 'admin' ? '#ff6400' : '#fff', fontSize: '0.75rem', fontWeight: 800, border: userRole === 'admin' ? '1px solid rgba(255, 100, 0, 0.2)' : '1px solid rgba(255,255,255,0.1)' }}>
                                                        {userRole.toUpperCase()}
                                                    </span>
                                                </div>

                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                    <div>
                                                        <p style={{ margin: 0, fontWeight: 700 }}>Unlimited Admin Tokens</p>
                                                        <p style={{ margin: 0, fontSize: '0.75rem', opacity: 0.4 }}>Bypass token limits for admins</p>
                                                    </div>
                                                    <div 
                                                        onClick={() => updateConfig({ unlimited_admin_tokens: !config.unlimited_admin_tokens })}
                                                        style={{ width: '50px', height: '26px', borderRadius: '13px', background: config.unlimited_admin_tokens ? '#ff6400' : 'rgba(255,255,255,0.1)', cursor: 'pointer', position: 'relative', transition: 'all 0.3s' }}
                                                    >
                                                        <div style={{ position: 'absolute', top: '3px', left: config.unlimited_admin_tokens ? '27px' : '3px', width: '20px', height: '20px', borderRadius: '50%', background: '#fff', transition: 'all 0.3s' }}></div>
                                                    </div>
                                                </div>

                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                    <label style={{ fontSize: '0.75rem', fontWeight: 800, opacity: 0.4, letterSpacing: '0.1em' }}>TOKEN LIMIT (PER PROJECT)</label>
                                                    <GlassInput 
                                                        type="number" 
                                                        value={config.token_limit} 
                                                        onChange={(e) => updateConfig({ token_limit: parseInt(e.target.value) })}
                                                    />
                                                </div>
                                            </div>
                                        </GlassCard>
                                    </section>

                                    {/* Advanced Operations */}
                                    <section>
                                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 700 }}>
                                            <Terminal size={22} color="rgba(255,255,255,0.3)" /> SYSTEM OPERATIONS
                                        </h3>
                                        <GlassCard style={{ padding: '2rem', border: '1px solid rgba(255,70,70,0.15)' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                                <div>
                                                    <p style={{ margin: 0, fontWeight: 700, color: '#ff4646' }}>DANGER ZONE</p>
                                                    <p style={{ margin: 0, fontSize: '0.75rem', opacity: 0.4 }}>Irreversible system operations</p>
                                                </div>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                                    <GlassButton 
                                                        variant="secondary" 
                                                        style={{ width: '100%', borderColor: 'rgba(255,70,70,0.2)', color: '#ff4646' }}
                                                        icon={<RotateCcw size={18} />}
                                                        onClick={factoryReset}
                                                    >
                                                        FACTORY RESET SYSTEM
                                                    </GlassButton>
                                                </div>
                                            </div>
                                        </GlassCard>
                                    </section>
                                </div>
                            </div>

                            {/* MCP Tools Section */}
                            <section>
                                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '1.25rem', fontWeight: 700 }}>
                                    <Box size={22} color="var(--accent-primary)" /> MCP ECOSYSTEM
                                </h3>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '2rem' }}>
                                    {config.mcp_tools.map((tool: any) => (
                                        <GlassCard key={tool.name} style={{ padding: '1.5rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                                <div style={{ padding: '0.5rem', borderRadius: '8px', background: 'rgba(0, 243, 255, 0.05)', border: '1px solid rgba(0, 243, 255, 0.1)' }}>
                                                    <Box size={18} color="var(--accent-primary)" />
                                                </div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#00ff88' }}></div>
                                                    <span style={{ fontSize: '0.65rem', fontWeight: 800, color: '#00ff88' }}>{tool.status.toUpperCase()}</span>
                                                </div>
                                            </div>
                                            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>{tool.name}</h4>
                                            <p style={{ margin: 0, fontSize: '0.75rem', opacity: 0.4 }}>Standard Model Context Protocol Integration</p>
                                        </GlassCard>
                                    ))}
                                    <GlassCard style={{ padding: '1.5rem', border: '1px dashed rgba(255,255,255,0.1)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', opacity: 0.5 }}>
                                        <Plus size={24} style={{ marginBottom: '0.5rem' }} />
                                        <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>CONNECT NEW MCP</span>
                                    </GlassCard>
                                </div>
                            </section>
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}
