import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DocumentDrawer } from './components/DocumentDrawer';
import { ChatInterface, MessageItem } from './components/ChatInterface';
import { DashboardStats } from './components/DashboardStats';
import { checkHealth, fetchDocuments, uploadDocument, deleteDocument, queryRAG, submitFeedback } from './services/api';
import { Document, HealthResponse } from './types';

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  const loadData = async () => {
    try {
      const healthData = await checkHealth();
      setHealth(healthData);

      const docsData = await fetchDocuments();
      setDocuments(docsData.documents);
    } catch (e) {
      // Background retry
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadDocument(file);
      await loadData();
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    await deleteDocument(id);
    setSelectedDocIds(prev => prev.filter(d => d !== id));
    await loadData();
  };

  const handleToggleDocSelect = (id: string) => {
    setSelectedDocIds(prev =>
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const handleSendMessage = async (question: string) => {
    const userMsg: MessageItem = {
      id: Date.now().toString(),
      sender: 'user',
      text: question,
    };

    setMessages(prev => [...prev, userMsg]);
    setQuerying(true);

    try {
      const res = await queryRAG({
        question,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
        session_id: sessionId,
      });

      if (res.session_id) {
        setSessionId(res.session_id);
      }

      const assistantMsg: MessageItem = {
        id: res.message_id || (Date.now() + 1).toString(),
        sender: 'assistant',
        text: res.answer,
        citations: res.citations,
        retrieved_chunks: res.retrieved_chunks,
        feedback: null,
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: MessageItem = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: 'Sorry, an error occurred while processing your request. Please try again.',
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setQuerying(false);
    }
  };

  const handleFeedback = async (
    messageId: string,
    isHelpful: boolean,
    question: string,
    answer: string,
    chunks?: any[]
  ) => {
    try {
      await submitFeedback({
        message_id: messageId,
        question,
        answer,
        retrieved_chunks: chunks,
        is_helpful: isHelpful,
      });

      setMessages(prev =>
        prev.map(msg => (msg.id === messageId ? { ...msg, feedback: isHelpful } : msg))
      );
    } catch (e) {
      // Ignore
    }
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden font-sans">
      <Navbar health={health} />
      <DashboardStats />

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        <DocumentDrawer
          documents={documents}
          onUpload={handleUpload}
          onDelete={handleDelete}
          selectedDocIds={selectedDocIds}
          onToggleDocSelect={handleToggleDocSelect}
          uploading={uploading}
        />

        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          onFeedback={handleFeedback}
          loading={querying}
          hasDocuments={documents.length > 0}
        />
      </div>
    </div>
  );
}
