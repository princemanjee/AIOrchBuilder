// File: src/app/layout.tsx
import './globals.css'
import './components.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'AIOrchBuilder | The Multi-Agent Orchestration Framework',
    description: 'Transforming nebulous ideas into production-ready software through systematic, autonomous execution.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    )
}
