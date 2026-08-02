"use client";

import { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";
import { api } from "@/lib/api";
import type { AnalyticsResponse } from "@/types";
import { formatCurrency } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { SalaryTrendChart, TopSkillsBarChart } from "@/components/charts";

type GroupRow = { label: string; average_salary: number; count: number };

function GroupBars({ data }: { data: GroupRow[] }) {
  const rows = data.slice().sort((a, b) => b.average_salary - a.average_salary);
  const max = Math.max(...rows.map((r) => r.average_salary), 1);
  return (
    <div className="space-y-2">
      {rows.length === 0 && (
        <p className="py-6 text-center text-sm text-muted-foreground">
          No data yet.
        </p>
      )}
      {rows.map((r) => (
        <div key={r.label}>
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="font-medium">{r.label}</span>
            <span className="text-muted-foreground">
              {formatCurrency(r.average_salary)} · {r.count} preds
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-primary/20">
            <div
              className="h-full rounded-full bg-primary"
              style={{ width: `${(r.average_salary / max) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .analytics()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-72 w-full" />
          <Skeleton className="h-72 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Insights derived from your prediction history.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total predictions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{data?.total_predictions ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average predicted salary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{formatCurrency(data?.average_salary)}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Salary trend</CardTitle>
            <CardDescription>Predicted salary across your history</CardDescription>
          </CardHeader>
          <CardContent>
            {data && data.salary_trend.length > 0 ? (
              <SalaryTrendChart data={data.salary_trend} />
            ) : (
              <p className="py-16 text-center text-sm text-muted-foreground">
                No predictions yet.
              </p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top skills</CardTitle>
            <CardDescription>Most common skills on your resumes</CardDescription>
          </CardHeader>
          <CardContent>
            {data && data.top_skills.length > 0 ? (
              <TopSkillsBarChart data={data.top_skills} />
            ) : (
              <p className="py-16 text-center text-sm text-muted-foreground">
                No resume skills yet.
              </p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Salary by location</CardTitle>
            <CardDescription>Average predicted salary per location</CardDescription>
          </CardHeader>
          <CardContent>
            <GroupBars data={(data?.salary_by_location ?? []) as GroupRow[]} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Salary by industry</CardTitle>
            <CardDescription>Average predicted salary per industry</CardDescription>
          </CardHeader>
          <CardContent>
            <GroupBars data={(data?.salary_by_industry ?? []) as GroupRow[]} />
          </CardContent>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>
              <BarChart3 className="mr-2 inline h-5 w-5" />
              Most missing skills
            </CardTitle>
            <CardDescription>
              Skills your profiles commonly lack versus target roles
            </CardDescription>
          </CardHeader>
          <CardContent>
            {data && data.most_missing_skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.most_missing_skills.map((s) => (
                  <span
                    key={s.skill}
                    className="rounded-full border bg-destructive/10 px-3 py-1 text-sm"
                  >
                    {s.skill} <span className="text-muted-foreground">×{s.count}</span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="py-8 text-center text-sm text-muted-foreground">
                No skill-gap data yet.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
