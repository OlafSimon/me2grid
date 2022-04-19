# This Python file uses the following encoding: utf-8

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPalette


class IfNewText(QObject):
    signal = pyqtSignal()


class QEnterEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ifNewText = IfNewText()
        self.enterState = False
        self.previousText = ""

    def keyPressEvent(self, event):
        self.enterEditMode()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.leaveEditMode(True)
            self.ifNewText.signal.emit()
            return
        elif event.key() == Qt.Key_Escape:
            self.leaveEditMode(False)
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        # print("lost focus")
        if self.enterState:
            self.leaveEditMode(False)
        super().focusOutEvent(event)

    def focusInEvent(self, event):
        # print("got focus")
        super().focusInEvent(event)

    def text(self):
        # print("getText")
        return super().text()

    def setText(self, text):
        if not self.enterState:
            super().setText(text)

    def enterEditMode(self):
        if not self.enterState:
            self.previousText = super().text()
            self.enterState = True
            palette = QPalette()
            palette.setColor(QPalette.Base, Qt.green)
            self.setPalette(palette)

    def leaveEditMode(self, successfully):
        if not successfully:
            super().setText(self.previousText)
        self.enterState = False
        palette = QPalette()
        palette.setColor(QPalette.Base, Qt.white)
        self.setPalette(palette)
