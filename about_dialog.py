from PyQt5 import QtGui, QtWidgets, QtCore

from ui.py.about_dialog import Ui_about_dialog as AboutForm
import app_info
import datetime


class AboutDialog(QtWidgets.QDialog):

    def __init__(self, a_parent=None):
        super().__init__(a_parent)

        self.ui = AboutForm()
        self.ui.setupUi(self)
        self.show()

        self.ui.version_label.setText(f"Версия программы: {app_info.VERSION}")
        self.ui.copyright_year_label.setText(str(datetime.datetime.now().year))

        self.ui.close_button.clicked.connect(self.reject)

    def __del__(self):
        print("About deleted")
