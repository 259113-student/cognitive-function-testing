from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QHBoxLayout
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class EndScreen(QWidget):
    def __init__(self, on_restart, parent=None):
        super().__init__(parent)
        self.on_restart = on_restart

        self.summary_label = None
        self.details_label = None
        self.table = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f3f3f3;
                color: #222222;
            }

            QFrame#card {
                background-color: white;
                border: 1px solid #dddddd;
                border-radius: 18px;
            }

            QLabel#title {
                font-size: 24px;
                font-weight: 700;
                color: #111111;
                background: transparent;
            }

            QLabel#summary {
                font-size: 18px;
                font-weight: 700;
                color: #222222;
                background: transparent;
            }

            QLabel#details {
                font-size: 13px;
                color: #555555;
                background: transparent;
            }

            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #eeeeee;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #f7f7f7;
                color: #333333;
                border: none;
                border-bottom: 1px solid #e5e5e5;
                padding: 10px;
                font-weight: 600;
            }

            QPushButton {
                background-color: #333333;
                color: white;
                border-radius: 14px;
                padding: 12px 18px;
                min-width: 220px;
                min-height: 46px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #555555;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        title = QLabel("DMS Results")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("summary")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setWordWrap(True)

        self.details_label = QLabel("")
        self.details_label.setObjectName("details")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_label.setWordWrap(True)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Trial", "Result", "RT (s)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setMinimumHeight(360)

        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        restart_button = QPushButton("Restart DMS Test")
        restart_button.clicked.connect(self.on_restart)

        button_row.addWidget(restart_button)

        card_layout.addWidget(self.summary_label)
        card_layout.addWidget(self.details_label)
        card_layout.addWidget(self.table)
        card_layout.addLayout(button_row)

        main_layout.addWidget(title)
        main_layout.addWidget(card)

    def set_results(self, summary):
        self.summary_label.setText(
            f"Accuracy: {summary['correct_count']}/{summary['total']} ({summary['accuracy']:.1f}%)"
        )

        self.details_label.setText(
            f"Average RT: {summary['avg_rt']:.2f} s    •    "
            f"Fastest: {summary['min_rt']:.2f} s    •    "
            f"Slowest: {summary['max_rt']:.2f} s"
        )

        results = summary["results"]
        self.table.setRowCount(len(results))

        for row, result in enumerate(results):
            trial_item = QTableWidgetItem(str(result.trial))
            result_item = QTableWidgetItem("✓ Correct" if result.correct else "✗ Wrong")
            rt_item = QTableWidgetItem(f"{result.rt:.2f}")

            trial_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if result.correct:
                bg = QColor("#edf8f0")
                fg = QColor("#1f7a3e")
            else:
                bg = QColor("#fdeeee")
                fg = QColor("#b42318")

            for item in (trial_item, result_item, rt_item):
                item.setBackground(bg)
                item.setForeground(fg if item is result_item else QColor("#222222"))

            self.table.setItem(row, 0, trial_item)
            self.table.setItem(row, 1, result_item)
            self.table.setItem(row, 2, rt_item)

        self.table.resizeRowsToContents()