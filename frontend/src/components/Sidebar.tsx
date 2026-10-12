import React from 'react';
import { Plus, MessageSquare, Trash2, Cpu, Database, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { Session, SystemConfig } from '../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  config: SystemConfig | null;
  selectedProvider: string;
  onSelectProvider: (provider: string) => void;
  isBackendConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  config,
  selectedProvider,
  onSelectProvider,
  isBackendConnected,
}) => {
  return (
    <aside className="w-72 bg-[#0F172A] border-r border-[#334155] flex flex-col h-screen select-none shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#334155] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-cyan-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
              THE LENNY ASSISTANT
            </h1>
            <p className="text-[11px] text-cyan-400 font-medium">Product & Growth Intelligence</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-sm transition-all shadow-md shadow-violet-600/20 active:scale-[0.98] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Sessions History List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
        <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Conversations ({sessions.length})
        </div>

        {sessions.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-slate-400">
            No previous chats yet.<br />Start a new conversation above!
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <div
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium cursor-pointer transition-all ${
                  isActive
                    ? 'bg-[#1E293B] text-cyan-300 border border-indigo-500/40 shadow-sm'
                    : 'text-slate-300 hover:bg-[#1E293B]/60 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span className="truncate">{session.title || 'Conversation'}</span>
                </div>
                <button
                  onClick={(e) => onDeleteSession(session.id, e)}
                  title="Delete chat"
                  className="opacity-0 group-hover:opacity-100 hover:text-rose-400 p-1 rounded transition-opacity"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Model Provider & Knowledge Base Telemetry Footer */}
      <div className="p-3 border-t border-[#334155] bg-[#0B0F19]/80 space-y-2.5 text-xs">
        {/* Provider Selector */}
        <div>
          <label className="text-[11px] font-medium text-slate-400 flex items-center gap-1.5 mb-1">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            Model Provider
          </label>
          <select
            value={selectedProvider}
            onChange={(e) => onSelectProvider(e.target.value)}
            className="w-full bg-[#1E293B] border border-[#334155] text-white rounded-lg px-2.5 py-1.5 text-xs focus:outline-none focus:border-cyan-400 cursor-pointer"
          >
            <option value="ollama">Local Ollama (llama3.2:3b)</option>
            <option value="anthropic">Anthropic Claude (Agent SDK)</option>
          </select>
        </div>

        {/* Knowledge Base Status */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-800 text-[11px]">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>Transcripts Index</span>
          </div>
          <span className="font-semibold text-cyan-400">
            {config?.knowledge_status?.indexed_chunks
              ? `${config.knowledge_status.indexed_chunks.toLocaleString()} chunks`
              : 'Indexed'}
          </span>
        </div>

        {/* Backend Connection Indicator */}
        <div className="flex items-center justify-between text-[11px]">
          <span className="text-slate-400">Server Status</span>
          <div className="flex items-center gap-1 font-medium">
            {isBackendConnected ? (
              <>
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span className="text-emerald-400">Connected</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-3 h-3 text-rose-400" />
                <span className="text-rose-400">Offline</span>
              </>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};
