'use client';

import React from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Layers,
  Clock,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const OverviewSection: React.FC = () => {
  const { metrics, simulationState, setActiveSection } = useDemo();

  return (
    <div className="space-y-6">
      {/* Banner / Headline */}
      <div className="p-6 rounded-2xl bg-slate-900/60 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-[11px] font-mono font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Closed-Loop Autonomous Observability
            </span>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-white">
            DataOps Agent Control Center
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
            An agentic DataOps platform that monitors batch pipelines, diagnoses data-quality failures via Model Context Protocol (MCP), and executes human-approved recovery workflows.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => setActiveSection('pipeline')}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            View Pipeline Graph
          </button>
          <button
            onClick={() => setActiveSection('architecture')}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
          >
            System Architecture
          </button>
        </div>
      </div>

      {/* Top 6 Operational Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Metric 1: System Status */}
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">System Status</span>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="flex items-baseline justify-between">
            <span
              className={`text-lg font-bold ${
                metrics.systemStatus === 'HEALTHY'
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : 'text-rose-600 dark:text-rose-400'
              }`}
            >
              {metrics.systemStatus}
            </span>
            <span className="text-[10px] font-mono text-slate-400">Postgres 16</span>
          </div>
        </div>

        {/* Metric 2: Pipeline Health */}
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Pipeline Health</span>
            <TrendingUp className="w-4 h-4 text-sky-500" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100">
              {metrics.pipelineHealth}%
            </span>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">8 total nodes</span>
          </div>
        </div>

        {/* Metric 3: Active Incidents */}
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Active Incidents</span>
            <AlertTriangle className={`w-4 h-4 ${metrics.activeIncidentsCount > 0 ? 'text-rose-500' : 'text-slate-400'}`} />
          </div>
          <div className="flex items-baseline justify-between">
            <span className={`text-2xl font-bold font-mono ${metrics.activeIncidentsCount > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-slate-100'}`}>
              {metrics.activeIncidentsCount}
            </span>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">INC-001</span>
          </div>
        </div>

        {/* Metric 4: Failed Assets */}
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Failed Assets</span>
            <Layers className={`w-4 h-4 ${metrics.failedAssetsCount > 0 ? 'text-amber-500' : 'text-slate-400'}`} />
          </div>
          <div className="flex items-baseline justify-between">
            <span className={`text-2xl font-bold font-mono ${metrics.failedAssetsCount > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-slate-100'}`}>
              {metrics.failedAssetsCount}
            </span>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">stg_orders</span>
          </div>
        </div>

        {/* Metric 5: Data Quality Score */}
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Data Quality</span>
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100">
              {metrics.dataQualityScore}%
            </span>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">27 tests</span>
          </div>
        </div>

        {/* Metric 6: Last Run */}
        <div className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
            <span className="text-xs font-medium">Last Batch Run</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-xs font-semibold font-mono text-slate-900 dark:text-slate-200 truncate">
              {metrics.lastRun}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Status Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Operational Lifecycle */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
              Closed-Loop Operational Workflow
            </h3>
            <span className="text-xs font-mono text-slate-500">6 Stages</span>
          </div>

          <div className="space-y-2.5">
            {[
              { title: '1. Detect', desc: 'Catch NULL assertions via dbt tests and Dagster asset checks', status: 'ACTIVE' },
              { title: '2. Diagnose', desc: 'Trace lineage and query statistics over read-only MCP tools', status: 'ACTIVE' },
              { title: '3. Plan', desc: 'Formulate allowlisted remediation plan with risk score', status: 'ACTIVE' },
              { title: '4. Approve', desc: 'Mandatory Human Approval Gate (Agent cannot approve)', status: 'ACTIVE' },
              { title: '5. Remediate', desc: 'Execute idempotent quarantine and model refresh', status: 'ACTIVE' },
              { title: '6. Verify', desc: 'Audit recovery metrics before marking incident RESOLVED', status: 'ACTIVE' }
            ].map((step, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 text-xs">
                <div>
                  <span className="font-semibold text-slate-900 dark:text-slate-200">{step.title}</span>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">{step.desc}</p>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-mono font-medium rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  {step.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Security & Architecture Summary */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
              Security Boundaries & Safety Governance
            </h3>
            <span className="px-2 py-0.5 text-[10px] font-mono bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded-md">
              ENFORCED
            </span>
          </div>

          <div className="space-y-3 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
              <span className="font-semibold text-slate-900 dark:text-slate-200 block mb-1">
                Zero Direct Infrastructure Write Access
              </span>
              The AI Agent interacts exclusively over standard Model Context Protocol (MCP) tools. Direct raw SQL execution (<code className="font-mono text-emerald-500">execute_sql</code>) and shell commands are forbidden.
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
              <span className="font-semibold text-slate-900 dark:text-slate-200 block mb-1">
                Self-Approval Prevention
              </span>
              The agent proposes remediation plans but is strictly forbidden from approving its own actions. Human operator approval (with 30-minute TTL expiration) is mandatory.
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800">
              <span className="font-semibold text-slate-900 dark:text-slate-200 block mb-1">
                Allowlisted Remediation & Idempotency
              </span>
              Execution is restricted to explicit allowlisted actions (<code className="font-mono text-emerald-500">quarantine_invalid_records</code>, <code className="font-mono text-emerald-500">refresh_dbt_model</code>, <code className="font-mono text-emerald-500">rerun_dagster_asset</code>) with idempotent execution.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
