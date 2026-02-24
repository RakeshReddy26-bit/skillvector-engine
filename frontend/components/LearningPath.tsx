"use client";

import type { DisplayLearningStep } from "@/lib/types";

interface LearningPathProps {
  steps: DisplayLearningStep[];
}

export default function LearningPath({ steps }: LearningPathProps) {
  if (steps.length === 0) return null;

  return (
    <div className="timeline">
      {steps.map((step, i) => (
        <div key={`${step.skill}-${i}`} className="timeline-item">
          <div className="timeline-dot" />
          <div className="timeline-content">
            <div className="timeline-header">
              <span>{step.skill}</span>
              <span className="duration">{step.duration.toUpperCase()}</span>
            </div>
            <p>{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
