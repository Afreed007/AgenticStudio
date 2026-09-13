/** A2A Message from the Agentic Studio Python backend */
export type ActionType =
  | 'SCOPING_REQUEST'
  | 'PRD_GENERATED'
  | 'ARCH_SPEC_GENERATED'
  | 'TASK_ASSIGNMENT'
  | 'TASK_SUBMISSION'
  | 'BUG_REPORT'
  | 'CODE_REVIEW_REJECTED'
  | 'CODE_REVIEW_APPROVED'
  | 'TASK_APPROVED'
  | 'DELIVERY_COMPLETE'
  | 'ESCALATE';

export interface A2aMessage {
  message_id: string;
  timestamp: number;
  sender: string;
  recipient: string;
  action: ActionType;
  ticket_id: string | null;
  payload: Record<string, any>;
}

export type WsEvent =
  | { type: 'a2a_message'; data: A2aMessage }
  | { type: 'run_status'; data: RunSession };

export interface RunSession {
  run_id: string;
  prompt: string;
  workspace: string;
  mock_mode: boolean;
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'ESCALATED' | 'FAILED';
  created_at: number;
  finished_at: number | null;
  messages: A2aMessage[];
  files: string[];
  tickets_stats: Record<string, number>;
  summary: Record<string, any> | null;
  error: string | null;
}
