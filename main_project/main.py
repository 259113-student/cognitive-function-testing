import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
from app.translations import get_translator
from app.test_selection_screen import TestSelectionScreen
from app.test_instructions_screen import TestInstructionsScreen
from app.tests.stroop_test_screen import StroopTestScreen
from app.tests.reaction_time_test_screen import ReactionTimeTestScreen
from app.tests.dms_test_screen import DmsTestScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("welcomeScreen")

        self.setGeometry(100, 100, 900, 700)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)

        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self.setWindowTitle(self._tr.t('app.title'))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Ekrany
        self.test_selection_screen = TestSelectionScreen()
        self.test_instructions_screen = TestInstructionsScreen()
        self.stroop_test_screen = StroopTestScreen()
        self.reaction_time_test_screen = ReactionTimeTestScreen()
        self.dms_test_screen = DmsTestScreen()

        self.stacked_widget.addWidget(self.test_selection_screen)
        self.stacked_widget.addWidget(self.test_instructions_screen)
        self.stacked_widget.addWidget(self.stroop_test_screen)
        self.stacked_widget.addWidget(self.reaction_time_test_screen)
        self.stacked_widget.addWidget(self.dms_test_screen)

        # Sygnały
        self.test_selection_screen.testSelected.connect(self.show_test_instructions)
        self.test_instructions_screen.testReadyToStart.connect(self.run_test)
        self.test_instructions_screen.backToSelection.connect(self.show_test_selection)  # NOWE

        self.stroop_test_screen.backToSelection.connect(self.show_test_selection)
        self.reaction_time_test_screen.backToSelection.connect(self.show_test_selection)
        self.dms_test_screen.backToSelection.connect(self.show_test_selection)

        # Ekran startowy = wybór testu (panel lekarza)
        self.stacked_widget.setCurrentWidget(self.test_selection_screen)

    def show_test_selection(self):
        self.stacked_widget.setCurrentWidget(self.test_selection_screen)

    def show_test_instructions(self, test_id):
        self.test_instructions_screen.set_test_info(test_id)
        self.stacked_widget.setCurrentWidget(self.test_instructions_screen)

    def run_test(self, test_name):
        if test_name == "stroop":
            self.stroop_test_screen.reset()
            self.stacked_widget.setCurrentWidget(self.stroop_test_screen)
        elif test_name == "reaction_time":
            self.stacked_widget.setCurrentWidget(self.reaction_time_test_screen)
        elif test_name == "dms":
            sample_time_ms = self.test_selection_screen.get_dms_sample_time_ms()
            self.dms_test_screen.start_test(sample_time_ms)
            self.stacked_widget.setCurrentWidget(self.dms_test_screen)
        else:
            print(f"Error: No screen found for test '{test_name}'")
            self.stacked_widget.setCurrentWidget(self.test_selection_screen)

    def retranslate(self, lang):
        try:
            self.setWindowTitle(self._tr.t('app.title'))
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    app.setPalette(app.style().standardPalette())
    app.setStyleSheet("""
    #welcomeScreen {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #fffbf0,
            stop:1 #fef9e7
        );
    }
    """)
    screen = app.primaryScreen()
    if screen:
        geometry = screen.geometry()
        available = screen.availableGeometry()
        dpi = screen.logicalDotsPerInch()
    else:
        geometry = None
        available = None
        dpi = None

    window = MainWindow()

    if available:
        base = min(available.width(), available.height())
        margin = max(10, int(base * 0.03))

        screens = [
            window.test_selection_screen,
            window.test_instructions_screen,
            window.stroop_test_screen,
            window.reaction_time_test_screen,
            window.dms_test_screen,
        ]

        for w in screens:
            try:
                layout = w.layout()
                if layout is not None:
                    layout.setContentsMargins(margin, margin, margin, margin)
            except Exception:
                pass

    window.screen_info = {
        'geometry': (geometry.width(), geometry.height()) if geometry else None,
        'available': (available.width(), available.height()) if available else None,
        'dpi': dpi,
    }

    window.showMaximized()
    print('Screen info:', window.screen_info)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()