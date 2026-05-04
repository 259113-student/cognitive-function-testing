from app.tests.stroop_test.stroop import StroopScreen
from app.tests.stroop_test.start import StartScreen
from app.tests.stroop_test.end import EndScreen
from app.tests.base_test_screen import BaseTestScreen
from PyQt6.QtCore import pyqtSignal

class StroopTestScreen(BaseTestScreen):
    backToSelection = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("stroop", parent)

        self.start_screen  = StartScreen(self.start_test)
        self.stroop_screen = StroopScreen(self.show_results)
        self.end_screen    = EndScreen(self.go_back, self.restart_test)

        self.addWidget(self.start_screen)
        self.addWidget(self.stroop_screen)
        self.addWidget(self.end_screen)
        self.setCurrentWidget(self.start_screen)

    def reset(self):
        self.stroop_screen.results = []
        self.stroop_screen.trial   = 0
        self.setCurrentWidget(self.start_screen)

    def start_test(self):
        self.setCurrentWidget(self.stroop_screen)

    def show_results(self, summary: dict):
        self.end_screen.set_results(summary)
        self.setCurrentWidget(self.end_screen)

    def restart_test(self):
        self.reset()
        self.start_test()

    def go_back(self):
        self.reset()
        self.backToSelection.emit()