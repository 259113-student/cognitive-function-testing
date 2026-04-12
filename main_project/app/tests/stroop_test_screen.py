from main_project.app.tests.stroop_test.stroop import StroopScreen
from main_project.app.tests.stroop_test.start import StartScreen
from main_project.app.tests.stroop_test.end import EndScreen
from main_project.app.tests.base_test_screen import BaseTestScreen


class StroopTestScreen(BaseTestScreen):
    def __init__(self, parent=None):
        super().__init__("Stroop Test", parent)

        self.start_screen = StartScreen(self.start_test)
        self.stroop_screen = StroopScreen(self.show_results)
        self.end_screen = EndScreen()

        self.addWidget(self.start_screen)
        self.addWidget(self.stroop_screen)
        self.addWidget(self.end_screen)

    def start_test(self):
        self.stroop_screen.results = []
        self.stroop_screen.trial = 0
        self.setCurrentWidget(self.stroop_screen)
        self.stroop_screen.setFocus()

    def show_results(self, accuracy, avg_crt, avg_icrt):
        self.end_screen.set_results(accuracy, avg_crt, avg_icrt)
        self.setCurrentWidget(self.end_screen)
