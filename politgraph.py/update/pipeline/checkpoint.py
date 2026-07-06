import logging
import os
import pickle
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from update.extract.dtos import AffairDTO, MemberDTO

logger = logging.getLogger(__name__)

# Reihenfolge = Pipeline-Reihenfolge. Ein späterer Checkpoint impliziert, dass
# alle früheren Stages ebenfalls abgeschlossen sind.
STAGES: Tuple[str, ...] = ("fetched", "cleaned", "embedded")

PipelineState = Tuple[List[Tuple[MemberDTO, AffairDTO]], List[MemberDTO]]


class CheckpointStore:
    """
    Persistiert den Pipeline-Zustand (docs + members) nach jeder teuren Stage,
    damit ein Neustart nach einem Absturz an der letzten abgeschlossenen Stage
    weitermachen kann, statt Fetch/Clean/Embed erneut auszuführen.

    Serialisierung via einem einzigen pickle.dump: interned Lemma-Strings
    werden durch die pickle-Memoization als geteilte Objekte wiederhergestellt,
    die Speicher-Deduplizierung bleibt also über den Reload hinweg erhalten.
    """

    VERSION = 1

    def __init__(self, directory: Optional[Path], run_key: str = ""):
        self._dir = Path(directory) if directory is not None else None
        self._run_key = run_key
        if self._dir is not None:
            self._dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self) -> bool:
        return self._dir is not None

    def _data_path(self, stage: str) -> Path:
        return self._dir / f"{stage}.pkl"

    def _key_path(self, stage: str) -> Path:
        return self._dir / f"{stage}.key"

    def latest_completed_index(self) -> int:
        """
        Index der letzten abgeschlossenen Stage in STAGES, -1 wenn keiner
        (oder wenn der jüngste Checkpoint zu einem anderen Run gehört).
        """
        if not self.enabled:
            return -1
        for i in range(len(STAGES) - 1, -1, -1):
            stage = STAGES[i]
            if not (self._data_path(stage).exists() and self._key_path(stage).exists()):
                continue
            saved_key = self._key_path(stage).read_text(encoding="utf-8").strip()
            if saved_key != self._run_key:
                logger.warning(
                    f"Checkpoint '{stage}' gehört zu einem anderen Run "
                    f"(key '{saved_key}' != '{self._run_key}') und wird ignoriert. "
                    f"Löschen Sie {self._dir} oder starten Sie mit --no-checkpoint."
                )
                return -1
            return i
        return -1

    def save(self, stage: str, state: PipelineState) -> None:
        if not self.enabled:
            return
        docs, members = state
        payload = {
            "version": self.VERSION,
            "stage": stage,
            "docs": docs,
            "members": members,
        }
        # Atomar schreiben: erst in eine temp-Datei, dann umbenennen. Der
        # Key wird erst nach den Daten geschrieben, damit ein vorhandener Key
        # garantiert auch gültige Daten bedeutet.
        fd, tmp_name = tempfile.mkstemp(dir=self._dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as f:
                pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(tmp_name, self._data_path(stage))
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        self._key_path(stage).write_text(self._run_key, encoding="utf-8")
        logger.info(
            f"Checkpoint '{stage}' gespeichert "
            f"({len(docs)} docs, {len(members)} members) -> {self._data_path(stage)}"
        )

    def load(self, stage: str) -> PipelineState:
        with open(self._data_path(stage), "rb") as f:
            payload = pickle.load(f)
        if payload.get("version") != self.VERSION:
            raise ValueError(
                f"Checkpoint '{stage}' hat inkompatible Version "
                f"{payload.get('version')} (erwartet {self.VERSION})."
            )
        docs = payload["docs"]
        members = payload["members"]
        logger.info(
            f"Checkpoint '{stage}' geladen ({len(docs)} docs, {len(members)} members)"
        )
        return docs, members

    def clear(self) -> None:
        if not self.enabled:
            return
        for stage in STAGES:
            for path in (self._data_path(stage), self._key_path(stage)):
                if path.exists():
                    path.unlink()
        logger.info("Checkpoints gelöscht")
