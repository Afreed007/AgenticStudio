import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentState } from '../../../core/services/studio-state.service';

@Component({
  selector: 'app-agent-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="agent-badge" [class.active]="agent.active" [class.pulse-ring]="agent.active">
      <div class="agent-avatar" [style.background]="agent.active ? agent.color : 'transparent'"
           [style.border-color]="agent.color">
        <span class="agent-icon">{{ agent.icon }}</span>
      </div>
      <div class="agent-info">
        <span class="agent-label" [style.color]="agent.active ? agent.color : '#94a3b8'">
          {{ agent.label }}
        </span>
        @if (agent.active && agent.lastAction) {
          <span class="agent-action fade-in">{{ agent.lastAction | slice:0:20 }}</span>
        }
      </div>
    </div>
  `,
  styles: [`
    .agent-badge {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.6rem 0.75rem;
      border-radius: 10px;
      transition: background 0.2s;
      cursor: default;
    }
    .agent-badge.active {
      background: rgba(108, 99, 255, 0.08);
    }
    .agent-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid;
      font-size: 1.1rem;
      transition: background 0.3s, box-shadow 0.3s;
      flex-shrink: 0;
    }
    .agent-badge.active .agent-avatar {
      box-shadow: 0 0 12px var(--glow);
    }
    .agent-label {
      display: block;
      font-weight: 600;
      font-size: 0.8rem;
      transition: color 0.2s;
    }
    .agent-action {
      display: block;
      font-size: 0.65rem;
      color: #64748b;
      margin-top: 1px;
    }
    .agent-info { display: flex; flex-direction: column; }
  `]
})
export class AgentBadgeComponent {
  @Input({ required: true }) agent!: AgentState;
}
