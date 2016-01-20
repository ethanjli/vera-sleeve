#!/usr/bin/env python3
"""Tests creation of a simple GUI with PyQt."""
# Python imports
import sys
import time

# Dependency imports
from PyQt4.QtGui import QApplication, QMainWindow, QAction, QTextEdit, QFileDialog, QIcon

class SimpleTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_window()

    def __init_window(self):
        # Actions
        exit_action = QAction(QIcon.fromTheme('application-exit'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application.')
        exit_action.triggered.connect(QApplication.instance().quit)
        save_action = QAction(QIcon.fromTheme('document-save-as'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save text into a file.')
        save_action.triggered.connect(self.save_dialog)
        open_action = QAction(QIcon.fromTheme('document-open'), '&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open text from a file.')
        open_action.triggered.connect(self.open_dialog)

        # Populating the menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(save_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Populating the main tool bar
        tool_bar = self.addToolBar('Exit')
        tool_bar.addAction(exit_action)
        tool_bar.addSeparator()
        tool_bar.addAction(open_action)
        tool_bar.addAction(save_action)

        # Central widget
        self.paragraph_text = QTextEdit()
        self.setCentralWidget(self.paragraph_text)

        # Window
        self.setWindowTitle("Simple GUI")
        self.setWindowIcon(QIcon.fromTheme('utilities-terminal'))
        self.statusBar().showMessage("Started.")
        self.show()

    def save_dialog(self):
        file_name = QFileDialog.getSaveFileName(self, "Save file")
        if file_name[0]:
            with open(file_name[0], 'w') as output_file:
                output_file.write(self.paragraph_text.toPlainText())
            self.statusBar().showMessage("Saved to {}".format(file_name[0]))
    def open_dialog(self):
        file_name = QFileDialog.getOpenFileName(self, "Open file")
        if file_name[0]:
            with open(file_name[0], 'r') as input_file:
                self.paragraph_text.setText(input_file.read())
            self.statusBar().showMessage("Opened {}".format(file_name[0]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    simple_text_editor = SimpleTextEditor()
    sys.exit(app.exec_())
