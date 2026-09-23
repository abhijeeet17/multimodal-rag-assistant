import React, { useState, useRef, useEffect } from 'react';
import { Send, ThumbsUp, ThumbsDown, Bot, User, BookOpen, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import { Citation } from '../types';

export interface MessageItem {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: Citation[];
  retrieved_chunks?: any[];
  feedback?: boolean | null;
}

interface ChatInterfaceProps {
  messages: MessageItem[];
  onSendMessage: (question: string) => Promise<void>;
  onFeedback: (messageId: string, isHelpful: boolean, question: string, answer: string, chunks?: any[]) => Promise<void>;
  loading: boolean;
  hasDocuments: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onFeedback,
  loading,
  hasDocuments,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sampleQuestions = [
    "What was the revenue in 2025?",
    "What skills are mentioned in the resume?",
    "What is the total invoice amount?",
    "Compare revenue between 2024 and 2025.",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleSampleClick = (q: string) => {
    if (!loading) {
      onSendMessage(q);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950">
      {/* Messages Window */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto py-12">
            <div className="bg-indigo-950/60 border border-indigo-800/40 p-4 rounded-2xl text-indigo-400 mb-4 shadow-xl">
              <Sparkles className="h-10 w-10" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Multimodal RAG Document Assistant</h2>
            <p className="text-sm text-slate-400 mb-8 leading-relaxed">
              Upload documents (PDFs, scanned reports, invoices, resumes, or images) to ask questions.
              Answers are strictly grounded in retrieved vector search chunks with source citations.
            </p>

            <div className="w-full space-y-2">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Example Questions</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSampleClick(q)}
                    disabled={!hasDocuments || loading}
                    className="p-3 text-xs bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-indigo-950/20 text-slate-300 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-4 max-w-4xl mx-auto ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'assistant' && (
                <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md shadow-indigo-600/30">
                  <Bot className="h-5 w-5" />
                </div>
              )}

              <div
                className={`rounded-2xl p-4 text-sm max-w-2xl leading-relaxed shadow-lg ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* Citations section for Assistant response */}
                {msg.sender === 'assistant' && msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800 text-xs">
                    <div className="flex items-center gap-1.5 font-semibold text-indigo-400 mb-2">
                      <BookOpen className="h-3.5 w-3.5" />
                      <span>Sources & Citations</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cit, idx) => (
                        <div
                          key={idx}
                          className="bg-slate-950 border border-slate-700/60 px-2.5 py-1 rounded-lg text-[11px] text-slate-300 flex items-center gap-1.5"
                        >
                          <span className="font-medium text-slate-100">{cit.document}</span>
                          <span className="text-indigo-400 font-semibold">• Page {cit.page}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Feedback rating buttons */}
                {msg.sender === 'assistant' && (
                  <div className="mt-3 pt-2 flex items-center justify-between text-xs text-slate-500 border-t border-slate-800/50">
                    <span className="text-[11px]">Was this answer helpful?</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onFeedback(msg.id, true, "", msg.text, msg.retrieved_chunks)}
                        className={`p-1.5 rounded hover:bg-slate-800 transition-colors ${
                          msg.feedback === true ? 'text-emerald-400 bg-emerald-950/60' : 'hover:text-emerald-400'
                        }`}
                        title="Helpful"
                      >
                        <ThumbsUp className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => onFeedback(msg.id, false, "", msg.text, msg.retrieved_chunks)}
                        className={`p-1.5 rounded hover:bg-slate-800 transition-colors ${
                          msg.feedback === false ? 'text-rose-400 bg-rose-950/60' : 'hover:text-rose-400'
                        }`}
                        title="Not Helpful"
                      >
                        <ThumbsDown className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {msg.sender === 'user' && (
                <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                  <User className="h-5 w-5" />
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="flex gap-4 max-w-4xl mx-auto items-center text-slate-400 text-xs py-2">
            <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white shrink-0">
              <Bot className="h-5 w-5" />
            </div>
            <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-4 py-3 rounded-2xl">
              <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />
              <span>Retrieving relevant chunks & generating answer...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/40">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              hasDocuments
                ? "Ask a question about your uploaded documents..."
                : "Upload a document on the left to start asking questions..."
            }
            disabled={!hasDocuments || loading}
            className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-3.5 pl-4 pr-12 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || !hasDocuments || loading}
            className="absolute right-2 p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all disabled:opacity-40 disabled:hover:bg-indigo-600"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
