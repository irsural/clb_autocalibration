# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/test_graphs_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(838, 554)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 5, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.test_number_tabbar_layout = QtWidgets.QHBoxLayout()
        self.test_number_tabbar_layout.setObjectName("test_number_tabbar_layout")
        self.verticalLayout.addLayout(self.test_number_tabbar_layout)
        self.graph_name_tabbar_layout = QtWidgets.QHBoxLayout()
        self.graph_name_tabbar_layout.setObjectName("graph_name_tabbar_layout")
        self.verticalLayout.addLayout(self.graph_name_tabbar_layout)
        self.chart_layout = QtWidgets.QHBoxLayout()
        self.chart_layout.setObjectName("chart_layout")
        self.verticalLayout.addLayout(self.chart_layout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
