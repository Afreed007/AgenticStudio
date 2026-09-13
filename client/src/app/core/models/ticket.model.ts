export type TicketStatus = 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE' | 'BLOCKED';

export interface Ticket {
  ticket_id: string;
  title: string;
  description: string;
  acceptance_criteria: string[];
  target_files: string[];
  dependencies: string[];
  status: TicketStatus;
  assigned_to: string | null;
  retry_count: number;
  qa_approved: boolean;
  review_approved: boolean;
}
