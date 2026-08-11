'use client';

import React from 'react';
import {
  LayoutDashboard,
  GitMerge,
  AlertTriangle,
  Search,
  BrainCircuit,
  ShieldCheck,
  CheckCircle2,
  Workflow,
  Sparkles
} from 'lucide-react';
import { SectionId, useDemo } from '../context/DemoContext';

interface NavItem {
  id: SectionId;
  label: string;
  icon: React.ElementType;
  badge?: string;
}

export const Sidebar: React.FC = () => {
  const { activeSection, setActiveSection, simulationState } = useDemo();

  const navItems: NavItem[] = [
    { id: 'overview', label: '1. Overview', icon: LayoutDashboard },
    { id: 'pipeline', label: '2. Pipeline Health', icon: GitMerge },
    {
      id: 'incidents',
      label: '3. Incidents',
      icon: AlertTriangle,
      badge: simulationState !== 'HEALTHY' && simulationState !== 'RESOLVED' ? '1' : undefined
    },
    { id: 'investigation', label: '4. Investigation', icon: Search },
    { id: 'diagnosis', label: '5. Agent Diagnosis', icon: BrainCircuit },
    { id: 'remediation', label: '6. Remediation Plan', icon: ShieldCheck },
    { id: 'verification', label: '7. Verification', icon: CheckCircle2 },
    { id: 'architecture', label: '8. Architecture', icon: Workflow }
  ];

  return (
    <aside className="w-64 shrink-0 bg-slate-900/50 dark:bg-slate-950/80 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between p-4 min-h-screen select-none transition-colors duration-200">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-3 py-3 mb-6">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-500 dark:text-emerald-400 font-bold shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-900 dark:text-slate-100 text-sm tracking-tight">DataOps Agent</h1>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">Agentic Data Platform</p>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-slate-200/80 dark:bg-slate-800/90 text-slate-900 dark:text-slate-50 shadow-sm border border-slate-300/50 dark:border-slate-700/50'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 rounded-md">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer Box */}
      <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-xs">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Environment</span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-medium rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Sandbox Mode
          </span>
        </div>
        <p className="text-[11px] text-slate-500 dark:text-slate-500 leading-normal">
          Deterministic scenario simulation environment. Real credentials isolated.
        </p>
      </div>
    </aside>
  );
};
