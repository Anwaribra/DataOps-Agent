'use client';

import React, { useState } from 'react';
import { Workflow, Info, Database, Server, BrainCircuit, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { ARCHITECTURE_COMPONENTS } from '../data/demoData';

export const ArchitectureSection: React.FC = () => {
  const [selectedCompId, setSelectedCompId] = useState<string>('arch_mcp');

  const selectedComp = ARCHITECTURE_COMPONENTS.find(c => c.id === selectedCompId) || ARCHITECTURE_COMPONENTS[7];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-4 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          System Architecture & Component Graph
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Closed-loop DataOps Agent architecture. Click any component card to inspect its technology stack, purpose, and operational responsibilities.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Architectural Nodes Topology */}
        <div className="lg:col-span-2 space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Platform Components Flow
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ARCHITECTURE_COMPONENTS.map(comp => {
              const isSelected = selectedComp.id === comp.id;
              return (
                <div
                  key={comp.id}
                  onClick={() => setSelectedCompId(comp.id)}
                  className={`p-4 rounded-2xl bg-white dark:bg-slate-900/90 border cursor-pointer transition-all duration-150 ${
                    isSelected
                      ? 'border-emerald-500 ring-2 ring-emerald-500/20 shadow-md'
                      : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 shadow-sm'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <h4 className="font-bold text-xs text-slate-900 dark:text-slate-100">{comp.name}</h4>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                      {comp.tech}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-normal">
                    {comp.purpose}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Selected Component Inspector */}
        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Component Inspector
          </h3>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 sticky top-20">
            <div className="flex items-center gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center justify-center font-bold">
                <Workflow className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">{selectedComp.name}</h4>
                <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400">{selectedComp.tech}</span>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="font-semibold text-slate-400 block mb-1">Primary Purpose</span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{selectedComp.purpose}</p>
              </div>

              <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                <span className="font-semibold text-slate-400 block mb-1">Operational Responsibilities</span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{selectedComp.responsibility}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
