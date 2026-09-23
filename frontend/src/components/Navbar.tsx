import React from 'react';
import { FileText, Database, ShieldCheck } from 'lucide-react';
import { HealthResponse } from '../types';

interface NavbarProps {
  health: HealthResponse | null;
}

export const Navbar: React.FC<NavbarProps> = ({ health }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="bg-gradient-to-tr from-indigo-600 to-violet-600 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
          <FileText className="h-6 w-6" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-white tracking-tight">
            Multimodal Document Intelligence <span className="text-indigo-400 font-normal">& RAG Assistant</span>
          </h1>
          <p className="text-xs text-slate-400">PDF • Scanned OCR • Vision • ChromaDB • Grounded Citations</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden sm:flex items-center space-x-2 bg-slate-800/80 border border-slate-700/50 px-3 py-1.5 rounded-full text-xs">
          <span className={`h-2 w-2 rounded-full ${health?.status === 'ok' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
          <span className="text-slate-300 font-medium">API: {health?.status || 'Connecting...'}</span>
        </div>
        <div className="hidden sm:flex items-center space-x-2 bg-slate-800/80 border border-slate-700/50 px-3 py-1.5 rounded-full text-xs">
          <Database className="h-3.5 w-3.5 text-indigo-400" />
          <span className="text-slate-300 font-medium">DB: {health?.database || 'SQLite'}</span>
        </div>
        <div className="flex items-center space-x-1 text-xs text-indigo-300 bg-indigo-950/60 border border-indigo-800/50 px-3 py-1.5 rounded-full">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Strict RAG</span>
        </div>
      </div>
    </header>
  );
};
