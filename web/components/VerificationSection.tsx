'use client';

import React from 'react';
import { CheckCircle2, ShieldCheck, TrendingUp, RefreshCw, Layers } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const VerificationSection: React.FC = () => {
  const { verificationChecks, simulationState, resetDemo } = useDemo();

  const isResolved = simulationState === 'RESOLVED';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Recovery Verification & Incident Resolution
            </h2>
            <span className="px-2.5 py-0.5 text-[10px] font-mono font-bold rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              {isResolved ? 'INCIDENT RESOLVED' : 'VERIFICATION PENDING'}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Post-remediation data quality assertions and Dagster asset health audit.
          </p>
        </div>

        <button
          onClick={resetDemo}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 shadow-sm transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Demo Environment</span>
        </button>
      </div>

      {/* Before / After Metrics Comparison Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
          <span className="text-xs font-medium text-slate-400">Data Quality Score</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">99.8%</span>
            <span className="text-xs font-mono text-slate-400 line-through">91.6%</span>
          </div>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium block pt-1">+8.2% Recovery</span>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
          <span className="text-xs font-medium text-slate-400">Failing dbt Assertions</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">0</span>
            <span className="text-xs font-mono text-slate-400 line-through">3</span>
          </div>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium block pt-1">All tests passing</span>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
          <span className="text-xs font-medium text-slate-400">Failed Dagster Assets</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">0</span>
            <span className="text-xs font-mono text-slate-400 line-through">2</span>
          </div>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium block pt-1">Pipeline healthy</span>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
          <span className="text-xs font-medium text-slate-400">Incident INC-001</span>
          <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 pt-1">
            RESOLVED
          </div>
          <span className="text-[10px] text-slate-400 block">Closed-loop recovery verified</span>
        </div>
      </div>

      {/* Automated Checks Table */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Automated Recovery Verification Checks
        </h3>

        <div className="space-y-3">
          {verificationChecks.map((chk, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-slate-100">{chk.checkName}</h4>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">{chk.evidence}</p>
                </div>
              </div>

              <div className="text-right font-mono">
                <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  {chk.status}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  Actual: {chk.actual}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
