"use client";

import { useState } from "react";
import { Loader2, Sparkles, X } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { SalaryPredictionRequest, SalaryPredictionResponse } from "@/types";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { WaterfallChart } from "@/components/charts";
import { Separator } from "@/components/ui/separator";

const LOCATIONS = [
  { value: "remote", label: "Remote" },
  { value: "san_francisco", label: "San Francisco, CA" },
  { value: "new_york", label: "New York, NY" },
  { value: "seattle", label: "Seattle, WA" },
  { value: "austin", label: "Austin, TX" },
  { value: "london", label: "London, UK" },
  { value: "bengaluru", label: "Bengaluru, IN" },
  { value: "berlin", label: "Berlin, DE" },
  { value: "toronto", label: "Toronto, CA" },
  { value: "singapore", label: "Singapore" },
];

const INDUSTRIES = [
  { value: "technology", label: "Technology" },
  { value: "finance", label: "Finance" },
  { value: "healthcare", label: "Healthcare" },
  { value: "retail", label: "Retail" },
  { value: "manufacturing", label: "Manufacturing" },
  { value: "consulting", label: "Consulting" },
  { value: "education", label: "Education" },
  { value: "media", label: "Media" },
  { value: "energy", label: "Energy" },
];

const COMPANY_SIZES = [
  { value: "startup", label: "Startup (1–50)" },
  { value: "small", label: "Small (51–200)" },
  { value: "mid", label: "Mid (201–1,000)" },
  { value: "large", label: "Large (1,001–10,000)" },
  { value: "enterprise", label: "Enterprise (10,000+)" },
];

const DEGREE_LEVELS = [
  { value: "none", label: "No degree" },
  { value: "associate", label: "Associate" },
  { value: "bachelor", label: "Bachelor's" },
  { value: "master", label: "Master's" },
  { value: "phd", label: "PhD" },
];

const TITLES = [
  { value: "software_engineer", label: "Software Engineer" },
  { value: "data_scientist", label: "Data Scientist" },
  { value: "ml_engineer", label: "ML Engineer" },
  { value: "devops_engineer", label: "DevOps Engineer" },
  { value: "product_manager", label: "Product Manager" },
  { value: "data_engineer", label: "Data Engineer" },
  { value: "backend_engineer", label: "Backend Engineer" },
  { value: "frontend_engineer", label: "Frontend Engineer" },
  { value: "fullstack_engineer", label: "Full-Stack Engineer" },
  { value: "site_reliability_engineer", label: "Site Reliability Engineer" },
];

const SUGGESTED_SKILLS = [
  "Python",
  "Java",
  "TypeScript",
  "React",
  "AWS",
  "Kubernetes",
  "Docker",
  "TensorFlow",
  "PyTorch",
  "Machine Learning",
  "Deep Learning",
  "NLP",
  "Spark",
  "Kafka",
  "PostgreSQL",
  "Redis",
  "LLM",
  "RAG",
  "FastAPI",
  "Terraform",
  "Golang",
  "Rust",
  "Snowflake",
  "Airflow",
];

export default function PredictPage() {
  const [form, setForm] = useState<SalaryPredictionRequest>({
    years_experience: 3,
    degree_level: "bachelor",
    location: "remote",
    industry: "technology",
    company_size: "mid",
    title: "software_engineer",
    skills: ["Python", "Machine Learning"],
  });
  const [skillInput, setSkillInput] = useState("");
  const [result, setResult] = useState<SalaryPredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const set = <K extends keyof SalaryPredictionRequest>(
    key: K,
    value: SalaryPredictionRequest[K],
  ) => setForm((f) => ({ ...f, [key]: value }));

  const addSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (!trimmed) return;
    if (form.skills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) return;
    set("skills", [...form.skills, trimmed]);
    setSkillInput("");
  };

  const removeSkill = (skill: string) =>
    set("skills", form.skills.filter((s) => s !== skill));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await api.predict(form);
      setResult(res);
      toast.success("Prediction complete");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Prediction failed. Is the backend running?",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Salary Predictor</h1>
        <p className="text-muted-foreground">
          Get an explainable, ML-driven estimate of your market salary.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Your profile</CardTitle>
            <CardDescription>
              Describe the role and your background for the model.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Job title</Label>
                  <Select
                    value={form.title}
                    onValueChange={(v) => set("title", v)}
                  >
                    <SelectTrigger id="title">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {TITLES.map((t) => (
                        <SelectItem key={t.value} value={t.value}>
                          {t.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="experience">Years of experience</Label>
                  <Input
                    id="experience"
                    type="number"
                    min={0}
                    max={60}
                    step={0.5}
                    value={form.years_experience}
                    onChange={(e) => set("years_experience", Number(e.target.value))}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="degree">Degree level</Label>
                  <Select
                    value={form.degree_level}
                    onValueChange={(v) => set("degree_level", v)}
                  >
                    <SelectTrigger id="degree">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {DEGREE_LEVELS.map((d) => (
                        <SelectItem key={d.value} value={d.value}>
                          {d.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="companySize">Company size</Label>
                  <Select
                    value={form.company_size}
                    onValueChange={(v) => set("company_size", v)}
                  >
                    <SelectTrigger id="companySize">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {COMPANY_SIZES.map((c) => (
                        <SelectItem key={c.value} value={c.value}>
                          {c.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Select
                    value={form.location}
                    onValueChange={(v) => set("location", v)}
                  >
                    <SelectTrigger id="location">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {LOCATIONS.map((l) => (
                        <SelectItem key={l.value} value={l.value}>
                          {l.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="industry">Industry</Label>
                  <Select
                    value={form.industry}
                    onValueChange={(v) => set("industry", v)}
                  >
                    <SelectTrigger id="industry">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {INDUSTRIES.map((i) => (
                        <SelectItem key={i.value} value={i.value}>
                          {i.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="skills">Skills</Label>
                <div className="flex gap-2">
                  <Input
                    id="skills"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addSkill(skillInput);
                      }
                    }}
                    placeholder="Type a skill and press Enter"
                  />
                  <Button type="button" variant="secondary" onClick={() => addSkill(skillInput)}>
                    Add
                  </Button>
                </div>
                {form.skills.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-2">
                    {form.skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="gap-1 pr-1">
                        {skill}
                        <button
                          type="button"
                          onClick={() => removeSkill(skill)}
                          className="rounded-full p-0.5 hover:bg-muted-foreground/20"
                          aria-label={`Remove ${skill}`}
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {SUGGESTED_SKILLS.filter(
                    (s) => !form.skills.some((f) => f.toLowerCase() === s.toLowerCase()),
                  )
                    .slice(0, 10)
                    .map((s) => (
                      <button
                        key={s}
                        type="button"
                        onClick={() => addSkill(s)}
                        className="rounded-full border px-2 py-0.5 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
                      >
                        + {s}
                      </button>
                    ))}
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                {loading ? "Analyzing…" : "Predict salary"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-6">
          {result ? (
            <>
              <Card className="border-primary">
                <CardHeader>
                  <CardDescription>Predicted annual salary</CardDescription>
                  <CardTitle className="text-4xl font-bold">
                    {formatCurrency(result.predicted_salary)}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Confidence range</p>
                      <p className="text-sm font-medium">
                        {formatCurrency(result.lower_bound)} –{" "}
                        {formatCurrency(result.upper_bound)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Confidence</p>
                      <p className="text-sm font-medium">
                        {result.confidence != null
                          ? `${(result.confidence * 100).toFixed(0)}%`
                          : "—"}
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Model</p>
                      <p className="text-sm font-medium">{result.model_name}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Version</p>
                      <p className="text-sm font-medium">{result.model_version}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {result.explanation?.features.length ? (
                <Card>
                  <CardHeader>
                    <CardTitle>Why this number?</CardTitle>
                    <CardDescription>
                      SHAP contributions — green increases salary, red decreases.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <WaterfallChart
                      baseValue={result.explanation.base_value}
                      predictedValue={result.explanation.predicted_value}
                      contributions={result.explanation.features.map((f) => ({
                        feature: f.feature,
                        contribution: f.contribution,
                      }))}
                    />
                    <Separator className="my-4" />
                    <ul className="space-y-2">
                      {result.explanation.features
                        .slice()
                        .sort(
                          (a, b) =>
                            Math.abs(b.contribution) - Math.abs(a.contribution),
                        )
                        .slice(0, 6)
                        .map((f) => (
                          <li key={f.feature} className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">{f.feature}</span>
                            <span
                              className={
                                f.contribution >= 0
                                  ? "font-medium text-emerald-600"
                                  : "font-medium text-red-500"
                              }
                            >
                              {f.contribution >= 0 ? "+" : ""}
                              {formatCurrency(f.contribution)}
                            </span>
                          </li>
                        ))}
                    </ul>
                  </CardContent>
                </Card>
              ) : null}
            </>
          ) : (
            <Card className="flex h-full min-h-[300px] items-center justify-center border-dashed">
              <CardContent className="text-center">
                <Sparkles className="mx-auto h-8 w-8 text-muted-foreground" />
                <p className="mt-3 text-sm text-muted-foreground">
                  Fill in the form and run a prediction to see your salary
                  estimate and what drives it.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
