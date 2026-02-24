"use client";

import { useState } from "react";
import type { DisplayEvidenceProject } from "@/lib/types";

interface EvidencePanelProps {
  projects: DisplayEvidenceProject[];
}

export default function EvidencePanel({ projects }: EvidencePanelProps) {
  if (projects.length === 0) return null;

  return (
    <div className="evidence-grid">
      {projects.map((project, i) => (
        <EvidenceCard key={`${project.skill_covered}-${i}`} item={project} />
      ))}
    </div>
  );
}

function EvidenceCard({ item }: { item: DisplayEvidenceProject }) {
  const [copied, setCopied] = useState(false);

  const copyBrief = () => {
    const text = [
      `Project: ${item.project_title}`,
      `Skill: ${item.skill_covered}`,
      `Description: ${item.description}`,
      `Deliverables:`,
      ...item.deliverables.map((d) => `  - ${d}`),
    ].join("\n");

    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="evidence-card">
      <span className="skill-tag">{item.skill_covered}</span>
      <h3>{item.project_title}</h3>
      <p>{item.description}</p>
      <ul>
        {item.deliverables.map((d, j) => (
          <li key={j}>{d}</li>
        ))}
      </ul>
      <div className="card-actions">
        <button onClick={copyBrief}>
          {copied ? "\u2713 COPIED" : "COPY BRIEF"}
        </button>
      </div>
    </div>
  );
}
