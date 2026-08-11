'use client';

import React from 'react';
import { CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const ExecutionSection: React.FC = () => {
  const { simulationState } = useDemo();

  const steps = [
    { title: '1. Human Approval Validated', desc: 'Approval TTL verified (30m window); Self-approval check passed', status: 'PASSED' },
    { title: '2. Action Safety Rules Validated', desc: 'Action type quarantine_invalid_records validated against allowlist', status: 'PASSED' },
    { title: '3. Quarantine Corrupt Records', desc: 'Moved 2 NULL customer_id records to staging_stg_orders_quarantine table', status: 'PASSED' },
    { title: '4. Refresh dbt Transformation', desc: 'Re-compiled and refreshed fct_orders dbt mart model cleanly', status: 'PASSED' },
    { title: '5. Re-run Dagster Asset Graph', desc: 'Re-executed Dagster asset pipeline check dagster_run_fct_orders_001', status: 'PASSED' },
    { title: '6. Trigger Recovery Verification', desc: 'Audited post-execution assertions and asset health metrics', status: 'PASSED' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Infrastructure Execution Timeline
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Step-by-step progress of approved allowlisted remediation actions.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {steps.map((step, idx) => (
          <div
            key={idx}
            className="p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-xs">{step.title}</h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">{step.desc}</p>
              </div>
            </div>
            <span className="px-2 py-0.5 text-[10px] font-mono font-medium rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              {step.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
