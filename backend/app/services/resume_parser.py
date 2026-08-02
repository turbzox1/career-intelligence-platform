"""Resume text extraction and structured parsing.

Extracts the raw text from PDF / DOCX / TXT uploads, then produces a
structured representation (contact info, experience, education, skills,
years of experience) using regex heuristics with optional spaCy enrichment.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

from app.core.exceptions import ValidationError

logger = logging.getLogger("app.resume_parser")

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {"pdf": "pdf", "docx": "docx", "txt": "txt"}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
YEARS_RE = re.compile(
    r"(?P<years>\d{1,2})\+?\s*(?:years?|yrs?|y)\s*(?:of\s*)?(?:professional\s*)?(?:work\s*)?experience",
    re.IGNORECASE,
)
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)

SECTION_HEADERS = {
    "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
    "education": ["education", "academic background", "academic history", "qualifications"],
    "projects": ["projects", "personal projects", "key projects", "selected projects"],
    "certifications": ["certifications", "certificates", "licenses", "licensures"],
    "technologies": ["technologies", "technical skills", "tools", "skills & tools", "tech stack"],
    "languages": ["languages", "spoken languages"],
}

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*\d{4})"
    r"[\s\-–to]*(?P<end>(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s-]*\d{4}|present|current|now)?",
    re.IGNORECASE,
)


def extract_text_from_bytes(content: bytes, filename: str, file_type: str) -> str:
    """Extract plain text from an uploaded document."""
    if len(content) > MAX_FILE_BYTES:
        raise ValidationError("File exceeds the 5 MB limit")
    if file_type not in ALLOWED_TYPES:
        raise ValidationError(f"Unsupported file type: {file_type}")

    if file_type == "pdf":
        return _extract_pdf(content)
    if file_type == "docx":
        return _extract_docx(content)
    return _extract_txt(content)


def detect_file_type(filename: str) -> str:
    """Infer the file type from the filename extension."""
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_TYPES:
        raise ValidationError(f"Unsupported file extension: .{ext}")
    return ALLOWED_TYPES[ext]


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ValidationError("PDF support is not installed") from exc
    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _extract_docx(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover
        raise ValidationError("DOCX support is not installed") from exc
    doc = Document(BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.append(cell.text)
    return "\n".join(p for p in paragraphs if p).strip()


def _extract_txt(content: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return content.decode(encoding).strip()
        except (UnicodeDecodeError, LookupError):
            continue
    return content.decode("utf-8", errors="ignore").strip()


def parse_resume_text(text: str) -> dict:
    """Produce a structured representation of a resume from raw text."""
    if not text:
        raise ValidationError("Resume contains no extractable text")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    email = _first_match(lines, EMAIL_RE)
    phone = _first_match(lines, PHONE_RE, ignore=email)
    name = _guess_name(lines, email=email)
    years = _extract_years_experience(text)
    sections = _split_sections(text, lines)

    experience_entries = _parse_experience_entries(sections.get("experience", []))
    education_entries = _parse_list_section(sections.get("education", []), max_items=8)
    projects = _parse_list_section(sections.get("projects", []), max_items=10)
    certifications = _parse_list_section(sections.get("certifications", []), max_items=10)
    technologies = _parse_list_section(sections.get("technologies", []), max_items=40)
    languages = _parse_list_section(sections.get("languages", []), max_items=10)

    if years == 0 and experience_entries:
        years = _infer_years_from_dates(experience_entries)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": _guess_summary(text),
        "experience": experience_entries,
        "education": education_entries,
        "projects": projects,
        "certifications": certifications,
        "technologies": technologies,
        "languages": languages,
        "skills": technologies,
        "years_of_experience": years,
    }


def _first_match(lines: list[str], pattern: re.Pattern, ignore: str | None = None) -> str | None:
    for line in lines[:60]:
        match = pattern.search(line)
        if match:
            candidate = match.group(0)
            if ignore and candidate.lower() in ignore.lower():
                continue
            return candidate
    return None


def _guess_name(lines: list[str], *, email: str | None) -> str | None:
    """Heuristic: the first line that is short, has no URL/email/phone, and is title case."""
    skip_tokens = {"resume", "cv", "curriculum", "vitae", "profile", "contact"}
    for line in lines[:10]:
        lower = line.lower()
        if email and email in line:
            continue
        if URL_RE.search(line) or EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        if len(line) > 80 or len(line.split()) < 2 or len(line.split()) > 6:
            continue
        words = line.split()
        if all(w.istitle() or w.isupper() for w in words) and not any(t in lower for t in skip_tokens):
            return " ".join(w.capitalize() if w.isupper() else w for w in words[:3])
    return None


def _extract_years_experience(text: str) -> float:
    match = YEARS_RE.search(text)
    if match:
        return float(match.group("years"))
    # "X+ years" without the word experience
    bare = re.search(r"(\d{1,2})\+?\s*(?:years?|yrs?)", text, re.IGNORECASE)
    if bare:
        return float(bare.group(1))
    return 0.0


def _split_sections(text: str, lines: list[str]) -> dict[str, list[str]]:
    """Split the resume into sections using header heuristics."""
    sections: dict[str, list[str]] = {}
    current: str | None = None

    def header_for(line: str) -> str | None:
        normalized = re.sub(r"[:\s]+", " ", line).strip().lower()
        for section, headers in SECTION_HEADERS.items():
            if normalized in headers or any(normalized == h or normalized.startswith(h) for h in headers):
                return section
        return None

    for line in lines:
        section = header_for(line)
        if section:
            current = section
            sections.setdefault(section, [])
            continue
        if current:
            sections[current].append(line)

    # Fallback: treat lines after a "Skills" header generically.
    if "skills" not in sections:
        skills = _extract_skills_from_lines(lines)
        if skills:
            sections["technologies"] = skills
    return sections


def _parse_list_section(lines: list[str], *, max_items: int) -> list[str]:
    items: list[str] = []
    for line in lines:
        cleaned = re.sub(r"^\s*[-•*·]+\s*", "", line).strip()
        if not cleaned or cleaned.lower() in {"skills", "projects", "education"}:
            continue
        for part in re.split(r"[,\u2022;]", cleaned):
            part = part.strip(" \t-•")
            if 2 <= len(part) <= 200 and part not in items:
                items.append(part)
        if len(items) >= max_items * 2:
            break
    return items[:max_items]


def _parse_experience_entries(lines: list[str]) -> list[dict]:
    """Build a list of experience entries with title, company and date range."""
    entries: list[dict] = []
    current: dict | None = None
    for line in lines:
        if DATE_RANGE_RE.search(line):
            current = {"title": line, "duration": line}
            entries.append(current)
            continue
        if current is not None and len(entries) <= 30:
            current.setdefault("details", []).append(line)
    return entries


def _infer_years_from_dates(entries: list[dict]) -> float:
    """Sum date ranges across experience entries to estimate years of experience."""
    total_days = 0
    for entry in entries:
        duration = entry.get("duration", "")
        match = DATE_RANGE_RE.search(duration)
        if not match:
            continue
        start = _parse_month_year(match.group("start"))
        end_raw = match.group("end") or ""
        end = datetime.now() if end_raw.lower() in {"present", "current", "now", ""} else _parse_month_year(end_raw)
        if start and end and end >= start:
            total_days += (end - start).days
    return round(total_days / 365.0, 1)


def _parse_month_year(value: str) -> datetime | None:
    match = re.match(r"([a-z]+)[\s-]*(\d{4})", value, re.IGNORECASE)
    if not match:
        return None
    month = MONTHS.get(match.group(1)[:3].lower())
    year = int(match.group(2))
    if month is None:
        month = 1
    return datetime(year, month, 1)


def _guess_summary(text: str) -> str | None:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in lines[2:20]:
        if 40 <= len(line) <= 600 and line.count(" ") >= 8:
            return line
    return None


def _extract_skills_from_lines(lines: list[str]) -> list[str]:
    """Naive skill-ish extraction used only as a fallback."""
    keywords = {
        "python",
        "java",
        "javascript",
        "sql",
        "aws",
        "react",
        "docker",
        "kubernetes",
        "machine learning",
        "data science",
        "git",
        "node.js",
        "typescript",
        "golang",
        "excel",
        "power bi",
        "tableau",
        "tensorflow",
        "pytorch",
        "fastapi",
        "django",
    }
    found: list[str] = []
    for line in lines:
        lower = line.lower()
        for kw in keywords:
            if kw in lower and kw not in found:
                found.append(kw)
    return found
