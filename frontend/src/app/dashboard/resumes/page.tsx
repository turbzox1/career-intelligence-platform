"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { FileText, Loader2, Trash2, Upload } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { ParsedResumeData, ResumeListItem, ResumeUploadResponse } from "@/types";
import { formatDate, formatCurrency } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";

const ACCEPTED = ".pdf,.docx,.doc,.txt";

function bytesToReadable(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ResumesPage() {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [selected, setSelected] = useState<ResumeUploadResponse["resume"] | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    try {
      const res = await api.listResumes(1, 50);
      setResumes(res.items);
      setTotal(res.total);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load resumes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const upload = async (file: File) => {
    if (!file) return;
    if (!/\.(pdf|docx?|txt)$/i.test(file.name)) {
      toast.error("Only PDF, DOCX and TXT files are supported.");
      return;
    }
    setUploading(true);
    try {
      const res = await api.uploadResume(file);
      toast.success(`Parsed "${res.resume.filename}" — found ${res.skills.length} skills`);
      await load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const openDetail = async (id: number) => {
    try {
      const resume = await api.getResume(id);
      setSelected(resume);
      setDetailOpen(true);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load resume");
    }
  };

  const remove = async (id: number) => {
    try {
      await api.deleteResume(id);
      toast.success("Resume deleted");
      await load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const parsed = selected?.parsed_data as ParsedResumeData | undefined;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Resumes</h1>
        <p className="text-muted-foreground">
          Upload a resume to extract structured skills, experience and more.
        </p>
      </div>

      <div
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
          dragging ? "border-primary bg-primary/5" : "border-border"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files?.[0];
          if (file) void upload(file);
        }}
      >
        <FileText className="h-10 w-10 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold">
          Drop your resume here
        </h3>
        <p className="mt-1 text-sm text-muted-foreground">
          PDF, DOCX or TXT · parsed locally then stored securely
        </p>
        <div className="mt-5 flex gap-3">
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            {uploading ? "Parsing…" : "Choose file"}
          </Button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void upload(file);
            e.target.value = "";
          }}
        />
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold">
          Your resumes <span className="text-muted-foreground">({total})</span>
        </h2>
        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        ) : resumes.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="py-10 text-center text-sm text-muted-foreground">
              No resumes uploaded yet.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {resumes.map((r) => (
              <Card key={r.id} className="flex flex-col">
                <CardContent className="flex flex-1 flex-col p-5">
                  <div className="flex items-start gap-3">
                    <FileText className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <button
                        className="truncate text-left text-sm font-medium hover:underline"
                        onClick={() => void openDetail(r.id)}
                        title={r.filename}
                      >
                        {r.filename}
                      </button>
                      <p className="text-xs text-muted-foreground">
                        {bytesToReadable(r.file_size_bytes)} ·{" "}
                        {formatDate(r.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    {r.parse_status === "completed" ? (
                      <Badge variant="success">Parsed</Badge>
                    ) : r.parse_status === "failed" ? (
                      <Badge variant="destructive">Failed</Badge>
                    ) : (
                      <Badge variant="warning">Pending</Badge>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="ml-auto"
                      onClick={() => void remove(r.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selected?.filename ?? "Resume"}</DialogTitle>
            <DialogDescription>
              Extracted structure from your parsed resume.
            </DialogDescription>
          </DialogHeader>
          {selected ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-xs text-muted-foreground">Name</p>
                  <p className="font-medium">{parsed?.name ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Email</p>
                  <p className="truncate font-medium">{parsed?.email ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Phone</p>
                  <p className="font-medium">{parsed?.phone ?? "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Years experience</p>
                  <p className="font-medium">{parsed?.years_of_experience ?? 0}</p>
                </div>
              </div>

              {parsed?.summary ? (
                <div>
                  <p className="mb-1 text-xs font-medium text-muted-foreground">Summary</p>
                  <p className="text-sm">{parsed.summary}</p>
                </div>
              ) : null}

              {parsed?.skills && parsed.skills.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {parsed.skills.map((s) => (
                      <Badge key={s} variant="secondary">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {parsed?.experience && parsed.experience.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">
                    Experience
                  </p>
                  <div className="space-y-3">
                    {parsed.experience.map((exp, i) => (
                      <div key={i} className="rounded-lg border p-3 text-sm">
                        <p className="font-medium">
                          {String(exp.role ?? exp.title ?? "")}
                          {exp.company ? ` · ${String(exp.company)}` : ""}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {exp.start_date ? `${String(exp.start_date)}` : ""}
                          {exp.end_date ? ` – ${String(exp.end_date)}` : ""}
                        </p>
                        {exp.duration_months ? (
                          <p className="text-xs text-muted-foreground">
                            {String(exp.duration_months)} months
                          </p>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {parsed?.education && parsed.education.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">Education</p>
                  <div className="space-y-2">
                    {parsed.education.map((edu, i) => (
                      <div key={i} className="rounded-lg border p-3 text-sm">
                        <p className="font-medium">{String(edu.institution ?? "")}</p>
                        <p className="text-xs text-muted-foreground">
                          {String(edu.degree ?? "")}
                          {edu.field ? ` in ${String(edu.field)}` : ""}
                          {edu.year ? ` · ${String(edu.year)}` : ""}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {parsed?.certifications && parsed.certifications.length > 0 && (
                <div>
                  <p className="mb-1 text-xs font-medium text-muted-foreground">
                    Certifications
                  </p>
                  <ul className="list-inside list-disc text-sm">
                    {parsed.certifications.map((c) => (
                      <li key={c}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}

              <p className="text-xs text-muted-foreground">
                Estimated market value:{" "}
                {formatCurrency(Number(parsed?.years_of_experience ?? 0) * 8000)}
              </p>
            </div>
          ) : (
            <Skeleton className="h-40 w-full" />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
