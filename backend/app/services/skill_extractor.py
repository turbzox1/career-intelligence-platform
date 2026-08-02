"""Skill extraction and normalisation service.

Combines a rule-based matcher against the master skill catalog with optional
spaCy enrichment. Skills are normalised (Python3/PYTHON -> Python) via the
catalog aliases and only canonical names are persisted.
"""

from __future__ import annotations

import logging
import re

from app.data.skills_master import get_canonical_skill, normalize_skill_token

logger = logging.getLogger("app.skill_extractor")

# Matches camelCase or snake_case tokens that might be skill names.
_TOKEN_SPLIT_RE = re.compile(r"[^a-zA-Z0-9+#.]+")


class SkillExtractor:
    """Extracts canonical skills from free text."""

    def extract(self, text: str) -> list[dict]:
        """Return a list of ``{name, category, source, confidence}`` dicts."""
        if not text:
            return []
        found: dict[str, dict] = {}
        for token in self._tokens(text):
            entry = get_canonical_skill(token)
            if entry is None:
                entry = self._normalize_compound(token)
            if entry is None:
                continue
            key = entry["name"]
            if key not in found:
                found[key] = {
                    "name": entry["name"],
                    "category": entry["category"],
                    "source": "rule",
                    "confidence": 1.0 if normalize_skill_token(token) == normalize_skill_token(key) else 0.9,
                }
        logger.info("skills_extracted", extra={"count": len(found)})
        return list(found.values())

    def _tokens(self, text: str) -> set[str]:
        """Yield normalised candidate skill tokens."""
        tokens: set[str] = set()
        # 1. Whole-line skills sections (comma separated).
        for line in re.split(r"[\n;]", text):
            if ":" in line and re.match(r"\s*(skills|tech|technologies)", line, re.I):
                header, _, body = line.partition(":")
                body = body.strip()
                if len(body) > 4 and len(header.strip().split()) <= 3:
                    for part in re.split(r"[,\u2022|]", body):
                        tokens.add(normalize_skill_token(part))
        # 2. All tokens, respecting words with '+', '#', '.'.
        for match in _TOKEN_SPLIT_RE.split(text):
            token = match.strip(".")
            if 2 <= len(token) <= 60:
                tokens.add(normalize_skill_token(token))
        # 3. Two-word phrases likely to be skills ("machine learning").
        words = re.findall(r"[A-Za-z][A-Za-z+#.]+", text)
        for pair in zip(words, words[1:], strict=False):
            tokens.add(normalize_skill_token(f"{pair[0]} {pair[1]}"))
        return tokens

    def _normalize_compound(self, token: str) -> dict | None:
        """Match multi-token phrases by re-joining hyphen/space variants."""
        # e.g. "next-js" vs "next js"
        for separator in ("-", " "):
            candidate = token.replace(separator, " ") if separator == "-" else token
            entry = get_canonical_skill(candidate)
            if entry:
                return entry
        # e.g. "postgresql" already handled; try case variants of the token itself.
        return get_canonical_skill(token.lower())
