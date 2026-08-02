"""Unit tests for the shared feature-engineering module."""

from __future__ import annotations

import numpy as np
import pytest
from career_ml.features import (
    COMPANY_SIZE_ORDINAL,
    DEGREE_ORDINAL,
    FEATURE_SPEC,
    SKILL_SALARY_DELTA,
    build_feature_vector,
    encode_ordinal,
    feature_names,
    onehot_encode,
    skill_delta,
)


class TestEncoding:
    def test_ordinal_mappings(self) -> None:
        assert DEGREE_ORDINAL["none"] == 0
        assert DEGREE_ORDINAL["phd"] == 4
        assert COMPANY_SIZE_ORDINAL["startup"] == 0
        assert COMPANY_SIZE_ORDINAL["enterprise"] == 4

    def test_encode_ordinal_unknown(self) -> None:
        degree, company = encode_ordinal("unknown-degree", "unknown-size")
        assert degree == 0
        assert company == 2

    def test_onehot_encode_known(self) -> None:
        vector = onehot_encode("remote", ["remote", "new_york"])
        assert vector == [1.0, 0.0]

    def test_onehot_encode_unknown(self) -> None:
        vector = onehot_encode("atlantis", ["remote", "new_york"])
        assert vector == [0.0, 0.0]


class TestFeatureVector:
    def test_vector_shape_and_length(self) -> None:
        vector = build_feature_vector(
            years_experience=5.0,
            degree="master",
            location="remote",
            industry="technology",
            company_size="mid",
            title="ml_engineer",
            skills=["Python", "AWS"],
        )
        assert isinstance(vector, np.ndarray)
        assert vector.shape == (FEATURE_SPEC.expected_length,)
        assert len(feature_names()) == FEATURE_SPEC.expected_length

    def test_vector_reproducible(self) -> None:
        kwargs = dict(
            years_experience=2.0,
            degree="bachelor",
            location="london",
            industry="finance",
            company_size="large",
            title="data_scientist",
            skills=["Python"],
        )
        assert np.array_equal(build_feature_vector(**kwargs), build_feature_vector(**kwargs))

    def test_skill_count_reflected(self) -> None:
        base = dict(
            years_experience=1.0,
            degree="bachelor",
            location="remote",
            industry="technology",
            company_size="mid",
            title="software_engineer",
        )
        a = build_feature_vector(skills=[], **base)
        b = build_feature_vector(skills=["Python", "AWS", "Docker"], **base)
        # index 1 is skill_count
        assert a[1] == 0.0
        assert b[1] == 3.0


class TestSkillDelta:
    def test_known_skills_sum(self) -> None:
        assert skill_delta(["Python", "AWS"]) == pytest.approx(SKILL_SALARY_DELTA["Python"] + SKILL_SALARY_DELTA["AWS"])

    def test_unknown_skills_ignored(self) -> None:
        assert skill_delta(["NotARealSkill"]) == 0.0

    def test_empty_list(self) -> None:
        assert skill_delta([]) == 0.0

    def test_cap_applied(self) -> None:
        many = ["Python"] * 100
        assert skill_delta(many) <= 60_000
