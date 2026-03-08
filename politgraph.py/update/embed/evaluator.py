from dataclasses import dataclass
from typing import List, Tuple, Optional
from update.extract.dtos import MemberDTO, AffairDTO
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report
from gensim.models.doc2vec import Doc2Vec
from tqdm.auto import tqdm
import logging

logger = logging.getLogger(__name__)


@dataclass
class Doc2VecConfig:
    vector_size: int = 256
    window: int = 8
    min_count: int = 2
    epochs: int = 40
    dm: int = 0
    sample: float = 1e-5

    def to_dict(self):
        return {
            "vector_size": self.vector_size,
            "window": self.window,
            "min_count": self.min_count,
            "epochs": self.epochs,
            "dm": self.dm,
            "sample": self.sample,
        }

    def __str__(self):
        mode = "DBOW" if self.dm == 0 else "DM"
        return f"{mode} vs={self.vector_size} w={self.window} ep={self.epochs} mc={self.min_count} sample={self.sample}"


DEFAULT_CONFIGS = [
    Doc2VecConfig(dm=0, vector_size=256, window=8, epochs=40),
    Doc2VecConfig(dm=0, vector_size=256, window=5, epochs=40, sample=1e-4),
    Doc2VecConfig(dm=0, vector_size=300, window=5, epochs=60),  
]


@dataclass
class EvalResult:
    config: Doc2VecConfig
    accuracy: float
    infer_stability: float
    confusion_matrix: np.ndarray
    classification_report: str
    labels: List[str]

    def __str__(self):
        return f"{self.config}  →  Acc={self.accuracy:.3f}  Stab={self.infer_stability:.4f}"


@dataclass
class QuickEvalResult:
    """Kompaktes Ergebnis für die schnelle Evaluation ohne --evaluate."""
    accuracy: float
    num_classes: int
    num_samples: int

    def __str__(self):
        return (
            f"Quick-Eval: Accuracy={self.accuracy:.1%} "
            f"({self.num_samples} Test-Dokumente, {self.num_classes} Parteien)"
        )


class Doc2VecEvaluator:
    """
    Evaluiert verschiedene Doc2Vec-Konfigurationen auf einem Korpus
    von parlamentarischen Geschäften via Partei-Klassifikation (kNN).
    """

    def __init__(
        self,
        docs: List[Tuple[MemberDTO, AffairDTO]],
        configs: Optional[List[Doc2VecConfig]] = None,
        test_size: float = 0.10,
        infer_epochs: int = 100,
        k_neighbors: int = 5,
        stability_sample_size: int = 20,
        workers: int = 4,
        random_state: int = 42,
    ):
        self.docs = docs
        self.configs = configs or DEFAULT_CONFIGS
        self.test_size = test_size
        self.infer_epochs = infer_epochs
        self.k_neighbors = k_neighbors
        self.stability_sample_size = stability_sample_size
        self.workers = workers
        self.random_state = random_state
        self.results: List[EvalResult] = []

    def run(self) -> List[EvalResult]:
        labels = [member.party for (member, _) in self.docs]

        train_docs, test_docs, train_labels, test_labels = train_test_split(
            self.docs, labels,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=labels,
        )

        train_corpus = [doc.tagged_doc for (_, doc) in train_docs]
        self.results = []

        pbar = tqdm(total=len(self.configs), desc="Evaluating configs", unit="config")
        for i, cfg in enumerate(self.configs):
            logger.info(f"[{i + 1}/{len(self.configs)}] Training: {cfg}")
            pbar.set_postfix_str(str(cfg))

            model = Doc2Vec(**cfg.to_dict(), workers=self.workers)
            model.build_vocab(train_corpus)
            model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

            result = self._evaluate(model, train_docs, train_labels, test_docs, test_labels, cfg)
            self.results.append(result)
            logger.info(f"  -> {result}")
            pbar.update(1)

        pbar.close()

        self.results.sort(key=lambda r: r.accuracy, reverse=True)
        self._log_summary()
        return self.results

    @staticmethod
    def quick_evaluate(
        model: Doc2Vec,
        docs: List[Tuple[MemberDTO, AffairDTO]],
        test_size: float = 0.10,
        k_neighbors: int = 5,
        infer_epochs: int = 50,
        random_state: int = 42,
    ) -> QuickEvalResult:
        """
        Schnelle Evaluation eines bereits trainierten Doc2Vec-Modells.
        Wird immer ausgeführt (auch ohne --evaluate) um eine kurze
        Zusammenfassung der Modellqualität zu liefern.
        """
        labels = [member.party for (member, _) in docs]

        train_docs, test_docs, train_labels, test_labels = train_test_split(
            docs, labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels,
        )

        train_vectors = np.array([model.dv[doc.id] for (_, doc) in train_docs])
        test_vectors = np.array([
            model.infer_vector(doc.tagged_doc.words, epochs=infer_epochs)
            for (_, doc) in test_docs
        ])

        clf = KNeighborsClassifier(n_neighbors=k_neighbors, metric="cosine")
        clf.fit(train_vectors, train_labels)
        accuracy = clf.score(test_vectors, test_labels)

        result = QuickEvalResult(
            accuracy=accuracy,
            num_classes=len(set(labels)),
            num_samples=len(test_docs),
        )

        logger.info(f"  {result}")
        return result

    def _evaluate(
        self,
        model: Doc2Vec,
        train_docs: List[Tuple],
        train_labels: List[str],
        test_docs: List[Tuple],
        test_labels: List[str],
        config: Doc2VecConfig,
    ) -> EvalResult:
        train_vectors = np.array([model.dv[doc.id] for (_, doc) in train_docs])
        test_vectors = np.array([
            model.infer_vector(doc.tagged_doc.words, epochs=self.infer_epochs)
            for (_, doc) in tqdm(test_docs, desc="  Inferring test vectors", unit="doc", leave=False)
        ])

        clf = KNeighborsClassifier(n_neighbors=self.k_neighbors, metric="cosine")
        clf.fit(train_vectors, train_labels)

        predictions = clf.predict(test_vectors)
        accuracy = clf.score(test_vectors, test_labels)

        sorted_labels = sorted(set(train_labels + test_labels))
        cm = confusion_matrix(test_labels, predictions, labels=sorted_labels)
        report = classification_report(test_labels, predictions, labels=sorted_labels, zero_division=0)

        stability = self._evaluate_infer_stability(model, test_docs)

        return EvalResult(
            config=config,
            accuracy=accuracy,
            infer_stability=stability,
            confusion_matrix=cm,
            classification_report=report,
            labels=sorted_labels,
        )

    def _evaluate_infer_stability(
        self,
        model: Doc2Vec,
        test_docs: List[Tuple],
    ) -> float:
        sample = test_docs[: self.stability_sample_size]
        similarities = []

        for (_, doc) in sample:
            words = doc.tagged_doc.words
            v1 = model.infer_vector(words, epochs=self.infer_epochs)
            v2 = model.infer_vector(words, epochs=self.infer_epochs)
            cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            similarities.append(cos_sim)

        return float(np.mean(similarities))

    def _log_summary(self):
        logger.debug("\n=== Ergebnisse (sortiert nach Accuracy) ===")
        for r in self.results:
            logger.info(f"  {r}")

        # Confusion Matrix und Report nur für die beste Config loggen
        if self.results:
            best = self.results[0]
            logger.info(f"\n=== Beste Config: {best.config} ===")
            logger.info(f"\nClassification Report:\n{best.classification_report}")
            logger.info(f"\nConfusion Matrix (Zeilen=Tatsächlich, Spalten=Vorhergesagt):")
            logger.info(f"Parteien: {best.labels}")
            logger.info(f"\n{best.confusion_matrix}")

    @property
    def best(self) -> Optional[EvalResult]:
        return self.results[0] if self.results else None