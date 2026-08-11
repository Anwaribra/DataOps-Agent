'use client';

import React from 'react';
import { BrainCircuit, CheckCircle2, ShieldAlert, ArrowRight, Layers, HelpCircle } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const DiagnosisSection: React.FC = () => {
  const { incident, setActiveSection } = useDemo();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              AI Agent Diagnosis Report
            </h2>
            <span className="px-2.5 py-0.5 text-[10px] font-mono font-bold rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              HIGH CONFIDENCE (95%)
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Evidence-grounded root cause analysis produced by the LLM DataOps Agent over read-only MCP tools.
          </p>
        </div>

        <button
          onClick={() => setActiveSection('remediation')}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
        >
          <span>View Remediation Plan</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Main Grid: Root Cause & Confidence */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Root Cause & Impact */}
        <div className="lg:col-span-2 space-y-4">
          {/* Root Cause Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Root Cause Analysis
              </span>
              <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-semibold">
                Grounding: MCP Grounded
              </span>
            </div>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 leading-relaxed">
              Upstream source data-quality regression introduced NULL customer_id values during the latest ingestion batch.
            </p>
          </div>

          {/* Impact Assessment Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Operational Impact
            </span>
            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              Order attribution metrics and customer lifetime value calculations in <code className="font-mono text-emerald-600 dark:text-emerald-400">fct_orders</code> and downstream analytics will contain incomplete data records if unaddressed.
            </p>
          </div>
        </div>

        {/* Right Col: Affected Assets & Confidence Gauge */}
        <div className="space-y-4">
          {/* Confidence Score Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm text-center space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Diagnosis Confidence
            </span>
            <div className="text-3xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400">
              95.0%
            </div>
            <span className="inline-block px-2.5 py-0.5 text-[10px] font-mono font-medium rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              HIGH CONFIDENCE
            </span>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 pt-2">
              Based on 6 agreeing MCP tool signals and dbt assertion failure matches.
            </p>
          </div>

          {/* Affected Assets Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Affected Assets
            </span>
            <div className="space-y-2">
              {['stg_orders', 'fct_orders', 'daily_revenue'].map(asset => (
                <div key={asset} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 text-xs">
                  <span className="font-mono text-slate-800 dark:text-slate-200">{asset}</span>
                  <span className="px-1.5 py-0.5 text-[10px] font-mono bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 rounded">
                    DEGRADED
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Facts vs Inferences Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Observed Evidence (Facts) */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
              Observed Evidence (Facts)
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              MCP Fact Stream
            </span>
          </div>

          <ul className="space-y-2.5 text-xs text-slate-600 dark:text-slate-300">
            {[
              'dbt test failure: not_null_stg_orders_customer_id (2 failing records)',
              'Dagster asset check halted downstream execution for stg_orders & fct_orders',
              'customer_id NULL count in stg_orders increased to 2 (20.0% null ratio)',
              'Failure isolated to raw_orders batch extraction timestamp 2026-02-25T12:00:00Z',
              'Lineage confirmed: raw_orders → stg_orders → fct_orders'
            ].map((fact, idx) => (
              <li key={idx} className="flex items-start gap-2.5 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>{fact}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Right: Agent Inferences (Reasoning) */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm">
              Inferences & Operational Reasoning
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
              Agent Inference
            </span>
          </div>

          <ul className="space-y-2.5 text-xs text-slate-600 dark:text-slate-300">
            {[
              'The latest ingestion batch extracted unpopulated customer foreign keys from source JSON payload.',
              'Transformation failed dbt not_null assertions on stg_orders prior to mart materialization.',
              'Isolating corrupt records via quarantine will allow clean rebuild of downstream analytical marts.'
            ].map((inf, idx) => (
              <li key={idx} className="flex items-start gap-2.5 p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                <BrainCircuit className="w-4 h-4 text-sky-500 shrink-0 mt-0.5" />
                <span>{inf}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
