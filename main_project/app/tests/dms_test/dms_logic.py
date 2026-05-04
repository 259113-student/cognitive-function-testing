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
        import math
        total = len(self.results)
        correct_count = sum(1 for r in self.results if r.correct)
        wrong_count = total - correct_count
        reaction_times = [r.rt for r in self.results]
        avg_rt = sum(reaction_times) / total if total else 0.0
        min_rt = min(reaction_times) if reaction_times else 0.0
        max_rt = max(reaction_times) if reaction_times else 0.0
        accuracy = (correct_count / total * 100.0) if total else 0.0
        sorted_rt = sorted(reaction_times)
        n = len(sorted_rt)
        median_rt = 0.0 if n == 0 else (sorted_rt[n//2] if n%2==1 else (sorted_rt[n//2-1]+sorted_rt[n//2])/2.0)
        variance = sum((t-avg_rt)**2 for t in reaction_times)/total if total else 0.0
        std_rt = math.sqrt(variance)
        half = total // 2
        first_half = self.results[:half] if half > 0 else []
        second_half = self.results[half:] if half > 0 else []
        first_acc  = (sum(1 for r in first_half  if r.correct)/len(first_half)*100)  if first_half  else 0.0
        second_acc = (sum(1 for r in second_half if r.correct)/len(second_half)*100) if second_half else 0.0
        within_1std = sum(1 for t in reaction_times if abs(t-avg_rt) <= std_rt)
        consistency = (within_1std/total*100.0) if total else 0.0
        return {
            "total": total,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "accuracy": accuracy,
            "avg_rt": avg_rt,
            "min_rt": min_rt,
            "max_rt": max_rt,
            "median_rt": median_rt,
            "std_rt": std_rt,
            "first_half_accuracy": first_acc,
            "second_half_accuracy": second_acc,
            "consistency": consistency,
            "results": self.results,
        }