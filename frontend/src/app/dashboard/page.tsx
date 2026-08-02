"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, DollarSign, FileText, LineChart, Target } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { AnalyticsResponse, Page, PredictionHistoryItem, ResumeListItem } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { SalaryTrendChart } from "@/components/charts";

export default function DashboardPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [history, setHistory] = useState<Page<PredictionHistoryItem> | null>(null);
  const [resumes, setResumes] = useState<Page<ResumeListItem> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      api.analytics(),
      api.predictionHistory(1, 5),
      api.listResumes(1, 3),
    ])
      .then(([a, h, r]) => {
        if (a.status === "fulfilled") setAnalytics(a.value);
        if (h.status === "fulfilled") setHistory(h.value);
        if (r.status === "fulfilled") setResumes(r.value);
      })
      .finally(() => setLoading(false));
  }, []);

  const firstName = (user?.full_name ?? "there").split(" ")[0];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Welcome back, {firstName}
        </h1>
        <p className="text-muted-foreground">
          Here is the latest on your career intelligence.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total predictions</CardTitle>
            <LineChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">
                {analytics?.total_predictions ?? history?.total ?? 0}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average salary</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <div className="text-2xl font-bold">
                {formatCurrency(analytics?.average_salary)}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resumes on file</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{resumes?.total ?? 0}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Skill match</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">
                {analytics ? "—" : "—"}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Salary trend</CardTitle>
            <CardDescription>Your predicted salary over time</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-[280px] w-full" />
            ) : analytics && analytics.salary_trend.length > 0 ? (
              <SalaryTrendChart data={analytics.salary_trend} />
            ) : (
              <p className="py-16 text-center text-sm text-muted-foreground">
                No predictions yet. Run your first one from the{" "}
                <Link href="/dashboard/predict" className="text-primary underline-offset-4 hover:underline">
                  salary predictor
                </Link>
                .
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent predictions</CardTitle>
              <CardDescription>Your latest salary estimates</CardDescription>
            </div>
            <Link href="/dashboard/predict">
              <Button variant="outline" size="sm">
                New prediction <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="space-y-3">
            {loading ? (
              <div className="space-y-3">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : history && history.items.length > 0 ? (
              history.items.map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div>
                    <p className="font-medium">{formatCurrency(p.predicted_salary)}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(p.created_at)} · {p.model_name}
                    </p>
                  </div>
                  {p.lower_bound != null && p.upper_bound != null && (
                    <Badge variant="secondary">
                      {formatCurrency(p.lower_bound)} – {formatCurrency(p.upper_bound)}
                    </Badge>
                  )}
                </div>
              ))
            ) : (
              <p className="py-8 text-center text-sm text-muted-foreground">
                No predictions yet.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
