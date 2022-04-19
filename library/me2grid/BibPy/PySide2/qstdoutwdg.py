# -*- coding: utf-8 -*-

import sys

from PySide2.QtCore import Qt, QObject, Signal
from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QPalette


class StdoutSignal(QObject):
    signal = Signal(str)


class QStdoutObject():
    def __init__(self, wdg, color):
        self.wdg = wdg
        self.color = color
        self.newOutputSignal = StdoutSignal()
        self.newOutputSignal.signal.connect(self.onNewOutput)

    def write(self, text):
        self.newOutputSignal.signal.emit(str(text))
        return

    def flush(self):
        return

    def onNewOutput(self, text):
        palette = QPalette()
        palette.setColor(QPalette.Text, self.color)
        self.wdg.setPalette(palette)
        cursor = self.wdg.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        if not self.wdg.hasFocus():
            self.wdg.verticalScrollBar().setValue(self.wdg.verticalScrollBar().maximum())


class QStdoutWdg(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        getStdout = QStdoutObject(self, Qt.black)
        getStderr = QStdoutObject(self, Qt.red)
        sys.stdout = getStdout
        sys.stderr = getStderr

    def __destroy__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
