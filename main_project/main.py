import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
from app.welcome_screen import WelcomeScreen
from app.test_selection_screen import TestSelectionScreen
from app.test_instructions_screen import TestInstructionsScreen
from app.tests.stroop_test_screen import StroopTestScreen
from app.tests.reaction_time_test_screen import ReactionTimeTestScreen
from app.tests.dms_test_screen import DmsTestScreen

TEST_INSTRUCTIONS = {
    "Stroop Test": (
        'In this test, you will see color words displayed in different colors.<br><br>'
        'Your task is to identify the <b>COLOR</b> of the text, not the word itself.<br><br>'
        'For example, if you see the word "<span style=\'color: red;\'>RED</span>" '
        'in "<span style=\'color: blue;\'>blue</span>" text, you should select "<span style=\'color: blue;\'>blue</span>".<br><br>'
        'You will complete 20 trials. Respond as quickly and accurately as possible.'
    ),
    "DMS Test": (
    'A sample image will appear briefly (it will be visible for around <b>0.8 seconds</b>).<br><br>'
    'After it disappears, <b>four images</b> will be shown.<br><br>'
    'Your task is to select the image that <b>matches the original</b>.<br><br>'
    'Only one image is correct. Respond as quickly and accurately as possible.'
    )
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Application for cognitive function testing")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add all screens to the stacked widget
        self.welcome_screen = WelcomeScreen()
        self.test_selection_screen = TestSelectionScreen()
        self.test_instructions_screen = TestInstructionsScreen()
        self.stroop_test_screen = StroopTestScreen()
        self.reaction_time_test_screen = ReactionTimeTestScreen()
        self.dms_test_screen = DmsTestScreen()

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.test_selection_screen)
        self.stacked_widget.addWidget(self.test_instructions_screen)
        self.stacked_widget.addWidget(self.stroop_test_screen)
        self.stacked_widget.addWidget(self.reaction_time_test_screen)
        self.stacked_widget.addWidget(self.dms_test_screen)

        # Connect signals to slots
        self.welcome_screen.startAssessment.connect(self.show_test_selection)
        self.test_selection_screen.testSelected.connect(self.show_test_instructions)
        self.test_instructions_screen.testReadyToStart.connect(self.run_test)
        
        self.stroop_test_screen.backToSelection.connect(self.show_test_selection)
        self.reaction_time_test_screen.backToSelection.connect(self.show_test_selection)
        self.dms_test_screen.backToSelection.connect(self.show_test_selection)

        # Set initial screen
        self.stacked_widget.setCurrentWidget(self.welcome_screen)

    def show_test_selection(self):
        self.stacked_widget.setCurrentWidget(self.test_selection_screen)

    def show_test_instructions(self, test_name):
        instructions = TEST_INSTRUCTIONS.get(test_name, "No instructions available for this test.")
        self.test_instructions_screen.set_test_info(test_name, instructions)
        self.stacked_widget.setCurrentWidget(self.test_instructions_screen)

    def run_test(self, test_name):
        if test_name == "Stroop Test":
            self.stroop_test_screen.reset()
            self.stacked_widget.setCurrentWidget(self.stroop_test_screen)
        elif test_name == "Reaction Time Test":
            self.stacked_widget.setCurrentWidget(self.reaction_time_test_screen)
        elif test_name == "DMS Test":
            self.dms_test_screen.start_test()
            self.stacked_widget.setCurrentWidget(self.dms_test_screen)
        else:
            print(f"Error: No screen found for test '{test_name}'")
            self.stacked_widget.setCurrentWidget(self.test_selection_screen)


def main():
    app = QApplication(sys.argv)
    app.setPalette(app.style().standardPalette())
    app.setStyleSheet("")
    # Collect primary screen information (geometry, available area, DPI)
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

    # Compute margins as a percentage of the smaller display dimension
    if available:
        base = min(available.width(), available.height())
        margin = max(10, int(base * 0.03))  # at least 10 px

        # Apply margins to top-level layouts of known screens when possible
        screens = [
            window.welcome_screen,
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
                # ignore widgets that don't expose a layout
                pass

    # Store screen info on the window for later use/inspection
    window.screen_info = {
        'geometry': (geometry.width(), geometry.height()) if geometry else None,
        'available': (available.width(), available.height()) if available else None,
        'dpi': dpi,
    }

    # Show application maximized (keeps window decorations: title bar, minimize/close)
    window.showMaximized()
    print('Screen info:', window.screen_info)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
