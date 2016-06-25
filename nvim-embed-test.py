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
        self.buffer()[:] = text.split('\n')

    def text(self):
        return '\n'.join(self.buffer()[:])

    def buffer(self):
        return self.nvim.current.buffer

    def cursorPosition(self):
        return self.nvim.windows[0].cursor

    def cursorAnchor(self):
        return [self.nvim.eval('line("v")'), self.nvim.eval('col("v")')]

    def keyPress(self, key):
        self.nvim.input(key)

    def mode(self):
        return self.eval('mode()')

    def commandLine(self):
        return self.eval('getcmdline()')

    def commandLineType(self):
        return self.eval('getcmdtype()')

    def byte(self, row, col):
        return self.eval('line2byte(' + str(row) + ')') + col - 1

    def eval(self, expr):
        return self.nvim.eval(expr)

class Editor (QTextEdit):
    """ Editor widget driven by FakeVim. """
    def __init__(self, nvim, statusBar, parent = None):
        sup = super(Editor, self)
        sup.__init__(parent)

        self.nvim = nvim
        self.statusBar = statusBar

        self.update()

    def keyPressEvent(self, e):
        key = e.text()
        if key:
            self.nvim.keyPress(key)
            self.update()

    def update(self):
        self.setPlainText(self.nvim.text())

        mode = self.nvim.mode()

        row, col = self.nvim.cursorPosition()
        cursor = QTextCursor(self.document())
        cursor.setPosition(self.nvim.byte(row, col))
        self.setTextCursor(cursor)

        selections = []

        if mode != 'i' and mode != 'v' and mode != 'V' and mode != '' and mode[0] != 'c':
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            selection.format = QTextCharFormat()
            selection.format.setBackground(Qt.black)
            selection.format.setForeground(Qt.white)
            selections.append(selection)

        if mode == 'v' or mode == 'V' or mode == '':
            row2, col2 = self.nvim.cursorAnchor()
            if row2 > 0 and col2 >= 0:
                begin = self.nvim.byte(row, col)
                end = self.nvim.byte(row2, col2)

                if end <= begin + 1:
                    begin += 1
                    end -= 1

                selection = QTextEdit.ExtraSelection()

                selection.cursor = QTextCursor(self.document())

                selection.cursor.setPosition(begin)
                if mode == 'V':
                    if begin <= end:
                        selection.cursor.movePosition(QTextCursor.StartOfBlock)
                    else:
                        selection.cursor.movePosition(QTextCursor.EndOfBlock)

                selection.cursor.setPosition(end, QTextCursor.KeepAnchor)
                if mode == 'V':
                    if end <= begin:
                        selection.cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                    else:
                        selection.cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

                selection.format = QTextCharFormat()
                selection.format.setBackground(Qt.black)
                selection.format.setForeground(Qt.white)
                selections.append(selection)

        self.setExtraSelections(selections)


        self.statusBar.setCommandLineType(self.nvim.commandLineType())
        self.statusBar.setCommandLine(self.nvim.commandLine())
        self.statusBar.setMode(mode)

class StatusBar (QStatusBar):
    def __init__(self, window):
        super(QStatusBar, self).__init__(window)

        self.mode = QLabel(self)
        self.addPermanentWidget(self.mode)

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

    def setMode(self, text):
        self.mode.setText(text)

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

