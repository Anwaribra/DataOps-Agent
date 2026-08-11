'use client';

import React from 'react';
import { ThemeProvider } from '../context/ThemeContext';
import { DemoProvider, useDemo } from '../context/DemoContext';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';
import { OverviewSection } from '../components/OverviewSection';
import { PipelineHealthSection } from '../components/PipelineHealthSection';
import { IncidentsSection } from '../components/IncidentsSection';
import { InvestigationSection } from '../components/InvestigationSection';
import { DiagnosisSection } from '../components/DiagnosisSection';
import { RemediationSection } from '../components/RemediationSection';
import { ExecutionSection } from '../components/ExecutionSection';
import { VerificationSection } from '../components/VerificationSection';
import { ArchitectureSection } from '../components/ArchitectureSection';
import { Footer } from '../components/Footer';

function MainContent() {
  const { activeSection, simulationState } = useDemo();

  return (
    <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Dynamic Section Rendering */}
      {activeSection === 'overview' && <OverviewSection />}
      {activeSection === 'pipeline' && <PipelineHealthSection />}
      {activeSection === 'incidents' && <IncidentsSection />}
      {activeSection === 'investigation' && <InvestigationSection />}
      {activeSection === 'diagnosis' && <DiagnosisSection />}
      {activeSection === 'remediation' && (
        <>
          <RemediationSection />
          {(simulationState === 'EXECUTING' || simulationState === 'VERIFYING' || simulationState === 'RESOLVED') && (
            <ExecutionSection />
          )}
        </>
      )}
      {activeSection === 'verification' && <VerificationSection />}
      {activeSection === 'architecture' && <ArchitectureSection />}

      <Footer />
    </main>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <DemoProvider>
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col md:flex-row transition-colors duration-200">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Topbar />
            <MainContent />
          </div>
        </div>
      </DemoProvider>
    </ThemeProvider>
  );
}
