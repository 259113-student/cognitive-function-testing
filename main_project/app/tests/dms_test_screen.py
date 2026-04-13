from main_project.app.tests.dms_test.dms import DMSTaskScreen
from main_project.app.tests.dms_test.end import EndScreen
from main_project.app.tests.base_test_screen import BaseTestScreen


class DmsTestScreen(BaseTestScreen):
    def __init__(self, parent=None):
        super().__init__("DMS Test", parent)

        self.task_screen = DMSTaskScreen(self.show_results)
        self.end_screen = EndScreen(self.restart_test)

        self.addWidget(self.task_screen)
        self.addWidget(self.end_screen)

    def start_test(self):
        self.task_screen.reset_task()
        self.setCurrentWidget(self.task_screen)

    def restart_test(self):
        self.start_test()

    def show_results(self, summary):
        self.end_screen.set_results(summary)
        self.setCurrentWidget(self.end_screen)