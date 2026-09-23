import React, { useEffect, useState } from 'react';
import { FileText, CheckCircle2, AlertCircle, HelpCircle, ThumbsUp, ThumbsDown, BarChart2 } from 'lucide-react';
import apiClient from '../services/api';

interface StatsData {
  total_documents: number;
  completed_documents: number;
  failed_documents: number;
  total_questions: number;
  helpful_responses: number;
  unhelpful_responses: number;
}

export const DashboardStats: React.FC = () => {
  const [stats, setStats] = useState<StatsData | null>(null);

  const loadStats = async () => {
    try {
      const res = await apiClient.get<StatsData>('/feedback/stats');
      setStats(res.data);
    } catch (e) {
      // Ignore if stats not ready
    }
  };

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) return null;

  return (
    <div className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center justify-between text-xs overflow-x-auto gap-4">
      <div className="flex items-center gap-2 text-slate-400 font-medium shrink-0">
        <BarChart2 className="h-4 w-4 text-indigo-400" />
        <span>RAG Dashboard:</span>
      </div>

      <div className="flex items-center gap-6 shrink-0">
        <div className="flex items-center gap-1.5 text-slate-300">
          <FileText className="h-3.5 w-3.5 text-indigo-400" />
          <span>Total Docs: <strong className="text-white">{stats.total_documents}</strong></span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-300">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
          <span>Completed: <strong className="text-emerald-400">{stats.completed_documents}</strong></span>
        </div>

        {stats.failed_documents > 0 && (
          <div className="flex items-center gap-1.5 text-slate-300">
            <AlertCircle className="h-3.5 w-3.5 text-rose-400" />
            <span>Failed: <strong className="text-rose-400">{stats.failed_documents}</strong></span>
          </div>
        )}

        <div className="flex items-center gap-1.5 text-slate-300">
          <HelpCircle className="h-3.5 w-3.5 text-amber-400" />
          <span>Questions: <strong className="text-white">{stats.total_questions}</strong></span>
        </div>

        <div className="flex items-center gap-3 bg-slate-950 px-3 py-1 rounded-full border border-slate-800">
          <span className="flex items-center gap-1 text-emerald-400">
            <ThumbsUp className="h-3 w-3" /> {stats.helpful_responses}
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1 text-rose-400">
            <ThumbsDown className="h-3 w-3" /> {stats.unhelpful_responses}
          </span>
        </div>
      </div>
    </div>
  );
};
