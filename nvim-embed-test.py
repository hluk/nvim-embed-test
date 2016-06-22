#!/usr/bin/env python
import neovim

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import os

class NVim ():
    def __init__(self):
        self.nvim = neovim.attach('child', argv=['nvim', '--embed'])

    def setText(self, text):
        self.nvim.buffers[0][:] = text.split('\n')

    def text(self):
        return '\n'.join(self.nvim.buffers[0][:])

    def cursorPosition(self):
        return self.nvim.windows[0].cursor

    def keyPress(self, key):
        self.nvim.feedkeys(key, 't')

    def commandLine(self):
        return self.eval('getcmdline()')

    def commandLineType(self):
        return self.eval('getcmdtype()')

    def eval(self, expr):
        return self.nvim.eval(expr)

class Editor (QTextEdit):
    """ Editor widget driven by FakeVim. """
    def __init__(self, nvim, statusBar, parent = None):
        sup = super(Editor, self)
        sup.__init__(parent)

        self.nvim = nvim
        self.statusBar = statusBar

        self.setPlainText(self.nvim.text())

    def keyPressEvent(self, e):
        key = e.text()
        if key:
            self.nvim.keyPress(key)

            self.setPlainText(self.nvim.text())

            row, col = self.nvim.cursorPosition()
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, row - 1)
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, col)
            self.setTextCursor(cursor)

            self.statusBar.setCommandLineType(self.nvim.commandLineType())
            self.statusBar.setCommandLine(self.nvim.commandLine())

class StatusBar (QStatusBar):
    def __init__(self, window):
        super(QStatusBar, self).__init__(window)

        self.commandLineType = QLabel(self)
        self.addPermanentWidget(self.commandLineType)

        self.commandLine = QLabel(self)
        self.commandLine.hide()
        self.addPermanentWidget(self.commandLine, 1)

        window.setStatusBar(self)

    def setCommandLineType(self, text):
        self.commandLineType.setText(text)
        self.commandLine.setVisible(text != "")

    def setCommandLine(self, text):
        self.commandLine.setText(text)

class MainWindow (QMainWindow):
    def __init__(self, nvim, parent = None):
        super(MainWindow, self).__init__(parent)
        self.statusBar = StatusBar(self)
        self.editor = Editor(nvim, self.statusBar, self)
        font = self.editor.font()
        font.setFamily("Monospace")
        self.editor.setFont(font)

        self.setCentralWidget(self.editor)

        self.move(0, 0)
        self.resize(600, 600)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

def main():
    nvim = NVim()

    if len(sys.argv) > 1:
        filePath = os.path.expanduser(sys.argv[0])

        try:
            if os.path.isfile(filePath):
                with open(filePath, 'r') as f:
                    nvim.setText(f.read())
        except:
            self.__handler.showMessage( MessageError,
                    self.tr('Cannot open file "{filePath}"')
                    .format(filePath = filePath) )

    app = QApplication(sys.argv)

    window = MainWindow(nvim)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

