"use client";

import type { DisplayMissingSkill } from "@/lib/types";

interface SkillGapGridProps {
  skills: DisplayMissingSkill[];
}

export default function SkillGapGrid({ skills }: SkillGapGridProps) {
  if (skills.length === 0) return null;

  return (
    <div className="skill-grid">
      {skills.map((skill, i) => {
        const prio = skill.priority.toLowerCase();
        return (
          <div
            key={`${skill.skill}-${i}`}
            className={`skill-card priority-${prio}`}
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            <span className="priority-badge">
              {prio === "high" ? "\u25cf" : prio === "medium" ? "\u25d0" : "\u25cb"}{" "}
              {skill.priority}
            </span>
            <h3>{skill.skill}</h3>
            <p>{skill.why}</p>
            {skill.frequency && (
              <span className="freq">In {skill.frequency} of roles</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
