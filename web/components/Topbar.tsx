'use client';

import React from 'react';
import { Play, RotateCcw, Sun, Moon, ShieldCheck, Activity, Radio } from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { useTheme } from '../context/ThemeContext';

export const Topbar: React.FC = () => {
  const { simulationState, runDemoIncident, resetDemo, metrics, isLiveMode } = useDemo();
  const { theme, toggleTheme } = useTheme();

  const isSimulating = simulationState !== 'HEALTHY' && simulationState !== 'RESOLVED';

  return (
    <header className="h-16 shrink-0 bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30 backdrop-blur-md transition-colors duration-200">
      {/* Title & Tagline */}
      <div className="flex items-center gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="font-bold text-slate-900 dark:text-slate-100 text-sm tracking-tight">
              DataOps Control Center
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-mono font-medium rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              v1.0.0-MCP
            </span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden md:block">
            Intelligent Incident Detection, Diagnosis & Recovery • Observe → Investigate → Diagnose → Approve → Remediate → Verify
          </p>
        </div>
      </div>

      {/* Controller & Action Buttons */}
      <div className="flex items-center gap-3">
        {/* System Status Pill */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs">
          <Activity className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-slate-500 dark:text-slate-400">Status:</span>
          <span
            className={`font-semibold ${
              metrics.systemStatus === 'HEALTHY'
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-rose-600 dark:text-rose-400'
            }`}
          >
            {metrics.systemStatus}
          </span>
        </div>

        {/* Live vs Sandbox Indicator Badge */}
        <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-600 dark:text-slate-300">
          <span className={`w-2 h-2 rounded-full ${isLiveMode ? 'bg-sky-500 animate-pulse' : 'bg-emerald-500'}`} />
          <span className="text-[11px] font-semibold">
            {isLiveMode ? '● LIVE PROJECT' : '● DEMO / SANDBOX'}
          </span>
        </div>

        {/* Theme Switcher Button */}
        <button
          onClick={toggleTheme}
          title="Toggle Light / Dark Mode"
          className="p-2 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
        </button>

        {/* Run Demo Button */}
        <button
          onClick={runDemoIncident}
          disabled={isSimulating}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold shadow-sm transition-all duration-150 ${
            isSimulating
              ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed border border-slate-300 dark:border-slate-700'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white border border-emerald-500 shadow-emerald-500/10'
          }`}
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isSimulating ? 'SIMULATING INCIDENT...' : 'RUN DEMO INCIDENT'}</span>
        </button>

        {/* Reset Demo Button */}
        <button
          onClick={resetDemo}
          title="Reset pipeline to healthy"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 text-xs font-medium transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">RESET</span>
        </button>
      </div>
    </header>
  );
};
