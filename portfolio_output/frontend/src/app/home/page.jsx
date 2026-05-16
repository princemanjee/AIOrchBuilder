// File: app/home/page.jsx
import React from 'react';
import { Hero } from '../../components/Hero';
import { ExperienceTimeline } from '../../components/ExperienceTimeline';
import { ContactForm } from '../../components/ContactForm';
import { AnalyticsChart } from '../../components/AnalyticsChart';
import { RoleCardUxStrategyDigitalTransformationConsultant } from '../../components/RoleCardUxStrategyDigitalTransformationConsultant';
import { RoleCardInformationTechnologySolutionsArchitect } from '../../components/RoleCardInformationTechnologySolutionsArchitect';
import { RoleCardDigitalTransformationDirector } from '../../components/RoleCardDigitalTransformationDirector';

export default function HomePage() {
    return (
        <main className="page-wrapper fade-in-up">
            <header className="page-header">
                <div className="tag-pill" style={{ color: '#00f3ff', borderColor: '#00f3ff40', backgroundColor: '#00f3ff10' }}>Intelligent Module</div>
                <h1 className="page-title">Home Workspace</h1>
                <p className="page-subtitle">Sandbox environment for the Home data models and interactive tools.</p>
            </header>
            
            <section className="component-grid">
                <Hero />
<ExperienceTimeline />
<ContactForm />
<AnalyticsChart />
<RoleCardUxStrategyDigitalTransformationConsultant />
<RoleCardInformationTechnologySolutionsArchitect />
<RoleCardDigitalTransformationDirector />
            </section>
        </main>
    );
}
