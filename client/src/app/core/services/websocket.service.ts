import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { WsEvent } from '../models/a2a-message.model';

@Injectable({ providedIn: 'root' })
export class WebsocketService {
  private ws: WebSocket | null = null;
  private eventSubject = new Subject<WsEvent>();

  connect(runId: string): Observable<WsEvent> {
    this.disconnect();

    this.ws = new WebSocket(`ws://localhost:8000/api/ws/runs/${runId}`);

    this.ws.onmessage = (event) => {
      try {
        const parsed: WsEvent = JSON.parse(event.data);
        this.eventSubject.next(parsed);
      } catch (e) {
        console.error('[WS] Failed to parse message:', e);
      }
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Error:', err);
    };

    this.ws.onclose = () => {
      console.log('[WS] Connection closed');
    };

    return this.eventSubject.asObservable();
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
