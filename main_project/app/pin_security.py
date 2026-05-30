import hashlib
import hmac
import os

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import QSettings

from app.translations import get_translator


class DoctorPinService:
    ORG = "SIiCA"
    APP = "CFT"
    KEY_SALT = "doctor/pin_salt"
    KEY_HASH = "doctor/pin_hash"
    KEY_ITER = "doctor/pin_iterations"
    DEFAULT_ITERATIONS = 200000
    DEFAULT_PIN = "0000"

    def __init__(self):
        self.settings = QSettings(self.ORG, self.APP)

    def has_pin(self):
        return bool(self.settings.value(self.KEY_SALT, "")) and bool(self.settings.value(self.KEY_HASH, ""))

    def set_pin(self, pin: str):
        salt = os.urandom(16)
        pin_hash = self._pbkdf2(pin, salt, self.DEFAULT_ITERATIONS)
        self.settings.setValue(self.KEY_SALT, salt.hex())
        self.settings.setValue(self.KEY_HASH, pin_hash.hex())
        self.settings.setValue(self.KEY_ITER, self.DEFAULT_ITERATIONS)

    def verify_pin(self, pin: str):
        salt_hex = self.settings.value(self.KEY_SALT, "")
        expected_hash_hex = self.settings.value(self.KEY_HASH, "")
        iterations = int(self.settings.value(self.KEY_ITER, self.DEFAULT_ITERATIONS))

        if not salt_hex or not expected_hash_hex:
            return pin == self.DEFAULT_PIN

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(expected_hash_hex)
        actual_hash = self._pbkdf2(pin, salt, iterations)
        return hmac.compare_digest(actual_hash, expected_hash)

    @staticmethod
    def _pbkdf2(pin: str, salt: bytes, iterations: int):
        return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)


class DoctorPinVerifyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tr = get_translator()
        self._tr.languageChanged.connect(self.retranslate)
        self._build()

    def _build(self):
        self.setWindowTitle(self._tr.t('doctor_panel.verify_title'))
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.prompt_label = QLabel(self._tr.t('doctor_panel.verify_prompt'))
        layout.addWidget(self.prompt_label)

        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText(self._tr.t('doctor_panel.pin_placeholder'))
        self.pin_input.returnPressed.connect(self.accept)
        layout.addWidget(self.pin_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def pin(self):
        return self.pin_input.text()

    def retranslate(self, lang=None):
        try:
            self.setWindowTitle(self._tr.t('doctor_panel.verify_title'))
            self.prompt_label.setText(self._tr.t('doctor_panel.verify_prompt'))
            self.pin_input.setPlaceholderText(self._tr.t('doctor_panel.pin_placeholder'))
        except Exception:
            pass


def verify_doctor_pin(parent=None):
    tr = get_translator()
    service = DoctorPinService()

    dlg = DoctorPinVerifyDialog(parent)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return False

    if service.verify_pin(dlg.pin()):
        return True

    QMessageBox.warning(
        parent,
        tr.t('doctor_panel.pin_invalid_title'),
        tr.t('doctor_panel.pin_invalid_message'),
    )
    return False