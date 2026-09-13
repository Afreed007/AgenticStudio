import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RunSession } from '../models/a2a-message.model';

export interface StartRunRequest {
  prompt: string;
  workspace?: string;
  mock_mode: boolean;
}

export interface FileContentResponse {
  path: string;
  content: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';
  private http = inject(HttpClient);

  startRun(req: StartRunRequest): Observable<RunSession> {
    return this.http.post<RunSession>(`${this.baseUrl}/runs`, req);
  }

  listRuns(): Observable<RunSession[]> {
    return this.http.get<RunSession[]>(`${this.baseUrl}/runs`);
  }

  getRun(runId: string): Observable<RunSession> {
    return this.http.get<RunSession>(`${this.baseUrl}/runs/${runId}`);
  }

  getRunFiles(runId: string): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}/runs/${runId}/files`);
  }

  getFileContent(runId: string, path: string): Observable<FileContentResponse> {
    return this.http.get<FileContentResponse>(
      `${this.baseUrl}/runs/${runId}/files/content`,
      { params: { path } }
    );
  }
}
