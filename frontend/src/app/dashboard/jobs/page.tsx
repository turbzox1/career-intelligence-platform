"use client";

import { useState } from "react";
import { Briefcase, ExternalLink, Loader2, Search } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { JobMatchResponse } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";

const DEMO_QUERY = `Senior Machine Learning Engineer with 5 years of experience in Python,
PyTorch, AWS and Kubernetes looking for a role in San Francisco. Strong
background in building LLM and RAG systems at scale.`;

export default function JobsPage() {
  const [query, setQuery] = useState(DEMO_QUERY);
  const [result, setResult] = useState<JobMatchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const match = async () => {
    if (query.trim().length < 10) {
      toast.error("Query must be at least 10 characters.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.matchJobs(query, 6);
      setResult(res);
      toast.success(`Found ${res.results.length} matching roles`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Matching failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Job Matching</h1>
        <p className="text-muted-foreground">
          Describe your profile and let semantic matching rank the best-fit roles.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your profile summary</CardTitle>
          <CardDescription>
            Free-form text is embedded and compared against job descriptions.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            rows={5}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Data engineer with Spark, Airflow and Snowflake…"
          />
          <Button onClick={match} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            {loading ? "Matching…" : "Find matching jobs"}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">
            {result.results.length} matching role
            {result.results.length === 1 ? "" : "s"}
          </h2>
          {result.results.length === 0 && (
            <Card className="border-dashed">
              <CardContent className="py-10 text-center text-sm text-muted-foreground">
                No matching jobs in the catalog yet.
              </CardContent>
            </Card>
          )}
          {result.results.map((r) => (
            <Card key={r.job.id}>
              <CardContent className="flex flex-col gap-4 p-5 md:flex-row md:items-center">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Briefcase className="h-5 w-5 shrink-0 text-muted-foreground" />
                    <h3 className="truncate font-semibold">{r.job.title}</h3>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {r.job.company} · {r.job.location}
                  </p>
                  {r.job.salary_min != null && (
                    <p className="mt-1 text-sm font-medium">
                      {formatCurrency(r.job.salary_min)}
                      {r.job.salary_max != null
                        ? ` – ${formatCurrency(r.job.salary_max)}`
                        : ""}{" "}
                      <span className="text-xs font-normal text-muted-foreground">
                        {r.job.currency}
                      </span>
                    </p>
                  )}
                </div>

                <div className="w-full md:w-64">
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Match</span>
                    <span className="font-semibold">
                      {Math.round(r.similarity * 100)}%
                    </span>
                  </div>
                  <Progress value={r.similarity * 100} />
                </div>

                {r.matched_skills.length > 0 && (
                  <div className="flex w-full flex-wrap gap-1.5 md:w-auto md:max-w-[240px] md:justify-end">
                    {r.matched_skills.slice(0, 4).map((s) => (
                      <Badge key={s} variant="success">
                        {s}
                      </Badge>
                    ))}
                    {r.missing_skills.slice(0, 2).map((s) => (
                      <Badge key={s} variant="destructive">
                        -{s}
                      </Badge>
                    ))}
                  </div>
                )}

                {r.job.source_url && (
                  <a
                    href={r.job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0"
                  >
                    <Button variant="outline" size="sm">
                      Apply <ExternalLink className="h-4 w-4" />
                    </Button>
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
