import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { WelcomeScreen } from './components/WelcomeScreen';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { ArtifactPanel } from './components/ArtifactPanel';
import { api } from './services/api';
import { Session, Message, Artifact, SystemConfig } from './types';
import { AlertCircle, X } from 'lucide-react';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama');
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Initial Data Fetch
  useEffect(() => {
    const bootstrap = async () => {
      try {
        const [cfg, sessList] = await Promise.all([api.getConfig(), api.listSessions()]);
        setConfig(cfg);
        setSessions(sessList);
        setIsBackendConnected(true);
        if (sessList.length > 0) {
          loadSession(sessList[0].id);
        }
      } catch (err: any) {
        console.error('Bootstrap error:', err);
        setIsBackendConnected(false);
        setErrorMessage(err.message || 'Failed to connect to backend.');
      }
    };
    bootstrap();
  }, []);

  // Periodic health check
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        await api.getHealth();
        setIsBackendConnected(true);
      } catch {
        setIsBackendConnected(false);
      }
    }, 15000);
    return () => clearInterval(timer);
  }, []);

  const loadSession = async (id: string) => {
    try {
      setIsLoading(true);
      setActiveSessionId(id);
      const detail = await api.getSession(id);
      setMessages(detail.messages || []);
      setArtifacts(detail.artifacts || []);
      if (detail.artifacts && detail.artifacts.length > 0) {
        setActiveArtifact(detail.artifacts[detail.artifacts.length - 1]);
      } else {
        setActiveArtifact(null);
      }
      setSelectedProvider(detail.provider || 'ollama');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load session.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSess = await api.createSession('New Conversation', selectedProvider);
      setSessions([newSess, ...sessions]);
      setActiveSessionId(newSess.id);
      setMessages([]);
      setArtifacts([]);
      setActiveArtifact(null);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create conversation.');
    }
  };

  const handleDeleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteSession(id);
      const updated = sessions.filter((s) => s.id !== id);
      setSessions(updated);
      if (activeSessionId === id) {
        if (updated.length > 0) {
          loadSession(updated[0].id);
        } else {
          setActiveSessionId(null);
          setMessages([]);
          setArtifacts([]);
          setActiveArtifact(null);
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to delete session.');
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    setErrorMessage(null);

    // Optimistic user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const res = await api.sendMessage({
        message: text,
        sessionId: activeSessionId || undefined,
        provider: selectedProvider,
      });

      // Update active session ID if this was the first message
      if (!activeSessionId) {
        setActiveSessionId(res.sessionId);
        const refreshedList = await api.listSessions();
        setSessions(refreshedList);
      }

      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, res.message]);

      if (res.artifact) {
        setArtifacts((prev) => [...prev, res.artifact!]);
        setActiveArtifact(res.artifact);
      }
    } catch (err: any) {
      console.error('Chat error:', err);
      setErrorMessage(err.message || 'Failed to generate response.');
      // Remove optimistic message on failure
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateEssay = async () => {
    const topic = window.prompt(
      'Enter the product or growth topic for your ~1,250-word Ship 30 for 30 essay:',
      'Founder-led roadmaps vs feature factories'
    );
    if (!topic || !topic.trim()) return;

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await api.generateEssay({
        topic: topic.trim(),
        sessionId: activeSessionId || undefined,
        provider: selectedProvider,
      });

      if (!activeSessionId) {
        setActiveSessionId(res.sessionId);
        const refreshedList = await api.listSessions();
        setSessions(refreshedList);
      }

      setMessages((prev) => [...prev, res.message]);
      setArtifacts((prev) => [...prev, res.artifact]);
      setActiveArtifact(res.artifact);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate essay.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateHtmlArtifact = async () => {
    const prompt = window.prompt(
      'Describe the HTML UI component or experiment dashboard widget to create:',
      'A feature prioritization matrix dashboard comparing user impact vs engineering effort with interactive filters'
    );
    if (!prompt || !prompt.trim()) return;

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await api.generateArtifact({
        prompt: prompt.trim(),
        artifactType: 'html',
        sessionId: activeSessionId || undefined,
        provider: selectedProvider,
      });

      if (!activeSessionId) {
        setActiveSessionId(res.sessionId);
        const refreshedList = await api.listSessions();
        setSessions(refreshedList);
      }

      setMessages((prev) => [...prev, res.message]);
      setArtifacts((prev) => [...prev, res.artifact]);
      setActiveArtifact(res.artifact);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate HTML artifact.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateMarkdownArtifact = async () => {
    const prompt = window.prompt(
      'Describe the Markdown strategy document or PRD to create:',
      'A comprehensive PRD for launching self-serve onboarding in a B2B SaaS product'
    );
    if (!prompt || !prompt.trim()) return;

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await api.generateArtifact({
        prompt: prompt.trim(),
        artifactType: 'markdown',
        sessionId: activeSessionId || undefined,
        provider: selectedProvider,
      });

      if (!activeSessionId) {
        setActiveSessionId(res.sessionId);
        const refreshedList = await api.listSessions();
        setSessions(refreshedList);
      }

      setMessages((prev) => [...prev, res.message]);
      setArtifacts((prev) => [...prev, res.artifact]);
      setActiveArtifact(res.artifact);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate Markdown artifact.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#0B0F19] text-white overflow-hidden font-sans">
      {/* Left Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={loadSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        config={config}
        selectedProvider={selectedProvider}
        onSelectProvider={setSelectedProvider}
        isBackendConnected={isBackendConnected}
      />

      {/* Center Chat Area */}
      <main className="flex-1 flex flex-col h-screen min-w-0 bg-[#0B0F19] relative">
        {/* Error Toast */}
        {errorMessage && (
          <div className="absolute top-4 left-4 right-4 z-50 flex items-center justify-between p-3.5 rounded-xl bg-rose-950/90 border border-rose-700/60 text-rose-200 text-xs shadow-xl backdrop-blur-md">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="p-1 hover:text-white rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Message Feed Canvas */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6">
          {messages.length === 0 ? (
            <WelcomeScreen onSelectPrompt={handleSendMessage} />
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  hasArtifact={artifacts.some((a) => a.message_id === msg.id || artifacts.length > 0)}
                  onOpenArtifact={() => {
                    const matched = artifacts.find((a) => a.message_id === msg.id) || artifacts[artifacts.length - 1];
                    if (matched) setActiveArtifact(matched);
                  }}
                />
              ))}

              {/* Streaming / Loading Indicator */}
              {isLoading && (
                <div className="flex gap-3 py-3 items-center text-xs text-cyan-400 font-medium animate-pulse">
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  <span>Searching transcripts & formulating grounded answer...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Chat Input Bar */}
        <ChatInput
          onSendMessage={handleSendMessage}
          onGenerateEssay={handleGenerateEssay}
          onGenerateHtmlArtifact={handleGenerateHtmlArtifact}
          onGenerateMarkdownArtifact={handleGenerateMarkdownArtifact}
          isLoading={isLoading}
        />
      </main>

      {/* Right Artifact Studio Panel */}
      {activeArtifact && (
        <ArtifactPanel
          artifact={activeArtifact}
          onClose={() => setActiveArtifact(null)}
        />
      )}
    </div>
  );
};

export default App;
