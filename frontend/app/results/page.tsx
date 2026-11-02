"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type JsonObject = Record<string, any>;

function asRecord(value: unknown): JsonObject {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonObject)
    : {};
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String) : [];
}

export default function ResultsPage() {
  const [result, setResult] = useState<JsonObject | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("hireloop_result");
    if (stored) setResult(JSON.parse(stored));
  }, []);

  if (!result) {
    return (
      <main className="min-h-screen bg-[#050505] text-[#e4e1ed] flex flex-col items-center justify-center">
        <h1 className="text-3xl font-bold">No analysis found</h1>
        <Link href="/" className="mt-4 text-[#4cd7f6]">
          Go back
        </Link>
      </main>
    );
  }

  const matching = asRecord(result.matching_analysis);
  const evidence = asRecord(result.evidence_analysis);
  const suggestions = asRecord(result.suggestion_analysis);
  const company = asRecord(result.company_info);

  const score =
    typeof matching.match_score === "number"
      ? Math.round(matching.match_score * 100)
      : "N/A";

  return (
    <main className="min-h-screen bg-[#050505] text-[#e4e1ed] px-6 py-10">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold">HireLoop Results</h1>
            <p className="text-[#908fa0] mt-2">
              Multi-agent analysis for {String(result.company_name)}
            </p>
          </div>

          <Link
            href="/"
            className="rounded-lg bg-[#292932] px-4 py-2 text-sm hover:bg-[#34343d]"
          >
            New Analysis
          </Link>
        </div>

        <Card title="Match Score">
          <p className="text-6xl font-bold text-[#c0c1ff]">{score}%</p>
          <p className="mt-3 text-[#c7c4d7]">
            {String(matching.reasoning_summary || "")}
          </p>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card title="Matched Skills">
            <List items={asStringArray(matching.matched_skills)} />
          </Card>

          <Card title="Missing Skills">
            <List items={asStringArray(matching.missing_skills)} />
          </Card>
        </div>

        <Card title="Semantic Matches">
          <KeyValue data={asRecord(matching.semantic_matches)} />
        </Card>

        <Card title="Evidence">
          <KeyValue data={asRecord(evidence.skill_evidence)} />
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card title="Projects to Emphasize">
            <List items={asStringArray(suggestions.projects_to_emphasize)} />
          </Card>

          <Card title="Skills to Learn">
            <List items={asStringArray(suggestions.skills_to_learn)} />
          </Card>
        </div>

        <Card title="Resume Improvements">
          <List items={asStringArray(suggestions.resume_improvements)} />
        </Card>

        <Card title="Company Research">
          <div className="space-y-4">
            {Array.isArray(company.research_results) ? (
              company.research_results.map((item: any, index: number) => (
                <div
                  key={index}
                  className="rounded-lg border border-[#464554]/30 bg-[#13131b] p-4"
                >
                  <h3 className="font-semibold">{item.title}</h3>
                  <p className="text-sm text-[#c7c4d7] mt-2">{item.content}</p>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[#4cd7f6] text-sm mt-2 inline-block"
                  >
                    View source
                  </a>
                </div>
              ))
            ) : (
              <p className="text-[#908fa0]">No company research found.</p>
            )}
          </div>
        </Card>
      </div>
    </main>
  );
}

function Card({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-xl border border-[#464554]/30 bg-[#121212]/70 p-6">
      <h2 className="mb-4 font-mono text-sm uppercase tracking-wider text-[#c0c1ff]">
        {title}
      </h2>
      {children}
    </section>
  );
}

function List({ items }: { items: string[] }) {
  if (!items.length) {
    return <p className="text-[#908fa0]">No data returned.</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li
          key={index}
          className="rounded-lg bg-[#13131b] border border-[#464554]/20 p-3 text-[#c7c4d7]"
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

function KeyValue({ data }: { data: JsonObject }) {
  const entries = Object.entries(data);

  if (!entries.length) {
    return <p className="text-[#908fa0]">No data returned.</p>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="rounded-lg bg-[#13131b] border border-[#464554]/20 p-3"
        >
          <p className="font-semibold text-[#4cd7f6]">{key}</p>
          <p className="text-sm text-[#c7c4d7] mt-1">{String(value)}</p>
        </div>
      ))}
    </div>
  );
}
