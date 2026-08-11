'use client';

import React from 'react';
import { AlertTriangle, ArrowRight, ShieldCheck, CheckCircle2, Clock } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const IncidentsSection: React.FC = () => {
  const { incident, setActiveSection, simulationState } = useDemo();

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'HIGH':
      case 'CRITICAL':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
            HIGH
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            MEDIUM
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    if (status === 'RESOLVED') {
      return (
        <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
          RESOLVED
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Pipeline Incidents Log
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Recorded pipeline assertion failures and AI Agent diagnostic reports.
          </p>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <th className="py-3.5 px-4">Incident ID</th>
                <th className="py-3.5 px-4">Severity</th>
                <th className="py-3.5 px-4">Incident Title</th>
                <th className="py-3.5 px-4">Affected Asset</th>
                <th className="py-3.5 px-4">Failed Assertion</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Created</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs">
              <tr className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                <td className="py-4 px-4 font-mono font-semibold text-slate-900 dark:text-slate-100">
                  {incident.id}
                </td>
                <td className="py-4 px-4">{getSeverityBadge(incident.severity)}</td>
                <td className="py-4 px-4 font-medium text-slate-900 dark:text-slate-200 max-w-xs truncate">
                  {incident.title}
                </td>
                <td className="py-4 px-4 font-mono text-slate-600 dark:text-slate-400">
                  {incident.affectedAsset}
                </td>
                <td className="py-4 px-4 font-mono text-rose-600 dark:text-rose-400 text-[11px]">
                  {incident.failedTest}
                </td>
                <td className="py-4 px-4">{getStatusBadge(incident.status)}</td>
                <td className="py-4 px-4 text-slate-400 text-[11px] font-mono">{incident.createdAt}</td>
                <td className="py-4 px-4 text-right">
                  <button
                    onClick={() => setActiveSection('investigation')}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium transition-colors"
                  >
                    <span>Investigate</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
