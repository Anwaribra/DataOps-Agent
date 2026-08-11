'use client';

import React from 'react';
import {
  ArrowRight,
  Database,
  GitCommit,
  Layers,
  Activity,
  Server,
  BrainCircuit,
  FileJson,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Info
} from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { NodeDetailDrawer } from './NodeDetailDrawer';

export const PipelineHealthSection: React.FC = () => {
  const { nodes, activeNode, setActiveNodeId } = useDemo();

  const getNodeIcon = (id: string) => {
    switch (id) {
      case 'data_sources': return FileJson;
      case 'dlt_ingestion': return GitCommit;
      case 'postgres_raw': return Database;
      case 'dbt_transformation': return Layers;
      case 'dagster_orchestrator': return Activity;
      case 'health_signals': return AlertTriangle;
      case 'mcp_server': return Server;
      case 'dataops_agent': return BrainCircuit;
      default: return Database;
    }
  };

  const getStatusBadge = (status: 'HEALTHY' | 'WARNING' | 'FAILED') => {
    switch (status) {
      case 'HEALTHY':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-medium rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
            HEALTHY
          </span>
        );
      case 'WARNING':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-medium rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3 text-amber-500" />
            WARNING
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-medium rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3 text-rose-500" />
            FAILED
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Pipeline Health & Dependency Graph
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            End-to-end data platform stage topology from raw source extraction to AI Agent MCP interface. Click any node to inspect detailed operational metadata.
          </p>
        </div>
      </div>

      {/* Visual Pipeline Graph Nodes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {nodes.map((node, idx) => {
          const Icon = getNodeIcon(node.id);
          const isSelected = activeNode?.id === node.id;

          return (
            <div
              key={node.id}
              onClick={() => setActiveNodeId(node.id)}
              className={`p-5 rounded-2xl bg-white dark:bg-slate-900/90 border cursor-pointer transition-all duration-150 relative ${
                isSelected
                  ? 'border-emerald-500 ring-2 ring-emerald-500/20 shadow-md'
                  : node.status === 'FAILED'
                  ? 'border-rose-500/50 hover:border-rose-500 shadow-sm'
                  : node.status === 'WARNING'
                  ? 'border-amber-500/50 hover:border-amber-500 shadow-sm'
                  : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 shadow-sm'
              }`}
            >
              {/* Top Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="w-9 h-9 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-700 dark:text-slate-300">
                  <Icon className="w-4 h-4" />
                </div>
                {getStatusBadge(node.status)}
              </div>

              {/* Node Title & Description */}
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm mb-1">
                {node.name}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mb-4 leading-normal">
                {node.description}
              </p>

              {/* Tech Badge */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
                <span className="px-2 py-0.5 text-[10px] font-mono rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200/80 dark:border-slate-700/80">
                  {node.tech}
                </span>
                <span className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                  Inspect <Info className="w-3 h-3" />
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Node Details Drawer Component */}
      {activeNode && <NodeDetailDrawer node={activeNode} onClose={() => setActiveNodeId(null)} />}
    </div>
  );
};
