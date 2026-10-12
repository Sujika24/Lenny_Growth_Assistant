export interface Citation {
  guest: string;
  title: string;
  episode_url?: string;
  publish_date?: string;
  chunk_id?: string;
  snippet: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Artifact {
  id: string;
  session_id: string;
  message_id?: string | null;
  title: string;
  artifact_type: 'markdown' | 'html';
  content: string;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  provider: string;
  model_name: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail extends Session {
  messages: Message[];
  artifacts: Artifact[];
}

export interface ProviderInfo {
  id: string;
  name: string;
  is_available: boolean;
  models: string[];
  default_model: string;
  description: string;
}

export interface KnowledgeStatus {
  indexed_chunks: number;
  total_episodes: number;
  is_ready: boolean;
  persist_dir: string;
}

export interface SystemConfig {
  active_provider: string;
  providers: ProviderInfo[];
  knowledge_status: KnowledgeStatus;
}
