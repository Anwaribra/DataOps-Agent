'use client';

import React from 'react';
import { ShieldCheck, AlertOctagon, CheckCircle2, XCircle, ArrowRight, Lock } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const RemediationSection: React.FC = () => {
  const { remediationActions, simulationState, approvePlan, rejectPlan, setActiveSection } = useDemo();

  const isApproved = simulationState === 'APPROVED' || simulationState === 'EXECUTING' || simulationState === 'VERIFYING' || simulationState === 'RESOLVED';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Remediation Plan & Human Approval Gate
            </h2>
            <span className="px-2.5 py-0.5 text-[10px] font-mono font-bold rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              PLAN-001 (LOW RISK)
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Allowlisted recovery actions proposed by AI DataOps Agent. Human operator authorization required before execution.
          </p>
        </div>

        {isApproved && (
          <button
            onClick={() => setActiveSection('verification')}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
          >
            <span>View Recovery Verification</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Human Approval Gate Warning Banner */}
      <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-900 dark:text-amber-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-amber-900 dark:text-amber-100">
              HUMAN APPROVAL REQUIRED (PLAN-001)
            </h3>
            <p className="text-xs text-amber-800 dark:text-amber-300 leading-normal mt-0.5 max-w-xl">
              <strong className="font-bold">THE AGENT CANNOT APPROVE ITS OWN ACTION.</strong> The AI agent can propose remediation plans over MCP tools, but cannot authorize write executions. Operator approval required.
            </p>
          </div>
        </div>

        {/* Approval Action Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          {!isApproved ? (
            <>
              <button
                onClick={rejectPlan}
                className="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold border border-slate-300 dark:border-slate-700 transition-colors"
              >
                Reject Plan
              </button>
              <button
                onClick={approvePlan}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-500/20 border border-emerald-500 transition-all duration-150"
              >
                APPROVE REMEDIATION
              </button>
            </>
          ) : (
            <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/40 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>APPROVED BY HUMAN OPERATOR</span>
            </div>
          )}
        </div>
      </div>

      {/* Proposed Actions List */}
      <div className="space-y-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Proposed Allowlisted Actions
        </h3>

        <div className="space-y-3">
          {remediationActions.map((action, idx) => (
            <div
              key={action.id}
              className="p-5 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-mono font-bold text-xs text-slate-700 dark:text-slate-300">
                    {idx + 1}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-900 dark:text-slate-100 text-sm">
                        {action.actionType}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        Target: {action.target}
                      </span>
                    </div>
                  </div>
                </div>

                <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  Risk: {action.risk}
                </span>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-normal pl-10">
                {action.expectedOutcome}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
