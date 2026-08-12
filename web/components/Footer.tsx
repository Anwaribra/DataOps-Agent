'use client';

import React from 'react';
import { FileText, ShieldCheck, Sparkles, Code2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-12 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 p-6 md:p-8 text-xs text-slate-500 dark:text-slate-400 space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Left Brand */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-500" />
            <span className="font-bold text-slate-900 dark:text-slate-100 text-sm">DataOps Agent</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-md">
            An agentic DataOps platform that investigates pipeline failures, diagnoses root causes, and executes approved recovery workflows.
          </p>
        </div>

        {/* Security Statement */}
        <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
          <span className="font-mono text-[11px] font-semibold text-slate-700 dark:text-slate-300">
            AI proposes. Humans approve. The platform executes.
          </span>
        </div>
      </div>

      {/* Tech Stack Pills */}
      <div className="pt-4 border-t border-slate-200/60 dark:border-slate-800/60 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-slate-400 font-medium">Built with:</span>
          {['Python 3.11', 'dlt', 'PostgreSQL 16', 'dbt-core', 'Dagster', 'MCP SDK', 'Next.js 16', 'Tailwind CSS'].map(tech => (
            <span key={tech} className="px-2 py-0.5 text-[10px] font-mono rounded-md bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
              {tech}
            </span>
          ))}
        </div>

        {/* Links */}
        <div className="flex items-center gap-4 text-[11px]">
          <a
            href="https://github.com/Anwaribra/DataOps-Agent"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>GitHub Repository</span>
          </a>
        </div>
      </div>
    </footer>
  );
};
