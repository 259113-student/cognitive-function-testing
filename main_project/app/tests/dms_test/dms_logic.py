from dataclasses import dataclass
from pathlib import Path
import random
import time


@dataclass
class DMSResult:
    trial: int
    correct: bool
    rt: float


class DMSLogic:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = Path(dataset_dir)
        self.trial_dirs = sorted(
            [path for path in self.dataset_dir.iterdir() if path.is_dir()],
            key=lambda p: p.name
        )
        self.current_trial_index = 0
        self.results = []
        self.response_start_time = 0.0

    def has_next_trial(self):
        return self.current_trial_index < len(self.trial_dirs)

    def get_sample_path(self):
        return self.trial_dirs[self.current_trial_index] / "sample.png"

    def get_answer_paths(self):
        answers = [
            path for path in self.trial_dirs[self.current_trial_index].iterdir()
            if path.name.startswith("answer_")
        ]
        random.shuffle(answers)
        return answers

    def start_response_timer(self):
        self.response_start_time = time.perf_counter()

    def submit_answer(self, selected_filename: str):
        rt = time.perf_counter() - self.response_start_time
        correct = "correct" in selected_filename

        self.results.append(
            DMSResult(
                trial=self.current_trial_index + 1,
                correct=correct,
                rt=rt
            )
        )

        self.current_trial_index += 1
        return correct, rt

    def summary(self):
        total = len(self.results)
        correct_count = sum(1 for r in self.results if r.correct)
        wrong_count = total - correct_count

        reaction_times = [r.rt for r in self.results]
        avg_rt = sum(reaction_times) / total if total else 0.0
        min_rt = min(reaction_times) if reaction_times else 0.0
        max_rt = max(reaction_times) if reaction_times else 0.0
        accuracy = (correct_count / total * 100.0) if total else 0.0

        return {
            "total": total,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "accuracy": accuracy,
            "avg_rt": avg_rt,
            "min_rt": min_rt,
            "max_rt": max_rt,
            "results": self.results,
        }