import React, { useState, useRef, useEffect } from 'react';
import { Send, Feather, Code2, FileText, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onGenerateEssay: () => void;
  onGenerateHtmlArtifact: () => void;
  onGenerateMarkdownArtifact: () => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onGenerateEssay,
  onGenerateHtmlArtifact,
  onGenerateMarkdownArtifact,
  isLoading,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-3 sm:p-4 bg-[#0F172A]/90 border-t border-[#334155] backdrop-blur-md">
      {/* Quick Action Skill Triggers */}
      <div className="flex items-center gap-2 mb-2.5 overflow-x-auto pb-1 text-xs">
        <span className="text-[11px] font-semibold text-slate-400 shrink-0">Quick Skills:</span>
        <button
          onClick={onGenerateEssay}
          disabled={isLoading}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-violet-950/60 hover:bg-violet-900 border border-violet-700/50 text-violet-300 hover:text-white transition-all text-[11px] font-medium whitespace-nowrap cursor-pointer disabled:opacity-50"
        >
          <Feather className="w-3 h-3 text-cyan-400" />
          <span>Ship 30 for 30 Essay (~1,250w)</span>
        </button>
        <button
          onClick={onGenerateHtmlArtifact}
          disabled={isLoading}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-950/60 hover:bg-indigo-900 border border-indigo-700/50 text-indigo-300 hover:text-white transition-all text-[11px] font-medium whitespace-nowrap cursor-pointer disabled:opacity-50"
        >
          <Code2 className="w-3 h-3 text-cyan-400" />
          <span>HTML UI / Experiment Card</span>
        </button>
        <button
          onClick={onGenerateMarkdownArtifact}
          disabled={isLoading}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 hover:text-white transition-all text-[11px] font-medium whitespace-nowrap cursor-pointer disabled:opacity-50"
        >
          <FileText className="w-3 h-3 text-violet-400" />
          <span>Product PRD / Strategy Doc</span>
        </button>
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a product or growth question grounded in Lenny's podcast..."
          rows={1}
          disabled={isLoading}
          className="flex-1 bg-[#1E293B] border border-[#334155] focus:border-cyan-400 text-white rounded-2xl px-4 py-3 text-sm resize-none focus:outline-none transition-all placeholder:text-slate-400 leading-relaxed max-h-44 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="w-11 h-11 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white flex items-center justify-center shrink-0 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md shadow-violet-600/20 active:scale-95 cursor-pointer"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-4 h-4 ml-0.5" />
          )}
        </button>
      </form>
    </div>
  );
};
