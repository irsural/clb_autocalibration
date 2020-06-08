# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/settings_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(672, 526)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        Dialog.setFont(font)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layout = QtWidgets.QWidget(Dialog)
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
        self.horizontalLayout.addWidget(self.layout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.settings_stackedwidget = QtWidgets.QStackedWidget(self.frame)
        self.settings_stackedwidget.setObjectName("settings_stackedwidget")
        self.step_parameters_page = QtWidgets.QWidget()
        self.step_parameters_page.setObjectName("step_parameters_page")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.step_parameters_page)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.fixed_range_groupbox = QtWidgets.QGroupBox(self.step_parameters_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fixed_range_groupbox.sizePolicy().hasHeightForWidth())
        self.fixed_range_groupbox.setSizePolicy(sizePolicy)
        self.fixed_range_groupbox.setObjectName("fixed_range_groupbox")
        self.edit_fixed_step_widget_layout = QtWidgets.QVBoxLayout(self.fixed_range_groupbox)
        self.edit_fixed_step_widget_layout.setObjectName("edit_fixed_step_widget_layout")
        self.horizontalLayout_3.addWidget(self.fixed_range_groupbox)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalGroupBox_2 = QtWidgets.QGroupBox(self.step_parameters_page)
        self.verticalGroupBox_2.setObjectName("verticalGroupBox_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalGroupBox_2)
        self.verticalLayout_5.setContentsMargins(-1, 6, -1, 6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.verticalGroupBox_2)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.exact_step_spinbox = QtWidgets.QDoubleSpinBox(self.verticalGroupBox_2)
        self.exact_step_spinbox.setDecimals(3)
        self.exact_step_spinbox.setMaximum(100.0)
        self.exact_step_spinbox.setProperty("value", 0.002)
        self.exact_step_spinbox.setObjectName("exact_step_spinbox")
        self.verticalLayout_5.addWidget(self.exact_step_spinbox)
        self.label_2 = QtWidgets.QLabel(self.verticalGroupBox_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.common_step_spinbox = QtWidgets.QDoubleSpinBox(self.verticalGroupBox_2)
        self.common_step_spinbox.setDecimals(3)
        self.common_step_spinbox.setMaximum(100.0)
        self.common_step_spinbox.setProperty("value", 0.05)
        self.common_step_spinbox.setObjectName("common_step_spinbox")
        self.verticalLayout_5.addWidget(self.common_step_spinbox)
        self.label_3 = QtWidgets.QLabel(self.verticalGroupBox_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3)
        self.rough_step_spinbox = QtWidgets.QDoubleSpinBox(self.verticalGroupBox_2)
        self.rough_step_spinbox.setDecimals(3)
        self.rough_step_spinbox.setMaximum(100.0)
        self.rough_step_spinbox.setProperty("value", 0.5)
        self.rough_step_spinbox.setObjectName("rough_step_spinbox")
        self.verticalLayout_5.addWidget(self.rough_step_spinbox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.verticalLayout_4.addWidget(self.verticalGroupBox_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.settings_stackedwidget.addWidget(self.step_parameters_page)
        self.verticalLayout.addWidget(self.settings_stackedwidget)
        self.verticalLayout_3.addWidget(self.frame)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.save_and_exit_button = QtWidgets.QPushButton(Dialog)
        self.save_and_exit_button.setAutoDefault(True)
        self.save_and_exit_button.setObjectName("save_and_exit_button")
        self.horizontalLayout_2.addWidget(self.save_and_exit_button)
        self.cancel_button = QtWidgets.QPushButton(Dialog)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.save_button = QtWidgets.QPushButton(Dialog)
        self.save_button.setAutoDefault(True)
        self.save_button.setDefault(True)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout_2.addWidget(self.save_button)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.retranslateUi(Dialog)
        self.settings_menu_list.setCurrentRow(-1)
        self.settings_stackedwidget.setCurrentIndex(0)
        self.settings_menu_list.currentRowChanged['int'].connect(self.settings_stackedwidget.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Настройки"))
        self.settings_menu_list.setSortingEnabled(False)
        __sortingEnabled = self.settings_menu_list.isSortingEnabled()
        self.settings_menu_list.setSortingEnabled(False)
        item = self.settings_menu_list.item(0)
        item.setText(_translate("Dialog", "Параметры шага"))
        self.settings_menu_list.setSortingEnabled(__sortingEnabled)
        self.fixed_range_groupbox.setTitle(_translate("Dialog", "Фиксированный шаг"))
        self.verticalGroupBox_2.setWhatsThis(_translate("Dialog", "Относительный шаг устанавливается в процентах от максимума шкалы поверяемого прибора"))
        self.verticalGroupBox_2.setTitle(_translate("Dialog", "Относительный шаг"))
        self.label.setText(_translate("Dialog", "Точный, %"))
        self.label_2.setText(_translate("Dialog", "Обычный, %"))
        self.label_3.setText(_translate("Dialog", "Грубый, %"))
        self.save_and_exit_button.setText(_translate("Dialog", "Ок"))
        self.cancel_button.setText(_translate("Dialog", "Отмена"))
        self.save_button.setText(_translate("Dialog", "Принять"))
import icons_rc
