'use client';

import React from 'react';
import { X, CheckCircle2, AlertTriangle, XCircle, Info, Database } from 'lucide-react';
import { PipelineNode } from '../data/demoData';

interface NodeDetailDrawerProps {
  node: PipelineNode;
  onClose: () => void;
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({ node, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 shadow-xl space-y-5 text-slate-900 dark:text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-700 dark:text-slate-200">
              <Database className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h3 className="font-bold text-base">{node.name}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">{node.category} Stage</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Description */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Description</h4>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{node.description}</p>
        </div>

        {/* Metadata Grid */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Operational Metadata</h4>
          <div className="grid grid-cols-2 gap-2.5">
            {Object.entries(node.metadata).map(([key, val]) => (
              <div key={key} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-xs">
                <span className="text-[11px] text-slate-400 block mb-0.5">{key}</span>
                <span className="font-mono font-medium text-slate-800 dark:text-slate-200">{val}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Action Close */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            Close Metadata
          </button>
        </div>
      </div>
    </div>
  );
};
