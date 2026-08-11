'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  DEMO_INCIDENT,
  DEMO_MCP_STEPS,
  DEMO_REMEDIATION_ACTIONS,
  DEMO_VERIFICATION_CHECKS,
  INITIAL_PIPELINE_NODES,
  IncidentItem,
  MCPToolStep,
  PipelineNode,
  RemediationActionItem,
  VerificationCheckItem
} from '../data/demoData';
import {
  approvePlanApi,
  executePlanApi,
  fetchPipelineNodes,
  fetchSystemHealth,
  injectScenarioApi,
  investigateIncidentApi,
  resetDemoApi,
  verifyRecoveryApi
} from '../lib/api';

export type SimulationState =
  | 'HEALTHY'
  | 'FAILURE_INJECTED'
  | 'INVESTIGATING'
  | 'DIAGNOSED'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'EXECUTING'
  | 'VERIFYING'
  | 'RESOLVED';

export type SectionId =
  | 'overview'
  | 'pipeline'
  | 'incidents'
  | 'investigation'
  | 'diagnosis'
  | 'remediation'
  | 'verification'
  | 'architecture';

interface DemoContextType {
  simulationState: SimulationState;
  activeSection: SectionId;
  setActiveSection: (sec: SectionId) => void;
  nodes: PipelineNode[];
  activeNode: PipelineNode | null;
  setActiveNodeId: (id: string | null) => void;
  incident: IncidentItem;
  mcpSteps: MCPToolStep[];
  mcpStepsCount: number;
  remediationActions: RemediationActionItem[];
  verificationChecks: VerificationCheckItem[];
  runDemoIncident: () => void;
  approvePlan: () => void;
  rejectPlan: () => void;
  resetDemo: () => void;
  isLiveMode: boolean;
  metrics: {
    systemStatus: 'HEALTHY' | 'DEGRADED' | 'RECOVERED';
    pipelineHealth: number;
    activeIncidentsCount: number;
    failedAssetsCount: number;
    dataQualityScore: number;
    lastRun: string;
  };
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const DemoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [simulationState, setSimulationState] = useState<SimulationState>('HEALTHY');
  const [activeSection, setActiveSection] = useState<SectionId>('overview');
  const [nodes, setNodes] = useState<PipelineNode[]>(INITIAL_PIPELINE_NODES);
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);
  const [incident, setIncident] = useState<IncidentItem>({ ...DEMO_INCIDENT, status: 'RESOLVED' });
  const [mcpStepsCount, setMcpStepsCount] = useState<number>(0);
  const [remediationActions, setRemediationActions] = useState<RemediationActionItem[]>(DEMO_REMEDIATION_ACTIONS);
  const [isLiveMode, setIsLiveMode] = useState<boolean>(false);

  // Check live API connectivity on mount
  useEffect(() => {
    async function checkApi() {
      const health = await fetchSystemHealth();
      if (health) {
        setIsLiveMode(true);
        const remoteNodes = await fetchPipelineNodes();
        if (remoteNodes) setNodes(remoteNodes);
      }
    }
    checkApi();
  }, []);

  const activeNode = nodes.find(n => n.id === activeNodeId) || null;

  // Run Demo Incident Simulation Flow (API or Sandbox)
  const runDemoIncident = async () => {
    setSimulationState('FAILURE_INJECTED');
    setActiveSection('investigation');
    setMcpStepsCount(0);
    setIncident({ ...DEMO_INCIDENT, status: 'DETECTED' });

    // Call live API if connected
    if (isLiveMode) {
      await injectScenarioApi('null_customer_id');
      const remoteNodes = await fetchPipelineNodes();
      if (remoteNodes) setNodes(remoteNodes);
    } else {
      setNodes(prev =>
        prev.map(node => {
          if (node.id === 'dbt_transformation' || node.id === 'dagster_orchestrator') {
            return { ...node, status: 'FAILED' };
          }
          if (node.id === 'health_signals') {
            return { ...node, status: 'WARNING' };
          }
          return node;
        })
      );
    }

    // Step sequence timer
    setTimeout(async () => {
      setSimulationState('INVESTIGATING');
      
      if (isLiveMode) {
        await investigateIncidentApi(incident.id);
      }

      let currentStep = 0;
      const interval = setInterval(() => {
        currentStep += 1;
        setMcpStepsCount(currentStep);
        if (currentStep >= DEMO_MCP_STEPS.length) {
          clearInterval(interval);
          setSimulationState('DIAGNOSED');
          setIncident(prev => ({ ...prev, status: 'DIAGNOSED' }));
        }
      }, 500);
    }, 1000);
  };

  // Human Approval Action
  const approvePlan = async () => {
    setSimulationState('APPROVED');
    setIncident(prev => ({ ...prev, status: 'APPROVED' }));
    
    if (isLiveMode) {
      await approvePlanApi(incident.id, 'HUMAN_OPERATOR');
    }

    // Simulate execution timeline
    setTimeout(async () => {
      setSimulationState('EXECUTING');
      setRemediationActions(prev => prev.map(a => ({ ...a, status: 'EXECUTING' })));

      if (isLiveMode) {
        await executePlanApi(incident.id);
      }

      setTimeout(async () => {
        setSimulationState('VERIFYING');
        setRemediationActions(prev => prev.map(a => ({ ...a, status: 'SUCCESS' })));

        if (isLiveMode) {
          await verifyRecoveryApi(incident.id);
        }

        setTimeout(() => {
          setSimulationState('RESOLVED');
          setIncident(prev => ({ ...prev, status: 'RESOLVED' }));
          setNodes(INITIAL_PIPELINE_NODES.map(n => ({ ...n, status: 'HEALTHY' })));
        }, 1200);
      }, 1200);
    }, 800);
  };

  const rejectPlan = () => {
    setSimulationState('DIAGNOSED');
    setIncident(prev => ({ ...prev, status: 'DIAGNOSED' }));
  };

  const resetDemo = async () => {
    setSimulationState('HEALTHY');
    setActiveSection('overview');
    setNodes(INITIAL_PIPELINE_NODES);
    setMcpStepsCount(6);
    setIncident({ ...DEMO_INCIDENT, status: 'RESOLVED' });
    setRemediationActions(DEMO_REMEDIATION_ACTIONS.map(a => ({ ...a, status: 'PENDING' })));

    if (isLiveMode) {
      await resetDemoApi();
    }
  };

  const isHealthy = simulationState === 'HEALTHY' || simulationState === 'RESOLVED';
  const metrics = {
    systemStatus: isHealthy ? ('HEALTHY' as const) : ('DEGRADED' as const),
    pipelineHealth: isHealthy ? 100 : 87,
    activeIncidentsCount: isHealthy ? 0 : 1,
    failedAssetsCount: isHealthy ? 0 : 2,
    dataQualityScore: isHealthy ? 99.8 : 91.6,
    lastRun: isHealthy ? '2 mins ago' : 'Just now (Halted on test error)'
  };

  return (
    <DemoContext.Provider
      value={{
        simulationState,
        activeSection,
        setActiveSection,
        nodes,
        activeNode,
        setActiveNodeId,
        incident,
        mcpSteps: DEMO_MCP_STEPS,
        mcpStepsCount,
        remediationActions,
        verificationChecks: DEMO_VERIFICATION_CHECKS,
        runDemoIncident,
        approvePlan,
        rejectPlan,
        resetDemo,
        isLiveMode,
        metrics
      }}
    >
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = () => {
  const ctx = useContext(DemoContext);
  if (!ctx) throw new Error('useDemo must be used within DemoProvider');
  return ctx;
};
