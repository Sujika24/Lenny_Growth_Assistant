import { Session, SessionDetail, Message, Artifact, SystemConfig, KnowledgeStatus } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    try {
      const res = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(options?.headers || {}),
        },
      });

      if (!res.ok) {
        let errMessage = `Error ${res.status}: ${res.statusText}`;
        try {
          const data = await res.json();
          if (data.detail) errMessage = data.detail;
        } catch {
          // ignore json parse error
        }
        throw new Error(errMessage);
      }

      if (res.status === 204) {
        return null as unknown as T;
      }

      return await res.json();
    } catch (err: any) {
      if (err.message?.includes('Failed to fetch')) {
        throw new Error(`Cannot reach backend at ${API_BASE || 'http://127.0.0.1:8000'}. Make sure the FastAPI backend is running.`);
      }
      throw err;
    }
  }

  // Config & Health
  async getConfig(): Promise<SystemConfig> {
    return this.request<SystemConfig>('/api/v1/config');
  }

  async getHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  async getKnowledgeStatus(): Promise<KnowledgeStatus> {
    return this.request<KnowledgeStatus>('/api/v1/knowledge/status');
  }

  // Sessions
  async listSessions(): Promise<Session[]> {
    return this.request<Session[]>('/api/v1/sessions');
  }

  async getSession(id: string): Promise<SessionDetail> {
    return this.request<SessionDetail>(`/api/v1/sessions/${id}`);
  }

  async createSession(title?: string, provider = 'ollama', model_name = 'llama3.2:3b'): Promise<Session> {
    return this.request<Session>('/api/v1/sessions', {
      method: 'POST',
      body: JSON.stringify({ title: title || 'New Conversation', provider, model_name }),
    });
  }

  async deleteSession(id: string): Promise<void> {
    return this.request<void>(`/api/v1/sessions/${id}`, { method: 'DELETE' });
  }

  // Chat & Generation
  async sendMessage(params: {
    message: string;
    sessionId?: string;
    provider?: string;
    modelName?: string;
  }): Promise<{ sessionId: string; message: Message; artifact?: Artifact | null }> {
    const res = await this.request<{ session_id: string; message: Message; artifact?: Artifact | null }>(
      '/api/v1/chat',
      {
        method: 'POST',
        body: JSON.stringify({
          message: params.message,
          session_id: params.sessionId,
          provider: params.provider,
          model_name: params.modelName,
        }),
      }
    );
    return {
      sessionId: res.session_id,
      message: res.message,
      artifact: res.artifact,
    };
  }

  async generateEssay(params: {
    topic: string;
    sessionId?: string;
    provider?: string;
    modelName?: string;
  }): Promise<{ sessionId: string; message: Message; artifact: Artifact }> {
    const res = await this.request<{ session_id: string; message: Message; artifact: Artifact }>(
      '/api/v1/essays',
      {
        method: 'POST',
        body: JSON.stringify({
          topic: params.topic,
          session_id: params.sessionId,
          provider: params.provider,
          model_name: params.modelName,
        }),
      }
    );
    return {
      sessionId: res.session_id,
      message: res.message,
      artifact: res.artifact,
    };
  }

  async generateArtifact(params: {
    prompt: string;
    title?: string;
    artifactType: 'markdown' | 'html';
    sessionId?: string;
    provider?: string;
    modelName?: string;
  }): Promise<{ sessionId: string; message: Message; artifact: Artifact }> {
    const res = await this.request<{ session_id: string; message: Message; artifact: Artifact }>(
      '/api/v1/artifacts',
      {
        method: 'POST',
        body: JSON.stringify({
          prompt: params.prompt,
          title: params.title,
          artifact_type: params.artifactType,
          session_id: params.sessionId,
          provider: params.provider,
          model_name: params.modelName,
        }),
      }
    );
    return {
      sessionId: res.session_id,
      message: res.message,
      artifact: res.artifact,
    };
  }

  async getArtifact(id: string): Promise<Artifact> {
    return this.request<Artifact>(`/api/v1/artifacts/${id}`);
  }
}

export const api = new ApiService();
