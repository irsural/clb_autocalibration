# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_settings_dialog(object):
    def setupUi(self, settings_dialog):
        settings_dialog.setObjectName("settings_dialog")
        settings_dialog.resize(547, 359)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(settings_dialog.sizePolicy().hasHeightForWidth())
        settings_dialog.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        settings_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settings_dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(settings_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.layout = QtWidgets.QWidget(settings_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.layout.sizePolicy().hasHeightForWidth())
        self.layout.setSizePolicy(sizePolicy)
        self.layout.setMaximumSize(QtCore.QSize(150, 16777215))
        self.layout.setObjectName("layout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layout)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.settings_menu_list = QtWidgets.QListWidget(self.layout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_menu_list.sizePolicy().hasHeightForWidth())
        self.settings_menu_list.setSizePolicy(sizePolicy)
        self.settings_menu_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.settings_menu_list.setStyleSheet("QListWidget::item { border-bottom: 1px solid black; }\n"
"QListWidget::item:selected:active {\n"
"    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                stop: 0 #4e55c6, stop: 1 #888dd9);\n"
"}\n"
"QListWidget:item:selected:!active {\n"
"    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                stop: 0 #4e55c6, stop: 1 #888dd9);\n"
"    color: white\n"
"}\n"
"QListWidget::item {\n"
"    height: 50;\n"
"}")
        self.settings_menu_list.setProperty("isWrapping", False)
        self.settings_menu_list.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.settings_menu_list.setViewMode(QtWidgets.QListView.ListMode)
        self.settings_menu_list.setUniformItemSizes(False)
        self.settings_menu_list.setBatchSize(200)
        self.settings_menu_list.setWordWrap(True)
        self.settings_menu_list.setSelectionRectVisible(False)
        self.settings_menu_list.setObjectName("settings_menu_list")
        item = QtWidgets.QListWidgetItem()
        self.settings_menu_list.addItem(item)
        self.verticalLayout_2.addWidget(self.settings_menu_list)
        self.gridLayout.addWidget(self.layout, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(settings_dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.settings_stackedwidget = QtWidgets.QStackedWidget(self.frame)
        self.settings_stackedwidget.setObjectName("settings_stackedwidget")
        self.measure_table_settings_layout = QtWidgets.QWidget()
        self.measure_table_settings_layout.setObjectName("measure_table_settings_layout")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.measure_table_settings_layout)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.settings_stackedwidget.addWidget(self.measure_table_settings_layout)
        self.verticalLayout.addWidget(self.settings_stackedwidget)
        self.verticalLayout_3.addWidget(self.frame)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.save_and_exit_button = QtWidgets.QPushButton(settings_dialog)
        self.save_and_exit_button.setAutoDefault(True)
        self.save_and_exit_button.setObjectName("save_and_exit_button")
        self.horizontalLayout_2.addWidget(self.save_and_exit_button)
        self.cancel_button = QtWidgets.QPushButton(settings_dialog)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.save_button = QtWidgets.QPushButton(settings_dialog)
        self.save_button.setAutoDefault(True)
        self.save_button.setDefault(True)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout_2.addWidget(self.save_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 1, 1, 1)

        self.retranslateUi(settings_dialog)
        self.settings_menu_list.setCurrentRow(-1)
        self.settings_stackedwidget.setCurrentIndex(0)
        self.settings_menu_list.currentRowChanged['int'].connect(self.settings_stackedwidget.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(settings_dialog)

    def retranslateUi(self, settings_dialog):
        _translate = QtCore.QCoreApplication.translate
        settings_dialog.setWindowTitle(_translate("settings_dialog", "Настройки"))
        self.settings_menu_list.setSortingEnabled(False)
        __sortingEnabled = self.settings_menu_list.isSortingEnabled()
        self.settings_menu_list.setSortingEnabled(False)
        item = self.settings_menu_list.item(0)
        item.setText(_translate("settings_dialog", "Таблица измерения"))
        self.settings_menu_list.setSortingEnabled(__sortingEnabled)
        self.save_and_exit_button.setText(_translate("settings_dialog", "Ок"))
        self.cancel_button.setText(_translate("settings_dialog", "Отмена"))
        self.save_button.setText(_translate("settings_dialog", "Принять"))
from irspy.qt.resources import icons
