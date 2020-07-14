# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1104, 744)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setAnimated(True)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_2 = QtWidgets.QSplitter(self.centralWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.meter_combobox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.meter_combobox.sizePolicy().hasHeightForWidth())
        self.meter_combobox.setSizePolicy(sizePolicy)
        self.meter_combobox.setObjectName("meter_combobox")
        self.meter_combobox.addItem("")
        self.gridLayout_2.addWidget(self.meter_combobox, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.meter_settings_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.meter_settings_button.setMaximumSize(QtCore.QSize(40, 16777215))
        self.meter_settings_button.setObjectName("meter_settings_button")
        self.gridLayout_2.addWidget(self.meter_settings_button, 1, 2, 1, 1)
        self.clb_list_combobox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clb_list_combobox.sizePolicy().hasHeightForWidth())
        self.clb_list_combobox.setSizePolicy(sizePolicy)
        self.clb_list_combobox.setMinimumSize(QtCore.QSize(140, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.clb_list_combobox.setFont(font)
        self.clb_list_combobox.setObjectName("clb_list_combobox")
        self.gridLayout_2.addWidget(self.clb_list_combobox, 0, 1, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.add_measure_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.add_measure_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_measure_button.setIcon(icon)
        self.add_measure_button.setIconSize(QtCore.QSize(30, 30))
        self.add_measure_button.setObjectName("add_measure_button")
        self.horizontalLayout_2.addWidget(self.add_measure_button)
        self.delete_measure_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.delete_measure_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/minus2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_measure_button.setIcon(icon1)
        self.delete_measure_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_measure_button.setObjectName("delete_measure_button")
        self.horizontalLayout_2.addWidget(self.delete_measure_button)
        self.rename_measure_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.rename_measure_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rename_measure_button.setIcon(icon2)
        self.rename_measure_button.setIconSize(QtCore.QSize(30, 30))
        self.rename_measure_button.setObjectName("rename_measure_button")
        self.horizontalLayout_2.addWidget(self.rename_measure_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.enable_all_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.enable_all_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/icons/checkboxes.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.enable_all_button.setIcon(icon3)
        self.enable_all_button.setIconSize(QtCore.QSize(30, 30))
        self.enable_all_button.setObjectName("enable_all_button")
        self.horizontalLayout_2.addWidget(self.enable_all_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.measures_table = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        self.measures_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.measures_table.setStyleSheet("")
        self.measures_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.measures_table.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.measures_table.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.measures_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.measures_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.measures_table.setObjectName("measures_table")
        self.measures_table.setColumnCount(3)
        self.measures_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.measures_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.measures_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.measures_table.setHorizontalHeaderItem(2, item)
        self.measures_table.horizontalHeader().setStretchLastSection(True)
        self.measures_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.measures_table)
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.save_current_measure_button = QtWidgets.QPushButton(self.groupBox)
        self.save_current_measure_button.setMinimumSize(QtCore.QSize(35, 35))
        self.save_current_measure_button.setMaximumSize(QtCore.QSize(35, 35))
        self.save_current_measure_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/icons/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.save_current_measure_button.setIcon(icon4)
        self.save_current_measure_button.setIconSize(QtCore.QSize(25, 25))
        self.save_current_measure_button.setObjectName("save_current_measure_button")
        self.horizontalLayout_3.addWidget(self.save_current_measure_button)
        self.open_cell_config_button = QtWidgets.QPushButton(self.groupBox)
        self.open_cell_config_button.setMinimumSize(QtCore.QSize(35, 35))
        self.open_cell_config_button.setMaximumSize(QtCore.QSize(35, 35))
        self.open_cell_config_button.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_cell_config_button.setIcon(icon5)
        self.open_cell_config_button.setIconSize(QtCore.QSize(25, 25))
        self.open_cell_config_button.setObjectName("open_cell_config_button")
        self.horizontalLayout_3.addWidget(self.open_cell_config_button)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.start_current_measure_button = QtWidgets.QPushButton(self.groupBox)
        self.start_current_measure_button.setMinimumSize(QtCore.QSize(35, 35))
        self.start_current_measure_button.setMaximumSize(QtCore.QSize(35, 35))
        self.start_current_measure_button.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.start_current_measure_button.setIcon(icon6)
        self.start_current_measure_button.setIconSize(QtCore.QSize(25, 25))
        self.start_current_measure_button.setObjectName("start_current_measure_button")
        self.horizontalLayout_3.addWidget(self.start_current_measure_button)
        self.continue_current_measure_button = QtWidgets.QPushButton(self.groupBox)
        self.continue_current_measure_button.setMinimumSize(QtCore.QSize(35, 35))
        self.continue_current_measure_button.setMaximumSize(QtCore.QSize(35, 35))
        self.continue_current_measure_button.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/icons/next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.continue_current_measure_button.setIcon(icon7)
        self.continue_current_measure_button.setIconSize(QtCore.QSize(25, 25))
        self.continue_current_measure_button.setObjectName("continue_current_measure_button")
        self.horizontalLayout_3.addWidget(self.continue_current_measure_button)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.add_row_button = QtWidgets.QPushButton(self.groupBox)
        self.add_row_button.setMinimumSize(QtCore.QSize(35, 35))
        self.add_row_button.setMaximumSize(QtCore.QSize(35, 35))
        self.add_row_button.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/icons/add_row.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_row_button.setIcon(icon8)
        self.add_row_button.setIconSize(QtCore.QSize(25, 25))
        self.add_row_button.setObjectName("add_row_button")
        self.horizontalLayout_3.addWidget(self.add_row_button)
        self.remove_row_button = QtWidgets.QPushButton(self.groupBox)
        self.remove_row_button.setMinimumSize(QtCore.QSize(35, 35))
        self.remove_row_button.setMaximumSize(QtCore.QSize(35, 35))
        self.remove_row_button.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/icons/remove_row.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_row_button.setIcon(icon9)
        self.remove_row_button.setIconSize(QtCore.QSize(25, 25))
        self.remove_row_button.setObjectName("remove_row_button")
        self.horizontalLayout_3.addWidget(self.remove_row_button)
        self.add_column_button = QtWidgets.QPushButton(self.groupBox)
        self.add_column_button.setMinimumSize(QtCore.QSize(35, 35))
        self.add_column_button.setMaximumSize(QtCore.QSize(35, 35))
        self.add_column_button.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/icons/add_col.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_column_button.setIcon(icon10)
        self.add_column_button.setIconSize(QtCore.QSize(25, 25))
        self.add_column_button.setObjectName("add_column_button")
        self.horizontalLayout_3.addWidget(self.add_column_button)
        self.remove_column_button = QtWidgets.QPushButton(self.groupBox)
        self.remove_column_button.setMinimumSize(QtCore.QSize(35, 35))
        self.remove_column_button.setMaximumSize(QtCore.QSize(35, 35))
        self.remove_column_button.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icons/icons/remove_col.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_column_button.setIcon(icon11)
        self.remove_column_button.setIconSize(QtCore.QSize(25, 25))
        self.remove_column_button.setObjectName("remove_column_button")
        self.horizontalLayout_3.addWidget(self.remove_column_button)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.displayed_data_type_combobox = QtWidgets.QComboBox(self.groupBox)
        self.displayed_data_type_combobox.setObjectName("displayed_data_type_combobox")
        self.displayed_data_type_combobox.addItem("")
        self.displayed_data_type_combobox.addItem("")
        self.displayed_data_type_combobox.addItem("")
        self.displayed_data_type_combobox.addItem("")
        self.horizontalLayout_3.addWidget(self.displayed_data_type_combobox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.measure_data_view = QtWidgets.QTableView(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.measure_data_view.setFont(font)
        self.measure_data_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.measure_data_view.setStyleSheet("selection-color: rgb(0, 0, 0);\n"
"selection-background-color: rgb(170, 170, 255);")
        self.measure_data_view.setObjectName("measure_data_view")
        self.measure_data_view.horizontalHeader().setVisible(False)
        self.measure_data_view.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.measure_data_view)
        self.log_text_edit = QtWidgets.QPlainTextEdit(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.log_text_edit.sizePolicy().hasHeightForWidth())
        self.log_text_edit.setSizePolicy(sizePolicy)
        self.log_text_edit.setObjectName("log_text_edit")
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1104, 21))
        self.menuBar.setObjectName("menuBar")
        self.settings_menu = QtWidgets.QMenu(self.menuBar)
        self.settings_menu.setObjectName("settings_menu")
        self.menu = QtWidgets.QMenu(self.menuBar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menuBar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.change_fixed_range_action = QtWidgets.QAction(MainWindow)
        self.change_fixed_range_action.setObjectName("change_fixed_range_action")
        self.enter_settings_action = QtWidgets.QAction(MainWindow)
        self.enter_settings_action.setObjectName("enter_settings_action")
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.open_tstlan_action = QtWidgets.QAction(MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/icons/icons/tstlan.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_tstlan_action.setIcon(icon12)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.open_tstlan_action.setFont(font)
        self.open_tstlan_action.setObjectName("open_tstlan_action")
        self.save_action = QtWidgets.QAction(MainWindow)
        self.save_action.setIcon(icon4)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.save_action.setFont(font)
        self.save_action.setObjectName("save_action")
        self.open_action = QtWidgets.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/icons/icons/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_action.setIcon(icon13)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.open_action.setFont(font)
        self.open_action.setObjectName("open_action")
        self.save_as_action = QtWidgets.QAction(MainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/icons/icons/save_as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.save_as_action.setIcon(icon14)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.save_as_action.setFont(font)
        self.save_as_action.setObjectName("save_as_action")
        self.start_all_action = QtWidgets.QAction(MainWindow)
        self.start_all_action.setIcon(icon6)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.start_all_action.setFont(font)
        self.start_all_action.setObjectName("start_all_action")
        self.continue_all_action = QtWidgets.QAction(MainWindow)
        self.continue_all_action.setIcon(icon7)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.continue_all_action.setFont(font)
        self.continue_all_action.setObjectName("continue_all_action")
        self.stop_all_action = QtWidgets.QAction(MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/icons/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stop_all_action.setIcon(icon15)
        self.stop_all_action.setObjectName("stop_all_action")
        self.correction_action = QtWidgets.QAction(MainWindow)
        self.correction_action.setCheckable(True)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/icons/icons/correction.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.correction_action.setIcon(icon16)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.correction_action.setFont(font)
        self.correction_action.setObjectName("correction_action")
        self.flash_all_action = QtWidgets.QAction(MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/icons/icons/memory.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.flash_all_action.setIcon(icon17)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.flash_all_action.setFont(font)
        self.flash_all_action.setObjectName("flash_all_action")
        self.verify_action = QtWidgets.QAction(MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(":/icons/icons/eye_checked.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.verify_action.setIcon(icon18)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.verify_action.setFont(font)
        self.verify_action.setObjectName("verify_action")
        self.graphs_action = QtWidgets.QAction(MainWindow)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap(":/icons/icons/graph_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.graphs_action.setIcon(icon19)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.graphs_action.setFont(font)
        self.graphs_action.setObjectName("graphs_action")
        self.lock_action = QtWidgets.QAction(MainWindow)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap(":/icons/icons/lock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lock_action.setIcon(icon20)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lock_action.setFont(font)
        self.lock_action.setObjectName("lock_action")
        self.unlock_action = QtWidgets.QAction(MainWindow)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap(":/icons/icons/unlock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.unlock_action.setIcon(icon21)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.unlock_action.setFont(font)
        self.unlock_action.setObjectName("unlock_action")
        self.show_equal_action = QtWidgets.QAction(MainWindow)
        self.show_equal_action.setCheckable(True)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap(":/icons/icons/squares.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.show_equal_action.setIcon(icon22)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.show_equal_action.setFont(font)
        self.show_equal_action.setObjectName("show_equal_action")
        self.copy_cell_config_action = QtWidgets.QAction(MainWindow)
        self.copy_cell_config_action.setObjectName("copy_cell_config_action")
        self.paste_cell_config_action = QtWidgets.QAction(MainWindow)
        self.paste_cell_config_action.setObjectName("paste_cell_config_action")
        self.copy_cell_value_action = QtWidgets.QAction(MainWindow)
        self.copy_cell_value_action.setObjectName("copy_cell_value_action")
        self.paste_cell_value_action = QtWidgets.QAction(MainWindow)
        self.paste_cell_value_action.setObjectName("paste_cell_value_action")
        self.show_cell_graph_action = QtWidgets.QAction(MainWindow)
        self.show_cell_graph_action.setObjectName("show_cell_graph_action")
        self.flash_current_measure_action = QtWidgets.QAction(MainWindow)
        self.flash_current_measure_action.setObjectName("flash_current_measure_action")
        self.flash_diapason_of_cell_action = QtWidgets.QAction(MainWindow)
        self.flash_diapason_of_cell_action.setObjectName("flash_diapason_of_cell_action")
        self.settings_menu.addAction(self.enter_settings_action)
        self.menu.addAction(self.action)
        self.menuBar.addAction(self.settings_menu.menuAction())
        self.menuBar.addAction(self.menu.menuAction())
        self.toolBar.addAction(self.open_action)
        self.toolBar.addAction(self.save_action)
        self.toolBar.addAction(self.save_as_action)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.start_all_action)
        self.toolBar.addAction(self.continue_all_action)
        self.toolBar.addAction(self.stop_all_action)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.correction_action)
        self.toolBar.addAction(self.flash_all_action)
        self.toolBar.addAction(self.verify_action)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.open_tstlan_action)
        self.toolBar.addAction(self.graphs_action)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.lock_action)
        self.toolBar.addAction(self.unlock_action)
        self.toolBar.addAction(self.show_equal_action)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "Измеритель"))
        self.meter_combobox.setItemText(0, _translate("MainWindow", "Agilent 3458A"))
        self.label.setText(_translate("MainWindow", "Калибратор"))
        self.meter_settings_button.setText(_translate("MainWindow", "..."))
        self.add_measure_button.setToolTip(_translate("MainWindow", "Добавить измерение"))
        self.delete_measure_button.setToolTip(_translate("MainWindow", "Удалить измерение"))
        self.rename_measure_button.setToolTip(_translate("MainWindow", "Переименовать измерение"))
        self.enable_all_button.setToolTip(_translate("MainWindow", "Включить/выключить все"))
        item = self.measures_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Измерение"))
        item = self.measures_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Парам."))
        item = self.measures_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Вкл."))
        self.groupBox.setTitle(_translate("MainWindow", "Таблица измерения"))
        self.save_current_measure_button.setToolTip(_translate("MainWindow", "Сохранить текущее измерение"))
        self.open_cell_config_button.setToolTip(_translate("MainWindow", "Настройки ячейки"))
        self.start_current_measure_button.setToolTip(_translate("MainWindow", "Начать измерение по текущей таблице"))
        self.continue_current_measure_button.setToolTip(_translate("MainWindow", "Продолжить измерение по текущей таблице"))
        self.displayed_data_type_combobox.setItemText(0, _translate("MainWindow", "Измерено"))
        self.displayed_data_type_combobox.setItemText(1, _translate("MainWindow", "СКО"))
        self.displayed_data_type_combobox.setItemText(2, _translate("MainWindow", "Ошибка"))
        self.displayed_data_type_combobox.setItemText(3, _translate("MainWindow", "Доверительный интервал"))
        self.settings_menu.setTitle(_translate("MainWindow", "Настройки"))
        self.menu.setTitle(_translate("MainWindow", "Справка"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "Панель инструментов"))
        self.change_fixed_range_action.setText(_translate("MainWindow", "Изменить фиксированный шаг"))
        self.enter_settings_action.setText(_translate("MainWindow", "Настройки..."))
        self.action.setText(_translate("MainWindow", "О программе"))
        self.open_tstlan_action.setText(_translate("MainWindow", "tstlan"))
        self.open_tstlan_action.setToolTip(_translate("MainWindow", "Открыть tstlan"))
        self.open_tstlan_action.setShortcut(_translate("MainWindow", "T"))
        self.save_action.setText(_translate("MainWindow", "save"))
        self.save_action.setIconText(_translate("MainWindow", "save"))
        self.save_action.setToolTip(_translate("MainWindow", "Сохранить"))
        self.save_action.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.open_action.setText(_translate("MainWindow", "open_action"))
        self.open_action.setToolTip(_translate("MainWindow", "Открыть конфигурацию"))
        self.open_action.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.save_as_action.setText(_translate("MainWindow", "save_as_action"))
        self.save_as_action.setIconText(_translate("MainWindow", "save_as_action"))
        self.save_as_action.setToolTip(_translate("MainWindow", "Сохранить как..."))
        self.save_as_action.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.start_all_action.setText(_translate("MainWindow", "start_all_action"))
        self.start_all_action.setToolTip(_translate("MainWindow", "Начать измерение"))
        self.continue_all_action.setText(_translate("MainWindow", "continue_all_action"))
        self.continue_all_action.setToolTip(_translate("MainWindow", "Продолжить измерение"))
        self.stop_all_action.setText(_translate("MainWindow", "stop_all_action"))
        self.stop_all_action.setToolTip(_translate("MainWindow", "Остановить измерение"))
        self.correction_action.setText(_translate("MainWindow", "correction_action"))
        self.correction_action.setToolTip(_translate("MainWindow", "Коррекция"))
        self.flash_all_action.setText(_translate("MainWindow", "flash_all_action"))
        self.flash_all_action.setToolTip(_translate("MainWindow", "Прошить все измерения"))
        self.verify_action.setText(_translate("MainWindow", "verify_action"))
        self.verify_action.setToolTip(_translate("MainWindow", "Проверить все измерения"))
        self.graphs_action.setText(_translate("MainWindow", "graphs_action"))
        self.graphs_action.setToolTip(_translate("MainWindow", "Открыть графики"))
        self.lock_action.setText(_translate("MainWindow", "lock_action"))
        self.lock_action.setToolTip(_translate("MainWindow", "Заблокировать ячейки"))
        self.unlock_action.setText(_translate("MainWindow", "unlock_action"))
        self.unlock_action.setToolTip(_translate("MainWindow", "Разблокировать ячейки"))
        self.show_equal_action.setText(_translate("MainWindow", "show_equal_action"))
        self.show_equal_action.setToolTip(_translate("MainWindow", "Показать ячейки с одинаковыми конфигурациями"))
        self.copy_cell_config_action.setText(_translate("MainWindow", "Копировать настройки ячейки"))
        self.copy_cell_config_action.setShortcut(_translate("MainWindow", "Ctrl+C"))
        self.paste_cell_config_action.setText(_translate("MainWindow", "Вставить настройки ячейки"))
        self.paste_cell_config_action.setShortcut(_translate("MainWindow", "Ctrl+V"))
        self.copy_cell_value_action.setText(_translate("MainWindow", "Копировать значение"))
        self.paste_cell_value_action.setText(_translate("MainWindow", "Вставить значение"))
        self.show_cell_graph_action.setText(_translate("MainWindow", "График измерения"))
        self.flash_current_measure_action.setText(_translate("MainWindow", "Прошить таблицу"))
        self.flash_diapason_of_cell_action.setText(_translate("MainWindow", "Прошить диапазон ячейки"))
import icons_rc
