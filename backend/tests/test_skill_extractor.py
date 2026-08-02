"""Unit tests for the skill extractor and master skill catalog."""

from __future__ import annotations

from app.data.skills_master import (
    SKILL_CATALOG,
    all_skills,
    get_canonical_skill,
    normalize_skill_token,
)
from app.services.skill_extractor import SkillExtractor


class TestNormalization:
    def test_aliases_resolve_to_canonical(self) -> None:
        assert get_canonical_skill("Python3")["name"] == "Python"
        assert get_canonical_skill("PYTHON")["name"] == "Python"
        assert get_canonical_skill("machine learning")["name"] == "Machine Learning"
        assert get_canonical_skill("golang")["name"] == "Go"

    def test_case_insensitive(self) -> None:
        assert get_canonical_skill("python")["name"] == "Python"
        assert get_canonical_skill("AWS")["name"] == "AWS"

    def test_normalize_token(self) -> None:
        assert normalize_skill_token("  Python  3 ") == "python 3"

    def test_unknown_skill(self) -> None:
        assert get_canonical_skill("quantum-nonsense-xyz") is None

    def test_catalog_non_empty(self) -> None:
        assert len(SKILL_CATALOG) > 50
        assert len(all_skills()) == len(SKILL_CATALOG)


class TestSkillExtractor:
    def setup_method(self) -> None:
        self.extractor = SkillExtractor()

    def test_extract_from_skill_line(self) -> None:
        result = self.extractor.extract("Skills: Python, AWS, Docker, Kubernetes")
        names = {r["name"] for r in result}
        assert "Python" in names
        assert "AWS" in names

    def test_extract_from_prose(self) -> None:
        result = self.extractor.extract("Experience with machine learning models and deep learning using PyTorch.")
        names = {r["name"] for r in result}
        assert "Machine Learning" in names
        assert "Deep Learning" in names
        assert "PyTorch" in names

    def test_no_duplicates(self) -> None:
        result = self.extractor.extract("Python, Python3, PYTHON, python")
        assert len(result) == 1
        assert result[0]["name"] == "Python"

    def test_empty_text(self) -> None:
        assert self.extractor.extract("") == []
        assert self.extractor.extract(None) == []

    def test_confidence_present(self) -> None:
        result = self.extractor.extract("Skills: Python")
        assert result[0]["confidence"] > 0
        assert result[0]["source"] == "rule"
