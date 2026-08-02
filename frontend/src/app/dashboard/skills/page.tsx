"use client";

import { useEffect, useState } from "react";
import { BookOpen, ExternalLink, Loader2, Search, X } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { LearningRoadmapResponse, SkillGapResponse, SkillOut } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";

const DEMO_JOB_DESCRIPTION = `We are looking for a Machine Learning Engineer to build production
ML systems. Requirements: Python, PyTorch, Machine Learning, Deep
Learning, AWS, Kubernetes, Docker, FastAPI, PostgreSQL, Spark, CI/CD,
LLM, RAG. Bonus: Terraform, Kafka, Snowflake.`;

export default function SkillsPage() {
  const [resumeSkills, setResumeSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState("");
  const [catalog, setCatalog] = useState<SkillOut[]>([]);
  const [jobDescription, setJobDescription] = useState(DEMO_JOB_DESCRIPTION);
  const [gap, setGap] = useState<SkillGapResponse | null>(null);
  const [roadmap, setRoadmap] = useState<LearningRoadmapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [dailyHours, setDailyHours] = useState(1);

  useEffect(() => {
    api
      .skillCatalog("", 200)
      .then(setCatalog)
      .catch(() => setCatalog([]));
  }, []);

  const addSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (!trimmed) return;
    if (resumeSkills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) return;
    setResumeSkills((prev) => [...prev, trimmed]);
    setSkillInput("");
  };

  const removeSkill = (skill: string) =>
    setResumeSkills((prev) => prev.filter((s) => s !== skill));

  const analyze = async () => {
    if (resumeSkills.length === 0) {
      toast.error("Add at least one skill from your resume.");
      return;
    }
    if (jobDescription.trim().length < 10) {
      toast.error("Job description is too short.");
      return;
    }
    setLoading(true);
    try {
      const gapRes = await api.skillGap(resumeSkills, jobDescription);
      setGap(gapRes);
      setRoadmap(null);
      if (gapRes.missing_skills.length > 0) {
        const roadmapRes = await api.roadmap(
          gapRes.missing_skills.map((m) => m.skill),
          dailyHours,
        );
        setRoadmap(roadmapRes);
      }
      toast.success(
        gapRes.missing_skills.length === 0
          ? "You match this role! No gaps detected."
          : `Found ${gapRes.missing_skills.length} missing skills`,
      );
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const catalogSuggestions = catalog
    .filter((c) => !resumeSkills.some((s) => s.toLowerCase() === c.name.toLowerCase()))
    .filter(
      (c) =>
        !skillInput ||
        c.name.toLowerCase().includes(skillInput.toLowerCase()),
    )
    .slice(0, 12);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Skill Gap &amp; Roadmap</h1>
        <p className="text-muted-foreground">
          Compare your skills against a target job and get a learning plan.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Analysis inputs</CardTitle>
            <CardDescription>
              Your skills and the target job description.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Your skills</Label>
              <div className="flex gap-2">
                <Input
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addSkill(skillInput);
                    }
                  }}
                  placeholder="Add skills from your resume"
                />
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => addSkill(skillInput)}
                >
                  Add
                </Button>
              </div>
              {resumeSkills.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {resumeSkills.map((s) => (
                    <Badge key={s} variant="secondary" className="gap-1 pr-1">
                      {s}
                      <button
                        type="button"
                        onClick={() => removeSkill(s)}
                        className="rounded-full p-0.5 hover:bg-muted-foreground/20"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
              {catalogSuggestions.length > 0 && (
                <div className="max-h-28 overflow-y-auto rounded-lg border p-2">
                  <p className="mb-1 px-1 text-xs font-medium text-muted-foreground">
                    Suggested skills
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {catalogSuggestions.map((c) => (
                      <button
                        key={c.name}
                        type="button"
                        onClick={() => addSkill(c.name)}
                        className="rounded-full border px-2 py-0.5 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
                      >
                        + {c.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="jobDescription">Target job description</Label>
              <Textarea
                id="jobDescription"
                rows={8}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste a job description here…"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="dailyHours">Study hours per day</Label>
              <Input
                id="dailyHours"
                type="number"
                min={0.25}
                max={12}
                step={0.25}
                value={dailyHours}
                onChange={(e) => setDailyHours(Number(e.target.value))}
              />
            </div>

            <Button onClick={analyze} className="w-full" disabled={loading}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              {loading ? "Analyzing…" : "Analyze skill gap"}
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-6">
          {gap ? (
            <Card>
              <CardHeader>
                <CardTitle>Skill match</CardTitle>
                <CardDescription>
                  Priority:{" "}
                  <Badge variant={gap.recommendation_priority === "high" ? "destructive" : gap.recommendation_priority === "medium" ? "warning" : "success"}>
                    {gap.recommendation_priority}
                  </Badge>
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {gap.matched_skills.length} matched ·{" "}
                      {gap.missing_skills.length} missing
                    </span>
                    <span className="font-semibold">
                      {Math.round(gap.skill_match_percentage)}%
                    </span>
                  </div>
                  <Progress value={gap.skill_match_percentage} />
                </div>

                {gap.matched_skills.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs font-medium text-muted-foreground">
                      Matched skills
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {gap.matched_skills.map((s) => (
                        <Badge key={s} variant="success">
                          {s}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {gap.missing_skills.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs font-medium text-muted-foreground">
                      Missing skills (prioritized)
                    </p>
                    <div className="space-y-2">
                      {gap.missing_skills.map((m) => (
                        <div
                          key={m.skill}
                          className="flex items-center justify-between rounded-lg border p-3 text-sm"
                        >
                          <div>
                            <p className="font-medium">{m.skill}</p>
                            <p className="text-xs text-muted-foreground">{m.category}</p>
                          </div>
                          <Badge variant={m.importance === "high" ? "destructive" : m.importance === "medium" ? "warning" : "secondary"}>
                            {m.importance}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card className="flex h-full min-h-[280px] items-center justify-center border-dashed">
              <CardContent className="text-center">
                <Search className="mx-auto h-8 w-8 text-muted-foreground" />
                <p className="mt-3 text-sm text-muted-foreground">
                  Run an analysis to see your match percentage and missing skills.
                </p>
              </CardContent>
            </Card>
          )}

          {roadmap && (
            <Card>
              <CardHeader>
                <CardTitle>
                  <BookOpen className="mr-2 inline h-5 w-5" />
                  Learning roadmap
                </CardTitle>
                <CardDescription>
                  {roadmap.total_estimated_hours.toFixed(0)} total hours · ~
                  {roadmap.estimated_weeks.toFixed(1)} weeks at {dailyHours}h/day
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {roadmap.steps.map((step, idx) => (
                  <div key={step.skill} className="rounded-lg border p-4">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">
                        <span className="mr-2 text-muted-foreground">
                          {idx + 1}.
                        </span>
                        {step.skill}
                      </p>
                      <Badge variant="secondary">
                        ~{step.estimated_hours.toFixed(0)}h
                      </Badge>
                    </div>
                    {step.resources.length > 0 && (
                      <>
                        <Separator className="my-3" />
                        <div className="space-y-2">
                          {step.resources.map((r) => (
                            <a
                              key={r.id}
                              href={r.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center justify-between rounded-md border p-2 text-sm hover:bg-accent"
                            >
                              <div className="min-w-0">
                                <p className="truncate font-medium">{r.title}</p>
                                <p className="text-xs text-muted-foreground">
                                  {r.provider} · {r.resource_type} · {r.difficulty}
                                </p>
                              </div>
                              <ExternalLink className="ml-2 h-4 w-4 shrink-0 text-muted-foreground" />
                            </a>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
