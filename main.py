from irspy.qt import ui_to_py
ui_to_py.convert_ui("./ui", "./ui/py")
ui_to_py.convert_resources("./resources", ".")

import sys

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui

from irspy.dlls import mxsrlib_dll
from irspy.utils import exception_decorator_print

from mainwindow import MainWindow


@exception_decorator_print
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont("MS Shell Dlg 2", 10))

    translator = QtCore.QTranslator(app)
    path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)
    translator.load("/".join([path, "qtbase_ru.qm"]))
    app.installTranslator(translator)

    w = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    # input("Error. Press enter to continue...")
