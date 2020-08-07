from irspy.qt import ui_to_py
ui_to_py.convert_ui("./ui", "./ui/py")
ui_to_py.convert_resources("./resources", ".")


import traceback


def main():
    # Импорты здесь, чтобы ловить их исключения в скомпиленной версии программы, если они возникнут при импорте
    import sys

    from PyQt5.QtWidgets import QApplication
    from PyQt5 import QtCore, QtGui

    from mainwindow import MainWindow

    # Попробовать это, если будут проблемы с размерами иконок на дисплеях с высоким разрешением
    # os.environ["QT_SCALE_FACTOR"] = "1"
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

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
    try:
        main()
    except Exception as err:
        print(traceback.format_exc())
        input("Error. Press enter to continue...")
