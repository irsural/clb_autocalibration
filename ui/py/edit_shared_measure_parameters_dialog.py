# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_shared_measure_parameters_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_shared_measure_parameters_dialog(object):
    def setupUi(self, shared_measure_parameters_dialog):
        shared_measure_parameters_dialog.setObjectName("shared_measure_parameters_dialog")
        shared_measure_parameters_dialog.resize(584, 438)
        font = QtGui.QFont()
        font.setPointSize(10)
        shared_measure_parameters_dialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        shared_measure_parameters_dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(shared_measure_parameters_dialog)
        self.verticalLayout.setContentsMargins(5, 5, 5, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(shared_measure_parameters_dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.shared_parameters_splitter = QtWidgets.QSplitter(self.tab)
        self.shared_parameters_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.shared_parameters_splitter.setObjectName("shared_parameters_splitter")
        self.devices_list = QtWidgets.QListWidget(self.shared_parameters_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.devices_list.sizePolicy().hasHeightForWidth())
        self.devices_list.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.devices_list.setFont(font)
        self.devices_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.devices_list.setObjectName("devices_list")
        self.widget = QtWidgets.QWidget(self.shared_parameters_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.device_coefs_view = QtWidgets.QTableView(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.device_coefs_view.sizePolicy().hasHeightForWidth())
        self.device_coefs_view.setSizePolicy(sizePolicy)
        self.device_coefs_view.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.device_coefs_view.setObjectName("device_coefs_view")
        self.device_coefs_view.horizontalHeader().setStretchLastSection(True)
        self.device_coefs_view.verticalHeader().setVisible(True)
        self.horizontalLayout.addWidget(self.device_coefs_view)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.add_coefficient_button = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_coefficient_button.sizePolicy().hasHeightForWidth())
        self.add_coefficient_button.setSizePolicy(sizePolicy)
        self.add_coefficient_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_coefficient_button.setIcon(icon1)
        self.add_coefficient_button.setObjectName("add_coefficient_button")
        self.verticalLayout_2.addWidget(self.add_coefficient_button)
        self.remove_coefficient_button = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remove_coefficient_button.sizePolicy().hasHeightForWidth())
        self.remove_coefficient_button.setSizePolicy(sizePolicy)
        self.remove_coefficient_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_coefficient_button.setIcon(icon2)
        self.remove_coefficient_button.setObjectName("remove_coefficient_button")
        self.verticalLayout_2.addWidget(self.remove_coefficient_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout.addWidget(self.shared_parameters_splitter, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttons_layout.addItem(spacerItem1)
        self.accept_button = QtWidgets.QPushButton(shared_measure_parameters_dialog)
        self.accept_button.setDefault(True)
        self.accept_button.setObjectName("accept_button")
        self.buttons_layout.addWidget(self.accept_button)
        self.cancel_button = QtWidgets.QPushButton(shared_measure_parameters_dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_layout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.retranslateUi(shared_measure_parameters_dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(shared_measure_parameters_dialog)
        shared_measure_parameters_dialog.setTabOrder(self.tabWidget, self.devices_list)
        shared_measure_parameters_dialog.setTabOrder(self.devices_list, self.device_coefs_view)
        shared_measure_parameters_dialog.setTabOrder(self.device_coefs_view, self.add_coefficient_button)
        shared_measure_parameters_dialog.setTabOrder(self.add_coefficient_button, self.remove_coefficient_button)
        shared_measure_parameters_dialog.setTabOrder(self.remove_coefficient_button, self.accept_button)
        shared_measure_parameters_dialog.setTabOrder(self.accept_button, self.cancel_button)

    def retranslateUi(self, shared_measure_parameters_dialog):
        _translate = QtCore.QCoreApplication.translate
        shared_measure_parameters_dialog.setWindowTitle(_translate("shared_measure_parameters_dialog", "Общие параметры для всех измерений"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("shared_measure_parameters_dialog", "Коэффициенты приборов"))
        self.accept_button.setText(_translate("shared_measure_parameters_dialog", "Принять"))
        self.cancel_button.setText(_translate("shared_measure_parameters_dialog", "Отмена"))
from irspy.qt.resources import icons
