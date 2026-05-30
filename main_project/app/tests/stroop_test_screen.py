from app.tests.stroop_test.stroop import StroopScreen
from app.tests.stroop_test.end import EndScreen
from app.tests.practice_complete_screen import PracticeCompleteScreen
from app.tests.post_test_screen import PostTestScreen
from app.pin_security import verify_doctor_pin
from app.tests.practice_intro_dialog import PracticeIntroDialog
from app.tests.base_test_screen import BaseTestScreen
from PyQt6.QtCore import pyqtSignal


class StroopTestScreen(BaseTestScreen):
    backToSelection = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("stroop", parent)

        self.practice_screen = StroopScreen(self._on_practice_done, practice_mode=True)
        self.real_screen = StroopScreen(self.show_results, practice_mode=False)
        self.practice_complete_screen = PracticeCompleteScreen()
        self.post_test_screen = PostTestScreen()
        self.end_screen = EndScreen(self.go_back, self.restart_test)

        self.practice_complete_screen.startRealTest.connect(self._start_real_test)
        self.practice_complete_screen.repeatPractice.connect(self._start_practice)
        self.post_test_screen.continueToResults.connect(self._show_results)

        self.addWidget(self.practice_screen)
        self.addWidget(self.real_screen)
        self.addWidget(self.practice_complete_screen)
        self.addWidget(self.post_test_screen)
        self.addWidget(self.end_screen)

        self.setCurrentWidget(self.practice_screen)

    def reset(self):
        """Wywoływane z MainWindow — pokazuje popup, potem rundę próbną."""
        dlg = PracticeIntroDialog(self)
        dlg.exec()
        self._start_practice()

    def _start_practice(self):
        self.practice_screen.start_fresh()
        self.setCurrentWidget(self.practice_screen)

    def _on_practice_done(self, _summary):
        self.setCurrentWidget(self.practice_complete_screen)

    def _start_real_test(self):
        self.real_screen.start_fresh()
        self.setCurrentWidget(self.real_screen)

    def restart_test(self):
        # Restart całego testu — popup też się pokaże
        self.reset()

    def show_results(self, summary: dict):
        self._pending_summary = summary
        self.setCurrentWidget(self.post_test_screen)

    def _show_results(self):
        if getattr(self, '_pending_summary', None) is None:
            return
        if not verify_doctor_pin(self):
            return
        self.end_screen.set_results(self._pending_summary)
        self.setCurrentWidget(self.end_screen)

    def go_back(self):
        self.backToSelection.emit()