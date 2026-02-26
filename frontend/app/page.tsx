"use client";

import { useState, useCallback, useRef } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { DisplayResult } from "@/lib/types";
import { DEMO_RESULT } from "@/lib/demo-data";
import HealthBanner from "@/components/HealthBanner";
import UploadZone from "@/components/UploadZone";
import ScoreRing from "@/components/ScoreRing";
import SkillGapGrid from "@/components/SkillGapGrid";
import LearningPath from "@/components/LearningPath";
import EvidencePanel from "@/components/EvidencePanel";
import RelatedJobs from "@/components/RelatedJobs";
import ErrorBoundary from "@/components/ErrorBoundary";
import AuthModal from "@/components/AuthModal";
import PaywallModal from "@/components/PaywallModal";
import ProfilePanel from "@/components/ProfilePanel";
import { ScoreRingSkeleton, GridSkeleton, SectionSkeleton } from "@/components/Skeleton";

const TECH_STACK = [
  "Python 3.11",
  "Claude Sonnet (Anthropic)",
  "FastAPI",
  "Next.js 14",
  "Pinecone",
  "Neo4j",
  "LangChain",
  "Sentence Transformers",
  "124 Pytest Tests",
  "Render (Free Tier)",
];

export default function Home() {
  const { user, refreshUser } = useAuth();
  const [result, setResult] = useState<DisplayResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAuth, setShowAuth] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);

  const scrollToResults = useCallback(() => {
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }, []);

  const handleAnalyze = useCallback(async (resume: string, targetJob: string) => {
    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await api.analyze({ resume, target_job: targetJob });
      setResult(data);
      scrollToResults();
      // Refresh usage count for authenticated users
      await refreshUser();
    } catch (err) {
      const status = (err as Error & { status?: number }).status;
      if (status === 403) {
        setShowPaywall(true);
      } else {
        const message = err instanceof Error ? err.message : "Something went wrong.";
        setError(message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [scrollToResults, refreshUser]);

  const handleFileUpload = useCallback(async (file: File, targetJob: string) => {
    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await api.uploadResume(file, targetJob);
      setResult(data);
      scrollToResults();
      await refreshUser();
    } catch (err) {
      const status = (err as Error & { status?: number }).status;
      if (status === 403) {
        setShowPaywall(true);
      } else {
        const message = err instanceof Error ? err.message : "Something went wrong.";
        setError(message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [scrollToResults, refreshUser]);

  const handleDemo = useCallback(() => {
    setError("");
    setResult(DEMO_RESULT);
    scrollToResults();
  }, [scrollToResults]);

  return (
    <>
      <HealthBanner onSignIn={() => setShowAuth(true)} onProfile={() => setShowProfile(true)} />

      {/* Auth, Paywall & Profile Modals */}
      <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
      <PaywallModal open={showPaywall} onClose={() => setShowPaywall(false)} />
      <ProfilePanel
        open={showProfile}
        onClose={() => setShowProfile(false)}
        onUpgrade={() => { setShowProfile(false); setShowPaywall(true); }}
      />

      <main className="max-w-7xl mx-auto px-6">
        {/* Hero */}
        <section className="py-20 text-center">
          <div className="inline-block font-mono text-[11px] tracking-[2px] text-accent bg-accent/[0.06] border border-accent/15 px-4 py-1.5 rounded-sm mb-8 animate-fade-up">
            AI CAREER INTELLIGENCE PLATFORM
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold leading-[1.05] tracking-tight animate-fade-up" style={{ animationDelay: "0.1s" }}>
            Your Career,
            <br />
            <span className="text-accent">Signal-First.</span>
          </h1>
          <p className="mt-5 font-mono text-sm text-muted max-w-lg mx-auto leading-relaxed animate-fade-up" style={{ animationDelay: "0.2s" }}>
            Deterministic skill gap analysis. Real evidence projects.
            Prerequisite-ordered learning paths. Built on Claude Sonnet.
            124 tests. Open source.
          </p>
        </section>

        {/* Upload Zone */}
        <section className="pb-16">
          <ErrorBoundary>
            <UploadZone
              onAnalyze={handleAnalyze}
              onFileUpload={handleFileUpload}
              onDemo={handleDemo}
              isLoading={isLoading}
            />
          </ErrorBoundary>
        </section>

        {/* API Error */}
        {error && (
          <div className="error-card max-w-3xl mx-auto mb-12">
            <h3>Analysis Failed</h3>
            <p>{error}</p>
            <button
              onClick={handleDemo}
              className="mt-4 px-6 py-2 bg-accent/10 border border-accent/20 text-accent rounded-md font-mono text-xs cursor-pointer hover:bg-accent/20 transition-all"
            >
              Load Demo Results Instead
            </button>
          </div>
        )}

        {/* Stats Bar */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 py-10 border-t border-b border-white/10 mb-16">
          {[
            ["124", "AUTOMATED TESTS"],
            ["32", "SKILLS IN DAG"],
            ["55", "INDEXED JOBS"],
            ["7", "PIPELINE STEPS"],
          ].map(([num, label]) => (
            <div key={label} className="text-center">
              <div className="text-3xl font-extrabold text-accent font-mono leading-none mb-1.5">
                {num}
              </div>
              <div className="font-mono text-[10px] text-muted tracking-widest">
                {label}
              </div>
            </div>
          ))}
        </section>

        {/* Loading Skeletons */}
        {isLoading && (
          <div ref={resultsRef} className="space-y-16 pb-20">
            <div className="loading-state">
              <div className="spinner" />
              <p style={{ color: "#e8edf5" }}>Claude is analyzing your profile...</p>
              <p className="font-mono text-xs" style={{ color: "#5a6478", marginTop: "8px" }}>Usually 10-20 seconds</p>
            </div>
            <Section num="01" title="Intelligence Score">
              <ScoreRingSkeleton />
            </Section>
            <Section num="02" title="Missing Skills">
              <GridSkeleton count={6} />
            </Section>
            <Section num="03" title="Learning Path">
              <SectionSkeleton rows={4} />
            </Section>
            <Section num="04" title="Evidence Projects">
              <SectionSkeleton rows={2} />
            </Section>
          </div>
        )}

        {/* Results — show when data exists */}
        {result && !isLoading && (
          <div id="results-section" ref={resultsRef}>

            {/* PANEL 01 — SCORE */}
            <section className="panel">
              <div className="section-header"><span className="num">01</span> Intelligence Score</div>
              <ErrorBoundary>
                <ScoreRing score={result.match_score} requestId={result.request_id} latencyMs={result.latency_ms} />
              </ErrorBoundary>
            </section>

            {/* PANEL 02 — MISSING SKILLS */}
            {result.missing_skills.length > 0 && (
              <section className="panel">
                <div className="section-header"><span className="num">02</span> Missing Skills &mdash; Critical Gaps</div>
                <ErrorBoundary>
                  <SkillGapGrid skills={result.missing_skills} />
                </ErrorBoundary>
              </section>
            )}

            {/* PANEL 03 — LEARNING PATH */}
            {result.learning_path.length > 0 && (
              <section className="panel">
                <div className="section-header"><span className="num">03</span> Learning Path &mdash; Prerequisite Ordered</div>
                <ErrorBoundary>
                  <LearningPath steps={result.learning_path} />
                </ErrorBoundary>
              </section>
            )}

            {/* PANEL 04 — EVIDENCE */}
            {result.evidence.length > 0 && (
              <section className="panel">
                <div className="section-header"><span className="num">04</span> Evidence Builder &mdash; Portfolio Projects</div>
                <ErrorBoundary>
                  <EvidencePanel projects={result.evidence} />
                </ErrorBoundary>
              </section>
            )}

            {/* PANEL 05 — JOBS (only if data exists) */}
            {result.related_jobs.length > 0 && (
              <section className="panel">
                <div className="section-header"><span className="num">05</span> Related Jobs &mdash; Semantic Match via Pinecone</div>
                <ErrorBoundary>
                  <RelatedJobs jobs={result.related_jobs} />
                </ErrorBoundary>
              </section>
            )}

            {/* Latency bar */}
            <div className="text-center font-mono text-[11px] text-muted pb-16">
              Analysis completed in{" "}
              <span className="text-accent">{(result.latency_ms / 1000).toFixed(1)}s</span>
              {" "}&middot; Request ID: {result.request_id}
            </div>

          </div>
        )}

        {/* Tech Stack */}
        <section className="py-10">
          <div className="flex items-center gap-3 justify-center mb-8">
            <span className="font-mono text-[11px] text-accent border border-accent/20 px-2.5 py-1 rounded-sm">
              STACK
            </span>
            <span className="text-xl font-bold">What Powers SkillVector</span>
          </div>
          <div className="flex gap-3 flex-wrap justify-center">
            {TECH_STACK.map((t) => (
              <span
                key={t}
                className="font-mono text-[11px] px-4 py-2 bg-surface border border-white/10 rounded-md text-muted transition-all hover:border-accent/30 hover:text-white"
              >
                {t}
              </span>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="my-16 p-16 text-center bg-surface border border-white/10 rounded-xl relative overflow-hidden">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full bg-accent/[0.06] blur-3xl" />
          <h2 className="text-3xl font-extrabold tracking-tight mb-3 relative">
            Try It Free. <span className="text-accent">Right Now.</span>
          </h2>
          <p className="font-mono text-sm text-muted max-w-md mx-auto leading-relaxed mb-8 relative">
            Paste any resume. Paste any job description. Get your skill gap
            analysis in under 30 seconds. 3 free analyses per month.
          </p>
          <div className="flex gap-4 justify-center relative">
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              className="px-8 py-3 bg-accent text-black font-bold text-sm rounded-lg hover:bg-[#00ffb3] transition-all hover:-translate-y-0.5"
            >
              START ANALYSIS &rarr;
            </button>
            <a
              href="https://github.com/RakeshReddy26-bit/skillvector-engine"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3 border border-accent/30 text-accent font-bold text-sm rounded-lg hover:border-accent hover:bg-accent/5 transition-all"
            >
              VIEW SOURCE CODE
            </a>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-10 border-t border-white/10 py-8 text-center">
        <p className="font-mono text-[11px] text-muted">
          SkillVector v3.0 &middot; Powered by{" "}
          <span className="text-accent">Claude Sonnet</span> &middot; Open
          source &middot; Built by Rakesh Reddy
        </p>
        <div className="flex gap-6 justify-center mt-3">
          <a
            href="https://github.com/RakeshReddy26-bit/skillvector-engine"
            target="_blank"
            rel="noopener noreferrer"
            className="font-mono text-[11px] text-muted hover:text-accent transition-colors"
          >
            GitHub
          </a>
        </div>
      </footer>
    </>
  );
}

// Section wrapper (used by loading skeletons)
function Section({
  num,
  title,
  children,
}: {
  num: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <div className="section-header">
        <span className="num">{num}</span>
        <span dangerouslySetInnerHTML={{ __html: title }} />
      </div>
      {children}
    </section>
  );
}
