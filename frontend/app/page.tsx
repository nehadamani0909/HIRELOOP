"use client";

import { useRouter } from "next/navigation";
import {
  type ChangeEvent,
  type DragEvent,
  type ReactNode,
  useEffect,
  useRef,
  useState,
} from "react";

type IconName =
  | "alert"
  | "analytics"
  | "bolt"
  | "brain"
  | "building"
  | "check"
  | "file"
  | "history"
  | "hub"
  | "sparkles"
  | "upload"
  | "user"
  | "view";

type JsonObject = Record<string, unknown>;

type AnalysisResult = {
  company_name?: string;
  company_info?: JsonObject;
  matching_analysis?: JsonObject;
  evidence_analysis?: JsonObject;
  suggestion_analysis?: JsonObject;
  matched_skills?: string[];
  missing_skills?: string[];
  match_score?: number;
};

const agentProgressSteps = [
  "Resume Agent running...",
  "JD Agent running...",
  "Company Research Agent running...",
  "Matching Agent running...",
  "Generating suggestions...",
];

const iconPaths: Record<IconName, string[]> = {
  alert: [
    "M12 9v4",
    "M12 17h.01",
    "M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z",
  ],
  analytics: ["M3 3v18h18", "M8 17V9", "M13 17V5", "M18 17v-7"],
  bolt: ["M13 2 4 14h7l-2 8 9-12h-7l2-8Z"],
  brain: [
    "M9.5 2A3.5 3.5 0 0 0 6 5.5v.35A4 4 0 0 0 4 13a4 4 0 0 0 4 4h1.5V2Z",
    "M14.5 2A3.5 3.5 0 0 1 18 5.5v.35A4 4 0 0 1 20 13a4 4 0 0 1-4 4h-1.5V2Z",
    "M9.5 8H8",
    "M14.5 8H16",
    "M9.5 13H8",
    "M14.5 13H16",
    "M12 17v5",
  ],
  building: [
    "M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16",
    "M18 21V9h-2",
    "M2 21h20",
    "M8 7h4",
    "M8 11h4",
    "M8 15h4",
  ],
  check: ["M20 6 9 17l-5-5"],
  file: [
    "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z",
    "M14 2v6h6",
    "M8 13h8",
    "M8 17h5",
  ],
  history: ["M3 12a9 9 0 1 0 3-6.7", "M3 3v6h6", "M12 7v5l3 2"],
  hub: [
    "M12 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
    "M5 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
    "M19 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
    "M12 7v4",
    "m7 16-4-3",
    "m17 16-4-3",
  ],
  sparkles: [
    "M12 3 13.8 8.2 19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z",
    "M5 3v4",
    "M3 5h4",
    "M19 17v4",
    "M17 19h4",
  ],
  upload: [
    "M12 16V4",
    "m7 9 5-5 5 5",
    "M20 16v3a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-3",
  ],
  user: ["M20 21a8 8 0 0 0-16 0", "M12 13a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z"],
  view: [
    "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z",
    "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z",
  ],
};

function Icon({
  name,
  className = "",
  size = 20,
}: {
  name: IconName;
  className?: string;
  size?: number;
}) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      height={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
      width={size}
    >
      {iconPaths[name].map((path) => (
        <path d={path} key={path} />
      ))}
    </svg>
  );
}

function asRecord(value: unknown): JsonObject {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonObject)
    : {};
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) =>
      typeof item === "string" ? item : JSON.stringify(item, null, 2),
    )
    .filter(Boolean);
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

function EmptyState() {
  return (
    <p className="text-sm text-[#908fa0]">
      Strong match — all critical JD requirements were found.
    </p>
  );
}

function ResultCard({
  children,
  title,
}: {
  children: ReactNode;
  title: string;
}) {
  return (
    <article className="rounded-lg border border-[#464554]/25 bg-[#0d0d15]/70 p-5">
      <h3 className="mb-4 font-mono text-xs font-medium uppercase tracking-[0.14em] text-[#c0c1ff]">
        {title}
      </h3>
      {children}
    </article>
  );
}

function ChipList({
  emptyLabel = "No skills returned",
  items,
  tone = "primary",
}: {
  emptyLabel?: string;
  items: string[];
  tone?: "primary" | "secondary" | "tertiary";
}) {
  const toneClass = {
    primary: "border-[#c0c1ff]/30 bg-[#c0c1ff]/10 text-[#e1e0ff]",
    secondary: "border-[#4cd7f6]/30 bg-[#4cd7f6]/10 text-[#acedff]",
    tertiary: "border-[#ffb783]/30 bg-[#ffb783]/10 text-[#ffdcc5]",
  }[tone];

  if (!items.length) {
    return <p className="text-sm text-[#908fa0]">{emptyLabel}</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span
          className={`rounded-lg border px-3 py-1.5 text-sm ${toneClass}`}
          key={item}
        >
          {item}
        </span>
      ))}
    </div>
  );
}

function KeyValueList({ data }: { data: JsonObject }) {
  const entries = Object.entries(data);

  if (!entries.length) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-3">
      {entries.map(([key, value]) => (
        <div
          className="rounded-lg border border-[#464554]/20 bg-[#13131b]/70 p-3"
          key={key}
        >
          <p className="mb-1 text-sm font-semibold text-[#e4e1ed]">
            {key.replaceAll("_", " ")}
          </p>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-[#c7c4d7]">
            {displayValue(value)}
          </p>
        </div>
      ))}
    </div>
  );
}

function BulletList({ items }: { items: string[] }) {
  if (!items.length) {
    return <EmptyState />;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li
          className="rounded-lg border border-[#464554]/20 bg-[#13131b]/70 p-3 text-sm leading-relaxed text-[#c7c4d7]"
          key={item}
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

function CompanyResearch({ companyInfo }: { companyInfo: JsonObject }) {
  const researchResults = Array.isArray(companyInfo.research_results)
    ? companyInfo.research_results.map(asRecord)
    : [];

  if (companyInfo.error) {
    return (
      <p className="rounded-lg border border-[#ffb4ab]/25 bg-[#93000a]/15 p-3 text-sm text-[#ffdad6]">
        {displayValue(companyInfo.error)}
      </p>
    );
  }

  if (!researchResults.length) {
    return <KeyValueList data={companyInfo} />;
  }

  return (
    <div className="space-y-3">
      {researchResults.map((item, index) => (
        <div
          className="rounded-lg border border-[#464554]/20 bg-[#13131b]/70 p-3"
          key={`${item.title ?? "source"}-${index}`}
        >
          <p className="mb-1 text-sm font-semibold text-[#e4e1ed]">
            {displayValue(item.title)}
          </p>
          <p className="mb-2 text-sm leading-relaxed text-[#c7c4d7]">
            {displayValue(item.content)}
          </p>
          {typeof item.url === "string" && (
            <a
              className="text-sm font-medium text-[#4cd7f6] hover:text-[#acedff]"
              href={item.url}
              rel="noreferrer"
              target="_blank"
            >
              View source
            </a>
          )}
        </div>
      ))}
    </div>
  );
}

async function postAnalysis(formData: FormData, timeoutMs = 120000) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
    "http://127.0.0.1:8000";

  try {
    return await fetch(`${apiBaseUrl}/analyze-langgraph`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
  } finally {
    window.clearTimeout(timeout);
  }
}

export default function Home() {
  const router = useRouter();
  const [resume, setResume] = useState<File | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState("Ready");
  const [agentStepIndex, setAgentStepIndex] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isLoading) {
      return;
    }

    const interval = window.setInterval(() => {
      setAgentStepIndex((currentStep) =>
        Math.min(currentStep + 1, agentProgressSteps.length - 1),
      );
    }, 1800);

    return () => window.clearInterval(interval);
  }, [isLoading]);

  const updateResume = (file?: File) => {
    if (!file) {
      setResume(null);
      return;
    }

    const isPdf =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {
      setError("Please upload a PDF resume");
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setError("Resume must be 25MB or smaller");
      return;
    }

    setError(null);
    setResume(file);
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    updateResume(event.target.files?.[0]);
  };

  const handleDrop = (event: DragEvent<HTMLElement>) => {
    event.preventDefault();
    setIsDragging(false);
    updateResume(event.dataTransfer.files?.[0]);
  };

  const startAnalyze = () => {
    if (isLoading) return;

    setStatus("Analyze button clicked...");
    void handleAnalyze();
  };

  const handleAnalyze = async () => {
    setStatus("Validating inputs...");

    if (!resume || !companyName.trim() || !jobDescription.trim()) {
      setError("Please fill all fields and upload a resume");
      setStatus("Missing required fields");
      return;
    }

    setIsLoading(true);
    setAgentStepIndex(0);
    setError(null);
    sessionStorage.removeItem("hireloop_result");
    localStorage.removeItem("hireloop_result");
    setStatus("Sending LangGraph analysis request...");

    try {
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("company_name", companyName);
      formData.append("job_description", jobDescription);

      const response = await postAnalysis(formData);

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      setStatus("Reading analysis result...");
      const data = (await response.json()) as AnalysisResult;
      const serializedResult = JSON.stringify(data);
      sessionStorage.setItem("hireloop_result", serializedResult);
      localStorage.setItem("hireloop_result", serializedResult);
      setStatus("Opening results page...");
      setIsLoading(false);
      window.location.assign("/results");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Analysis failed";
      const readableMessage =
        message === "Failed to fetch"
          ? "Backend is not reachable. Check your API URL and try again."
          : message;
      setError(readableMessage);
      setStatus(readableMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const matchingAnalysis = asRecord(result?.matching_analysis);
  const evidenceAnalysis = asRecord(result?.evidence_analysis);
  const suggestionAnalysis = asRecord(result?.suggestion_analysis);
  const companyInfo = asRecord(result?.company_info);
  const matchScore =
    typeof matchingAnalysis.match_score === "number"
      ? matchingAnalysis.match_score
      : Number(matchingAnalysis.match_score ?? 0);
  const matchedSkills = asStringArray(matchingAnalysis.matched_skills);
  const missingSkills = asStringArray(matchingAnalysis.missing_skills);
  const resumeSuggestions = [
    ...asStringArray(suggestionAnalysis.strengths_to_highlight),
    ...asStringArray(suggestionAnalysis.projects_to_emphasize),
    ...asStringArray(suggestionAnalysis.resume_improvements),
    ...asStringArray(suggestionAnalysis.skills_to_learn),
    ...asStringArray(suggestionAnalysis.section_order_suggestions),
  ];

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#050505] px-4 pb-20 pt-16 text-[#e4e1ed] selection:bg-[#c0c1ff]/30 sm:px-6">
      <style jsx>{`
        .scanline {
          animation: scan 3s linear infinite;
        }

        @keyframes scan {
          0% {
            top: -2px;
          }
          100% {
            top: 100%;
          }
        }
      `}</style>

      <div className="pointer-events-none absolute -left-24 top-16 h-72 w-72 rounded-full bg-[#4cd7f6]/10 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 bottom-28 h-72 w-72 rounded-full bg-[#c0c1ff]/10 blur-3xl" />

      <header className="fixed inset-x-0 top-0 z-50 flex h-12 items-center justify-between border-b border-[#464554]/20 bg-[#13131b]/70 px-4 shadow-[0_0_20px_rgba(192,193,255,0.1)] backdrop-blur-xl sm:px-6">
        <div className="flex items-center gap-3">
          <Icon name="hub" className="text-[#c0c1ff]" size={22} />
          <span className="font-sans text-xl font-bold tracking-normal text-[#c0c1ff]">
            HireLoop
          </span>
        </div>
        <button
          aria-label="Profile"
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#464554]/30 bg-[#292932] text-[#c7c4d7] transition hover:bg-[#c0c1ff]/10 hover:text-[#c0c1ff]"
          type="button"
        >
          <Icon name="user" size={17} />
        </button>
      </header>

      <section className="relative mx-auto mb-10 max-w-2xl text-center">
        <h1 className="inline-block bg-gradient-to-r from-[#c0c1ff] via-[#4cd7f6] to-[#8083ff] bg-clip-text text-5xl font-bold tracking-normal text-transparent sm:text-6xl">
          HireLoop
        </h1>
        <p className="mt-3 font-mono text-xs font-medium uppercase tracking-[0.2em] text-[#908fa0]">
          Multi-Agent Career Intelligence
        </p>
      </section>

      {error && (
        <div className="mx-auto mb-5 flex max-w-2xl items-center gap-3 rounded-lg border border-[#ffb4ab]/30 bg-[#93000a]/20 p-4 text-[#ffdad6]">
          <Icon name="alert" className="shrink-0 text-[#ffb4ab]" size={20} />
          <p>{error}</p>
        </div>
      )}

      <section className="relative mx-auto mb-8 max-w-2xl overflow-hidden rounded-lg border border-[#464554]/30 bg-[#121212]/60 p-6 shadow-2xl backdrop-blur-xl sm:p-8">
        <div className="scanline pointer-events-none absolute left-0 h-px w-full bg-gradient-to-r from-transparent via-[#c0c1ff] to-transparent opacity-40" />

        <div className="relative z-10 space-y-8">
          <div className="space-y-3">
            <p className="ml-1 font-mono text-xs font-medium uppercase tracking-wider text-[#c0c1ff]">
              Identity Feed
            </p>
            <div
              className={`group relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-all ${
                resume
                  ? "border-[#4cd7f6]/50 bg-[#4cd7f6]/10"
                  : isDragging
                    ? "border-[#c0c1ff] bg-[#c0c1ff]/10"
                    : "border-[#464554]/40 bg-[#1f1f27]/30 hover:border-[#c0c1ff]/60 hover:bg-[#1f1f27]/50"
              }`}
              onDragLeave={() => setIsDragging(false)}
              onDragOver={(event) => {
                event.preventDefault();
                setIsDragging(true);
              }}
              onDrop={handleDrop}
            >
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-[#c0c1ff]/10 text-[#c0c1ff] transition-transform group-hover:scale-105">
                <Icon name={resume ? "check" : "upload"} size={28} />
              </div>
              <p className="max-w-full break-words text-center text-base text-[#e4e1ed]">
                {resume ? `File Ready: ${resume.name}` : "Choose a resume PDF"}
              </p>
              <p className="mt-1 text-xs text-[#908fa0]">
                Maximum file size: 25MB
              </p>
              <input
                accept=".pdf,application/pdf"
                aria-label="Upload resume PDF"
                className="mt-5 block w-full max-w-sm cursor-pointer rounded-lg border border-[#464554]/40 bg-[#0d0d15] text-sm text-[#c7c4d7] file:mr-4 file:cursor-pointer file:border-0 file:bg-[#c0c1ff] file:px-4 file:py-2 file:text-sm file:font-semibold file:text-[#1000a9] hover:file:bg-[#e1e0ff]"
                id="resumeInput"
                onChange={handleFileChange}
                onClick={(event) => {
                  event.currentTarget.value = "";
                }}
                ref={fileInputRef}
                type="file"
              />
              <p className="mt-3 text-center text-xs text-[#908fa0]">
                Selected file: {resume?.name ?? "none"}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <label
              className="ml-1 font-mono text-xs font-medium uppercase tracking-wider text-[#4cd7f6]"
              htmlFor="companyName"
            >
              Target Organization
            </label>
            <div className="relative">
              <Icon
                name="building"
                className="absolute left-4 top-1/2 -translate-y-1/2 text-[#908fa0]"
                size={18}
              />
              <input
                className="w-full rounded-lg border border-[#464554]/40 bg-[#0d0d15] py-3.5 pl-12 pr-4 text-base outline-none transition-all placeholder:text-[#908fa0]/50 focus:border-[#c0c1ff] focus:ring-2 focus:ring-[#c0c1ff]/30"
                id="companyName"
                onChange={(event) => setCompanyName(event.target.value)}
                placeholder="e.g. Datadog"
                type="text"
                value={companyName}
              />
            </div>
          </div>

          <div className="space-y-3">
            <label
              className="ml-1 font-mono text-xs font-medium uppercase tracking-wider text-[#ffb783]"
              htmlFor="jobDescription"
            >
              Operational Context
            </label>
            <div className="relative">
              <textarea
                className="w-full resize-none rounded-lg border border-[#464554]/40 bg-[#0d0d15] p-4 text-base outline-none transition-all placeholder:text-[#908fa0]/50 focus:border-[#c0c1ff] focus:ring-2 focus:ring-[#c0c1ff]/30"
                id="jobDescription"
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the Job Description here..."
                rows={5}
                value={jobDescription}
              />
              <div className="pointer-events-none absolute bottom-3 right-3 hidden items-center gap-1 rounded border border-[#464554]/30 bg-[#292932] px-2 py-1 text-[#c7c4d7]/70 sm:flex">
                <Icon name="sparkles" size={14} />
                <span className="font-mono text-[10px] font-medium">
                  AI ASSIST
                </span>
              </div>
            </div>
          </div>

          <button
            className="block w-full rounded-lg bg-[#c0c1ff] px-6 py-5 text-center text-xl font-bold text-[#1000a9] hover:bg-[#e1e0ff] active:scale-[0.99] disabled:cursor-wait disabled:opacity-75"
            data-testid="analyze-button"
            disabled={isLoading}
            onClick={startAnalyze}
            type="button"
          >
            {isLoading ? "Analyzing..." : "Analyze Application"}
          </button>

          {isLoading && (
            <div className="rounded-lg border border-[#464554]/25 bg-[#0d0d15]/70 p-4">
              <div className="space-y-2">
                {agentProgressSteps.map((step, index) => {
                  const isDone = index < agentStepIndex;
                  const isActive = index === agentStepIndex;

                  return (
                    <div
                      className={`flex items-center gap-3 text-sm transition ${
                        isActive
                          ? "text-[#4cd7f6]"
                          : isDone
                            ? "text-[#c0c1ff]"
                            : "text-[#908fa0]"
                      }`}
                      key={step}
                    >
                      <span
                        className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border font-mono text-[9px] ${
                          isActive
                            ? "border-[#4cd7f6] bg-[#4cd7f6]/15"
                            : isDone
                              ? "border-[#c0c1ff] bg-[#c0c1ff]/15"
                              : "border-[#464554] bg-[#13131b]"
                        }`}
                      >
                        {isDone ? "OK" : index + 1}
                      </span>
                      <span className="font-mono">{step}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <p className="text-center font-mono text-[10px] uppercase tracking-[0.1em] text-[#908fa0]">
            {status}
          </p>
        </div>
      </section>

      {result && (
        <section className="mx-auto mb-8 max-w-4xl rounded-lg border border-[#464554]/30 bg-[#121212]/60 p-6 backdrop-blur-xl sm:p-8">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="font-mono text-xs font-medium uppercase tracking-[0.18em] text-[#4cd7f6]">
                Analysis Report
              </p>
              <h2 className="mt-2 text-3xl font-semibold text-[#e4e1ed]">
                {result.company_name ?? companyName} Match Intelligence
              </h2>
            </div>
            <button
              className="rounded-lg border border-[#464554]/40 bg-[#292932] px-4 py-2 text-sm text-[#c7c4d7] transition hover:bg-[#34343d]"
              onClick={() => setResult(null)}
              type="button"
            >
              Clear Results
            </button>
          </div>

          <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
            <ResultCard title="Match Score">
              <div className="flex items-end gap-2">
                <span className="text-6xl font-bold text-[#c0c1ff]">
                  {Number.isFinite(matchScore) ? Math.round(matchScore) : 0}
                </span>
                <span className="pb-2 text-xl text-[#908fa0]">%</span>
              </div>
              {typeof matchingAnalysis.reasoning_summary === "string" && (
                <p className="mt-4 text-sm leading-relaxed text-[#c7c4d7]">
                  {matchingAnalysis.reasoning_summary}
                </p>
              )}
            </ResultCard>

            <div className="grid gap-4 sm:grid-cols-2">
              <ResultCard title="Matched Skills">
                <ChipList items={matchedSkills} tone="secondary" />
              </ResultCard>
              <ResultCard title="Missing Skills">
                <ChipList
                  emptyLabel="No missing skills returned"
                  items={missingSkills}
                  tone="tertiary"
                />
              </ResultCard>
            </div>
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <ResultCard title="Evidence">
              <div className="space-y-5">
                <KeyValueList
                  data={asRecord(evidenceAnalysis.skill_evidence)}
                />
                {Object.keys(
                  asRecord(evidenceAnalysis.weak_or_inferred_matches),
                ).length > 0 && (
                  <div>
                    <p className="mb-3 text-sm font-semibold text-[#ffdcc5]">
                      Weak or inferred matches
                    </p>
                    <KeyValueList
                      data={asRecord(evidenceAnalysis.weak_or_inferred_matches)}
                    />
                  </div>
                )}
              </div>
            </ResultCard>

            <ResultCard title="Resume Suggestions">
              <BulletList items={resumeSuggestions} />
            </ResultCard>
          </div>

          <div className="mt-4">
            <ResultCard title="Company Research">
              <CompanyResearch companyInfo={companyInfo} />
            </ResultCard>
          </div>
        </section>
      )}

      <section className="mx-auto grid max-w-2xl grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-[#464554]/20 bg-[#121212]/60 p-4 backdrop-blur-xl">
          <div className="mb-2 flex items-center gap-2">
            <Icon name="bolt" className="text-[#4cd7f6]" size={16} />
            <span className="font-mono text-xs font-medium uppercase text-[#c7c4d7]">
              Fast Lane
            </span>
          </div>
          <p className="text-sm leading-snug text-[#908fa0]">
            Quick scan for core keywords and ATS compatibility.
          </p>
        </div>
        <div className="rounded-lg border border-[#464554]/20 bg-[#121212]/60 p-4 backdrop-blur-xl">
          <div className="mb-2 flex items-center gap-2">
            <Icon name="view" className="text-[#ffb783]" size={16} />
            <span className="font-mono text-xs font-medium uppercase text-[#c7c4d7]">
              Deep Vision
            </span>
          </div>
          <p className="text-sm leading-snug text-[#908fa0]">
            Full profile match and interview prediction.
          </p>
        </div>
      </section>

      <nav className="fixed inset-x-0 bottom-0 z-50 grid h-12 grid-cols-2 rounded-t-lg border-t border-[#464554]/20 bg-[#0d0d15]/85 px-2 shadow-[0_-4px_24px_rgba(0,0,0,0.4)] backdrop-blur-2xl">
        {[
          ["analytics", "Analyze", "active", "/"],
          ["history", "Results", "", "/results"],
        ].map(([icon, label, active, href]) => (
          <button
            className={`flex items-center justify-center gap-2 rounded-lg px-3 py-1.5 transition active:scale-95 ${
              active
                ? "bg-[#03b5d3]/20 text-[#4cd7f6] shadow-[0_0_12px_rgba(76,215,246,0.25)]"
                : "text-[#908fa0] hover:text-[#c0c1ff]"
            }`}
            key={label}
            onClick={() => router.push(href)}
            type="button"
          >
            <Icon name={icon as IconName} size={17} />
            <span className="font-mono text-[11px] font-medium">{label}</span>
          </button>
        ))}
      </nav>
    </main>
  );
}
