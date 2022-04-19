# This Python file uses the following encoding: utf-8
import sys
import os


from PySide2.QtWidgets import QApplication, QFrame, QWidget, QDialog, QComboBox, QPushButton
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import Qt
from serial import Serial

class SerialConfigWdg(QDialog):
    def __init__(self):
        super(SerialConfigWdg, self).__init__(f=Qt.WindowTitleHint|Qt.WindowCloseButtonHint)
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "SerialConfigWdg.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()
        self.serial = None
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Configuration")
        # self.setWindowFlag(Qt.WindowTitleHint)
        # self.setWindowFlag(Qt.Dialog)
        self.comboBaud = self.findChild(QComboBox, 'comboBaud')
        self.comboBaud.addItem("1200")
        self.comboBaud.addItem("2400")
        self.comboBaud.addItem("4800")
        self.comboBaud.addItem("9600")
        self.comboBaud.addItem("19200")
        self.comboBaud.addItem("38400")
        self.comboBaud.addItem("56000")
        self.comboBaud.addItem("115200")
        self.comboBaud.addItem("128000")
        self.comboBaud.addItem("256000")
        self.comboData = self.findChild(QComboBox, 'comboData')
        self.comboData.addItem("5")
        self.comboData.addItem("6")
        self.comboData.addItem("7")
        self.comboData.addItem("8")
        self.comboData.addItem("9")
        self.comboStop = self.findChild(QComboBox, 'comboStop')
        self.comboStop.addItem("one")
        self.comboStop.addItem("one and half")
        self.comboStop.addItem("two")
        self.comboParity = self.findChild(QComboBox, 'comboParity')
        self.comboParity.addItem("None")
        self.comboParity.addItem("Even")
        self.comboParity.addItem("Odd")
        self.comboParity.addItem("Mark")
        self.comboParity.addItem("Space")
        self.comboFlow = self.findChild(QComboBox, 'comboFlow')
        self.comboFlow.addItem("None")
        self.comboFlow.addItem("XON/XOFF")
        self.comboFlow.addItem("RTS/CTS")
        self.comboFlow.addItem("DTR/DSR")
        self.pushOk = self.findChild(QPushButton, 'pushOk')
        self.pushOk.clicked.connect(self.accept)
        self.pushOk.setDefault(True)
        self.pushQuit = self.findChild(QPushButton, 'pushQuit')
        self.pushQuit.clicked.connect(self.reject)

    def setSerial(self, serial: Serial):
        self.serial = serial
        self.comboBaud.setCurrentIndex(self.comboBaud.findText(str(self.serial.baudrate)))

#  __init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)


if __name__ == "__main__":
    app = QApplication([])
    widget = SerialConfigWdg()
    widget.show()
    sys.exit(app.exec_())
