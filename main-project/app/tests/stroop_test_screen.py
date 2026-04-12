from app.tests.base_test_screen import BaseTestScreen

class StroopTestScreen(BaseTestScreen):
    def __init__(self, parent=None):
        super().__init__("Stroop Test", parent)
        # Możesz dodać tutaj specyficzną logikę dla tego testu