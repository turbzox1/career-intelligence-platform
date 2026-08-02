"""Unit tests for the resume parser."""

from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.services.resume_parser import (
    detect_file_type,
    extract_text_from_bytes,
    parse_resume_text,
)

FULL_RESUME = """\
John Q. Smith
john.smith@email.com
+1 (415) 555-0199
www.johnsmith.dev

Senior Data Scientist with 10+ years of experience in Machine Learning and NLP.

EXPERIENCE
Senior Data Scientist, Acme Corp, San Francisco
Mar 2018 - Present
Led ML platform with Python, TensorFlow, AWS.

Data Scientist, Globex, New York
Jun 2014 - Feb 2018
Built predictive models.

EDUCATION
MSc Computer Science, Stanford University, 2013

SKILLS
Python, TensorFlow, AWS, SQL, Docker

PROJECTS
Recommendation engine using collaborative filtering.

CERTIFICATIONS
AWS Solutions Architect

LANGUAGES
English, French
"""


class TestFileType:
    def test_detect_pdf(self) -> None:
        assert detect_file_type("file.pdf") == "pdf"

    def test_detect_docx(self) -> None:
        assert detect_file_type("file.DOCX") == "docx"

    def test_detect_txt(self) -> None:
        assert detect_file_type("file.txt") == "txt"

    def test_reject_unknown(self) -> None:
        try:
            detect_file_type("file.py")
            raise AssertionError("should raise ValidationError")
        except ValidationError:
            pass


class TestTextExtraction:
    def test_txt_roundtrip(self) -> None:
        text = "hello world\nsecond line"
        assert extract_text_from_bytes(text.encode(), "f.txt", "txt") == text

    def test_oversize_rejected(self) -> None:
        with pytest.raises(ValidationError):
            extract_text_from_bytes(b"x" * (5 * 1024 * 1024 + 1), "f.txt", "txt")

    def test_unsupported_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            extract_text_from_bytes(b"x", "f.bin", "bin")


class TestParsing:
    def test_full_parse(self) -> None:
        result = parse_resume_text(FULL_RESUME)
        assert result["name"] is not None and "Smith" in result["name"]
        assert result["email"] == "john.smith@email.com"
        assert result["phone"]
        assert result["years_of_experience"] >= 10
        assert result["experience"]
        assert any("Stanford" in e for e in result["education"] if isinstance(e, str)) or result["education"]
        assert "English" in result["languages"]

    def test_empty_text_rejected(self) -> None:
        with pytest.raises(ValidationError):
            parse_resume_text("")

    def test_years_regex(self) -> None:
        result = parse_resume_text("Backend Engineer with 5+ years of experience\nSkills: Python")
        assert result["years_of_experience"] == 5.0

    def test_name_guessing(self) -> None:
        result = parse_resume_text("Maria Lopez\nmaria@x.com\nPython developer")
        assert result["name"] is not None
