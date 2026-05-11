from app.tests.dms_test.dms import DMSTaskScreen
from app.tests.dms_test.end import EndScreen
from app.tests.practice_complete_screen import PracticeCompleteScreen
from app.tests.practice_intro_dialog import PracticeIntroDialog
from app.tests.base_test_screen import BaseTestScreen
from PyQt6.QtCore import pyqtSignal


class DmsTestScreen(BaseTestScreen):
    backToSelection = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("dms", parent)

        self.sample_time_ms = 800
        self.practice_screen = DMSTaskScreen(self._on_practice_done, practice_mode=True)
        self.real_screen = DMSTaskScreen(self.show_results, practice_mode=False)
        self.practice_complete_screen = PracticeCompleteScreen()
        self.end_screen = EndScreen(self.restart_test, self.go_back)

        self.practice_complete_screen.startRealTest.connect(self._start_real_test)
        self.practice_complete_screen.repeatPractice.connect(self._start_practice)

        self.addWidget(self.practice_screen)
        self.addWidget(self.real_screen)
        self.addWidget(self.practice_complete_screen)
        self.addWidget(self.end_screen)

        self.setCurrentWidget(self.practice_screen)

    def start_test(self, sample_time_ms=None):
        """Wywoływane z MainWindow — pokazuje popup, potem rundę próbną."""
        if sample_time_ms is not None:
            self.sample_time_ms = sample_time_ms
        self.practice_screen.set_sample_time(self.sample_time_ms)
        self.real_screen.set_sample_time(self.sample_time_ms)

        dlg = PracticeIntroDialog(self)
        dlg.exec()
        self._start_practice()

    def _start_practice(self):
        self.practice_screen.reset_task()
        self.setCurrentWidget(self.practice_screen)

    def _on_practice_done(self, _summary):
        self.setCurrentWidget(self.practice_complete_screen)

    def _start_real_test(self):
        self.real_screen.reset_task()
        self.setCurrentWidget(self.real_screen)

    def restart_test(self):
        self.start_test()

    def show_results(self, summary):
        self.end_screen.set_results(summary)
        self.setCurrentWidget(self.end_screen)

    def go_back(self):
        self.backToSelection.emit()