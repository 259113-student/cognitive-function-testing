from app.tests.dms_test.dms import DMSTaskScreen
from app.tests.dms_test.end import EndScreen
from app.tests.base_test_screen import BaseTestScreen
from PyQt6.QtCore import pyqtSignal


class DmsTestScreen(BaseTestScreen):
    backToSelection = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("dms", parent)

        self.sample_time_ms = 800
        self.task_screen = DMSTaskScreen(self.show_results)
        self.end_screen = EndScreen(self.restart_test, self.go_back)

        self.addWidget(self.task_screen)
        self.addWidget(self.end_screen)

        self.setCurrentWidget(self.task_screen)

    def start_test(self, sample_time_ms=None):
        if sample_time_ms is not None:
            self.sample_time_ms = sample_time_ms

        self.task_screen.set_sample_time(self.sample_time_ms)
        self.task_screen.reset_task()
        self.setCurrentWidget(self.task_screen)

    def restart_test(self):
        self.start_test()

    def show_results(self, summary):
        self.end_screen.set_results(summary)
        self.setCurrentWidget(self.end_screen)

    def go_back(self):
        self.backToSelection.emit()
