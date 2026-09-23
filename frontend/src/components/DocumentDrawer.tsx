import React, { useState } from 'react';
import { Upload, File, Trash2, CheckCircle2, AlertCircle, Loader2, FileType, HardDrive } from 'lucide-react';
import { Document } from '../types';

interface DocumentDrawerProps {
  documents: Document[];
  onUpload: (file: javaFile) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  selectedDocIds: string[];
  onToggleDocSelect: (id: string) => void;
  uploading: boolean;
}

// Rename File type for DOM browser File
type javaFile = globalThis.File;

export const DocumentDrawer: React.FC<DocumentDrawerProps> = ({
  documents,
  onUpload,
  onDelete,
  selectedDocIds,
  onToggleDocSelect,
  uploading,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      try {
        setError(null);
        await onUpload(e.target.files[0]);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Upload failed');
      }
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      try {
        setError(null);
        await onUpload(e.dataTransfer.files[0]);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Upload failed');
      }
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 px-2 py-0.5 rounded-full">
            <CheckCircle2 className="h-3 w-3" /> Indexed
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-amber-950/80 text-amber-400 border border-amber-800/50 px-2 py-0.5 rounded-full">
            <Loader2 className="h-3 w-3 animate-spin" /> Processing
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-rose-950/80 text-rose-400 border border-rose-800/50 px-2 py-0.5 rounded-full">
            <AlertCircle className="h-3 w-3" /> Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-full">
            Uploaded
          </span>
        );
    }
  };

  return (
    <div className="w-full lg:w-80 bg-slate-900 border-b lg:border-b-0 lg:border-r border-slate-800 flex flex-col h-full">
      {/* Upload Zone */}
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-sm font-semibold text-slate-200 mb-3 flex items-center justify-between">
          <span>Uploaded Documents</span>
          <span className="text-xs font-normal text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
            {documents.length}
          </span>
        </h2>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-4 text-center transition-all cursor-pointer ${
            dragActive ? 'border-indigo-500 bg-indigo-950/20' : 'border-slate-700 hover:border-indigo-500/50 bg-slate-950/40'
          }`}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.png,.jpg,.jpeg,.docx"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <label htmlFor="file-upload" className="cursor-pointer block">
            {uploading ? (
              <div className="flex flex-col items-center py-2">
                <Loader2 className="h-8 w-8 text-indigo-400 animate-spin mb-2" />
                <span className="text-xs text-slate-300">Parsing & Chunking Document...</span>
              </div>
            ) : (
              <div className="flex flex-col items-center py-2">
                <Upload className="h-7 w-7 text-indigo-400 mb-2" />
                <span className="text-xs font-medium text-slate-200">Click to upload or drag files</span>
                <span className="text-[10px] text-slate-500 mt-1">PDF, Scanned PDF, Images, DOCX (Max 20MB)</span>
              </div>
            )}
          </label>
        </div>

        {error && (
          <div className="mt-2 text-xs text-rose-400 bg-rose-950/50 border border-rose-900/50 p-2 rounded-lg flex items-center gap-1.5">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
        {documents.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            <FileType className="h-8 w-8 mx-auto text-slate-600 mb-2" />
            No documents uploaded yet. Upload a PDF, resume, or invoice to start asking questions.
          </div>
        ) : (
          documents.map((doc) => {
            const isSelected = selectedDocIds.includes(doc.id);
            return (
              <div
                key={doc.id}
                onClick={() => onToggleDocSelect(doc.id)}
                className={`p-3 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-indigo-950/40 border-indigo-500/60 shadow-md shadow-indigo-950/30'
                    : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <File className="h-4 w-4 text-indigo-400 shrink-0" />
                    <span className="text-xs font-medium text-slate-200 truncate" title={doc.filename}>
                      {doc.filename}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(doc.id);
                    }}
                    className="text-slate-500 hover:text-rose-400 p-1 rounded transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                  <div className="flex items-center gap-2">
                    <span>{formatBytes(doc.file_size)}</span>
                    {doc.total_pages > 0 && <span>• {doc.total_pages} pgs</span>}
                  </div>
                  <div>{getStatusBadge(doc.status)}</div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
