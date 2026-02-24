"use client";

import { useState, useCallback, useRef } from "react";

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"];
const ALLOWED_ACCEPT = ALLOWED_EXTENSIONS.join(",");

interface UploadZoneProps {
  onAnalyze: (resume: string, targetJob: string) => void;
  onFileUpload: (file: File, targetJob: string) => void;
  onDemo: () => void;
  isLoading: boolean;
}

function getFileExtension(name: string): string {
  const dot = name.lastIndexOf(".");
  return dot >= 0 ? name.slice(dot).toLowerCase() : "";
}

function buildTargetJob(role: string, jobDesc: string): string {
  const parts: string[] = [];
  if (role.trim()) parts.push(`Target Role: ${role.trim()}`);
  if (jobDesc.trim()) parts.push(jobDesc.trim());
  return parts.join("\n\n");
}

export default function UploadZone({ onAnalyze, onFileUpload, onDemo, isLoading }: UploadZoneProps) {
  const [resume, setResume] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((f: File): boolean => {
    const ext = getFileExtension(f.name);
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported file type: ${ext}. Allowed: PDF, DOCX, TXT, JPG, PNG.`);
      return false;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError("File too large. Maximum size is 10 MB.");
      return false;
    }
    return true;
  }, []);

  const handleFileSelect = useCallback((f: File) => {
    if (validateFile(f)) {
      setFile(f);
      setResume("");
      setError("");
    }
  }, [validateFile]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFileSelect(dropped);
  }, [handleFileSelect]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFileSelect(selected);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, [handleFileSelect]);

  const clearFile = useCallback(() => {
    setFile(null);
    setError("");
  }, []);

  const handleSubmit = useCallback(() => {
    const targetJob = buildTargetJob(targetRole, jobDesc);

    if (targetJob.length < 50) {
      setError("Please provide a target role and/or job description (at least 50 characters combined).");
      return;
    }

    // File upload path
    if (file) {
      setError("");
      onFileUpload(file, targetJob);
      return;
    }

    // Text paste path
    if (resume.trim().length < 50) {
      setError("Resume must be at least 50 characters.");
      return;
    }
    setError("");
    onAnalyze(resume.trim(), targetJob);
  }, [file, resume, targetRole, jobDesc, onAnalyze, onFileUpload]);

  return (
    <div className="w-full max-w-3xl mx-auto animate-fade-up">
      <div
        className={`rounded-xl border bg-surface p-8 transition-all ${
          dragOver
            ? "border-accent bg-accent/5"
            : "border-white/10"
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {/* File Upload Zone */}
        <label className="block font-mono text-[11px] text-muted tracking-widest mb-2">
          UPLOAD RESUME
        </label>
        <div
          className={`rounded-lg border-2 border-dashed p-6 text-center cursor-pointer transition-all mb-5 ${
            file
              ? "border-accent/40 bg-accent/5"
              : dragOver
                ? "border-accent bg-accent/10"
                : "border-white/15 hover:border-accent/30 hover:bg-white/[0.02]"
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          {file ? (
            <div className="flex items-center justify-center gap-3">
              <span className="font-mono text-sm text-accent">{file.name}</span>
              <span className="font-mono text-[10px] text-muted">
                ({(file.size / 1024).toFixed(0)} KB)
              </span>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); clearFile(); }}
                className="ml-2 font-mono text-[11px] text-warn hover:text-warn/80 transition-colors"
              >
                REMOVE
              </button>
            </div>
          ) : (
            <>
              <div className="font-mono text-sm text-muted mb-1">
                Drag &amp; drop your resume here
              </div>
              <div className="font-mono text-[10px] text-muted/60">
                PDF &middot; DOCX &middot; TXT &middot; JPG &middot; PNG &mdash; or click to browse
              </div>
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept={ALLOWED_ACCEPT}
            className="hidden"
            onChange={handleInputChange}
            disabled={isLoading}
          />
        </div>

        {/* OR divider */}
        {!file && (
          <>
            <div className="flex items-center gap-4 mb-5">
              <div className="flex-1 h-px bg-white/10" />
              <span className="font-mono text-[10px] text-muted tracking-widest">OR PASTE TEXT</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>

            {/* Resume Text */}
            <label className="block font-mono text-[11px] text-muted tracking-widest mb-2">
              PASTE YOUR RESUME
            </label>
            <textarea
              className="w-full min-h-[140px] bg-surface2 border border-white/10 text-white/90 p-4 rounded-lg font-mono text-xs leading-relaxed outline-none resize-y transition-colors focus:border-accent/40 placeholder:text-muted"
              placeholder="Paste your full resume text here..."
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              disabled={isLoading}
            />
          </>
        )}

        {/* Job Description (optional) */}
        <label className="block font-mono text-[11px] text-muted tracking-widest mb-2 mt-5">
          PASTE JOB DESCRIPTION <span className="text-muted/50">(OPTIONAL)</span>
        </label>
        <textarea
          className="w-full min-h-[100px] bg-surface2 border border-white/10 text-white/90 p-4 rounded-lg font-mono text-xs leading-relaxed outline-none resize-y transition-colors focus:border-accent/40 placeholder:text-muted"
          placeholder="Paste job description here (optional — improves accuracy)"
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          disabled={isLoading}
          rows={4}
        />

        {/* Target Role */}
        <label className="block font-mono text-[11px] text-muted tracking-widest mb-2 mt-5">
          TARGET ROLE
        </label>
        <input
          type="text"
          className="w-full bg-surface2 border border-white/10 text-white/90 p-4 rounded-lg font-mono text-xs outline-none transition-colors focus:border-accent/40 placeholder:text-muted"
          placeholder="e.g. Senior ML Engineer at Stripe"
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          disabled={isLoading}
        />

        {/* Error */}
        {error && (
          <div className="mt-3 px-4 py-3 rounded-md bg-warn/10 border border-warn/20 font-mono text-xs text-warn">
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="px-8 py-3 bg-accent text-black font-bold text-sm rounded-lg tracking-wide transition-all hover:bg-[#00ffb3] hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:translate-y-0"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                ANALYZING...
              </span>
            ) : (
              "ANALYZE MY RESUME \u2192"
            )}
          </button>

          <button
            onClick={onDemo}
            disabled={isLoading}
            className="px-6 py-3 bg-transparent text-accent border border-accent/30 font-bold text-sm rounded-lg tracking-wide transition-all hover:border-accent hover:bg-accent/5 disabled:opacity-50"
          >
            TRY DEMO
          </button>
        </div>

        {/* Loading message */}
        {isLoading && (
          <div className="mt-4 px-4 py-3 rounded-md bg-accent/5 border border-accent/15 font-mono text-xs text-accent flex items-center gap-2">
            <span className="w-3.5 h-3.5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
            Claude is analyzing your profile... This typically takes 10-20 seconds.
          </div>
        )}
      </div>
    </div>
  );
}
