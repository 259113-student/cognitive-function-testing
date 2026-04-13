from PIL import Image, ImageDraw
import random
import os
import shutil


class DMSGenerator:
    def __init__(self, output_dir="dms_dataset", grid_size=4):
        self.GRID_SIZE = grid_size
        self.CELL_SIZE = 40
        self.PADDING = 10
        self.BG_COLOR = (220, 220, 220)

        self.COLOR_POOL = [
            (255, 0, 0),
            (255, 255, 0),
            (0, 128, 255),
            (0, 200, 0),
            (255, 0, 255),
            (255, 165, 0),
        ]

        self.PANEL_SIZE = self.GRID_SIZE * self.CELL_SIZE + 2 * self.PADDING
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def draw_grid(self, pattern):
        img = Image.new("RGB", (self.PANEL_SIZE, self.PANEL_SIZE), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                x0 = self.PADDING + c * self.CELL_SIZE
                y0 = self.PADDING + r * self.CELL_SIZE
                x1 = x0 + self.CELL_SIZE
                y1 = y0 + self.CELL_SIZE
                draw.rectangle([x0, y0, x1, y1], fill=pattern[r][c])

        return img

    def random_pattern(self, colors):
        return [
            [random.choice(colors) for _ in range(self.GRID_SIZE)]
            for _ in range(self.GRID_SIZE)
        ]

    def rearrange(self, pattern, min_swaps=2, max_swaps=10):
        flat = [cell for row in pattern for cell in row]
        n = len(flat)
        num_swaps = random.randint(min_swaps, max_swaps)
        new_flat = flat.copy()

        for _ in range(num_swaps):
            i, j = random.sample(range(n), 2)
            new_flat[i], new_flat[j] = new_flat[j], new_flat[i]

        return [
            new_flat[i * self.GRID_SIZE:(i + 1) * self.GRID_SIZE]
            for i in range(self.GRID_SIZE)
        ]

    def remap_colors(self, pattern):
        unique_colors = list(set(cell for row in pattern for cell in row))
        num_changes = min(random.choice([1, 2, 3]), len(unique_colors))

        colors_to_change = random.sample(unique_colors, num_changes)
        available_colors = [c for c in self.COLOR_POOL if c not in unique_colors]

        if len(available_colors) < num_changes:
            available_colors = self.COLOR_POOL.copy()

        new_colors = random.sample(available_colors, num_changes)

        mapping = {}
        new_idx = 0

        for original in unique_colors:
            if original in colors_to_change:
                mapping[original] = new_colors[new_idx]
                new_idx += 1
            else:
                mapping[original] = original

        result = [[mapping[cell] for cell in row] for row in pattern]

        flat_colors = set(cell for row in result for cell in row)
        if len(flat_colors) < 3:
            fallback_colors = random.sample(self.COLOR_POOL, len(unique_colors))
            fallback_map = dict(zip(unique_colors, fallback_colors))
            result = [[fallback_map[cell] for cell in row] for row in pattern]

        return result

    def completely_random(self):
        colors = random.sample(self.COLOR_POOL, k=3)
        return self.random_pattern(colors)

    def generate_trial(self, index):
        trial_dir = os.path.join(self.output_dir, f"trial_{index}")
        os.makedirs(trial_dir, exist_ok=True)

        sample_colors = random.sample(self.COLOR_POOL, k=3)
        sample = self.random_pattern(sample_colors)

        swapped = self.remap_colors(sample)
        rearranged = self.rearrange(sample, min_swaps=2, max_swaps=10)

        labeled = [
            ("correct", sample),
            ("swapped", swapped),
            ("rearranged", rearranged),
            ("random", self.completely_random()),
        ]

        random.shuffle(labeled)

        self.draw_grid(sample).save(os.path.join(trial_dir, "sample.png"))

        for i, (label, pattern) in enumerate(labeled):
            self.draw_grid(pattern).save(
                os.path.join(trial_dir, f"answer_{i}_{label}.png")
            )

        return labeled

    def generate_dataset(self, n_trials=10):
        if os.path.exists(self.output_dir):
            for item in os.listdir(self.output_dir):
                path = os.path.join(self.output_dir, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

        os.makedirs(self.output_dir, exist_ok=True)

        for i in range(n_trials):
            self.generate_trial(i)