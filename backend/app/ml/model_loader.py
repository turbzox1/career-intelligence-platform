"""Salary model loading with graceful cold-start fallback.

Loads the trained artifact from local storage (with optional MLflow source).
When no artifact exists, falls back to the deterministic baseline model so
the API never returns 5xx due to a missing model artifact.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

import joblib

logger = logging.getLogger("app.ml.model_loader")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _candidate_paths() -> list[Path]:
    """Ordered list of plausible artifact locations."""
    return [
        REPO_ROOT / "ml" / "models" / "trained",
        Path.cwd() / "ml" / "models" / "trained",
        REPO_ROOT / "ml" / "mlruns",
    ]


class LoadedModel:
    """A loaded model artifact with its metadata."""

    def __init__(self, pipeline: object | None, metadata: dict | None) -> None:
        self.pipeline = pipeline
        self.metadata = metadata or {}
        self.model_name = self.metadata.get("model_name", "baseline")
        self.model_version = self.metadata.get("model_version", "1.0.0")

    @property
    def is_baseline(self) -> bool:
        return self.pipeline is None


class ModelLoader:
    """Thread-safe singleton that loads the salary model once."""

    _instance: ModelLoader | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._model: LoadedModel | None = None
        self._loaded_path: Path | None = None

    @classmethod
    def instance(cls) -> ModelLoader:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load(self, *, force_reload: bool = False) -> LoadedModel:
        """Load (or reload) the model artifact."""
        with self._lock:
            if self._model is not None and not force_reload:
                return self._model
            self._model = self._load_from_disk()
            if self._model.is_baseline:
                logger.warning("no trained model artifact found; using baseline model")
            else:
                logger.info(
                    "model_loaded",
                    extra={"model": self._model.model_name, "version": self._model.model_version},
                )
            return self._model

    def reload(self) -> LoadedModel:
        """Force a reload (used after a re-train)."""
        return self.load(force_reload=True)

    def _load_from_disk(self) -> LoadedModel:
        for path in _candidate_paths():
            model_file = path / "model.joblib"
            meta_file = path / "metadata.json"
            if model_file.exists() and meta_file.exists():
                try:
                    pipeline = joblib.load(model_file)
                    metadata = json.loads(meta_file.read_text())
                    self._loaded_path = path
                    return LoadedModel(pipeline, metadata)
                except Exception as exc:  # pragma: no cover
                    logger.exception("failed to load artifact at %s", path, exc_info=exc)
                    continue
        return LoadedModel(None, None)


def get_model() -> LoadedModel:
    """Convenience accessor for the loaded model."""
    return ModelLoader.instance().load()
