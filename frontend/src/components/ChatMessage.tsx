import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ExternalLink, ChevronDown, ChevronUp, FileCode, Bot, User, Bookmark } from 'lucide-react';
import { Message, Citation } from '../types';

interface ChatMessageProps {
  message: Message;
  onOpenArtifact?: () => void;
  hasArtifact?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onOpenArtifact,
  hasArtifact,
}) => {
  const isUser = message.role === 'user';
  const [expandedCitationIdx, setExpandedCitationIdx] = useState<number | null>(null);

  const toggleCitation = (idx: number) => {
    setExpandedCitationIdx(expandedCitationIdx === idx ? null : idx);
  };

  return (
    <div className={`flex gap-3 py-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Bot Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center shrink-0 shadow-md shadow-violet-600/10">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      {/* Message Bubble Container */}
      <div className={`max-w-[85%] sm:max-w-[78%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3.5 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-gradient-to-r from-violet-700 to-indigo-700 text-white shadow-md shadow-indigo-600/10 rounded-tr-sm'
              : 'bg-[#1E293B] border border-[#334155] text-slate-100 shadow-sm rounded-tl-sm'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert max-w-none prose-p:my-2 prose-headings:text-cyan-300 prose-headings:font-bold prose-headings:my-3 prose-a:text-cyan-400 prose-code:text-violet-300 prose-code:bg-slate-900 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-800 text-xs sm:text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* View Attached Artifact Button */}
        {!isUser && hasArtifact && onOpenArtifact && (
          <button
            onClick={onOpenArtifact}
            className="mt-2.5 inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-violet-950/80 hover:bg-violet-900 border border-violet-600/40 text-violet-200 text-xs font-medium transition-all shadow-sm cursor-pointer"
          >
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span>Open Generated Artifact in Side Panel</span>
          </button>
        )}

        {/* Citations & Evidence Container */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-3 w-full space-y-1.5">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400">
              <Bookmark className="w-3 h-3 text-cyan-400" />
              <span>Transcript Citations ({message.citations.length})</span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {message.citations.map((citation: Citation, idx: number) => {
                const isExpanded = expandedCitationIdx === idx;
                return (
                  <div key={idx} className="w-full">
                    <div
                      onClick={() => toggleCitation(idx)}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#0F172A] hover:bg-[#1E293B] border border-cyan-800/40 text-[11px] text-cyan-300 font-medium cursor-pointer transition-colors max-w-full truncate"
                    >
                      <span className="font-semibold text-white">{citation.guest}</span>
                      <span className="text-slate-500">|</span>
                      <span className="truncate max-w-[220px] text-slate-300">{citation.title}</span>
                      {citation.episode_url && (
                        <a
                          href={citation.episode_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          title="Open episode on YouTube"
                          className="hover:text-cyan-400 ml-1"
                        >
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="w-3 h-3 text-slate-400 ml-0.5" />
                      ) : (
                        <ChevronDown className="w-3 h-3 text-slate-400 ml-0.5" />
                      )}
                    </div>

                    {/* Expandable Transcript Evidence Drawer */}
                    {isExpanded && (
                      <div className="mt-1.5 p-3 rounded-xl bg-[#090D16] border border-cyan-900/40 text-[11px] text-slate-300 leading-relaxed font-mono">
                        <div className="text-[10px] text-cyan-400 uppercase font-semibold mb-1">
                          Verbatim Transcript Snippet:
                        </div>
                        <p className="italic text-slate-300">&ldquo;{citation.snippet}&rdquo;</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-violet-900 border border-violet-600/40 flex items-center justify-center shrink-0">
          <User className="w-4 h-4 text-violet-200" />
        </div>
      )}
    </div>
  );
};
