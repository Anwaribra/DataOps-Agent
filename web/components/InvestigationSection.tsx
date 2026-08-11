'use client';

import React from 'react';
import { Search, CheckCircle2, Server, Terminal, FileText, ArrowRight } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const InvestigationSection: React.FC = () => {
  const { mcpSteps, mcpStepsCount, simulationState, setActiveSection } = useDemo();

  const activeSteps = mcpSteps.slice(0, mcpStepsCount);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Agent Investigation & MCP Tool Trace
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              Read-Only Governance
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time auditable trace of tool calls executed by the DataOps Agent over standard Model Context Protocol (MCP).
          </p>
        </div>

        {simulationState === 'DIAGNOSED' && (
          <button
            onClick={() => setActiveSection('diagnosis')}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
          >
            <span>View Agent Diagnosis</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Timeline Steps Container */}
      <div className="space-y-4">
        {activeSteps.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800">
            <Search className="w-8 h-8 text-slate-400 mx-auto mb-3" />
            <h3 className="font-semibold text-slate-900 dark:text-slate-200 text-sm mb-1">
              No Investigation Currently Active
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mb-4">
              Click &quot;RUN DEMO INCIDENT&quot; in the top bar to trigger an automated investigation loop.
            </p>
          </div>
        ) : (
          activeSteps.map((step, idx) => (
            <div
              key={step.step}
              className="p-5 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3 transition-all duration-200"
            >
              {/* Step Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center text-xs font-mono font-bold">
                    {step.step}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-900 dark:text-slate-100 text-sm">
                        {step.tool}()
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        MCP Tool Call
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal">
                      {step.purpose}
                    </p>
                  </div>
                </div>

                <span className="flex items-center gap-1.5 px-2.5 py-1 text-[10px] font-mono font-semibold rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  SUCCESS
                </span>
              </div>

              {/* Arguments & Operational Result */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-2 border-t border-slate-100 dark:border-slate-800/80">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800/80">
                  <span className="text-[11px] font-medium text-slate-400 block mb-1">
                    Input Parameters (Arguments)
                  </span>
                  <code className="font-mono text-slate-800 dark:text-slate-200 text-[11px] block truncate">
                    {JSON.stringify(step.arguments)}
                  </code>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800/80">
                  <span className="text-[11px] font-medium text-slate-400 block mb-1">
                    Fact Extracted (Evidence)
                  </span>
                  <span className="font-medium text-emerald-700 dark:text-emerald-300 text-[11px] block">
                    {step.factExtracted}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
