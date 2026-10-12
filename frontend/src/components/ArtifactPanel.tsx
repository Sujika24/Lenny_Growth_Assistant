import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Eye, Code, Copy, Check, Download, X, ShieldAlert, Sparkles } from 'lucide-react';
import { Artifact } from '../types';

interface ArtifactPanelProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactPanel: React.FC<ArtifactPanelProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const isHtml = artifact.artifact_type.toLowerCase() === 'html';

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = isHtml ? 'html' : 'md';
    const mime = isHtml ? 'text/html' : 'text/markdown';
    const blob = new Blob([artifact.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Secure sandboxed HTML with strict CSP
  const renderSecureHtml = () => {
    const csp = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:;">`;
    const safeContent = `
      <!DOCTYPE html>
      <html>
        <head>
          ${csp}
          <meta charset="utf-8">
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 16px; color: #F1F5F9; background: #0B0F19; }
          </style>
        </head>
        <body>
          ${artifact.content}
        </body>
      </html>
    `;
    return safeContent;
  };

  return (
    <div className="w-full lg:w-[500px] xl:w-[600px] bg-[#0F172A] border-l border-[#334155] flex flex-col h-screen shrink-0 shadow-2xl z-20">
      {/* Header */}
      <div className="p-3.5 border-b border-[#334155] flex items-center justify-between bg-[#111827]">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shrink-0">
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="min-w-0">
            <h3 className="text-xs font-bold text-white truncate max-w-[220px] sm:max-w-[300px]">
              {artifact.title}
            </h3>
            <span className="text-[10px] text-cyan-400 uppercase font-semibold tracking-wider">
              {artifact.artifact_type} Artifact
            </span>
          </div>
        </div>

        {/* Tab Controls & Actions */}
        <div className="flex items-center gap-1.5 shrink-0">
          <div className="flex bg-[#1E293B] rounded-lg p-0.5 border border-[#334155]">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                activeTab === 'preview'
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                activeTab === 'code'
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Code className="w-3 h-3" />
              <span>Code</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            title="Copy to clipboard"
            className="p-1.5 rounded-lg bg-[#1E293B] hover:bg-[#334155] text-slate-300 hover:text-white border border-[#334155] transition-colors cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={handleDownload}
            title={`Download .${isHtml ? 'html' : 'md'}`}
            className="p-1.5 rounded-lg bg-[#1E293B] hover:bg-[#334155] text-slate-300 hover:text-white border border-[#334155] transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onClose}
            title="Close panel"
            className="p-1.5 rounded-lg bg-[#1E293B] hover:bg-rose-950 text-slate-400 hover:text-rose-400 border border-[#334155] transition-colors cursor-pointer ml-1"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Security Banner for HTML */}
      {isHtml && activeTab === 'preview' && (
        <div className="px-3 py-1.5 bg-indigo-950/40 border-b border-indigo-900/40 flex items-center gap-1.5 text-[10px] text-indigo-300">
          <ShieldAlert className="w-3 h-3 text-cyan-400 shrink-0" />
          <span>Rendered inside an isolated sandbox iframe with zero parent DOM or cookie access.</span>
        </div>
      )}

      {/* Content Area */}
      <div className="flex-1 overflow-auto bg-[#0B0F19] p-4">
        {activeTab === 'preview' ? (
          isHtml ? (
            <iframe
              title="Artifact Preview"
              srcDoc={renderSecureHtml()}
              sandbox="allow-popups"
              className="w-full h-full min-h-[480px] rounded-xl border border-[#334155] bg-[#090D16]"
            />
          ) : (
            <div className="prose prose-invert max-w-none text-xs sm:text-sm text-slate-200 leading-relaxed font-sans prose-headings:text-cyan-300 prose-headings:font-bold prose-a:text-cyan-400 prose-code:text-violet-300 prose-code:bg-slate-900 prose-code:px-1 prose-pre:bg-slate-900">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
            </div>
          )
        ) : (
          <pre className="text-xs font-mono text-cyan-300 bg-[#090D16] p-4 rounded-xl border border-[#334155] overflow-x-auto whitespace-pre-wrap leading-relaxed select-text">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
};
