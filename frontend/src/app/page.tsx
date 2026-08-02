import Link from "next/link";
import {
  BarChart3,
  Brain,
  Briefcase,
  FileText,
  LineChart,
  Sparkles,
  Target,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: LineChart,
    title: "AI Salary Predictions",
    description:
      "Machine-learning models trained on structured labour-market data with confidence intervals and model transparency.",
  },
  {
    icon: Brain,
    title: "Explainable Insights",
    description:
      "SHAP-based explanations show exactly which factors drive your predicted compensation.",
  },
  {
    icon: FileText,
    title: "Resume Parsing",
    description:
      "Upload PDF, DOCX or TXT resumes and get structured skill extraction in seconds.",
  },
  {
    icon: Target,
    title: "Skill Gap & Roadmap",
    description:
      "Compare your profile against target roles and get a curated, prioritized learning roadmap.",
  },
  {
    icon: Briefcase,
    title: "Job Matching",
    description:
      "Semantic matching surfaces roles aligned with your skills and experience level.",
  },
  {
    icon: BarChart3,
    title: "Personal Analytics",
    description:
      "Track salary trends by location, industry and experience over time.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-2 font-semibold">
            <Sparkles className="h-5 w-5 text-primary" />
            Career Intelligence Platform
          </div>
          <nav className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost">Sign in</Button>
            </Link>
            <Link href="/signup">
              <Button>Get started</Button>
            </Link>
          </nav>
        </div>
      </header>

      <section className="bg-muted/30">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-20 md:grid-cols-2 md:items-center">
          <div>
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
              Know your worth.
              <br />
              Plan your growth.
            </h1>
            <p className="mt-4 text-lg text-muted-foreground">
              The Career Intelligence Platform combines ML-driven salary
              prediction, resume analysis, skill-gap detection and personalized
              learning roadmaps — so you can make data-backed career decisions.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/signup">
                <Button size="lg">Try it free</Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline">
                  Sign in
                </Button>
              </Link>
            </div>
          </div>
          <Card className="p-6">
            <CardContent className="p-0">
              <div className="flex items-center justify-between border-b pb-4">
                <div>
                  <p className="text-sm text-muted-foreground">Predicted salary</p>
                  <p className="text-3xl font-bold">$336,875</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">San Francisco, CA</p>
                  <p className="text-sm text-muted-foreground">Senior ML Engineer</p>
                </div>
              </div>
              <div className="mt-4 space-y-3">
                {[
                  { label: "Years of experience", value: "5+ years" },
                  { label: "Degree level", value: "Master's" },
                  { label: "Top skills", value: "Python, PyTorch, MLOps" },
                  { label: "Confidence", value: "High (R² = 0.94)" },
                ].map((row) => (
                  <div key={row.label} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{row.label}</span>
                    <span className="font-medium">{row.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-center text-3xl font-bold">
          Everything you need to steer your career
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <Card key={f.title} className="p-6">
              <CardContent className="p-0">
                <f.icon className="h-8 w-8 text-primary" />
                <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{f.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <footer className="border-t">
        <div className="mx-auto max-w-6xl px-4 py-8 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Career Intelligence Platform · Built for
          data-driven career growth
        </div>
      </footer>
    </div>
  );
}
