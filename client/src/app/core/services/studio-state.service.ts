import { Injectable, signal, computed } from '@angular/core';
import { A2aMessage, RunSession } from '../models/a2a-message.model';

export interface AgentState {
  name: string;
  label: string;
  color: string;
  icon: string;
  active: boolean;
  lastAction: string | null;
}

const AGENT_DEFS: Omit<AgentState, 'active' | 'lastAction'>[] = [
  { name: 'BusinessAnalyst',    label: 'Business Analyst',   color: '#06b6d4', icon: '📋' },
  { name: 'SolutionsArchitect', label: 'Architect',          color: '#3b82f6', icon: '📐' },
  { name: 'ProjectManager',     label: 'Project Manager',    color: '#f59e0b', icon: '📌' },
  { name: 'DeveloperAgent',     label: 'Developer',          color: '#22c55e', icon: '💻' },
  { name: 'QAEngineer',         label: 'QA Engineer',        color: '#a855f7', icon: '🔬' },
  { name: 'CodeReviewer',       label: 'Code Reviewer',      color: '#ef4444', icon: '🛡️' },
  { name: 'DevOpsEngineer',     label: 'DevOps',             color: '#10b981', icon: '🚀' },
];

@Injectable({ providedIn: 'root' })
export class StudioStateService {
  // Signals - reactive state
  readonly activeRun = signal<RunSession | null>(null);
  readonly messages = signal<A2aMessage[]>([]);
  readonly agents = signal<AgentState[]>(
    AGENT_DEFS.map(d => ({ ...d, active: false, lastAction: null }))
  );
  readonly runStatus = signal<string>('IDLE');
  readonly selectedFile = signal<string | null>(null);
  readonly fileContent = signal<string | null>(null);

  // Computed values
  readonly isRunning = computed(() => this.runStatus() === 'RUNNING');
  readonly isDone = computed(() =>
    ['SUCCESS', 'ESCALATED', 'FAILED'].includes(this.runStatus())
  );
  readonly totalMessages = computed(() => this.messages().length);
  readonly ticketStats = computed(() => this.activeRun()?.tickets_stats ?? {});

  setRun(run: RunSession): void {
    this.activeRun.set(run);
    this.runStatus.set(run.status);
    this.messages.set(run.messages ?? []);
  }

  appendMessage(msg: A2aMessage): void {
    this.messages.update(msgs => [...msgs, msg]);
    this.setAgentActive(msg.sender, msg.action);
  }

  updateRunStatus(run: RunSession): void {
    this.activeRun.set(run);
    this.runStatus.set(run.status);
    this.messages.set(run.messages ?? []);
    // Deactivate all agents when done
    this.agents.update(agents =>
      agents.map(a => ({ ...a, active: false }))
    );
  }

  private setAgentActive(sender: string, action: string): void {
    this.agents.update(agents =>
      agents.map(a => ({
        ...a,
        active: a.name === sender,
        lastAction: a.name === sender ? action : a.lastAction
      }))
    );
    // Auto-clear active state after 1.5s
    setTimeout(() => {
      this.agents.update(agents =>
        agents.map(a => a.name === sender ? { ...a, active: false } : a)
      );
    }, 1500);
  }

  reset(): void {
    this.activeRun.set(null);
    this.messages.set([]);
    this.runStatus.set('IDLE');
    this.selectedFile.set(null);
    this.fileContent.set(null);
    this.agents.update(a => a.map(agent => ({ ...agent, active: false, lastAction: null })));
  }
}
