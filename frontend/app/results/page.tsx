"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type JsonObject = Record<string, unknown>;

type AnalysisResult = {
  company_name?: string;
  company_info?: JsonObject;
  jd_analysis?: JsonObject;
  job_description?: string;
  matching_analysis?: JsonObject;
  evidence_analysis?: JsonObject;
  suggestion_analysis?: JsonObject;
  matched_skills?: string[];
  missing_skills?: string[];
  match_score?: number;
};

function asRecord(value: unknown): JsonObject {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonObject)
    : {};
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.map((item) => (typeof item === "string" ? item : JSON.stringify(item)))
    : [];
}

function normalizeSkillLabel(skill: string): string {
  const normalized = skill
    .toLowerCase()
    .replace(/[-/(),]/g, " ")
    .replace(/&/g, " and ")
    .replace(/\s+/g, " ")
    .trim();

  const aliases: Record<string, string> = {
    "fastapi or similar backend frameworks": "fastapi",
    "fastapi or similar frameworks": "fastapi",
    "backend frameworks": "fastapi",
    "backend development": "fastapi",
    "backend systems": "fastapi",
    "backend services and apis": "backend apis",
    "developing backend services and apis": "backend apis",
    "postgresql and sql": "sql databases",
    "sql and postgresql": "sql databases",
    "postgresql sql": "sql databases",
    "postgresql": "sql databases",
    "sql": "sql databases",
    "sql databases": "sql databases",
    "database system": "sql databases",
    "database systems": "sql databases",
    "vector database": "vector databases",
    "vector databases and embeddings": "vector databases",
    "embeddings and vector databases": "vector databases",
    "pgvector": "vector databases",
    "supabase pgvector": "vector databases",
    "semantic search": "vector databases",
    "retrieval augmented generation": "rag",
    "retrieval augmented generation rag": "rag",
    "retrieval augmented generation rag systems": "rag",
    "rag systems": "rag",
    "retrieval systems": "rag",
    "retrieval system": "rag",
    "retrieval": "rag",
    "hybrid retrieval": "rag",
    "monitoring and observability systems": "observability",
    "monitoring evaluation and observability systems": "observability",
    "monitoring evaluation and observability": "observability",
    "monitoring systems": "observability",
    "observability systems": "observability",
    "monitoring observability": "observability",
    "version control": "git github",
    "git": "git github",
    "github": "git github",
    "git/github": "git github",
    "git and github": "git github",
    "performance optimization and scalability": "performance optimization",
    "scalability": "performance optimization",
    "cloud platforms": "cloud",
    "large language model applications": "llm applications",
    "large language model llm applications": "llm applications",
    "large language models": "llm applications",
    "large language models llms": "llm applications",
  };

  return aliases[normalized] ?? normalized;
}

function prettySkillLabel(skill: string): string {
  const normalized = normalizeSkillLabel(skill);
  const labels: Record<string, string> = {
    "backend apis": "Backend APIs",
    cloud: "Cloud Platforms",
    fastapi: "FastAPI",
    "git github": "Git/GitHub",
    "llm applications": "LLM Applications",
    observability: "Monitoring & Observability",
    "performance optimization": "Performance Optimization",
    rag: "Retrieval-Augmented Generation (RAG)",
    "sql databases": "SQL Databases",
    "vector databases": "Vector Databases",
  };

  return labels[normalized] ?? skill;
}

function dedupeSkillLabels(skills: string[]): string[] {
  const seen = new Set<string>();
  const deduped: string[] = [];

  for (const skill of skills) {
    const normalized = normalizeSkillLabel(skill);
    const prettyLabel = prettySkillLabel(skill);
    const labelKey = prettyLabel.toLowerCase();

    if (!skill || seen.has(normalized) || seen.has(labelKey)) {
      continue;
    }

    deduped.push(prettyLabel);
    seen.add(normalized);
    seen.add(labelKey);
  }

  return deduped;
}

function summarizeSkills(skills: string[], limit = 5): string {
  const shown = skills.slice(0, limit);

  if (!shown.length) {
    return "none";
  }

  if (skills.length <= limit) {
    return shown.join(", ");
  }

  return `${shown.join(", ")} and ${skills.length - limit} more`;
}

function buildReasoningSummary(
  matchedSkills: string[],
  missingSkills: string[],
  score: number | string,
): string {
  const scoreText = typeof score === "number" ? `${score}%` : "the current";
  let summary = `The resume matches ${matchedSkills.length} JD-requested skill areas for a ${scoreText} fit.`;

  if (matchedSkills.length) {
    summary += ` Strongest evidence includes ${summarizeSkills(matchedSkills)}.`;
  }

  if (missingSkills.length) {
    summary += ` Remaining gaps include ${summarizeSkills(missingSkills)}.`;
  } else {
    summary += " No major skill gaps were identified.";
  }

  return summary;
}

function jdValuesFromMatchRecord(value: unknown): string[] {
  const record = asRecord(value);

  return Object.values(record).flatMap((item) => {
    if (typeof item === "string") {
      return [item];
    }

    if (Array.isArray(item)) {
      return asStringArray(item);
    }

    return [];
  });
}

function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "No major skill gaps identified";
  }

  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }

  return JSON.stringify(value, null, 2);
}

function displayAgentError(error: string): string {
  if (error.toLowerCase().includes("rate limit")) {
    return "The AI provider hit a rate limit. Run a fresh analysis after switching to the smaller model.";
  }

  return error;
}

function firstString(...values: unknown[]): string | null {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return null;
}

function extractRoleFromJobDescription(jobDescription: string): string | null {
  const lines = jobDescription
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of lines.slice(0, 12)) {
    const match = line.match(
      /^(?:job\s*title|role|position|title)\s*[:\-]\s*(.+)$/i,
    );

    if (match?.[1]) {
      return match[1].trim();
    }
  }

  return lines[0]?.length <= 90 ? lines[0] : null;
}

function ResultCard({
  children,
  title,
}: {
  children: React.ReactNode;
  title: string;
}) {
  return (
    <article className="rounded-lg border border-[#464554]/25 bg-[#0d0d15]/70 p-4">
      <h2 className="mb-3 font-mono text-[11px] font-medium uppercase tracking-[0.14em] text-[#c0c1ff]">
        {title}
      </h2>
      {children}
    </article>
  );
}

function FitScoreCard({
  score,
  summary,
}: {
  score: number | "N/A";
  summary: string;
}) {
  const normalizedScore =
    typeof score === "number" ? Math.max(0, Math.min(100, score)) : 0;
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const progressOffset =
    circumference - (normalizedScore / 100) * circumference;

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-lg border border-[#464554]/35 bg-[#101013]/95 p-4 shadow-[0_0_24px_rgba(76,215,246,0.08)]">
      <h2 className="mb-3 font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[#c0c1ff]">
        Match Fit Summary
      </h2>
      <div className="flex items-center justify-center">
        <div className="relative flex h-44 w-44 items-center justify-center">
          <div className="absolute inset-8 rounded-full bg-[#4cd7f6]/10 blur-2xl" />
          <svg
            aria-label={`Fit score ${score}`}
            className="absolute inset-0 -rotate-90"
            viewBox="0 0 200 200"
          >
            <circle
              cx="100"
              cy="100"
              fill="none"
              r={radius}
              stroke="#30313d"
              strokeLinecap="round"
              strokeWidth="7"
            />
            <circle
              cx="100"
              cy="100"
              fill="none"
              r={radius}
              stroke="#4cd7f6"
              strokeDasharray={circumference}
              strokeDashoffset={progressOffset}
              strokeLinecap="round"
              strokeWidth="7"
              className="drop-shadow-[0_0_10px_rgba(76,215,246,0.8)] transition-all duration-700"
            />
          </svg>
          <div className="relative text-center">
            <p className="text-4xl font-black tracking-normal text-[#eeeafd]">
              {score}
              {score !== "N/A" && "%"}
            </p>
            <p className="mt-2 font-mono text-[10px] font-semibold uppercase tracking-[0.24em] text-[#4cd7f6]">
              Fit Score
            </p>
          </div>
        </div>
      </div>

      <div className="mt-3 flex-1">
        <div className="mb-2 flex items-center gap-2 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-[#aaa6b8]">
          <svg
            aria-hidden="true"
            className="h-4 w-4 text-[#aaa6b8]"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="M9.5 2A3.5 3.5 0 0 0 6 5.5v.35A4 4 0 0 0 4 13a4 4 0 0 0 4 4h1.5V2Z" />
            <path d="M14.5 2A3.5 3.5 0 0 1 18 5.5v.35A4 4 0 0 1 20 13a4 4 0 0 1-4 4h-1.5V2Z" />
          </svg>
          Reasoning Summary
        </div>
        <p className="border-l-2 border-[#2b2b35] pl-3 text-xs font-semibold leading-5 text-[#d8d5e4]">
          {summary}
        </p>
      </div>
    </article>
  );
}

function ChipList({
  items,
  tone = "cyan",
}: {
  items: string[];
  tone?: "cyan" | "redOrange";
}) {
  if (!items.length) {
    return <p className="text-sm text-[#908fa0]">No major skill gaps identified</p>;
  }

  const chipClass =
    tone === "redOrange"
      ? "border-[#ff6b35]/35 bg-[#ff6b35]/10 text-[#ffb088] shadow-[0_0_12px_rgba(255,107,53,0.08)]"
      : "border-[#4cd7f6]/30 bg-[#4cd7f6]/10 text-[#acedff]";

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, index) => (
        <span
          className={`rounded-lg border px-2.5 py-1 text-xs ${chipClass}`}
          key={`${item}-${index}`}
        >
          {item}
        </span>
      ))}
    </div>
  );
}

function SkillSummaryCard({
  items,
  title,
  tone,
}: {
  items: string[];
  title: string;
  tone: "cyan" | "redOrange";
}) {
  const isMissing = tone === "redOrange";
  const cardClass = isMissing
    ? "border-[#ff6b35]/25 bg-[#171014]/85 shadow-[0_0_22px_rgba(255,107,53,0.08)]"
    : "border-[#4cd7f6]/25 bg-[#101720]/85 shadow-[0_0_22px_rgba(76,215,246,0.08)]";
  const titleClass = isMissing ? "text-[#ffb088]" : "text-[#4cd7f6]";
  const iconClass = isMissing
    ? "border-[#ff6b35]/35 bg-[#ff6b35]/10 text-[#ff9b72]"
    : "border-[#4cd7f6]/35 bg-[#4cd7f6]/10 text-[#4cd7f6]";

  return (
    <article className={`h-full rounded-lg border p-4 ${cardClass}`}>
      <div className="mb-4 flex items-center gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <span
            className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border ${iconClass}`}
          >
            {isMissing ? (
              <svg
                aria-hidden="true"
                className="h-3.5 w-3.5"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path d="M12 9v4" />
                <path d="M12 17h.01" />
                <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
              </svg>
            ) : (
              <svg
                aria-hidden="true"
                className="h-3.5 w-3.5"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path d="M20 6 9 17l-5-5" />
              </svg>
            )}
          </span>
          <h2
            className={`truncate font-mono text-xs font-semibold uppercase tracking-[0.14em] ${titleClass}`}
          >
            {title}
          </h2>
        </div>
      </div>
      <ChipList items={items} tone={tone} />
    </article>
  );
}

function GroupedEvidenceList({ data }: { data: JsonObject }) {
  const groupedEntries = Object.entries(data).reduce<
    Array<{ evidence: string; skills: string[] }>
  >((groups, [skill, value]) => {
    const evidence = displayValue(value);
    const existingGroup = groups.find((group) => group.evidence === evidence);

    if (existingGroup) {
      existingGroup.skills.push(skill);
      return groups;
    }

    groups.push({ evidence, skills: [skill] });
    return groups;
  }, []);

  if (!groupedEntries.length) {
    return <p className="text-sm text-[#908fa0]">No evidence available yet</p>;
  }

  return (
    <div className="space-y-3">
      {groupedEntries.map((group) => (
        <div
          className="rounded-lg border border-[#464554]/20 bg-[#13131b]/70 p-3"
          key={`${group.skills.join("-")}-${group.evidence}`}
        >
          <div className="mb-2 flex flex-wrap gap-2">
            {group.skills.map((skill) => (
              <span
                className="rounded-lg border border-[#d8d5e4]/20 bg-[#eeeafd]/10 px-2.5 py-1 text-xs font-semibold capitalize text-[#eeeafd]"
                key={skill}
              >
                {skill.replaceAll("_", " ")}
              </span>
            ))}
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-[#c7c4d7]">
            {group.evidence}
          </p>
        </div>
      ))}
    </div>
  );
}

function CompanyInsights({
  items,
}: {
  items: JsonObject[];
}) {
  const insightVisuals = [
    {
      backgroundImage:
        "linear-gradient(180deg, rgba(12,12,16,0.1), rgba(12,12,16,0.88)), radial-gradient(circle at 18% 24%, rgba(238,234,253,0.2), transparent 18%), radial-gradient(circle at 62% 20%, rgba(76,215,246,0.11), transparent 22%), repeating-linear-gradient(90deg, rgba(238,234,253,0.1) 0 1px, transparent 1px 52px), repeating-linear-gradient(0deg, rgba(238,234,253,0.07) 0 1px, transparent 1px 18px), linear-gradient(90deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02) 22%, transparent 23%, transparent 48%, rgba(255,255,255,0.06) 49%, rgba(255,255,255,0.02) 70%, transparent 72%)",
      backgroundPosition: "center",
      backgroundSize: "cover, cover, cover, auto, auto, cover",
    },
    {
      backgroundImage:
        "linear-gradient(180deg, rgba(12,12,16,0.05), rgba(12,12,16,0.9)), radial-gradient(circle at 78% 18%, rgba(238,234,253,0.24), transparent 7%), radial-gradient(circle at 88% 18%, rgba(238,234,253,0.18), transparent 6%), radial-gradient(circle at 68% 18%, rgba(238,234,253,0.14), transparent 6%), repeating-linear-gradient(90deg, transparent 0 20px, rgba(76,215,246,0.12) 20px 22px, transparent 22px 36px), linear-gradient(16deg, transparent 0 48%, rgba(192,193,255,0.16) 49%, transparent 50%), linear-gradient(166deg, transparent 0 55%, rgba(76,215,246,0.14) 56%, transparent 57%), linear-gradient(90deg, rgba(238,234,253,0.1), rgba(76,215,246,0.03))",
      backgroundPosition: "center",
      backgroundSize: "cover, cover, cover, cover, 140px 70px, cover, cover, cover",
    },
    {
      backgroundImage:
        "linear-gradient(180deg, rgba(12,12,16,0.02), rgba(12,12,16,0.9)), radial-gradient(ellipse at center, rgba(238,234,253,0.16), transparent 18%), repeating-linear-gradient(90deg, rgba(238,234,253,0.12) 0 2px, transparent 2px 18px, rgba(76,215,246,0.07) 18px 20px, transparent 20px 38px), repeating-linear-gradient(0deg, rgba(255,255,255,0.08) 0 1px, transparent 1px 32px), radial-gradient(circle at 50% 48%, rgba(238,234,253,0.18), transparent 13%), linear-gradient(90deg, rgba(255,255,255,0.06), transparent 16%, rgba(255,255,255,0.05) 50%, transparent 80%)",
      backgroundPosition: "center",
      backgroundSize: "cover, cover, auto, auto, cover, cover",
    },
    {
      backgroundImage:
        "linear-gradient(180deg, rgba(12,12,16,0.02), rgba(12,12,16,0.88)), radial-gradient(ellipse at 50% 76%, rgba(76,215,246,0.16), transparent 28%), repeating-radial-gradient(ellipse at 50% 78%, rgba(238,234,253,0.16) 0 1px, transparent 1px 15px), linear-gradient(8deg, transparent 38%, rgba(238,234,253,0.18) 39%, transparent 41%), linear-gradient(-7deg, transparent 45%, rgba(76,215,246,0.12) 46%, transparent 48%), linear-gradient(4deg, transparent 54%, rgba(238,234,253,0.1) 55%, transparent 57%)",
      backgroundPosition: "center",
      backgroundSize: "cover, cover, 220px 80px, cover, cover, cover",
    },
  ];

  if (!items.length) {
    return (
      <section className="rounded-lg border border-[#464554]/25 bg-[#0d0d15]/70 p-4">
        <h2 className="mb-3 flex items-center gap-2 text-xl font-bold text-[#eeeafd]">
          <svg
            aria-hidden="true"
            className="h-5 w-5 text-[#c0c1ff]"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="m3 17 6-6 4 4 7-7" />
            <path d="M14 8h6v6" />
          </svg>
          Company Insights
        </h2>
        <p className="text-sm text-[#908fa0]">
          No company insights returned.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <h2 className="flex items-center gap-2 text-xl font-bold text-[#eeeafd]">
        <svg
          aria-hidden="true"
          className="h-5 w-5 text-[#c0c1ff]"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
        >
          <path d="m3 17 6-6 4 4 7-7" />
          <path d="M14 8h6v6" />
        </svg>
        Company Insights
      </h2>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {items.slice(0, 4).map((item, index) => {
          const title = displayValue(item.title);
          const content = displayValue(item.content);
          const visual = insightVisuals[index % insightVisuals.length];
          const tag =
            typeof item.category === "string"
              ? item.category
              : typeof item.source_type === "string"
                ? item.source_type
                : index === 0
                  ? "Engineering Intel"
                  : index === 1
                    ? "Market Signal"
                    : index === 2
                      ? "Team Context"
                      : "Company Intel";

          return (
            <article
              className="overflow-hidden rounded-lg border border-[#464554]/25 bg-[#101013] shadow-[0_0_18px_rgba(0,0,0,0.2)]"
              key={`${title}-${index}`}
            >
              <div
                className="relative h-28 overflow-hidden border-b border-[#464554]/15 opacity-90"
                style={{
                  backgroundImage: visual.backgroundImage,
                  backgroundPosition: visual.backgroundPosition,
                  backgroundSize: visual.backgroundSize,
                }}
              >
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#101013]/10 to-[#101013]/85" />
                <div className="absolute inset-0 shadow-[inset_0_0_40px_rgba(0,0,0,0.55)]" />
              </div>
              <div className="p-4">
                <span className="inline-block rounded border border-[#464554]/35 bg-[#292932] px-2 py-1 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] text-[#c0c1ff]">
                  {tag}
                </span>
                <h3 className="mt-3 line-clamp-2 text-base font-bold text-[#eeeafd]">
                  {title}
                </h3>
                <p className="mt-2 line-clamp-3 text-xs font-semibold leading-5 text-[#aaa6b8]">
                  {content}
                </p>

                {typeof item.url === "string" && (
                  <a
                    className="mt-4 inline-flex items-center gap-2 font-mono text-[10px] font-bold uppercase tracking-[0.18em] text-[#4cd7f6] hover:text-[#acedff]"
                    href={item.url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    Read Intel
                    <svg
                      aria-hidden="true"
                      className="h-3.5 w-3.5"
                      fill="none"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                    >
                      <path d="M7 17 17 7" />
                      <path d="M7 7h10v10" />
                    </svg>
                  </a>
                )}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function BulletList({ items }: { items: string[] }) {
  if (!items.length) {
    return (
      <p className="text-sm text-[#908fa0]">
        Strong match — all critical JD requirements were found.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li
          className="rounded-lg border border-[#464554]/20 bg-[#13131b]/70 p-3 text-sm leading-relaxed text-[#c7c4d7]"
          key={`${item}-${index}`}
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

export default function ResultsPage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [hasLoadedResult, setHasLoadedResult] = useState(false);

  const handleExportPdf = () => {
    window.print();
  };

  useEffect(() => {
    const loadResult = window.setTimeout(() => {
      const storedResult =
        sessionStorage.getItem("hireloop_result") ??
        localStorage.getItem("hireloop_result");

      if (storedResult) {
        try {
          setResult(JSON.parse(storedResult) as AnalysisResult);
        } catch {
          setResult(null);
        }
      }

      setHasLoadedResult(true);
    }, 0);

    return () => window.clearTimeout(loadResult);
  }, []);

  const matchingAnalysis = asRecord(result?.matching_analysis);
  const jdAnalysis = asRecord(result?.jd_analysis);
  const evidenceAnalysis = asRecord(result?.evidence_analysis);
  const suggestionAnalysis = asRecord(result?.suggestion_analysis);
  const companyInfo = asRecord(result?.company_info);
  const semanticMatchSkills = jdValuesFromMatchRecord(
    matchingAnalysis.semantic_matches,
  );
  const partialMatchSkills = jdValuesFromMatchRecord(
    matchingAnalysis.partial_matches,
  );
  const matchedSkills = dedupeSkillLabels([
    ...asStringArray(matchingAnalysis.matched_skills ?? result?.matched_skills),
    ...semanticMatchSkills,
    ...partialMatchSkills,
  ]);
  const matchedSkillNorms = new Set(matchedSkills.map(normalizeSkillLabel));
  const missingSkills = dedupeSkillLabels(
    asStringArray(
      matchingAnalysis.missing_skills ??
        matchingAnalysis.missing_requirements ??
        matchingAnalysis.skill_gaps ??
        result?.missing_skills,
    ).filter((skill) => !matchedSkillNorms.has(normalizeSkillLabel(skill))),
  );
  const fallbackScore =
    matchedSkills.length + missingSkills.length > 0
      ? Math.round(
          (matchedSkills.length / (matchedSkills.length + missingSkills.length)) *
            100,
        )
      : Number.NaN;
  const rawScore =
    typeof matchingAnalysis.match_score === "number"
      ? matchingAnalysis.match_score
      : Number(matchingAnalysis.match_score ?? result?.match_score ?? fallbackScore);
  const score = Number.isFinite(rawScore)
    ? rawScore <= 1
      ? Math.round(rawScore * 100)
      : Math.round(rawScore)
    : "N/A";
  const companyResearchResults = Array.isArray(companyInfo.research_results)
    ? companyInfo.research_results.map(asRecord)
    : [];
  const companyName = result?.company_name ?? "HireLoop";
  const role =
    firstString(
      jdAnalysis.role_title,
      jdAnalysis.job_title,
      jdAnalysis.title,
      jdAnalysis.position,
      matchingAnalysis.role,
      matchingAnalysis.target_role,
    ) ??
    extractRoleFromJobDescription(result?.job_description ?? "") ??
    "Role from Job Description";
  const reasoningSummary = buildReasoningSummary(
    matchedSkills,
    missingSkills,
    score,
  );
  const resumeSuggestions = [
    ...asStringArray(suggestionAnalysis.strengths_to_highlight),
    ...asStringArray(suggestionAnalysis.projects_to_emphasize),
    ...asStringArray(suggestionAnalysis.resume_improvements),
    ...asStringArray(suggestionAnalysis.skills_to_learn),
    ...asStringArray(suggestionAnalysis.section_order_suggestions),
  ];
  const suggestionError =
    typeof suggestionAnalysis.error === "string" ? suggestionAnalysis.error : null;

  return (
    <main
      className="min-h-screen bg-[#111119] px-4 py-6 text-[#e4e1ed] sm:px-6"
      style={{
        backgroundImage:
          "radial-gradient(circle at 1px 1px, rgba(192,193,255,0.08) 1px, transparent 0)",
        backgroundSize: "18px 18px",
      }}
    >
      <style jsx global>{`
        @media print {
          .no-print {
            display: none !important;
          }

          body {
            background: #111119 !important;
          }
        }
      `}</style>

      <section className="mx-auto max-w-6xl">
        <div className="mb-5 flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.28em] text-[#4cd7f6]">
              System Analysis // Status: Verified
            </p>
            <div className="no-print flex flex-wrap gap-2">
              <button
                className="flex items-center gap-1.5 rounded-lg border border-[#c0c1ff]/40 bg-[#c0c1ff] px-3 py-1.5 font-mono text-[10px] font-semibold uppercase tracking-[0.12em] text-[#1000a9] transition hover:bg-[#d9d9ff]"
                onClick={handleExportPdf}
                type="button"
              >
                <svg
                  aria-hidden="true"
                  className="h-3.5 w-3.5"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 3v12" />
                  <path d="m7 10 5 5 5-5" />
                  <path d="M5 21h14" />
                </svg>
                Export Report
              </button>
              <Link
                className="rounded-lg border border-[#464554]/40 bg-transparent px-3 py-1.5 text-xs text-[#c7c4d7] transition hover:bg-[#292932]"
                href="/"
              >
                Back
              </Link>
              <Link
                className="rounded-lg border border-[#464554]/40 bg-[#292932] px-3 py-1.5 text-xs text-[#c7c4d7] transition hover:bg-[#34343d]"
                href="/"
              >
                Analyze Again
              </Link>
            </div>
          </div>

          <div>
            <h1 className="text-2xl font-black tracking-normal text-[#eeeafd] sm:text-3xl">
              Analysis Report
            </h1>
            <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-base font-semibold text-[#c7c4d7]">
              <div className="flex items-center gap-3">
                <span>Target Company:</span>
                <span className="rounded-full border border-[#d8d5e4]/25 bg-[#eeeafd]/10 px-3 py-1 font-mono text-xs uppercase tracking-[0.14em] text-[#eeeafd] shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                  {companyName}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span>Role:</span>
                <span className="rounded-full border border-[#d8d5e4]/25 bg-[#eeeafd]/10 px-3 py-1 font-mono text-xs uppercase tracking-[0.14em] text-[#eeeafd] shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                  {role}
                </span>
              </div>
            </div>
          </div>
        </div>

        {!hasLoadedResult ? (
          <ResultCard title="Loading Report">
            <p className="text-sm text-[#c7c4d7]">Reading saved analysis...</p>
          </ResultCard>
        ) : !result ? (
          <ResultCard title="No Result Found">
            <p className="text-sm text-[#c7c4d7]">
              Run an analysis first from the Analyze page to generate a report.
            </p>
          </ResultCard>
        ) : (
          <div className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-3">
              <FitScoreCard score={score} summary={reasoningSummary} />
              <SkillSummaryCard
                items={matchedSkills}
                title="Matched Skills"
                tone="cyan"
              />
              <SkillSummaryCard
                items={missingSkills}
                title="Missing Skills"
                tone="redOrange"
              />
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <ResultCard title="Evidence">
                <GroupedEvidenceList
                  data={asRecord(evidenceAnalysis.skill_evidence)}
                />
              </ResultCard>
              <ResultCard title="Resume Suggestions">
                {resumeSuggestions.length ? (
                  <BulletList items={resumeSuggestions} />
                ) : suggestionError ? (
                  <p className="text-sm leading-relaxed text-[#ffb088]">
                    Suggestion agent error: {displayAgentError(suggestionError)}
                  </p>
                ) : (
                  <p className="text-sm leading-relaxed text-[#908fa0]">
                    Strong match — all critical JD requirements were found.
                  </p>
                )}
              </ResultCard>
            </div>

            <CompanyInsights items={companyResearchResults} />
          </div>
        )}
      </section>
    </main>
  );
}
