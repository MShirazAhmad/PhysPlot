#!/usr/bin/env python
'''
    File name: PhysPlot.py
    Authors: Muhammad Shiraz Ahmad and Sabieh Anwar
    Date created: 8/20/2019
    Date last modified: 8/29/2019
    Script Version: 1.1.2 (Bleeding Edge)
    Python Version: 3.7.3
'''
import PyQt5
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QApplication, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import webbrowser

class Ui_ConfigWindow(object):
    def setupUiConfigWindow(self, ConfigWindow):
        ConfigWindow.setObjectName("ConfigWindow")
        ConfigWindow.resize(440, 555)
        ConfigWindow.setMinimumSize(QtCore.QSize(413, 550))
        self.centralwidget = QtWidgets.QWidget(ConfigWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_12.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_12, 1, 0, 1, 1)
        self.tabWidget1 = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.tabWidget1.setFont(font)
        self.tabWidget1.setObjectName("tabWidget1")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(self.tab_1)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 377, 562))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_Grid_Style = QtWidgets.QLabel(self.groupBox)
        self.label_Grid_Style.setObjectName("label_Grid_Style")
        self.verticalLayout_2.addWidget(self.label_Grid_Style)
        self.label_Grid_Width = QtWidgets.QLabel(self.groupBox)
        self.label_Grid_Width.setObjectName("label_Grid_Width")
        self.verticalLayout_2.addWidget(self.label_Grid_Width)
        self.label_Grid_Color = QtWidgets.QLabel(self.groupBox)
        self.label_Grid_Color.setObjectName("label_Grid_Color")
        self.verticalLayout_2.addWidget(self.label_Grid_Color)
        self.gridLayout_6.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox_Grid_Style = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_Grid_Style.setObjectName("comboBox_Grid_Style")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        self.comboBox_Grid_Style.addItem("")
        validator = QtGui.QDoubleValidator()
        self.verticalLayout.addWidget(self.comboBox_Grid_Style)
        self.lineEdit_Grid_Width = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_Grid_Width.setValidator(validator)
        self.lineEdit_Grid_Width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly|QtCore.Qt.ImhFormattedNumbersOnly)
        self.lineEdit_Grid_Width.setObjectName("lineEdit_Grid_Width")
        self.verticalLayout.addWidget(self.lineEdit_Grid_Width)
        self.comboBox_Grid_Color = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_Grid_Color.setObjectName("comboBox_Grid_Color")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.comboBox_Grid_Color.addItem("")
        self.verticalLayout.addWidget(self.comboBox_Grid_Color)
        self.gridLayout_6.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_Marker_Style = QtWidgets.QLabel(self.groupBox_2)
        self.label_Marker_Style.setObjectName("label_Marker_Style")
        self.verticalLayout_4.addWidget(self.label_Marker_Style)
        self.label_Marker_Size = QtWidgets.QLabel(self.groupBox_2)
        self.label_Marker_Size.setObjectName("label_Marker_Size")
        self.verticalLayout_4.addWidget(self.label_Marker_Size)
        self.label_Marker_Color = QtWidgets.QLabel(self.groupBox_2)
        self.label_Marker_Color.setObjectName("label_Marker_Color")
        self.verticalLayout_4.addWidget(self.label_Marker_Color)
        self.gridLayout_7.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.comboBox_Marker_Style = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_Marker_Style.setObjectName("comboBox_Marker_Style")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.comboBox_Marker_Style.addItem("")
        self.verticalLayout_3.addWidget(self.comboBox_Marker_Style)
        self.lineEdit_Marker_Size = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_Marker_Size.setValidator(validator)
        self.lineEdit_Marker_Size.setInputMethodHints(QtCore.Qt.ImhDigitsOnly|QtCore.Qt.ImhFormattedNumbersOnly)
        self.lineEdit_Marker_Size.setObjectName("lineEdit_Marker_Size")
        self.verticalLayout_3.addWidget(self.lineEdit_Marker_Size)
        self.comboBox_Marker_Color = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_Marker_Color.setObjectName("comboBox_Marker_Color")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.comboBox_Marker_Color.addItem("")
        self.verticalLayout_3.addWidget(self.comboBox_Marker_Color)
        self.gridLayout_7.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_Line_Style = QtWidgets.QLabel(self.groupBox_3)
        self.label_Line_Style.setObjectName("label_Line_Style")
        self.verticalLayout_5.addWidget(self.label_Line_Style)
        self.label_Line_Width = QtWidgets.QLabel(self.groupBox_3)
        self.label_Line_Width.setObjectName("label_Line_Width")
        self.verticalLayout_5.addWidget(self.label_Line_Width)
        self.label_Line_Color = QtWidgets.QLabel(self.groupBox_3)
        self.label_Line_Color.setObjectName("label_Line_Color")
        self.verticalLayout_5.addWidget(self.label_Line_Color)
        self.gridLayout_8.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.comboBox_Line_Style = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_Line_Style.setObjectName("comboBox_Line_Style")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.comboBox_Line_Style.addItem("")
        self.verticalLayout_6.addWidget(self.comboBox_Line_Style)
        self.lineEdit_Line_Width = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_Line_Width.setValidator(validator)
        self.lineEdit_Line_Width.setInputMethodHints(QtCore.Qt.ImhDigitsOnly|QtCore.Qt.ImhFormattedNumbersOnly)
        self.lineEdit_Line_Width.setObjectName("lineEdit_Line_Width")
        self.verticalLayout_6.addWidget(self.lineEdit_Line_Width)
        self.comboBox_Line_Color = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_Line_Color.setObjectName("comboBox_Line_Color")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.comboBox_Line_Color.addItem("")
        self.verticalLayout_6.addWidget(self.comboBox_Line_Color)
        self.gridLayout_8.addLayout(self.verticalLayout_6, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_title = QtWidgets.QLabel(self.groupBox_6)
        self.label_title.setObjectName("label_title")
        self.verticalLayout_9.addWidget(self.label_title)
        self.label_xLable = QtWidgets.QLabel(self.groupBox_6)
        self.label_xLable.setObjectName("label_xLable")
        self.verticalLayout_9.addWidget(self.label_xLable)
        self.label_yLable = QtWidgets.QLabel(self.groupBox_6)
        self.label_yLable.setObjectName("label_yLable")
        self.verticalLayout_9.addWidget(self.label_yLable)
        self.label_Legend = QtWidgets.QLabel(self.groupBox_6)
        self.label_Legend.setObjectName("label_Legend")
        self.verticalLayout_9.addWidget(self.label_Legend)
        self.gridLayout_9.addLayout(self.verticalLayout_9, 0, 0, 1, 1)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.lineEdit_PlotLabel = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotLabel.setObjectName("lineEdit_PlotLabel")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotLabel)
        self.lineEdit_PlotxLabel = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotxLabel.setObjectName("lineEdit_PlotxLabel")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotxLabel)
        self.lineEdit_PlotyLabel = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotyLabel.setObjectName("lineEdit_PlotyLabel")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotyLabel)
        self.lineEdit_PlotLegend = QtWidgets.QLineEdit(self.groupBox_6)
        self.lineEdit_PlotLegend.setObjectName("lineEdit_PlotLegend")
        self.verticalLayout_10.addWidget(self.lineEdit_PlotLegend)
        self.gridLayout_9.addLayout(self.verticalLayout_10, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_6, 3, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget1.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_4.setMinimumSize(QtCore.QSize(0, 401))
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 401))
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.checkBox__crvft_1 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_1.setObjectName("checkBox__crvft_1")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_1)
        self.checkBox__crvft_2 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_2.setObjectName("checkBox__crvft_2")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_2)
        self.checkBox__crvft_3 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_3.setObjectName("checkBox__crvft_3")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_3)
        self.checkBox__crvft_4 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_4.setObjectName("checkBox__crvft_4")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_4)
        self.checkBox__crvft_5 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_5.setObjectName("checkBox__crvft_5")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_5)
        self.checkBox__crvft_6 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_6.setObjectName("checkBox__crvft_6")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_6)
        self.checkBox__crvft_7 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_7.setObjectName("checkBox__crvft_7")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_7)
        self.checkBox__crvft_8 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_8.setObjectName("checkBox__crvft_8")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_8)
        self.checkBox__crvft_9 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_9.setObjectName("checkBox__crvft_9")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_9)
        self.checkBox__crvft_10 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_10.setObjectName("checkBox__crvft_10")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_10)
        self.checkBox__crvft_11 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox__crvft_11.setObjectName("checkBox__crvft_11")
        self.verticalLayout_7.addWidget(self.checkBox__crvft_11)
        self.gridLayout_5.addWidget(self.groupBox_4, 0, 0, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_5.setMinimumSize(QtCore.QSize(0, 401))
        self.groupBox_5.setMaximumSize(QtCore.QSize(16777215, 401))
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_27 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.radioButton_off_crvft_1 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_off_crvft_1.setChecked(True)
        self.radioButton_off_crvft_1.setAutoRepeat(True)
        self.radioButton_off_crvft_1.setAutoExclusive(False)
        self.radioButton_off_crvft_1.setObjectName("radioButton_off_crvft_1")
        self.horizontalLayout_27.addWidget(self.radioButton_off_crvft_1)
        self.radioButton_Equation_crvft_1 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_1.setAutoExclusive(False)
        self.radioButton_Equation_crvft_1.setObjectName("radioButton_Equation_crvft_1")
        self.horizontalLayout_27.addWidget(self.radioButton_Equation_crvft_1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButton_Label_crvft_1 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_1.setText("")
        self.radioButton_Label_crvft_1.setAutoExclusive(False)
        self.radioButton_Label_crvft_1.setObjectName("radioButton_Label_crvft_1")
        self.horizontalLayout.addWidget(self.radioButton_Label_crvft_1)
        self.lineEdit_crvft_1 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_1.setObjectName("lineEdit_crvft_1")
        self.horizontalLayout.addWidget(self.lineEdit_crvft_1)
        self.horizontalLayout_27.addLayout(self.horizontalLayout)
        self.verticalLayout_8.addLayout(self.horizontalLayout_27)
        self.horizontalLayout_28 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_28.setObjectName("horizontalLayout_28")
        self.radioButton__off_crvft_2 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_2.setChecked(True)
        self.radioButton__off_crvft_2.setAutoExclusive(False)
        self.radioButton__off_crvft_2.setObjectName("radioButton__off_crvft_2")
        self.horizontalLayout_28.addWidget(self.radioButton__off_crvft_2)
        self.radioButton_Equation_crvft_2 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_2.setAutoExclusive(False)
        self.radioButton_Equation_crvft_2.setObjectName("radioButton_Equation_crvft_2")
        self.horizontalLayout_28.addWidget(self.radioButton_Equation_crvft_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButton_Label_crvft_2 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_2.setText("")
        self.radioButton_Label_crvft_2.setAutoExclusive(False)
        self.radioButton_Label_crvft_2.setObjectName("radioButton_Label_crvft_2")
        self.horizontalLayout_2.addWidget(self.radioButton_Label_crvft_2)
        self.lineEdit_crvft_2 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_2.setObjectName("lineEdit_crvft_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_crvft_2)
        self.horizontalLayout_28.addLayout(self.horizontalLayout_2)
        self.verticalLayout_8.addLayout(self.horizontalLayout_28)
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.radioButton__off_crvft_3 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_3.setChecked(True)
        self.radioButton__off_crvft_3.setAutoExclusive(False)
        self.radioButton__off_crvft_3.setObjectName("radioButton__off_crvft_3")
        self.horizontalLayout_29.addWidget(self.radioButton__off_crvft_3)
        self.radioButton_Equation_crvft_3 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_3.setAutoExclusive(False)
        self.radioButton_Equation_crvft_3.setObjectName("radioButton_Equation_crvft_3")
        self.horizontalLayout_29.addWidget(self.radioButton_Equation_crvft_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.radioButton_Label_crvft_3 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_3.setText("")
        self.radioButton_Label_crvft_3.setAutoExclusive(False)
        self.radioButton_Label_crvft_3.setObjectName("radioButton_Label_crvft_3")
        self.horizontalLayout_3.addWidget(self.radioButton_Label_crvft_3)
        self.lineEdit_crvft_3 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_3.setObjectName("lineEdit_crvft_3")
        self.horizontalLayout_3.addWidget(self.lineEdit_crvft_3)
        self.horizontalLayout_29.addLayout(self.horizontalLayout_3)
        self.verticalLayout_8.addLayout(self.horizontalLayout_29)
        self.horizontalLayout_30 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_30.setObjectName("horizontalLayout_30")
        self.radioButton__off_crvft_4 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_4.setChecked(True)
        self.radioButton__off_crvft_4.setAutoExclusive(False)
        self.radioButton__off_crvft_4.setObjectName("radioButton__off_crvft_4")
        self.horizontalLayout_30.addWidget(self.radioButton__off_crvft_4)
        self.radioButton_Equation_crvft_4 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_4.setAutoExclusive(False)
        self.radioButton_Equation_crvft_4.setObjectName("radioButton_Equation_crvft_4")
        self.horizontalLayout_30.addWidget(self.radioButton_Equation_crvft_4)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.radioButton_Label_crvft_4 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_4.setText("")
        self.radioButton_Label_crvft_4.setAutoExclusive(False)
        self.radioButton_Label_crvft_4.setObjectName("radioButton_Label_crvft_4")
        self.horizontalLayout_4.addWidget(self.radioButton_Label_crvft_4)
        self.lineEdit_crvft_4 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_4.setObjectName("lineEdit_crvft_4")
        self.horizontalLayout_4.addWidget(self.lineEdit_crvft_4)
        self.horizontalLayout_30.addLayout(self.horizontalLayout_4)
        self.verticalLayout_8.addLayout(self.horizontalLayout_30)
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        self.radioButton__off_crvft_5 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_5.setChecked(True)
        self.radioButton__off_crvft_5.setAutoExclusive(False)
        self.radioButton__off_crvft_5.setObjectName("radioButton__off_crvft_5")
        self.horizontalLayout_31.addWidget(self.radioButton__off_crvft_5)
        self.radioButton_Equation_crvft_5 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_5.setAutoExclusive(False)
        self.radioButton_Equation_crvft_5.setObjectName("radioButton_Equation_crvft_5")
        self.horizontalLayout_31.addWidget(self.radioButton_Equation_crvft_5)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.radioButton_Label_crvft_5 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_5.setText("")
        self.radioButton_Label_crvft_5.setAutoExclusive(False)
        self.radioButton_Label_crvft_5.setObjectName("radioButton_Label_crvft_5")
        self.horizontalLayout_5.addWidget(self.radioButton_Label_crvft_5)
        self.lineEdit_crvft_5 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_5.setObjectName("lineEdit_crvft_5")
        self.horizontalLayout_5.addWidget(self.lineEdit_crvft_5)
        self.horizontalLayout_31.addLayout(self.horizontalLayout_5)
        self.verticalLayout_8.addLayout(self.horizontalLayout_31)
        self.horizontalLayout_32 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_32.setObjectName("horizontalLayout_32")
        self.radioButton__off_crvft_6 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_6.setChecked(True)
        self.radioButton__off_crvft_6.setAutoExclusive(False)
        self.radioButton__off_crvft_6.setObjectName("radioButton__off_crvft_6")
        self.horizontalLayout_32.addWidget(self.radioButton__off_crvft_6)
        self.radioButton_Equation_crvft_6 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_6.setAutoExclusive(False)
        self.radioButton_Equation_crvft_6.setObjectName("radioButton_Equation_crvft_6")
        self.horizontalLayout_32.addWidget(self.radioButton_Equation_crvft_6)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.radioButton_Label_crvft_6 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_6.setText("")
        self.radioButton_Label_crvft_6.setAutoExclusive(False)
        self.radioButton_Label_crvft_6.setObjectName("radioButton_Label_crvft_6")
        self.horizontalLayout_6.addWidget(self.radioButton_Label_crvft_6)
        self.lineEdit_crvft_6 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_6.setObjectName("lineEdit_crvft_6")
        self.horizontalLayout_6.addWidget(self.lineEdit_crvft_6)
        self.horizontalLayout_32.addLayout(self.horizontalLayout_6)
        self.verticalLayout_8.addLayout(self.horizontalLayout_32)
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.radioButton__off_crvft_7 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_7.setChecked(True)
        self.radioButton__off_crvft_7.setAutoExclusive(False)
        self.radioButton__off_crvft_7.setObjectName("radioButton__off_crvft_7")
        self.horizontalLayout_33.addWidget(self.radioButton__off_crvft_7)
        self.radioButton_Equation_crvft_7 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_7.setAutoExclusive(False)
        self.radioButton_Equation_crvft_7.setObjectName("radioButton_Equation_crvft_7")
        self.horizontalLayout_33.addWidget(self.radioButton_Equation_crvft_7)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.radioButton_Label_crvft_7 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_7.setText("")
        self.radioButton_Label_crvft_7.setAutoExclusive(False)
        self.radioButton_Label_crvft_7.setObjectName("radioButton_Label_crvft_7")
        self.horizontalLayout_7.addWidget(self.radioButton_Label_crvft_7)
        self.lineEdit_crvft_7 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_7.setObjectName("lineEdit_crvft_7")
        self.horizontalLayout_7.addWidget(self.lineEdit_crvft_7)
        self.horizontalLayout_33.addLayout(self.horizontalLayout_7)
        self.verticalLayout_8.addLayout(self.horizontalLayout_33)
        self.horizontalLayout_34 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_34.setObjectName("horizontalLayout_34")
        self.radioButton__off_crvft_8 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_8.setChecked(True)
        self.radioButton__off_crvft_8.setAutoExclusive(False)
        self.radioButton__off_crvft_8.setObjectName("radioButton__off_crvft_8")
        self.horizontalLayout_34.addWidget(self.radioButton__off_crvft_8)
        self.radioButton_Equation_crvft_8 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_8.setAutoExclusive(False)
        self.radioButton_Equation_crvft_8.setObjectName("radioButton_Equation_crvft_8")
        self.horizontalLayout_34.addWidget(self.radioButton_Equation_crvft_8)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.radioButton_Label_crvft_8 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_8.setText("")
        self.radioButton_Label_crvft_8.setAutoExclusive(False)
        self.radioButton_Label_crvft_8.setObjectName("radioButton_Label_crvft_8")
        self.horizontalLayout_8.addWidget(self.radioButton_Label_crvft_8)
        self.lineEdit_crvft_8 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_8.setObjectName("lineEdit_crvft_8")
        self.horizontalLayout_8.addWidget(self.lineEdit_crvft_8)
        self.horizontalLayout_34.addLayout(self.horizontalLayout_8)
        self.verticalLayout_8.addLayout(self.horizontalLayout_34)
        self.horizontalLayout_35 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.radioButton__off_crvft_9 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_9.setChecked(True)
        self.radioButton__off_crvft_9.setAutoExclusive(False)
        self.radioButton__off_crvft_9.setObjectName("radioButton__off_crvft_9")
        self.horizontalLayout_35.addWidget(self.radioButton__off_crvft_9)
        self.radioButton_Equation_crvft_9 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_9.setAutoExclusive(False)
        self.radioButton_Equation_crvft_9.setObjectName("radioButton_Equation_crvft_9")
        self.horizontalLayout_35.addWidget(self.radioButton_Equation_crvft_9)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.radioButton_Label_crvft_9 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_9.setText("")
        self.radioButton_Label_crvft_9.setAutoExclusive(False)
        self.radioButton_Label_crvft_9.setObjectName("radioButton_Label_crvft_9")
        self.horizontalLayout_9.addWidget(self.radioButton_Label_crvft_9)
        self.lineEdit_crvft_9 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_9.setObjectName("lineEdit_crvft_9")
        self.horizontalLayout_9.addWidget(self.lineEdit_crvft_9)
        self.horizontalLayout_35.addLayout(self.horizontalLayout_9)
        self.verticalLayout_8.addLayout(self.horizontalLayout_35)
        self.horizontalLayout_36 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_36.setObjectName("horizontalLayout_36")
        self.radioButton__off_crvft_10 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_10.setChecked(True)
        self.radioButton__off_crvft_10.setAutoExclusive(False)
        self.radioButton__off_crvft_10.setObjectName("radioButton__off_crvft_10")
        self.horizontalLayout_36.addWidget(self.radioButton__off_crvft_10)
        self.radioButton_Equation_crvft_10 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_10.setAutoExclusive(False)
        self.radioButton_Equation_crvft_10.setObjectName("radioButton_Equation_crvft_10")
        self.horizontalLayout_36.addWidget(self.radioButton_Equation_crvft_10)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.radioButton_Label_crvft_10 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_10.setText("")
        self.radioButton_Label_crvft_10.setAutoExclusive(False)
        self.radioButton_Label_crvft_10.setObjectName("radioButton_Label_crvft_10")
        self.horizontalLayout_10.addWidget(self.radioButton_Label_crvft_10)
        self.lineEdit_crvft_10 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_10.setObjectName("lineEdit_crvft_10")
        self.horizontalLayout_10.addWidget(self.lineEdit_crvft_10)
        self.horizontalLayout_36.addLayout(self.horizontalLayout_10)
        self.verticalLayout_8.addLayout(self.horizontalLayout_36)
        self.horizontalLayout_37 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_37.setObjectName("horizontalLayout_37")
        self.radioButton__off_crvft_11 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton__off_crvft_11.setChecked(True)
        self.radioButton__off_crvft_11.setAutoExclusive(False)
        self.radioButton__off_crvft_11.setObjectName("radioButton__off_crvft_11")
        self.horizontalLayout_37.addWidget(self.radioButton__off_crvft_11)
        self.radioButton_Equation_crvft_11 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Equation_crvft_11.setAutoExclusive(False)
        self.radioButton_Equation_crvft_11.setObjectName("radioButton_Equation_crvft_11")
        self.horizontalLayout_37.addWidget(self.radioButton_Equation_crvft_11)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.radioButton_Label_crvft_11 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_Label_crvft_11.setText("")
        self.radioButton_Label_crvft_11.setAutoExclusive(False)
        self.radioButton_Label_crvft_11.setObjectName("radioButton_Label_crvft_11")
        self.horizontalLayout_11.addWidget(self.radioButton_Label_crvft_11)
        self.lineEdit_crvft_11 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_crvft_11.setObjectName("lineEdit_crvft_11")
        self.horizontalLayout_11.addWidget(self.lineEdit_crvft_11)
        self.horizontalLayout_37.addLayout(self.horizontalLayout_11)
        self.verticalLayout_8.addLayout(self.horizontalLayout_37)
        self.gridLayout_5.addWidget(self.groupBox_5, 0, 1, 1, 1)
        self.tabWidget1.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget1, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        ConfigWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ConfigWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 440, 21))
        self.menubar.setObjectName("menubar")
        ConfigWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ConfigWindow)
        self.statusbar.setObjectName("statusbar")
        ConfigWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ConfigWindow)
        self.tabWidget1.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ConfigWindow)

    def retranslateUi(self, ConfigWindow):
        _translate = QtCore.QCoreApplication.translate
        ConfigWindow.setWindowTitle(_translate("ConfigWindow", "Configuration"))
        ConfigWindow.setWindowIcon(QtGui.QIcon('ico.ico'))
        self.pushButton.setText(_translate("ConfigWindow", "Apply"))
        self.groupBox.setTitle(_translate("ConfigWindow", "Grid Line"))
        self.label_Grid_Style.setText(_translate("ConfigWindow", "Style:"))
        self.label_Grid_Width.setText(_translate("ConfigWindow", "Width:"))
        self.label_Grid_Color.setText(_translate("ConfigWindow", "Color:"))
        self.comboBox_Grid_Style.setItemText(0, _translate("ConfigWindow", "Dotted Line"))
        self.comboBox_Grid_Style.setItemText(1, _translate("ConfigWindow", "Solid Line"))
        self.comboBox_Grid_Style.setItemText(2, _translate("ConfigWindow", "Dashed Line"))
        self.comboBox_Grid_Style.setItemText(3, _translate("ConfigWindow", "Dash-Dotted Line"))
        self.comboBox_Grid_Style.setItemText(4, _translate("ConfigWindow", "Draw Nothing"))
        self.lineEdit_Grid_Width.setText(_translate("ConfigWindow", "0.3"))
        self.comboBox_Grid_Color.setItemText(0, _translate("ConfigWindow", "Black"))
        self.comboBox_Grid_Color.setItemText(1, _translate("ConfigWindow", "Green"))
        self.comboBox_Grid_Color.setItemText(2, _translate("ConfigWindow", "Red"))
        self.comboBox_Grid_Color.setItemText(3, _translate("ConfigWindow", "Cyan"))
        self.comboBox_Grid_Color.setItemText(4, _translate("ConfigWindow", "Magenta"))
        self.comboBox_Grid_Color.setItemText(5, _translate("ConfigWindow", "Yellow"))
        self.comboBox_Grid_Color.setItemText(6, _translate("ConfigWindow", "White"))
        self.comboBox_Grid_Color.setItemText(7, _translate("ConfigWindow", "White"))
        self.groupBox_2.setTitle(_translate("ConfigWindow", "Marker"))
        self.label_Marker_Style.setText(_translate("ConfigWindow", "Style:"))
        self.label_Marker_Size.setText(_translate("ConfigWindow", "Size:"))
        self.label_Marker_Color.setText(_translate("ConfigWindow", "Color:"))
        self.comboBox_Marker_Style.setItemText(0, _translate("ConfigWindow", "Draw Nothing"))
        self.comboBox_Marker_Style.setItemText(1, _translate("ConfigWindow", "Point"))
        self.comboBox_Marker_Style.setItemText(2, _translate("ConfigWindow", "Pixel"))
        self.comboBox_Marker_Style.setItemText(3, _translate("ConfigWindow", "Circle"))
        self.comboBox_Marker_Style.setItemText(4, _translate("ConfigWindow", "Triangle-Down"))
        self.comboBox_Marker_Style.setItemText(5, _translate("ConfigWindow", "Triangle-Up"))
        self.comboBox_Marker_Style.setItemText(6, _translate("ConfigWindow", "Triangle-Left"))
        self.comboBox_Marker_Style.setItemText(7, _translate("ConfigWindow", "Triangle-Right"))
        self.comboBox_Marker_Style.setItemText(8, _translate("ConfigWindow", "Tri-Down"))
        self.comboBox_Marker_Style.setItemText(9, _translate("ConfigWindow", "Tri-Up"))
        self.comboBox_Marker_Style.setItemText(10, _translate("ConfigWindow", "Tri-Left"))
        self.comboBox_Marker_Style.setItemText(11, _translate("ConfigWindow", "Tri-Right"))
        self.comboBox_Marker_Style.setItemText(12, _translate("ConfigWindow", "Octagon"))
        self.comboBox_Marker_Style.setItemText(13, _translate("ConfigWindow", "Square"))
        self.comboBox_Marker_Style.setItemText(14, _translate("ConfigWindow", "Pentagon"))
        self.comboBox_Marker_Style.setItemText(15, _translate("ConfigWindow", "Star"))
        self.comboBox_Marker_Style.setItemText(16, _translate("ConfigWindow", "Hexagon1"))
        self.comboBox_Marker_Style.setItemText(17, _translate("ConfigWindow", "Hexagon2"))
        self.comboBox_Marker_Style.setItemText(18, _translate("ConfigWindow", "Plus"))
        self.comboBox_Marker_Style.setItemText(19, _translate("ConfigWindow", "x"))
        self.comboBox_Marker_Style.setItemText(20, _translate("ConfigWindow", "Diamond"))
        self.comboBox_Marker_Style.setItemText(21, _translate("ConfigWindow", "Thin-Diamond"))
        self.comboBox_Marker_Style.setItemText(22, _translate("ConfigWindow", "V-Line"))
        self.comboBox_Marker_Style.setItemText(23, _translate("ConfigWindow", "H-Line"))
        self.lineEdit_Marker_Size.setText(_translate("ConfigWindow", "1"))
        self.comboBox_Marker_Color.setItemText(0, _translate("ConfigWindow", "Red"))
        self.comboBox_Marker_Color.setItemText(1, _translate("ConfigWindow", "Green"))
        self.comboBox_Marker_Color.setItemText(2, _translate("ConfigWindow", "Blue"))
        self.comboBox_Marker_Color.setItemText(3, _translate("ConfigWindow", "Cyan"))
        self.comboBox_Marker_Color.setItemText(4, _translate("ConfigWindow", "Magenta"))
        self.comboBox_Marker_Color.setItemText(5, _translate("ConfigWindow", "Yellow"))
        self.comboBox_Marker_Color.setItemText(6, _translate("ConfigWindow", "Black"))
        self.comboBox_Marker_Color.setItemText(7, _translate("ConfigWindow", "White"))
        self.groupBox_3.setTitle(_translate("ConfigWindow", "Plot Line"))
        self.label_Line_Style.setText(_translate("ConfigWindow", "Style"))
        self.label_Line_Width.setText(_translate("ConfigWindow", "Width"))
        self.label_Line_Color.setText(_translate("ConfigWindow", "Color"))
        self.comboBox_Line_Style.setItemText(0, _translate("ConfigWindow", "Solid Line"))
        self.comboBox_Line_Style.setItemText(1, _translate("ConfigWindow", "Dotted Line"))
        self.comboBox_Line_Style.setItemText(2, _translate("ConfigWindow", "Dashed Line"))
        self.comboBox_Line_Style.setItemText(3, _translate("ConfigWindow", "Dash-Dotted Line"))
        self.comboBox_Line_Style.setItemText(4, _translate("ConfigWindow", "Draw Nothing"))
        self.lineEdit_Line_Width.setText(_translate("ConfigWindow", "1"))
        self.comboBox_Line_Color.setItemText(0, _translate("ConfigWindow", "Blue"))
        self.comboBox_Line_Color.setItemText(1, _translate("ConfigWindow", "Green"))
        self.comboBox_Line_Color.setItemText(2, _translate("ConfigWindow", "Red"))
        self.comboBox_Line_Color.setItemText(3, _translate("ConfigWindow", "Cyan"))
        self.comboBox_Line_Color.setItemText(4, _translate("ConfigWindow", "Magenta"))
        self.comboBox_Line_Color.setItemText(5, _translate("ConfigWindow", "Yellow"))
        self.comboBox_Line_Color.setItemText(6, _translate("ConfigWindow", "Black"))
        self.comboBox_Line_Color.setItemText(7, _translate("ConfigWindow", "White"))
        self.groupBox_6.setTitle(_translate("ConfigWindow", "Labels"))
        self.label_title.setText(_translate("ConfigWindow", "Title:"))
        self.label_xLable.setText(_translate("ConfigWindow", "xLabel:"))
        self.label_yLable.setText(_translate("ConfigWindow", "yLabel:"))
        self.label_Legend.setText(_translate("ConfigWindow", "Legend:"))
        self.lineEdit_PlotLabel.setText(_translate("ConfigWindow", "title"))
        self.lineEdit_PlotxLabel.setText(_translate("ConfigWindow", "x-axis"))
        self.lineEdit_PlotyLabel.setText(_translate("ConfigWindow", "y-axis"))
        self.lineEdit_PlotLegend.setText(_translate("ConfigWindow", "data"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tab_1), _translate("ConfigWindow", "Plot Formating"))
        self.groupBox_4.setTitle(_translate("ConfigWindow", "Curve Fit Type"))
        self.checkBox__crvft_1.setText(_translate("ConfigWindow", "Linear"))
        self.checkBox__crvft_2.setText(_translate("ConfigWindow", "Quardratic"))
        self.checkBox__crvft_3.setText(_translate("ConfigWindow", "Cubic"))
        self.checkBox__crvft_4.setText(_translate("ConfigWindow", "4th degree"))
        self.checkBox__crvft_5.setText(_translate("ConfigWindow", "5th degree"))
        self.checkBox__crvft_6.setText(_translate("ConfigWindow", "6th degree"))
        self.checkBox__crvft_7.setText(_translate("ConfigWindow", "7th degree"))
        self.checkBox__crvft_8.setText(_translate("ConfigWindow", "8th degree"))
        self.checkBox__crvft_9.setText(_translate("ConfigWindow", "9th degree"))
        self.checkBox__crvft_10.setText(_translate("ConfigWindow", "10th degree"))
        self.checkBox__crvft_11.setText(_translate("ConfigWindow", "A*exp(-bx)"))
        self.groupBox_5.setTitle(_translate("ConfigWindow", "Curve Fit Label"))
        self.radioButton_off_crvft_1.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_1.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_1.setText(_translate("ConfigWindow", "crvft_1"))
        self.radioButton__off_crvft_2.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_2.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_2.setText(_translate("ConfigWindow", "crvft_2"))
        self.radioButton__off_crvft_3.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_3.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_3.setText(_translate("ConfigWindow", "crvft_3"))
        self.radioButton__off_crvft_4.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_4.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_4.setText(_translate("ConfigWindow", "crvft_4"))
        self.radioButton__off_crvft_5.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_5.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_5.setText(_translate("ConfigWindow", "crvft_5"))
        self.radioButton__off_crvft_6.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_6.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_6.setText(_translate("ConfigWindow", "crvft_6"))
        self.radioButton__off_crvft_7.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_7.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_7.setText(_translate("ConfigWindow", "crvft_7"))
        self.radioButton__off_crvft_8.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_8.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_8.setText(_translate("ConfigWindow", "crvft_8"))
        self.radioButton__off_crvft_9.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_9.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_9.setText(_translate("ConfigWindow", "crvft_9"))
        self.radioButton__off_crvft_10.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_10.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_10.setText(_translate("ConfigWindow", "crvft_10"))
        self.radioButton__off_crvft_11.setText(_translate("ConfigWindow", "Off"))
        self.radioButton_Equation_crvft_11.setText(_translate("ConfigWindow", "Equation"))
        self.lineEdit_crvft_11.setText(_translate("ConfigWindow", "crvft_11"))
        self.tabWidget1.setTabText(self.tabWidget1.indexOf(self.tab_2), _translate("ConfigWindow", "Curve Fitting"))

        self.sourceScript()
    def sourceScript(self):

        # delayCmd.delay(self)

        # Tab 1
        #  self.comboBox_Grid_Style.activated[str].connect(self.onActivated_Grid_Style)
        self.lineEdit_Grid_Width.setText("0.3")
        #  self.comboBox_Grid_Color.activated[str].connect(self.onActivated_Grid_Color)

        #   self.comboBox_Marker_Style.activated[str].connect(self.onActivated_Marker_Style)
        self.lineEdit_Marker_Size.setText("2")
        #  self.comboBox_Marker_Color.activated[str].connect(self.onActivated_Marker_Color)

        #  self.comboBox_Line_Style.activated[str].connect(self.onActivated_Line_Style)
        self.lineEdit_Line_Width.setText("1")
        #  self.comboBox_Line_Color.activated[str].connect(self.onActivated_Line_Style)
        self.pushButton.clicked.connect(self.definePlotParameters)
        import numpy as np
        global plt_LableData
        plt_LableData = np.zeros((11, 4))
        plt_LableData[:, 1] = 1
        self.radioButton_off_crvft_1.clicked.connect(self.onClicked_radioButton_off_crvft_1)
        self.radioButton_Equation_crvft_1.clicked.connect(self.onClicked_radioButton_Equation_crvft_1)
        self.radioButton_Label_crvft_1.clicked.connect(self.onClicked_radioButton_Label_crvft_1)
        self.radioButton__off_crvft_2.clicked.connect(self.onClicked_radioButton_off_crvft_2)
        self.radioButton_Equation_crvft_2.clicked.connect(self.onClicked_radioButton_Equation_crvft_2)
        self.radioButton_Label_crvft_2.clicked.connect(self.onClicked_radioButton_Label_crvft_2)
        self.radioButton__off_crvft_3.clicked.connect(self.onClicked_radioButton_off_crvft_3)
        self.radioButton_Equation_crvft_3.clicked.connect(self.onClicked_radioButton_Equation_crvft_3)
        self.radioButton_Label_crvft_3.clicked.connect(self.onClicked_radioButton_Label_crvft_3)
        self.radioButton__off_crvft_4.clicked.connect(self.onClicked_radioButton_off_crvft_4)
        self.radioButton_Equation_crvft_4.clicked.connect(self.onClicked_radioButton_Equation_crvft_4)
        self.radioButton_Label_crvft_4.clicked.connect(self.onClicked_radioButton_Label_crvft_4)
        self.radioButton__off_crvft_5.clicked.connect(self.onClicked_radioButton_off_crvft_5)
        self.radioButton_Equation_crvft_5.clicked.connect(self.onClicked_radioButton_Equation_crvft_5)
        self.radioButton_Label_crvft_5.clicked.connect(self.onClicked_radioButton_Label_crvft_5)
        self.radioButton__off_crvft_6.clicked.connect(self.onClicked_radioButton_off_crvft_6)
        self.radioButton_Equation_crvft_6.clicked.connect(self.onClicked_radioButton_Equation_crvft_6)
        self.radioButton_Label_crvft_6.clicked.connect(self.onClicked_radioButton_Label_crvft_6)
        self.radioButton__off_crvft_7.clicked.connect(self.onClicked_radioButton_off_crvft_7)
        self.radioButton_Equation_crvft_7.clicked.connect(self.onClicked_radioButton_Equation_crvft_7)
        self.radioButton_Label_crvft_7.clicked.connect(self.onClicked_radioButton_Label_crvft_7)
        self.radioButton__off_crvft_8.clicked.connect(self.onClicked_radioButton_off_crvft_8)
        self.radioButton_Equation_crvft_8.clicked.connect(self.onClicked_radioButton_Equation_crvft_8)
        self.radioButton_Label_crvft_8.clicked.connect(self.onClicked_radioButton_Label_crvft_8)
        self.radioButton__off_crvft_9.clicked.connect(self.onClicked_radioButton_off_crvft_9)
        self.radioButton_Equation_crvft_9.clicked.connect(self.onClicked_radioButton_Equation_crvft_9)
        self.radioButton_Label_crvft_9.clicked.connect(self.onClicked_radioButton_Label_crvft_9)
        self.radioButton__off_crvft_10.clicked.connect(self.onClicked_radioButton_off_crvft_10)
        self.radioButton_Equation_crvft_10.clicked.connect(self.onClicked_radioButton_Equation_crvft_10)
        self.radioButton_Label_crvft_10.clicked.connect(self.onClicked_radioButton_Label_crvft_10)
        self.radioButton__off_crvft_11.clicked.connect(self.onClicked_radioButton_off_crvft_11)
        self.radioButton_Equation_crvft_11.clicked.connect(self.onClicked_radioButton_Equation_crvft_11)
        self.radioButton_Label_crvft_11.clicked.connect(self.onClicked_radioButton_Label_crvft_11)

        self.checkBox__crvft_1.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_2.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_3.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_4.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_5.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_6.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_7.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_8.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_9.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_10.stateChanged.connect(self.readFitType)
        self.checkBox__crvft_11.stateChanged.connect(self.readFitType)

        self.lineEdit_crvft_1.setText("Linear")
        self.lineEdit_crvft_2.setText("Quardratic")
        self.lineEdit_crvft_3.setText("Cubic")
        self.lineEdit_crvft_4.setText("4th degree")
        self.lineEdit_crvft_5.setText("5th degree")
        self.lineEdit_crvft_6.setText("6th degree")
        self.lineEdit_crvft_7.setText("7th degree")
        self.lineEdit_crvft_8.setText("8th degree")
        self.lineEdit_crvft_9.setText("9th degree")
        self.lineEdit_crvft_10.setText("10th degree")
        self.lineEdit_crvft_11.setText("Ae^(-bx)")
        global Grid_Style
        global Grid_Width
        global Grid_Color
        global Marker_Style
        global Marker_Size
        global Marker_Color
        global Line_Style
        global Line_Width
        global Line_Color
        global Label_lineEdit_crvft_1
        global Label_lineEdit_crvft_2
        global Label_lineEdit_crvft_3
        global Label_lineEdit_crvft_4
        global Label_lineEdit_crvft_5
        global Label_lineEdit_crvft_6
        global Label_lineEdit_crvft_7
        global Label_lineEdit_crvft_8
        global Label_lineEdit_crvft_9
        global Label_lineEdit_crvft_10
        global Label_lineEdit_crvft_11
        global Label_PlotLabel
        global Label_PlotxLabel
        global Label_PlotyLabel
        global Label_PlotLegend

        Label_PlotLabel = str(self.lineEdit_PlotLabel.text())
        Label_PlotxLabel = str(self.lineEdit_PlotxLabel.text())
        Label_PlotyLabel = str(self.lineEdit_PlotyLabel.text())
        Label_PlotLegend = str(self.lineEdit_PlotLegend.text())

        Label_lineEdit_crvft_1 = str(self.lineEdit_crvft_1.text())
        Label_lineEdit_crvft_2 = str(self.lineEdit_crvft_2.text())
        Label_lineEdit_crvft_3 = str(self.lineEdit_crvft_3.text())
        Label_lineEdit_crvft_4 = str(self.lineEdit_crvft_4.text())
        Label_lineEdit_crvft_5 = str(self.lineEdit_crvft_5.text())
        Label_lineEdit_crvft_6 = str(self.lineEdit_crvft_6.text())
        Label_lineEdit_crvft_7 = str(self.lineEdit_crvft_7.text())
        Label_lineEdit_crvft_8 = str(self.lineEdit_crvft_8.text())
        Label_lineEdit_crvft_9 = str(self.lineEdit_crvft_9.text())
        Label_lineEdit_crvft_10 = str(self.lineEdit_crvft_10.text())
        Label_lineEdit_crvft_11 = str(self.lineEdit_crvft_11.text())
        Grid_Style = self.comboBox_Grid_Style.currentText()
        Grid_Width = self.lineEdit_Grid_Width.text()
        Grid_Color = self.comboBox_Grid_Color.currentText()
        Marker_Style = self.comboBox_Marker_Style.currentText()
        Marker_Size = self.lineEdit_Marker_Size.text()
        Marker_Color = self.comboBox_Marker_Color.currentText()
        Line_Style = self.comboBox_Line_Style.currentText()
        Line_Width = self.lineEdit_Line_Width.text()
        Line_Color = self.comboBox_Line_Color.currentText()

        """
        Label_lineEdit_crvft_1= str(self.lineEdit_crvft_1.text())
        Label_lineEdit_crvft_2= str(self.lineEdit_crvft_2.text())
        Label_lineEdit_crvft_3= str(self.lineEdit_crvft_3.text())
        Label_lineEdit_crvft_4= str(self.lineEdit_crvft_4.text())
        Label_lineEdit_crvft_5 = str(self.lineEdit_crvft_5.text())
        Label_lineEdit_crvft_6 = str(self.lineEdit_crvft_6.text())
        Label_lineEdit_crvft_7 = str(self.lineEdit_crvft_7.text())
        Label_lineEdit_crvft_8 = str(self.lineEdit_crvft_8.text())
        Label_lineEdit_crvft_9 = str(self.lineEdit_crvft_9.text())
        Label_lineEdit_crvft_10 = str(self.lineEdit_crvft_10.text())
        Label_lineEdit_crvft_11 = str(self.lineEdit_crvft_11.text())
        """
    def readFitType(self):
        if self.checkBox__crvft_1.isChecked() == True:
            plt_LableData[0, 0] = True
        else:
            plt_LableData[0, 0] = False
        if self.checkBox__crvft_2.isChecked() == True:
            plt_LableData[1, 0] = True
        else:
            plt_LableData[1, 0] = False
        if self.checkBox__crvft_3.isChecked() == True:
            plt_LableData[2, 0] = True
        else:
            plt_LableData[2, 0] = False
        if self.checkBox__crvft_4.isChecked() == True:
            plt_LableData[3, 0] = True
        else:
            plt_LableData[3, 0] = False
        if self.checkBox__crvft_5.isChecked() == True:
            plt_LableData[4, 0] = True
        else:
            plt_LableData[4, 0] = False
        if self.checkBox__crvft_6.isChecked() == True:
            plt_LableData[5, 0] = True
        else:
            plt_LableData[5, 0] = False
        if self.checkBox__crvft_7.isChecked() == True:
            plt_LableData[6, 0] = True
        else:
            plt_LableData[6, 0] = False
        if self.checkBox__crvft_8.isChecked() == True:
            plt_LableData[7, 0] = True
        else:
            plt_LableData[7, 0] = False
        if self.checkBox__crvft_9.isChecked() == True:
            plt_LableData[8, 0] = True
        else:
            plt_LableData[8, 0] = False
        if self.checkBox__crvft_10.isChecked() == True:
            plt_LableData[9, 0] = True
        else:
            plt_LableData[9, 0] = False
        if self.checkBox__crvft_11.isChecked() == True:
            plt_LableData[10, 0] = True
        else:
            plt_LableData[10, 0] = False
    def onClicked_radioButton_off_crvft_1(self):
        self.radioButton_off_crvft_1.setChecked(True)
        self.radioButton_Equation_crvft_1.setChecked(False)
        self.radioButton_Label_crvft_1.setChecked(False)
        plt_LableData[0, 1] = True
        plt_LableData[0, 2] = False
        plt_LableData[0, 3] = False
    def onClicked_radioButton_Equation_crvft_1(self):
        self.radioButton_Equation_crvft_1.setChecked(True)
        self.radioButton_off_crvft_1.setChecked(False)
        self.radioButton_Label_crvft_1.setChecked(False)
        plt_LableData[0, 1] = False
        plt_LableData[0, 2] = True
        plt_LableData[0, 3] = False
    def onClicked_radioButton_Label_crvft_1(self):
        self.radioButton_Label_crvft_1.setChecked(True)
        self.radioButton_off_crvft_1.setChecked(False)
        self.radioButton_Equation_crvft_1.setChecked(False)
        plt_LableData[0, 1] = False
        plt_LableData[0, 2] = False
        plt_LableData[0, 3] = True
    def onClicked_radioButton_off_crvft_2(self):
        self.radioButton__off_crvft_2.setChecked(True)
        self.radioButton_Equation_crvft_2.setChecked(False)
        self.radioButton_Label_crvft_2.setChecked(False)
        plt_LableData[1, 1] = True
        plt_LableData[1, 2] = False
        plt_LableData[1, 3] = False
    def onClicked_radioButton_Equation_crvft_2(self):
        self.radioButton_Equation_crvft_2.setChecked(True)
        self.radioButton__off_crvft_2.setChecked(False)
        self.radioButton_Label_crvft_2.setChecked(False)
        plt_LableData[1, 1] = False
        plt_LableData[1, 2] = True
        plt_LableData[1, 3] = False
    def onClicked_radioButton_Label_crvft_2(self):
        self.radioButton_Label_crvft_2.setChecked(True)
        self.radioButton__off_crvft_2.setChecked(False)
        self.radioButton_Equation_crvft_2.setChecked(False)
        plt_LableData[1, 1] = False
        plt_LableData[1, 2] = False
        plt_LableData[1, 3] = True
    def onClicked_radioButton_off_crvft_3(self):
        self.radioButton__off_crvft_3.setChecked(True)
        self.radioButton_Equation_crvft_3.setChecked(False)
        self.radioButton_Label_crvft_3.setChecked(False)
        plt_LableData[2, 1] = True
        plt_LableData[2, 2] = False
        plt_LableData[2, 3] = False
    def onClicked_radioButton_Equation_crvft_3(self):
        self.radioButton_Equation_crvft_3.setChecked(True)
        self.radioButton__off_crvft_3.setChecked(False)
        self.radioButton_Label_crvft_3.setChecked(False)
        plt_LableData[2, 1] = False
        plt_LableData[2, 2] = True
        plt_LableData[2, 3] = False
    def onClicked_radioButton_Label_crvft_3(self):
        self.radioButton_Label_crvft_3.setChecked(True)
        self.radioButton__off_crvft_3.setChecked(False)
        self.radioButton_Equation_crvft_3.setChecked(False)
        plt_LableData[2, 1] = False
        plt_LableData[2, 2] = False
        plt_LableData[2, 3] = True
    def onClicked_radioButton_off_crvft_4(self):
        self.radioButton__off_crvft_4.setChecked(True)
        self.radioButton_Equation_crvft_4.setChecked(False)
        self.radioButton_Label_crvft_4.setChecked(False)
        plt_LableData[3, 1] = True
        plt_LableData[3, 2] = False
        plt_LableData[3, 3] = False
    def onClicked_radioButton_Equation_crvft_4(self):
        self.radioButton_Equation_crvft_4.setChecked(True)
        self.radioButton__off_crvft_4.setChecked(False)
        self.radioButton_Label_crvft_4.setChecked(False)
        plt_LableData[3, 1] = False
        plt_LableData[3, 2] = True
        plt_LableData[3, 3] = False
    def onClicked_radioButton_Label_crvft_4(self):
        self.radioButton_Label_crvft_4.setChecked(True)
        self.radioButton__off_crvft_4.setChecked(False)
        self.radioButton_Equation_crvft_4.setChecked(False)
        plt_LableData[3, 1] = False
        plt_LableData[3, 2] = False
        plt_LableData[3, 3] = True
    def onClicked_radioButton_off_crvft_5(self):
        self.radioButton__off_crvft_5.setChecked(True)
        self.radioButton_Equation_crvft_5.setChecked(False)
        self.radioButton_Label_crvft_5.setChecked(False)
        plt_LableData[4, 1] = True
        plt_LableData[4, 2] = False
        plt_LableData[4, 3] = False
    def onClicked_radioButton_Equation_crvft_5(self):
        self.radioButton_Equation_crvft_5.setChecked(True)
        self.radioButton__off_crvft_5.setChecked(False)
        self.radioButton_Label_crvft_5.setChecked(False)
        plt_LableData[4, 1] = False
        plt_LableData[4, 2] = True
        plt_LableData[4, 3] = False
    def onClicked_radioButton_Label_crvft_5(self):
        self.radioButton_Label_crvft_5.setChecked(True)
        self.radioButton__off_crvft_5.setChecked(False)
        self.radioButton_Equation_crvft_5.setChecked(False)
        plt_LableData[4, 1] = False
        plt_LableData[4, 2] = False
        plt_LableData[4, 3] = True
    def onClicked_radioButton_off_crvft_6(self):
        self.radioButton__off_crvft_6.setChecked(True)
        self.radioButton_Equation_crvft_6.setChecked(False)
        self.radioButton_Label_crvft_6.setChecked(False)
        plt_LableData[5, 1] = True
        plt_LableData[5, 2] = False
        plt_LableData[5, 3] = False
    def onClicked_radioButton_Equation_crvft_6(self):
        self.radioButton_Equation_crvft_6.setChecked(True)
        self.radioButton__off_crvft_6.setChecked(False)
        self.radioButton_Label_crvft_6.setChecked(False)
        plt_LableData[5, 1] = False
        plt_LableData[5, 2] = True
        plt_LableData[5, 3] = False
    def onClicked_radioButton_Label_crvft_6(self):
        self.radioButton_Label_crvft_6.setChecked(True)
        self.radioButton__off_crvft_6.setChecked(False)
        self.radioButton_Equation_crvft_6.setChecked(False)
        plt_LableData[5, 1] = False
        plt_LableData[5, 2] = False
        plt_LableData[5, 3] = True
    def onClicked_radioButton_off_crvft_7(self):
        self.radioButton__off_crvft_7.setChecked(True)
        self.radioButton_Equation_crvft_7.setChecked(False)
        self.radioButton_Label_crvft_7.setChecked(False)
        plt_LableData[6, 1] = True
        plt_LableData[6, 2] = False
        plt_LableData[6, 3] = False
    def onClicked_radioButton_Equation_crvft_7(self):
        self.radioButton_Equation_crvft_7.setChecked(True)
        self.radioButton__off_crvft_7.setChecked(False)
        self.radioButton_Label_crvft_7.setChecked(False)
        plt_LableData[6, 1] = False
        plt_LableData[6, 2] = True
        plt_LableData[6, 3] = False
    def onClicked_radioButton_Label_crvft_7(self):
        self.radioButton_Label_crvft_7.setChecked(True)
        self.radioButton__off_crvft_7.setChecked(False)
        self.radioButton_Equation_crvft_7.setChecked(False)
        plt_LableData[6, 1] = False
        plt_LableData[6, 2] = False
        plt_LableData[6, 3] = True
    def onClicked_radioButton_off_crvft_8(self):
        self.radioButton__off_crvft_8.setChecked(True)
        self.radioButton_Equation_crvft_8.setChecked(False)
        self.radioButton_Label_crvft_8.setChecked(False)
        plt_LableData[7, 1] = True
        plt_LableData[7, 2] = False
        plt_LableData[7, 3] = False
    def onClicked_radioButton_Equation_crvft_8(self):
        self.radioButton_Equation_crvft_8.setChecked(True)
        self.radioButton__off_crvft_8.setChecked(False)
        self.radioButton_Label_crvft_8.setChecked(False)
        plt_LableData[7, 1] = False
        plt_LableData[7, 2] = True
        plt_LableData[7, 3] = False
    def onClicked_radioButton_Label_crvft_8(self):
        self.radioButton_Label_crvft_8.setChecked(True)
        self.radioButton__off_crvft_8.setChecked(False)
        self.radioButton_Equation_crvft_8.setChecked(False)
        plt_LableData[7, 1] = False
        plt_LableData[7, 2] = False
        plt_LableData[7, 3] = True
    def onClicked_radioButton_off_crvft_9(self):
        self.radioButton__off_crvft_9.setChecked(True)
        self.radioButton_Equation_crvft_9.setChecked(False)
        self.radioButton_Label_crvft_9.setChecked(False)
        plt_LableData[8, 1] = True
        plt_LableData[8, 2] = False
        plt_LableData[8, 3] = False
    def onClicked_radioButton_Equation_crvft_9(self):
        self.radioButton_Equation_crvft_9.setChecked(True)
        self.radioButton__off_crvft_9.setChecked(False)
        self.radioButton_Label_crvft_9.setChecked(False)
        plt_LableData[8, 1] = False
        plt_LableData[8, 2] = True
        plt_LableData[8, 3] = False
    def onClicked_radioButton_Label_crvft_9(self):
        self.radioButton_Label_crvft_9.setChecked(True)
        self.radioButton__off_crvft_9.setChecked(False)
        self.radioButton_Equation_crvft_9.setChecked(False)
        plt_LableData[8, 1] = False
        plt_LableData[8, 2] = False
        plt_LableData[8, 3] = True
    def onClicked_radioButton_off_crvft_10(self):
        self.radioButton__off_crvft_10.setChecked(True)
        self.radioButton_Equation_crvft_10.setChecked(False)
        self.radioButton_Label_crvft_10.setChecked(False)
        plt_LableData[9, 1] = True
        plt_LableData[9, 2] = False
        plt_LableData[9, 3] = False
    def onClicked_radioButton_Equation_crvft_10(self):
        self.radioButton_Equation_crvft_10.setChecked(True)
        self.radioButton__off_crvft_10.setChecked(False)
        self.radioButton_Label_crvft_10.setChecked(False)
        plt_LableData[9, 1] = False
        plt_LableData[9, 2] = True
        plt_LableData[9, 3] = False
    def onClicked_radioButton_Label_crvft_10(self):
        self.radioButton_Label_crvft_10.setChecked(True)
        self.radioButton__off_crvft_10.setChecked(False)
        self.radioButton_Equation_crvft_10.setChecked(False)
        plt_LableData[9, 1] = False
        plt_LableData[9, 2] = False
        plt_LableData[9, 3] = True
    def onClicked_radioButton_off_crvft_11(self):
        self.radioButton__off_crvft_11.setChecked(True)
        self.radioButton_Equation_crvft_11.setChecked(False)
        self.radioButton_Label_crvft_11.setChecked(False)
        plt_LableData[10, 1] = True
        plt_LableData[10, 2] = False
        plt_LableData[10, 3] = False
    def onClicked_radioButton_Equation_crvft_11(self):
        self.radioButton_Equation_crvft_11.setChecked(True)
        self.radioButton__off_crvft_11.setChecked(False)
        self.radioButton_Label_crvft_11.setChecked(False)
        plt_LableData[10, 1] = False
        plt_LableData[10, 2] = True
        plt_LableData[10, 3] = False
    def onClicked_radioButton_Label_crvft_11(self):
        self.radioButton_Label_crvft_11.setChecked(True)
        self.radioButton__off_crvft_11.setChecked(False)
        self.radioButton_Equation_crvft_11.setChecked(False)
        plt_LableData[10, 1] = False
        plt_LableData[10, 2] = False
        plt_LableData[10, 3] = True
    def definePlotParameters(self):
        global Grid_Style
        global Grid_Width
        global Grid_Color
        global Marker_Style
        global Marker_Size
        global Marker_Color
        global Line_Style
        global Line_Width
        global Line_Color
        global Label_lineEdit_crvft_1
        global Label_lineEdit_crvft_2
        global Label_lineEdit_crvft_3
        global Label_lineEdit_crvft_4
        global Label_lineEdit_crvft_5
        global Label_lineEdit_crvft_6
        global Label_lineEdit_crvft_7
        global Label_lineEdit_crvft_8
        global Label_lineEdit_crvft_9
        global Label_lineEdit_crvft_10
        global Label_lineEdit_crvft_11
        global Label_PlotLabel
        global Label_PlotxLabel
        global Label_PlotyLabel
        global Label_PlotLegend
        Label_PlotLabel= str(self.lineEdit_PlotLabel.text())
        Label_PlotxLabel= str(self.lineEdit_PlotxLabel.text())
        Label_PlotyLabel= str(self.lineEdit_PlotyLabel.text())
        Label_PlotLegend= str(self.lineEdit_PlotLegend.text())
        Label_lineEdit_crvft_1 = str(self.lineEdit_crvft_1.text())
        Label_lineEdit_crvft_2 = str(self.lineEdit_crvft_2.text())
        Label_lineEdit_crvft_3 = str(self.lineEdit_crvft_3.text())
        Label_lineEdit_crvft_4 = str(self.lineEdit_crvft_4.text())
        Label_lineEdit_crvft_5 = str(self.lineEdit_crvft_5.text())
        Label_lineEdit_crvft_6 = str(self.lineEdit_crvft_6.text())
        Label_lineEdit_crvft_7 = str(self.lineEdit_crvft_7.text())
        Label_lineEdit_crvft_8 = str(self.lineEdit_crvft_8.text())
        Label_lineEdit_crvft_9 = str(self.lineEdit_crvft_9.text())
        Label_lineEdit_crvft_10 = str(self.lineEdit_crvft_10.text())
        Label_lineEdit_crvft_11 = str(self.lineEdit_crvft_11.text())
        Grid_Style       =    self.comboBox_Grid_Style.currentText()
        Grid_Width   =     self.lineEdit_Grid_Width.text()
        Grid_Color = self.comboBox_Grid_Color.currentText()
        Marker_Style=self.comboBox_Marker_Style.currentText()
        Marker_Size=self.lineEdit_Marker_Size.text()
        Marker_Color=self.comboBox_Marker_Color.currentText()
        Line_Style=self.comboBox_Line_Style.currentText()
        Line_Width=self.lineEdit_Line_Width.text()
        Line_Color=self.comboBox_Line_Color.currentText()
        try:
            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 3).count(True) == 1:
                Plot_Window().show()
        except Exception as e:
            pass


class about_gui(QWidget):

    def __init__(self):
        super().__init__()
    #    self.title = ''
    #    self.left = 1
    #    self.top = 1
    #    self.width = 1
    #    self.height = 1
        self.setWindowIcon(QtGui.QIcon('ico.ico'))
        self.initUI()

    def initUI(self):
        message = "<p><strong>PhysPlot<br /></strong>Version: 1.1.0 - Bleeding Edge (8/23/2019)</p><p><strong>Created by:</strong> <a href='mailto:shiraz.phy@gmail.com'>Muhammad Shiraz Ahmad</a> and <a href='mailto:sabieh@gmail.com'>Muhammad Sabieh Anwar</a></p><p><strong>Important Links: </strong><a href='https://www.physlab.org/'>PhysLab.org</a>, <a href='https://www.qosain.pk/'>Qosain.pk</a></p><p><strong>License:</strong> <a href='https://www.gnu.org/licenses/gpl-3.0.en.html'>GNU General Public License v3.0</a></p><p>Copyright &copy; 2019, all rights reserved.</p>"
        buttonReply = QMessageBox.question(self, 'About', message,
                                           QMessageBox.Ok, QMessageBox.Ok)
        self.show()


class pick_file_to_append(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Please Pick multiple Physlogger' exported files"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon('ico.ico'))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNamesDialog()
        self.show()
    def openFileNamesDialog(self):
        global files
        options = QFileDialog.Options()
        options |= QFileDialog.DontConfirmOverwrite
        files, _ = QFileDialog.getOpenFileName(self, "Pick Variables File", "",
                                                "All Files (*);;Excel Files (*.xlsx);; CSV (*.csv);;TSV (*.txt)", options=options)

class SaveFile(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon('ico.ico'))
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.saveFileDialog()

        self.show()

    def saveFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "",
                                                  "Text Files (*.txt);;All Files (*)")
        if fileName:
            global exportFilePath
            exportFilePath = fileName
            np.savetxt(exportFilePath, np.around(np.single(OutPut_Table), decimals=6), delimiter='\t', fmt='%.3f')


class Plot_Window(QDialog):
    def __init__(self, parent=None):
        super(Plot_Window, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon('ico.ico'))
        self.setWindowTitle("PhysPlot - Plot Window")
        # a figure instance to plot on
        self.figure = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # set the layout
        Markers = {"Point": ".", "Pixel": ",", "Circle": "o", "Triangle-Down": "v", "Triangle-Up": "^",
                   "Triangle-Left": "<", "Triangle-Right": ">", "Tri-Down": "1", "Tri-Up": "2", "Tri-Left": "3",
                   "Tri-Right": "4", "Octagon": "8", "Square": "s", "Pentagon": "p", "Star": "*", "Hexagon1": "h",
                   "Hexagon2": "H", "Plus": "+", "x": "x", "Diamond": "D", "Thin-Diamond": "d", "V-Line": "|",
                   "H-Line": "_", "Draw Nothing": "None"}
        Linestyle = {"Solid Line":"-", "Dashed Line": "--", "Dash-Dotted Line": "-.", "Dotted Line": ":", "Draw Nothing": "None"}
        Color = {"Blue": "b", "Green": "g", "Red": "r", "Cyan": "c", "Magenta": "m", "Yellow": "y", "Black": "k",
                 "White": "w"}
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        if list(tableLabels == 1).count(True) == 1:
            x = OutPut_Table[:, xIndex]
        if list(tableLabels == 2).count(True) == 1:
            xerr = OutPut_Table[:, uxIndex]
        if list(tableLabels == 3).count(True) == 1:
            y = OutPut_Table[:, yIndex]
        if list(tableLabels == 4).count(True) == 1:
            yerr = OutPut_Table[:, uyIndex]
        plt.xlabel(Label_PlotxLabel)
        plt.ylabel(Label_PlotyLabel)
        plt.title(Label_PlotLabel)
        ax = self.figure.add_subplot(111)
        ax.grid(color=Color[Grid_Color], linestyle=Linestyle[Grid_Style], linewidth=float(Grid_Width))
        try:
#        slope, intercept, r_value, p_value, stderr = linregress(x, y)
#        Equation = 'y = ' + str(np.round(slope, 7)) + 'x + ' + str(np.round(intercept, 7))
            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 2).count(True) == 1 and list(tableLabels == 3).count(True) == 1 and list(tableLabels == 4).count(True) == 1:
                plt.errorbar(x, y, yerr=yerr, xerr=xerr,
                             marker=Markers[Marker_Style],
                             markeredgecolor=Color[Marker_Color],
                             markersize=float(Marker_Size),
                             linestyle=Linestyle[Line_Style],
                             Linewidth=float(Line_Width),
                             color=Color[Line_Color],
                             elinewidth=1,
                             capsize=5,
                             capthick=1,
                             label=Label_PlotLegend,)

            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 2).count(True) == 0 and list(
                    tableLabels == 3).count(True) == 1 and list(tableLabels == 4).count(True) == 1:
                plt.errorbar(x, y, yerr=yerr,
                             marker=Markers[Marker_Style],
                             markeredgecolor=Color[Marker_Color],
                             markersize=float(Marker_Size),
                             linestyle=Linestyle[Line_Style],
                             Linewidth=float(Line_Width),
                             color=Color[Line_Color],
                             elinewidth=1,
                             capsize=5,
                             capthick=1,
                             label=Label_PlotLegend, )


            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 2).count(True) == 1 and list(
                    tableLabels == 3).count(True) == 1 and list(tableLabels == 4).count(True) == 0:
                plt.errorbar(x, y, xerr=xerr,
                             marker=Markers[Marker_Style],
                             markeredgecolor=Color[Marker_Color],
                             markersize=float(Marker_Size),
                             linestyle=Linestyle[Line_Style],
                             Linewidth=float(Line_Width),
                             color=Color[Line_Color],
                             elinewidth=1,
                             capsize=5,
                             capthick=1,
                             label=Label_PlotLegend, )

            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 2).count(True) == 0 and list(
                    tableLabels == 3).count(True) == 1 and list(tableLabels == 4).count(True) == 0:
                plt.errorbar(x, y,
                             marker=Markers[Marker_Style],
                             markeredgecolor=Color[Marker_Color],
                             markersize=float(Marker_Size),
                             linestyle=Linestyle[Line_Style],
                             Linewidth=float(Line_Width),
                             color=Color[Line_Color],
                             elinewidth=1,
                             capsize=5,
                             capthick=1,
                             label=Label_PlotLegend, )
        except Exception as e:
            self.errMessage("Generating Plot:", str(e))

        try:
            # P01
            try:
                if plt_LableData[0, 0] == True:
                    z01 = np.polyfit(x, y, 1)
                    if plt_LableData[0, 1] == True:
                        Label=""
                    if plt_LableData[0, 3] == True:
                        Label = Label_lineEdit_crvft_1
                    if plt_LableData[0, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, b={B[1]:2.2g}'.format(B=z01)
                    p01 = np.poly1d(z01)
                    plt.plot(x, p01(x), '-', label=Label)
            except Exception as e:
                self.errMessage("Linear Fit:", str(e))

            # P02
            try:
                if plt_LableData[1, 0] == True:
                    z02 = np.polyfit(x, y, 2)
                    p02 = np.poly1d(z02)
                    if plt_LableData[1, 1] == True:
                        Label=""
                    if plt_LableData[1, 3] == True:
                        Label = Label_lineEdit_crvft_2
                    if plt_LableData[1, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, b={B[1]:2.2g}, c={B[2]:2.2g}'.format(B=z02)
                    plt.plot(x, p02(x), '-', label=Label)
            except Exception as e:
                self.errMessage("Quadratic Fit:", str(e))

            # P03
            try:
                if plt_LableData[2, 0] == True:
                    z03 = np.polyfit(x, y, 3)
                    p03 = np.poly1d(z03)
                    if plt_LableData[2, 1] == True:
                        Label=""
                    if plt_LableData[2, 3] == True:
                        Label = Label_lineEdit_crvft_3
                    if plt_LableData[2, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, b={B[1]:2.2g}, c={B[2]:2.2g}, d={B[3]:2.2g}'.format(B=z03)
                    plt.plot(x, p03(x), '-', label=Label)
            except Exception as e:
                self.errMessage("Cubic Fit:", str(e))

            # P04
            try:
                if plt_LableData[3, 0] == True:
                    z04 = np.polyfit(x, y, 4)
                    p04 = np.poly1d(z04)
                    if plt_LableData[3, 1] == True:
                        Label=""
                    if plt_LableData[3, 3] == True:
                        Label = Label_lineEdit_crvft_4
                    if plt_LableData[3, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, b={B[1]:2.2g}, c={B[2]:2.2g}, d={B[3]:2.2g}, e={B[4]:2.2g}'.format(B=z04)
                    plt.plot(x, p04(x), '-', label=Label)
            except Exception as e:
                self.errMessage("4th Order Fit:", str(e))

            # P05
            try:
                if plt_LableData[4, 0] == True:
                    z05 = np.polyfit(x, y, 5)
                    p05 = np.poly1d(z05)
                    if plt_LableData[4, 1] == True:
                        Label=""
                    if plt_LableData[4, 3] == True:
                        Label = Label_lineEdit_crvft_5
                    if plt_LableData[4, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, b={B[1]:2.2g}, c={B[2]:2.2g}, d={B[3]:2.2g}, e={B[4]:2.2g}, f={B[5]:2.2g}'.format(B=z05)
                    plt.plot(x, p05(x), '-', label=Label)
            except Exception as e:
                self.errMessage("5th Order Fit:", str(e))

            # P06
            try:
                if plt_LableData[5, 0] == True:
                    z06 = np.polyfit(x, y, 6)
                    p06 = np.poly1d(z06)
                    if plt_LableData[5, 1] == True:
                        Label=""
                    if plt_LableData[5, 3] == True:
                        Label = Label_lineEdit_crvft_6
                    if plt_LableData[5, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, b={B[1]:2.2g}, c={B[2]:2.2g}, d={B[3]:2.2g}, e={B[4]:2.2g}, f={B[5]:2.2g}, g={B[6]:2.2g}'.format(B=z06)
                    plt.plot(x, p06(x), '-', label=Label)
            except Exception as e:
                self.errMessage("6th Order Fit:", str(e))
            # P07
            try:
                if plt_LableData[6, 0] == True:
                    z07 = np.polyfit(x, y, 7)
                    p07 = np.poly1d(z07)
                    if plt_LableData[6, 1] == True:
                        Label=""
                    if plt_LableData[6, 3] == True:
                        Label = Label_lineEdit_crvft_7
                    if plt_LableData[6, 2] == True:
                        Label = 'fit: {B[0]:2.2g}, {B[1]:2.2g}, {B[2]:2.2g}, {B[3]:2.2g}, {B[4]:2.2g}, {B[5]:2.2g}, {B[6]:2.2g}, {B[7]:2.2g}'.format(B=z07)
                    plt.plot(x, p07(x), '-', label=Label)
            except Exception as e:
                self.errMessage("7th Order Fit:", str(e))
            # P08
            try:
                if plt_LableData[7, 0] == True:
                    z08 = np.polyfit(x, y, 8)
                    p08 = np.poly1d(z08)
                    if plt_LableData[7, 1] == True:
                        Label=""
                    if plt_LableData[7, 3] == True:
                        Label = Label_lineEdit_crvft_8
                    if plt_LableData[7, 2] == True:
                        Label = 'fit: a={B[0]:2.2g}, {B[1]:2.2g}, {B[2]:2.2g}, {B[3]:2.2g}, {B[4]:2.2g}, {B[5]:2.2g}, {B[6]:2.2g}, {B[7]:2.2g}, {B[8]:2.2g}'.format(B=z08)
                    plt.plot(x, p08(x), '-', label=Label)
            except Exception as e:
                self.errMessage("8th Order Fit:", str(e))
            # P09
            try:
                if plt_LableData[8, 0] == True:
                    z09 = np.polyfit(x, y, 9)
                    p09 = np.poly1d(z09)
                    if plt_LableData[8, 1] == True:
                        Label=""
                    if plt_LableData[8, 3] == True:
                        Label = Label_lineEdit_crvft_9
                    if plt_LableData[8, 2] == True:
                        Label = 'fit: {B[0]:2.2g}, {B[1]:2.2g}, {B[2]:2.2g}, {B[3]:2.2g}, {B[4]:2.2g}, {B[5]:2.2g}, {B[6]:2.2g}, {B[7]:2.2g}, {B[8]:2.2g}, {B[9]:2.2g}'.format(B=z09)
                    plt.plot(x, p09(x), '-', label=Label)
            except Exception as e:
                self.errMessage("9th Order Fit:", str(e))
            # P10
            try:
                if plt_LableData[9, 0] == True:
                    z10 = np.polyfit(x, y, 10)
                    p10 = np.poly1d(z10)
                    if plt_LableData[9, 1] == True:
                        Label=""
                    if plt_LableData[9, 3] == True:
                        Label = Label_lineEdit_crvft_10
                    if plt_LableData[9, 2] == True:
                        Label = 'fit: {B[0]:2.2g}, {B[1]:2.2g}, {B[2]:2.2g}, {B[3]:2.2g}, {B[4]:2.2g}, {B[5]:2.2g}, {B[6]:2.2g}, {B[7]:2.2g}, {B[8]:2.2g}, {B[9]:2.2g}, {B[10]:2.2g}'.format(B=z10)
                    plt.plot(x, p10(x), '-', label=Label)
            except Exception as e:
                self.errMessage("10th Order Fit:", str(e))
            # P11
            try:
                if plt_LableData[10, 0] == True:
                    def funcGaus(x, a, b):
                        return a * np.exp(b * x)
                    popt, pcov = curve_fit(funcGaus, x, y)
                    #print(popt)
                    if plt_LableData[10, 1] == True:
                        Label = ""
                    if plt_LableData[10, 3] == True:
                        Label = Label_lineEdit_crvft_11
                    if plt_LableData[10, 2] == True:
                        Label = 'fit: A={B[0]:2.2g}, b={B[1]:2.2g}'.format(B=popt)
                    plt.plot(x, funcGaus(x, *popt), label=Label)
            except Exception as e:
                self.errMessage("A*exp(-b Fit):", str(e))
            #print(plt_LableData)
        except Exception as e:
            self.errMessage("Curve Fitting:", str(e))

        props = dict(facecolor='wheat', alpha=0.5)
 #       ax.text(0.05, 0.95, Equation, transform=ax.transAxes, fontsize=11,
  #              verticalalignment='top')
        plt.legend(loc='upper left',fontsize  = 'small')
        self.canvas.draw()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(601, 643)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        MainWindow.setFocusPolicy(QtCore.Qt.ClickFocus)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        MainWindow.setInputMethodHints(QtCore.Qt.ImhNone)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.VerticalTabs)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setTabletTracking(True)
        self.centralwidget.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.centralwidget.setAcceptDrops(True)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMaximumSize(QtCore.QSize(196.5, 91.5))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("PhysPlotLogo.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 0, 1, 2)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tableWidget.setAutoFillBackground(True)
        self.tableWidget.setInputMethodHints(QtCore.Qt.ImhNone)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.tableWidget.horizontalHeader().font()



        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.gridLayout_2.addWidget(self.tableWidget, 1, 0, 1, 2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 0, 0, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Rows_label = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Rows_label.setFont(font)
        self.Rows_label.setObjectName("Rows_label")
        self.verticalLayout_2.addWidget(self.Rows_label)
        self.Columns_label = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Columns_label.setFont(font)
        self.Columns_label.setObjectName("Columns_label")
        self.verticalLayout_2.addWidget(self.Columns_label)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Rows_lineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.Rows_lineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Rows_lineEdit.setObjectName("Rows_lineEdit")
        self.verticalLayout.addWidget(self.Rows_lineEdit)
        self.Columns_lineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.Columns_lineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Columns_lineEdit.setObjectName("Columns_lineEdit")


        validator = QtGui.QDoubleValidator()

        self.Rows_lineEdit.setText("10")
        self.Columns_lineEdit.setText("4")
        self.Rows_lineEdit.setValidator(validator)
        self.Columns_lineEdit.setValidator(validator)
        self.verticalLayout.addWidget(self.Columns_lineEdit)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_RP = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_RP.setMaximumSize(QtCore.QSize(40, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_RP.setFont(font)
        self.pushButton_RP.setObjectName("pushButton_RP")
        self.verticalLayout_3.addWidget(self.pushButton_RP)
        self.pushButton_CP = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_CP.setMaximumSize(QtCore.QSize(40, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_CP.setFont(font)
        self.pushButton_CP.setObjectName("pushButton_CP")
        self.verticalLayout_3.addWidget(self.pushButton_CP)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.pushButton_RM = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_RM.setMaximumSize(QtCore.QSize(39, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_RM.setFont(font)
        self.pushButton_RM.setObjectName("pushButton_RM")
        self.verticalLayout_6.addWidget(self.pushButton_RM)
        self.pushButton_CM = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_CM.setMaximumSize(QtCore.QSize(39, 29))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_CM.setFont(font)
        self.pushButton_CM.setObjectName("pushButton_CM")
        self.verticalLayout_6.addWidget(self.pushButton_CM)
        self.horizontalLayout_4.addLayout(self.verticalLayout_6)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pushButton = QtWidgets.QPushButton(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 0, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_3.addWidget(self.pushButton_3, 1, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_3.addWidget(self.pushButton_4, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_4, 2, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Rows_label_2 = QtWidgets.QLabel(self.groupBox_5)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Rows_label_2.setFont(font)
        self.Rows_label_2.setObjectName("Rows_label_2")
        self.verticalLayout_4.addWidget(self.Rows_label_2)
        self.Columns_label_2 = QtWidgets.QLabel(self.groupBox_5)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Columns_label_2.setFont(font)
        self.Columns_label_2.setObjectName("Columns_label_2")
        self.verticalLayout_4.addWidget(self.Columns_label_2)
        self.gridLayout_4.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Rows_lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_5)
        self.Rows_lineEdit_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Rows_lineEdit_2.setObjectName("Rows_lineEdit_2")
        self.verticalLayout_5.addWidget(self.Rows_lineEdit_2)
        self.Columns_lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_5)
        self.Columns_lineEdit_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Columns_lineEdit_2.setObjectName("Columns_lineEdit_2")
        self.verticalLayout_5.addWidget(self.Columns_lineEdit_2)
        self.gridLayout_4.addLayout(self.verticalLayout_5, 0, 1, 1, 1)
        self.horizontalLayout_9.addWidget(self.groupBox_5)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.comboBox_scale_x = QtWidgets.QComboBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_scale_x.sizePolicy().hasHeightForWidth())
        self.comboBox_scale_x.setSizePolicy(sizePolicy)
        self.comboBox_scale_x.setMinimumSize(QtCore.QSize(0, 0))
        self.comboBox_scale_x.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.comboBox_scale_x.setFont(font)
        self.comboBox_scale_x.setObjectName("comboBox_scale_x")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.comboBox_scale_x.addItem("")
        self.horizontalLayout_8.addWidget(self.comboBox_scale_x)
        spacerItem2 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setFamily("Kozuka Gothic Pr6N B")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.lineEdit_scale_x_x = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_scale_x_x.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEdit_scale_x_x.setMaximumSize(QtCore.QSize(120, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit_scale_x_x.setFont(font)
        self.lineEdit_scale_x_x.setObjectName("lineEdit_scale_x_x")
        self.horizontalLayout_2.addWidget(self.lineEdit_scale_x_x)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setFamily("Kozuka Gothic Pr6N B")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setTextFormat(QtCore.Qt.RichText)
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.lineEdit_scale_x_plus = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_scale_x_plus.setMaximumSize(QtCore.QSize(107, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit_scale_x_plus.setFont(font)
        self.lineEdit_scale_x_plus.setObjectName("lineEdit_scale_x_plus")
        self.horizontalLayout.addWidget(self.lineEdit_scale_x_plus)
        self.horizontalLayout_8.addLayout(self.horizontalLayout)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_8.addWidget(self.pushButton_2)
        self.horizontalLayout_9.addWidget(self.groupBox_2)
        self.gridLayout_2.addWidget(self.groupBox, 3, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 601, 21))
        self.menubar.setObjectName("menubar")
        self.menuABC = QtWidgets.QMenu(self.menubar)
        self.menuABC.setObjectName("menuABC")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionHome_Page = QtWidgets.QAction(MainWindow)
        self.actionHome_Page.setObjectName("actionHome_Page")
        self.actionHome_Page_2 = QtWidgets.QAction(MainWindow)
        self.actionHome_Page_2.setObjectName("actionHome_Page_2")
        self.actionHome_Page_2.triggered.connect(self.open_home_page)
        self.menuABC.addAction(self.actionHome_Page)
        self.actionHome_Page.triggered.connect(self.about_gui_command)
        self.menuABC.addAction(self.actionHome_Page_2)
        self.menubar.addAction(self.menuABC.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        validator1 = QtGui.QIntValidator(0,100)
        self.Rows_lineEdit_2.setValidator(validator1)
        self.Columns_lineEdit_2.setValidator(validator1)
        self.Rows_lineEdit_2.setText("0")
        self.Columns_lineEdit_2.setText("0")
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PhysPlot"))
        self.tableWidget.setSortingEnabled(False)
        self.pushButton_5.setText(_translate("MainWindow", "New Table"))
        self.checkBox_2.setText(_translate("MainWindow", "Delete Old Entries"))
        self.Rows_label.setText(_translate("MainWindow", "#Rows:"))
        self.Columns_label.setText(_translate("MainWindow", "#Columns:"))
        self.pushButton_RP.setText(_translate("MainWindow", "+"))
        self.pushButton_CP.setText(_translate("MainWindow", "+"))
        self.pushButton_RM.setText(_translate("MainWindow", "-"))
        self.pushButton_CM.setText(_translate("MainWindow", "-"))
        self.pushButton.setText(_translate("MainWindow", "Import Data"))
        self.pushButton_3.setText(_translate("MainWindow", "Export Data"))
        self.pushButton_4.setText(_translate("MainWindow", "Generate Plot"))
        self.groupBox.setTitle(_translate("MainWindow", "Apply Mathematical Transformation to Column"))
        self.Rows_label_2.setText(_translate("MainWindow", "Input Col.:"))
        self.Columns_label_2.setText(_translate("MainWindow", "Output Col.:"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Function"))
        self.comboBox_scale_x.setItemText(0, _translate("MainWindow", "x"))
        self.comboBox_scale_x.setItemText(1, _translate("MainWindow", "x^2"))
        self.comboBox_scale_x.setItemText(2, _translate("MainWindow", "x^3"))
        self.comboBox_scale_x.setItemText(3, _translate("MainWindow", "1/x"))
        self.comboBox_scale_x.setItemText(4, _translate("MainWindow", "log10(x)"))
        self.comboBox_scale_x.setItemText(5, _translate("MainWindow", "log(x)"))
        self.comboBox_scale_x.setItemText(6, _translate("MainWindow", "e^x"))
        self.comboBox_scale_x.setItemText(7, _translate("MainWindow", "cos(x)"))
        self.comboBox_scale_x.setItemText(8, _translate("MainWindow", "sin(x)"))
        self.comboBox_scale_x.setItemText(9, _translate("MainWindow", "tan(x)"))
        self.comboBox_scale_x.setItemText(10, _translate("MainWindow", "arccos(x)"))
        self.comboBox_scale_x.setItemText(11, _translate("MainWindow", "arsin(x)"))
        self.comboBox_scale_x.setItemText(12, _translate("MainWindow", "artan(x)"))
        self.label_3.setText(_translate("MainWindow", "x"))
        self.lineEdit_scale_x_x.setText(_translate("MainWindow", "1"))
        self.label_4.setText(_translate("MainWindow", "+"))
        self.lineEdit_scale_x_plus.setText(_translate("MainWindow", "0"))
        self.pushButton_2.setText(_translate("MainWindow", "Apply"))
        self.menuABC.setTitle(_translate("MainWindow", "Help"))
        self.actionHome_Page.setText(_translate("MainWindow", "About"))
        self.actionHome_Page_2.setText(_translate("MainWindow", "Home Page"))
        self.pushButton.clicked.connect(self.btn_LoadData)

        self.pushButton_4.clicked.connect(self.btn_GeneratePlot)
        self.menuABC.addAction(self.actionHome_Page)
        self.pushButton_5.clicked.connect(self.btn_ClearTable)
        self.pushButton_3.clicked.connect(self.btn_SaveTable)
        self.pushButton_2.clicked.connect(self.readRow)
        self.tableWidget.keyPressEvent = self.keyPressEvent
        self.pushButton_RP.clicked.connect(self.btn_RP)
        self.pushButton_RM.clicked.connect(self.btn_RM)
        self.pushButton_CP.clicked.connect(self.btn_CP)
        self.pushButton_CM.clicked.connect(self.btn_CM)
        validator = QtGui.QDoubleValidator()
        self.lineEdit_scale_x_x.setValidator(validator)
        self.lineEdit_scale_x_plus.setValidator(validator)
        global tableLabels
        tableLabels = np.zeros(100)
        global xIndex
        global uxIndex
        global yIndex
        global uyIndex
        self.btn_ClearTable()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.delRows()
            self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))
            self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
        else:
            e.ignore()
    def delRows(self):
        indices = self.tableWidget.selectionModel().selectedRows()
        for index in sorted(indices, reverse=True):
            if index != 0:
                self.tableWidget.removeRow(index.row())
    def shiftVal(self):
        if int(self.Rows_lineEdit_2.text()) > int(self.tableWidget.columnCount()):
            self.Rows_lineEdit_2.setText("0")
        if int(self.Columns_lineEdit_2.text()) > int(self.tableWidget.columnCount()):
            self.Columns_lineEdit_2.setText("0")
    def btn_RP(self):
        self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
        self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))
    def btn_RM(self):
        if int(self.tableWidget.rowCount()) > 4:
            self.tableWidget.setRowCount(self.tableWidget.rowCount()-1)
            self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))
    def btn_CP(self):
        self.tableWidget.setColumnCount(self.tableWidget.columnCount()+1)
        self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
        combo = QtWidgets.QComboBox()
        combo.addItems(["Ignore", "X-axis", "Xerr", "Y-axis", "Yerr"])
        self.tableWidget.setCellWidget(0, self.tableWidget.columnCount()-1, combo)
        self.tableWidget.cellWidget(0, self.tableWidget.columnCount()-1).currentIndexChanged.connect(lambda: self.btn_combobox_index(self.tableWidget.columnCount() - 1))
        self.tableWidget.cellWidget(0, self.tableWidget.columnCount()-1).currentIndexChanged.connect(self.btn_combobox_changed)
        self.shiftVal()
    def btn_CM(self):
        if int(self.tableWidget.columnCount()) > 2:
            #print("CM", self.tableWidget.columnCount())
            tableLabels[self.tableWidget.columnCount():99] = 0
            self.tableWidget.setColumnCount(self.tableWidget.columnCount()-1)
            self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
            self.shiftVal()
    def readRow(self):
        if (int(self.Rows_lineEdit_2.text()) <= int(self.tableWidget.columnCount())) and (int(self.Columns_lineEdit_2.text()) <= int(self.tableWidget.columnCount())) and (int(self.Rows_lineEdit_2.text()) > 0) and (int(self.Columns_lineEdit_2.text()) > 0):
            #print("Condition True")
            global inputRow
            global outputRow
            inputRow = int(self.Rows_lineEdit_2.text())-1
            outputRow = int(self.Columns_lineEdit_2.text())-1
            self.readTableRow()
            self.writeTableRow()
    def readTableRow(self):
        global xFormula
        global yFormula
        global xTimes
        global yTimes
        global xPlus
        global yPlus
        xFormula = self.comboBox_scale_x.currentText()
        xTimes = np.double(self.lineEdit_scale_x_x.text())
        xPlus = np.double(self.lineEdit_scale_x_plus.text())
        try:
            global rowData
            rowData = np.zeros((tableDimensions[0]-1))
            j = 0
            while j < tableDimensions[0]-1:
                a_item = self.tableWidget.item(j+1, inputRow)
                try:
                    a_name = np.single(a_item.text())
                except:
                    a_name = np.single(0)
                rowData[j] = a_name
                j += 1
            if xFormula == "x":
                rowData = rowData * xTimes + xPlus
            if xFormula == "x^2":
                rowData = np.power(rowData, 2) * xTimes + xPlus
            if xFormula == "x^3":
                rowData = np.power(rowData, 3) * xTimes + xPlus
            if xFormula == "1/x":
                rowData = (1 / rowData) * xTimes + xPlus
            if xFormula == "log10(x)":
                rowData = (np.log10(rowData)) * xTimes + xPlus
            if xFormula == "log(x)":
                rowData = (np.log(rowData)) * xTimes + xPlus
            if xFormula == "e^x":
                rowData = (np.exp(rowData)) * xTimes + xPlus
            if xFormula == "cos(x)":
                rowData = (np.cos(rowData)) * xTimes + xPlus
            if xFormula == "sin(x)":
                rowData = (np.sin(rowData)) * xTimes + xPlus
            if xFormula == "tan(x)":
                rowData = (np.tan(rowData)) * xTimes + xPlus
            if xFormula == "arccos(x)":
                rowData = (np.arccos(rowData)) * xTimes + xPlus
            if xFormula == "arcsin(x)":
                rowData = (np.arcsin(rowData)) * xTimes + xPlus
            if xFormula == "arctan(x)":
                rowData = (np.arctan(rowData)) * xTimes + xPlus

        except Exception as e:
            self.errMessage("readTableRow:", str(e))

    def writeTableRow(self):
        try:
            j=0
            while j < tableDimensions[0]-1:
                A = []
                #print(str(rowData[j]))
                A = str(np.round(rowData[j],6))
                cellinfo = QTableWidgetItem(A)
                self.tableWidget.setItem(j+1, outputRow, cellinfo)
                j += 1
        except Exception as e:
            self.errMessage("writeTableRow:", str(e))
    def btn_LoadData(self):
        pick_file_to_append()
        if files:
            import numpy as np
            import pandas as pd
            global tableLabels
            import os.path
            global data
            try:
                if os.path.splitext(files)[1] == ".xlsx":
                    data = pd.read_excel(files,header=None)
                    data = data.to_numpy()
                elif os.path.splitext(files)[1] == ".csv":
                    data = pd.read_csv(files,header=None)
                    data = data.to_numpy()
                elif os.path.splitext(files)[1] == ".txt":
                    data = np.loadtxt(files)
                else:
                    data = np.loadtxt(files)
                self.printTOTable()
            except:
                pass
    def printTOTable(self): #Prints data file to table
        try:
            import numpy as np
            ##print("Loaded Data:", data.shape[0], "R, ", data.shape[1], "C")
            global tableDimensions
            tableDimensions = [int(data.shape[0]) + 1, int(data.shape[1])]
            ##print("tableDimensions set to:", tableDimensions[0], "R, ", tableDimensions[1], "C")
            self.tableWidget.setRowCount(data.shape[0] + 1)
            self.tableWidget.setColumnCount(data.shape[1])

            row = 0

            while row < data.shape[1]:
                combo = QtWidgets.QComboBox()
                combo.addItems(["Ignore", "X-axis", "Xerr", "Y-axis", "Yerr"])
                # self.tableWidget.setItem(data.shape[1], data.shape[0], cellinfo)
                self.tableWidget.setCellWidget(0, row, combo)

                row += 1
            if 0 < data.shape[1]:
                self.tableWidget.cellWidget(0, 0).currentIndexChanged.connect(lambda: self.btn_combobox_index(0))
                self.tableWidget.cellWidget(0, 0).currentIndexChanged.connect(self.btn_combobox_changed)
            if 1 < data.shape[1]:
                self.tableWidget.cellWidget(0, 1).currentIndexChanged.connect(lambda: self.btn_combobox_index(1))
                self.tableWidget.cellWidget(0, 1).currentIndexChanged.connect(self.btn_combobox_changed)
            if 2 < data.shape[1]:
                self.tableWidget.cellWidget(0, 2).currentIndexChanged.connect(lambda: self.btn_combobox_index(2))
                self.tableWidget.cellWidget(0, 2).currentIndexChanged.connect(self.btn_combobox_changed)
            if 3 < data.shape[1]:
                self.tableWidget.cellWidget(0, 3).currentIndexChanged.connect(lambda: self.btn_combobox_index(3))
                self.tableWidget.cellWidget(0, 3).currentIndexChanged.connect(self.btn_combobox_changed)
            if 4 < data.shape[1]:
                self.tableWidget.cellWidget(0, 4).currentIndexChanged.connect(lambda: self.btn_combobox_index(4))
                self.tableWidget.cellWidget(0, 4).currentIndexChanged.connect(self.btn_combobox_changed)
            if 5 < data.shape[1]:
                self.tableWidget.cellWidget(0, 5).currentIndexChanged.connect(lambda: self.btn_combobox_index(5))
                self.tableWidget.cellWidget(0, 5).currentIndexChanged.connect(self.btn_combobox_changed)
            if 6 < data.shape[1]:
                self.tableWidget.cellWidget(0, 6).currentIndexChanged.connect(lambda: self.btn_combobox_index(6))
                self.tableWidget.cellWidget(0, 6).currentIndexChanged.connect(self.btn_combobox_changed)
            if 7 < data.shape[1]:
                self.tableWidget.cellWidget(0, 7).currentIndexChanged.connect(lambda: self.btn_combobox_index(7))
                self.tableWidget.cellWidget(0, 7).currentIndexChanged.connect(self.btn_combobox_changed)
            if 8 < data.shape[1]:
                self.tableWidget.cellWidget(0, 8).currentIndexChanged.connect(lambda: self.btn_combobox_index(8))
                self.tableWidget.cellWidget(0, 8).currentIndexChanged.connect(self.btn_combobox_changed)
            if 9 < data.shape[1]:
                self.tableWidget.cellWidget(0, 9).currentIndexChanged.connect(lambda: self.btn_combobox_index(9))
                self.tableWidget.cellWidget(0, 9).currentIndexChanged.connect(self.btn_combobox_changed)
            if 10 < data.shape[1]:
                self.tableWidget.cellWidget(0, 10).currentIndexChanged.connect(lambda: self.btn_combobox_index(10))
                self.tableWidget.cellWidget(0, 10).currentIndexChanged.connect(self.btn_combobox_changed)
            if 11 < data.shape[1]:
                self.tableWidget.cellWidget(0, 11).currentIndexChanged.connect(lambda: self.btn_combobox_index(11))
                self.tableWidget.cellWidget(0, 11).currentIndexChanged.connect(self.btn_combobox_changed)
            if 12 < data.shape[1]:
                self.tableWidget.cellWidget(0, 12).currentIndexChanged.connect(lambda: self.btn_combobox_index(12))
                self.tableWidget.cellWidget(0, 12).currentIndexChanged.connect(self.btn_combobox_changed)
            if 13 < data.shape[1]:
                self.tableWidget.cellWidget(0, 13).currentIndexChanged.connect(lambda: self.btn_combobox_index(13))
                self.tableWidget.cellWidget(0, 13).currentIndexChanged.connect(self.btn_combobox_changed)
            if 14 < data.shape[1]:
                self.tableWidget.cellWidget(0, 14).currentIndexChanged.connect(lambda: self.btn_combobox_index(14))
                self.tableWidget.cellWidget(0, 14).currentIndexChanged.connect(self.btn_combobox_changed)
            if 15 < data.shape[1]:
                self.tableWidget.cellWidget(0, 15).currentIndexChanged.connect(lambda: self.btn_combobox_index(15))
                self.tableWidget.cellWidget(0, 15).currentIndexChanged.connect(self.btn_combobox_changed)
            if 16 < data.shape[1]:
                self.tableWidget.cellWidget(0, 16).currentIndexChanged.connect(lambda: self.btn_combobox_index(16))
                self.tableWidget.cellWidget(0, 16).currentIndexChanged.connect(self.btn_combobox_changed)
            if 17 < data.shape[1]:
                self.tableWidget.cellWidget(0, 17).currentIndexChanged.connect(lambda: self.btn_combobox_index(17))
                self.tableWidget.cellWidget(0, 17).currentIndexChanged.connect(self.btn_combobox_changed)
            if 18 < data.shape[1]:
                self.tableWidget.cellWidget(0, 18).currentIndexChanged.connect(lambda: self.btn_combobox_index(18))
                self.tableWidget.cellWidget(0, 18).currentIndexChanged.connect(self.btn_combobox_changed)
            if 19 < data.shape[1]:
                self.tableWidget.cellWidget(0, 19).currentIndexChanged.connect(lambda: self.btn_combobox_index(19))
                self.tableWidget.cellWidget(0, 19).currentIndexChanged.connect(self.btn_combobox_changed)
            if 20 < data.shape[1]:
                self.tableWidget.cellWidget(0, 20).currentIndexChanged.connect(lambda: self.btn_combobox_index(20))
                self.tableWidget.cellWidget(0, 20).currentIndexChanged.connect(self.btn_combobox_changed)
            if 21 < data.shape[1]:
                self.tableWidget.cellWidget(0, 21).currentIndexChanged.connect(lambda: self.btn_combobox_index(21))
                self.tableWidget.cellWidget(0, 21).currentIndexChanged.connect(self.btn_combobox_changed)
            if 22 < data.shape[1]:
                self.tableWidget.cellWidget(0, 22).currentIndexChanged.connect(lambda: self.btn_combobox_index(22))
                self.tableWidget.cellWidget(0, 22).currentIndexChanged.connect(self.btn_combobox_changed)
            if 23 < data.shape[1]:
                self.tableWidget.cellWidget(0, 23).currentIndexChanged.connect(lambda: self.btn_combobox_index(23))
                self.tableWidget.cellWidget(0, 23).currentIndexChanged.connect(self.btn_combobox_changed)
            if 24 < data.shape[1]:
                self.tableWidget.cellWidget(0, 24).currentIndexChanged.connect(lambda: self.btn_combobox_index(24))
                self.tableWidget.cellWidget(0, 24).currentIndexChanged.connect(self.btn_combobox_changed)
            if 25 < data.shape[1]:
                self.tableWidget.cellWidget(0, 25).currentIndexChanged.connect(lambda: self.btn_combobox_index(25))
                self.tableWidget.cellWidget(0, 25).currentIndexChanged.connect(self.btn_combobox_changed)
            if 26 < data.shape[1]:
                self.tableWidget.cellWidget(0, 26).currentIndexChanged.connect(lambda: self.btn_combobox_index(26))
                self.tableWidget.cellWidget(0, 26).currentIndexChanged.connect(self.btn_combobox_changed)
            if 27 < data.shape[1]:
                self.tableWidget.cellWidget(0, 27).currentIndexChanged.connect(lambda: self.btn_combobox_index(27))
                self.tableWidget.cellWidget(0, 27).currentIndexChanged.connect(self.btn_combobox_changed)
            if 28 < data.shape[1]:
                self.tableWidget.cellWidget(0, 28).currentIndexChanged.connect(lambda: self.btn_combobox_index(28))
                self.tableWidget.cellWidget(0, 28).currentIndexChanged.connect(self.btn_combobox_changed)
            if 29 < data.shape[1]:
                self.tableWidget.cellWidget(0, 29).currentIndexChanged.connect(lambda: self.btn_combobox_index(29))
                self.tableWidget.cellWidget(0, 29).currentIndexChanged.connect(self.btn_combobox_changed)
            if 30 < data.shape[1]:
                self.tableWidget.cellWidget(0, 30).currentIndexChanged.connect(lambda: self.btn_combobox_index(30))
                self.tableWidget.cellWidget(0, 30).currentIndexChanged.connect(self.btn_combobox_changed)
            if 31 < data.shape[1]:
                self.tableWidget.cellWidget(0, 31).currentIndexChanged.connect(lambda: self.btn_combobox_index(31))
                self.tableWidget.cellWidget(0, 31).currentIndexChanged.connect(self.btn_combobox_changed)
            if 32 < data.shape[1]:
                self.tableWidget.cellWidget(0, 32).currentIndexChanged.connect(lambda: self.btn_combobox_index(32))
                self.tableWidget.cellWidget(0, 32).currentIndexChanged.connect(self.btn_combobox_changed)
            if 33 < data.shape[1]:
                self.tableWidget.cellWidget(0, 33).currentIndexChanged.connect(lambda: self.btn_combobox_index(33))
                self.tableWidget.cellWidget(0, 33).currentIndexChanged.connect(self.btn_combobox_changed)
            if 34 < data.shape[1]:
                self.tableWidget.cellWidget(0, 34).currentIndexChanged.connect(lambda: self.btn_combobox_index(34))
                self.tableWidget.cellWidget(0, 34).currentIndexChanged.connect(self.btn_combobox_changed)
            if 35 < data.shape[1]:
                self.tableWidget.cellWidget(0, 35).currentIndexChanged.connect(lambda: self.btn_combobox_index(35))
                self.tableWidget.cellWidget(0, 35).currentIndexChanged.connect(self.btn_combobox_changed)
            if 36 < data.shape[1]:
                self.tableWidget.cellWidget(0, 36).currentIndexChanged.connect(lambda: self.btn_combobox_index(36))
                self.tableWidget.cellWidget(0, 36).currentIndexChanged.connect(self.btn_combobox_changed)
            if 37 < data.shape[1]:
                self.tableWidget.cellWidget(0, 37).currentIndexChanged.connect(lambda: self.btn_combobox_index(37))
                self.tableWidget.cellWidget(0, 37).currentIndexChanged.connect(self.btn_combobox_changed)
            if 38 < data.shape[1]:
                self.tableWidget.cellWidget(0, 38).currentIndexChanged.connect(lambda: self.btn_combobox_index(38))
                self.tableWidget.cellWidget(0, 38).currentIndexChanged.connect(self.btn_combobox_changed)
            if 39 < data.shape[1]:
                self.tableWidget.cellWidget(0, 39).currentIndexChanged.connect(lambda: self.btn_combobox_index(39))
                self.tableWidget.cellWidget(0, 39).currentIndexChanged.connect(self.btn_combobox_changed)
            if 40 < data.shape[1]:
                self.tableWidget.cellWidget(0, 40).currentIndexChanged.connect(lambda: self.btn_combobox_index(40))
                self.tableWidget.cellWidget(0, 40).currentIndexChanged.connect(self.btn_combobox_changed)
            if 41 < data.shape[1]:
                self.tableWidget.cellWidget(0, 41).currentIndexChanged.connect(lambda: self.btn_combobox_index(41))
                self.tableWidget.cellWidget(0, 41).currentIndexChanged.connect(self.btn_combobox_changed)
            if 42 < data.shape[1]:
                self.tableWidget.cellWidget(0, 42).currentIndexChanged.connect(lambda: self.btn_combobox_index(42))
                self.tableWidget.cellWidget(0, 42).currentIndexChanged.connect(self.btn_combobox_changed)
            if 43 < data.shape[1]:
                self.tableWidget.cellWidget(0, 43).currentIndexChanged.connect(lambda: self.btn_combobox_index(43))
                self.tableWidget.cellWidget(0, 43).currentIndexChanged.connect(self.btn_combobox_changed)
            if 44 < data.shape[1]:
                self.tableWidget.cellWidget(0, 44).currentIndexChanged.connect(lambda: self.btn_combobox_index(44))
                self.tableWidget.cellWidget(0, 44).currentIndexChanged.connect(self.btn_combobox_changed)
            if 45 < data.shape[1]:
                self.tableWidget.cellWidget(0, 45).currentIndexChanged.connect(lambda: self.btn_combobox_index(45))
                self.tableWidget.cellWidget(0, 45).currentIndexChanged.connect(self.btn_combobox_changed)
            if 46 < data.shape[1]:
                self.tableWidget.cellWidget(0, 46).currentIndexChanged.connect(lambda: self.btn_combobox_index(46))
                self.tableWidget.cellWidget(0, 46).currentIndexChanged.connect(self.btn_combobox_changed)
            if 47 < data.shape[1]:
                self.tableWidget.cellWidget(0, 47).currentIndexChanged.connect(lambda: self.btn_combobox_index(47))
                self.tableWidget.cellWidget(0, 47).currentIndexChanged.connect(self.btn_combobox_changed)
            if 48 < data.shape[1]:
                self.tableWidget.cellWidget(0, 48).currentIndexChanged.connect(lambda: self.btn_combobox_index(48))
                self.tableWidget.cellWidget(0, 48).currentIndexChanged.connect(self.btn_combobox_changed)
            if 49 < data.shape[1]:
                self.tableWidget.cellWidget(0, 49).currentIndexChanged.connect(lambda: self.btn_combobox_index(49))
                self.tableWidget.cellWidget(0, 49).currentIndexChanged.connect(self.btn_combobox_changed)
            if 50 < data.shape[1]:
                self.tableWidget.cellWidget(0, 50).currentIndexChanged.connect(lambda: self.btn_combobox_index(50))
                self.tableWidget.cellWidget(0, 50).currentIndexChanged.connect(self.btn_combobox_changed)
            if 51 < data.shape[1]:
                self.tableWidget.cellWidget(0, 51).currentIndexChanged.connect(lambda: self.btn_combobox_index(51))
                self.tableWidget.cellWidget(0, 51).currentIndexChanged.connect(self.btn_combobox_changed)
            if 52 < data.shape[1]:
                self.tableWidget.cellWidget(0, 52).currentIndexChanged.connect(lambda: self.btn_combobox_index(52))
                self.tableWidget.cellWidget(0, 52).currentIndexChanged.connect(self.btn_combobox_changed)
            if 53 < data.shape[1]:
                self.tableWidget.cellWidget(0, 53).currentIndexChanged.connect(lambda: self.btn_combobox_index(53))
                self.tableWidget.cellWidget(0, 53).currentIndexChanged.connect(self.btn_combobox_changed)
            if 54 < data.shape[1]:
                self.tableWidget.cellWidget(0, 54).currentIndexChanged.connect(lambda: self.btn_combobox_index(54))
                self.tableWidget.cellWidget(0, 54).currentIndexChanged.connect(self.btn_combobox_changed)
            if 55 < data.shape[1]:
                self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(lambda: self.btn_combobox_index(55))
                self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(self.btn_combobox_changed)
            if 56 < data.shape[1]:
                self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(lambda: self.btn_combobox_index(56))
                self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(self.btn_combobox_changed)
            if 57 < data.shape[1]:
                self.tableWidget.cellWidget(0, 57).currentIndexChanged.connect(lambda: self.btn_combobox_index(57))
                self.tableWidget.cellWidget(0, 57).currentIndexChanged.connect(self.btn_combobox_changed)
            if 58 < data.shape[1]:
                self.tableWidget.cellWidget(0, 58).currentIndexChanged.connect(lambda: self.btn_combobox_index(58))
                self.tableWidget.cellWidget(0, 58).currentIndexChanged.connect(self.btn_combobox_changed)
            if 59 < data.shape[1]:
                self.tableWidget.cellWidget(0, 59).currentIndexChanged.connect(lambda: self.btn_combobox_index(59))
                self.tableWidget.cellWidget(0, 59).currentIndexChanged.connect(self.btn_combobox_changed)
            if 60 < data.shape[1]:
                self.tableWidget.cellWidget(0, 60).currentIndexChanged.connect(lambda: self.btn_combobox_index(60))
                self.tableWidget.cellWidget(0, 60).currentIndexChanged.connect(self.btn_combobox_changed)
            if 61 < data.shape[1]:
                self.tableWidget.cellWidget(0, 61).currentIndexChanged.connect(lambda: self.btn_combobox_index(61))
                self.tableWidget.cellWidget(0, 61).currentIndexChanged.connect(self.btn_combobox_changed)
            if 62 < data.shape[1]:
                self.tableWidget.cellWidget(0, 62).currentIndexChanged.connect(lambda: self.btn_combobox_index(62))
                self.tableWidget.cellWidget(0, 62).currentIndexChanged.connect(self.btn_combobox_changed)
            if 63 < data.shape[1]:
                self.tableWidget.cellWidget(0, 63).currentIndexChanged.connect(lambda: self.btn_combobox_index(63))
                self.tableWidget.cellWidget(0, 63).currentIndexChanged.connect(self.btn_combobox_changed)
            if 64 < data.shape[1]:
                self.tableWidget.cellWidget(0, 64).currentIndexChanged.connect(lambda: self.btn_combobox_index(64))
                self.tableWidget.cellWidget(0, 64).currentIndexChanged.connect(self.btn_combobox_changed)
            if 65 < data.shape[1]:
                self.tableWidget.cellWidget(0, 65).currentIndexChanged.connect(lambda: self.btn_combobox_index(65))
                self.tableWidget.cellWidget(0, 65).currentIndexChanged.connect(self.btn_combobox_changed)
            if 66 < data.shape[1]:
                self.tableWidget.cellWidget(0, 66).currentIndexChanged.connect(lambda: self.btn_combobox_index(66))
                self.tableWidget.cellWidget(0, 66).currentIndexChanged.connect(self.btn_combobox_changed)
            if 67 < data.shape[1]:
                self.tableWidget.cellWidget(0, 67).currentIndexChanged.connect(lambda: self.btn_combobox_index(67))
                self.tableWidget.cellWidget(0, 67).currentIndexChanged.connect(self.btn_combobox_changed)
            if 68 < data.shape[1]:
                self.tableWidget.cellWidget(0, 68).currentIndexChanged.connect(lambda: self.btn_combobox_index(68))
                self.tableWidget.cellWidget(0, 68).currentIndexChanged.connect(self.btn_combobox_changed)
            if 69 < data.shape[1]:
                self.tableWidget.cellWidget(0, 69).currentIndexChanged.connect(lambda: self.btn_combobox_index(69))
                self.tableWidget.cellWidget(0, 69).currentIndexChanged.connect(self.btn_combobox_changed)
            if 70 < data.shape[1]:
                self.tableWidget.cellWidget(0, 70).currentIndexChanged.connect(lambda: self.btn_combobox_index(70))
                self.tableWidget.cellWidget(0, 70).currentIndexChanged.connect(self.btn_combobox_changed)
            if 71 < data.shape[1]:
                self.tableWidget.cellWidget(0, 71).currentIndexChanged.connect(lambda: self.btn_combobox_index(71))
                self.tableWidget.cellWidget(0, 71).currentIndexChanged.connect(self.btn_combobox_changed)
            if 72 < data.shape[1]:
                self.tableWidget.cellWidget(0, 72).currentIndexChanged.connect(lambda: self.btn_combobox_index(72))
                self.tableWidget.cellWidget(0, 72).currentIndexChanged.connect(self.btn_combobox_changed)
            if 73 < data.shape[1]:
                self.tableWidget.cellWidget(0, 73).currentIndexChanged.connect(lambda: self.btn_combobox_index(73))
                self.tableWidget.cellWidget(0, 73).currentIndexChanged.connect(self.btn_combobox_changed)
            if 74 < data.shape[1]:
                self.tableWidget.cellWidget(0, 74).currentIndexChanged.connect(lambda: self.btn_combobox_index(74))
                self.tableWidget.cellWidget(0, 74).currentIndexChanged.connect(self.btn_combobox_changed)
            if 75 < data.shape[1]:
                self.tableWidget.cellWidget(0, 75).currentIndexChanged.connect(lambda: self.btn_combobox_index(75))
                self.tableWidget.cellWidget(0, 75).currentIndexChanged.connect(self.btn_combobox_changed)
            if 76 < data.shape[1]:
                self.tableWidget.cellWidget(0, 76).currentIndexChanged.connect(lambda: self.btn_combobox_index(76))
                self.tableWidget.cellWidget(0, 76).currentIndexChanged.connect(self.btn_combobox_changed)
            if 77 < data.shape[1]:
                self.tableWidget.cellWidget(0, 77).currentIndexChanged.connect(lambda: self.btn_combobox_index(77))
                self.tableWidget.cellWidget(0, 77).currentIndexChanged.connect(self.btn_combobox_changed)
            if 78 < data.shape[1]:
                self.tableWidget.cellWidget(0, 78).currentIndexChanged.connect(lambda: self.btn_combobox_index(78))
                self.tableWidget.cellWidget(0, 78).currentIndexChanged.connect(self.btn_combobox_changed)
            if 79 < data.shape[1]:
                self.tableWidget.cellWidget(0, 79).currentIndexChanged.connect(lambda: self.btn_combobox_index(79))
                self.tableWidget.cellWidget(0, 79).currentIndexChanged.connect(self.btn_combobox_changed)
            if 80 < data.shape[1]:
                self.tableWidget.cellWidget(0, 80).currentIndexChanged.connect(lambda: self.btn_combobox_index(80))
                self.tableWidget.cellWidget(0, 80).currentIndexChanged.connect(self.btn_combobox_changed)
            if 81 < data.shape[1]:
                self.tableWidget.cellWidget(0, 81).currentIndexChanged.connect(lambda: self.btn_combobox_index(81))
                self.tableWidget.cellWidget(0, 81).currentIndexChanged.connect(self.btn_combobox_changed)
            if 82 < data.shape[1]:
                self.tableWidget.cellWidget(0, 82).currentIndexChanged.connect(lambda: self.btn_combobox_index(82))
                self.tableWidget.cellWidget(0, 82).currentIndexChanged.connect(self.btn_combobox_changed)
            if 83 < data.shape[1]:
                self.tableWidget.cellWidget(0, 83).currentIndexChanged.connect(lambda: self.btn_combobox_index(83))
                self.tableWidget.cellWidget(0, 83).currentIndexChanged.connect(self.btn_combobox_changed)
            if 84 < data.shape[1]:
                self.tableWidget.cellWidget(0, 84).currentIndexChanged.connect(lambda: self.btn_combobox_index(84))
                self.tableWidget.cellWidget(0, 84).currentIndexChanged.connect(self.btn_combobox_changed)
            if 85 < data.shape[1]:
                self.tableWidget.cellWidget(0, 85).currentIndexChanged.connect(lambda: self.btn_combobox_index(85))
                self.tableWidget.cellWidget(0, 85).currentIndexChanged.connect(self.btn_combobox_changed)
            if 86 < data.shape[1]:
                self.tableWidget.cellWidget(0, 86).currentIndexChanged.connect(lambda: self.btn_combobox_index(86))
                self.tableWidget.cellWidget(0, 86).currentIndexChanged.connect(self.btn_combobox_changed)
            if 87 < data.shape[1]:
                self.tableWidget.cellWidget(0, 87).currentIndexChanged.connect(lambda: self.btn_combobox_index(87))
                self.tableWidget.cellWidget(0, 87).currentIndexChanged.connect(self.btn_combobox_changed)
            if 88 < data.shape[1]:
                self.tableWidget.cellWidget(0, 88).currentIndexChanged.connect(lambda: self.btn_combobox_index(88))
                self.tableWidget.cellWidget(0, 88).currentIndexChanged.connect(self.btn_combobox_changed)
            if 89 < data.shape[1]:
                self.tableWidget.cellWidget(0, 89).currentIndexChanged.connect(lambda: self.btn_combobox_index(89))
                self.tableWidget.cellWidget(0, 89).currentIndexChanged.connect(self.btn_combobox_changed)
            if 90 < data.shape[1]:
                self.tableWidget.cellWidget(0, 90).currentIndexChanged.connect(lambda: self.btn_combobox_index(90))
                self.tableWidget.cellWidget(0, 90).currentIndexChanged.connect(self.btn_combobox_changed)
            if 91 < data.shape[1]:
                self.tableWidget.cellWidget(0, 91).currentIndexChanged.connect(lambda: self.btn_combobox_index(91))
                self.tableWidget.cellWidget(0, 91).currentIndexChanged.connect(self.btn_combobox_changed)
            if 92 < data.shape[1]:
                self.tableWidget.cellWidget(0, 92).currentIndexChanged.connect(lambda: self.btn_combobox_index(92))
                self.tableWidget.cellWidget(0, 92).currentIndexChanged.connect(self.btn_combobox_changed)
            if 93 < data.shape[1]:
                self.tableWidget.cellWidget(0, 93).currentIndexChanged.connect(lambda: self.btn_combobox_index(93))
                self.tableWidget.cellWidget(0, 93).currentIndexChanged.connect(self.btn_combobox_changed)
            if 94 < data.shape[1]:
                self.tableWidget.cellWidget(0, 94).currentIndexChanged.connect(lambda: self.btn_combobox_index(94))
                self.tableWidget.cellWidget(0, 94).currentIndexChanged.connect(self.btn_combobox_changed)
            if 95 < data.shape[1]:
                self.tableWidget.cellWidget(0, 95).currentIndexChanged.connect(lambda: self.btn_combobox_index(95))
                self.tableWidget.cellWidget(0, 95).currentIndexChanged.connect(self.btn_combobox_changed)
            if 96 < data.shape[1]:
                self.tableWidget.cellWidget(0, 96).currentIndexChanged.connect(lambda: self.btn_combobox_index(96))
                self.tableWidget.cellWidget(0, 96).currentIndexChanged.connect(self.btn_combobox_changed)
            if 97 < data.shape[1]:
                self.tableWidget.cellWidget(0, 97).currentIndexChanged.connect(lambda: self.btn_combobox_index(97))
                self.tableWidget.cellWidget(0, 97).currentIndexChanged.connect(self.btn_combobox_changed)
            if 98 < data.shape[1]:
                self.tableWidget.cellWidget(0, 98).currentIndexChanged.connect(lambda: self.btn_combobox_index(98))
                self.tableWidget.cellWidget(0, 98).currentIndexChanged.connect(self.btn_combobox_changed)
            if 99 < data.shape[1]:
                self.tableWidget.cellWidget(0, 99).currentIndexChanged.connect(lambda: self.btn_combobox_index(99))
                self.tableWidget.cellWidget(0, 99).currentIndexChanged.connect(self.btn_combobox_changed)
            if 100 < data.shape[1]:
                self.tableWidget.cellWidget(0, 100).currentIndexChanged.connect(lambda: self.btn_combobox_index(100))
                self.tableWidget.cellWidget(0, 100).currentIndexChanged.connect(self.btn_combobox_changed)
            i = 0
            while i < data.shape[1]:
                j = 0
                while j < data.shape[0]:
                    j += 1
                    A = []
                    # ##print(data[j,i])
                    A = str(data[j - 1, i])
                    cellinfo = QTableWidgetItem(A)
                    self.tableWidget.setItem(j, i, cellinfo)
                i += 1
            self.Columns_lineEdit.setText(str(self.tableWidget.columnCount()))
            self.Rows_lineEdit.setText(str(self.tableWidget.rowCount()))

        except Exception as e:
            self.errMessage("Printing to Table:", str(e))


    def btn_combobox_index(self, value):
        global plot_AxisIndex
        plot_AxisIndex=value
        #print("btn_combobox_index:", plot_AxisIndex)
    def btn_combobox_changed(self, value):
        global combobox_Val
        btn_combobox_Val = value
        index = plot_AxisIndex
        if value == 1:
            global xIndex
            xIndex = plot_AxisIndex
        if value == 2:
            global uxIndex
            uxIndex = plot_AxisIndex
        if value == 3:
            global yIndex
            yIndex = plot_AxisIndex
        if value == 4:
            global uyIndex
            uyIndex = plot_AxisIndex
        tableLabels[int(plot_AxisIndex)] = int(value)
    def btn_ClearTable(self):

        ##print("Clear Table")
    #    self.Rows_lineEdit.text()
    #    self.Columns_lineEdit.text()
        import numpy as np
        self.tableWidget.setRowCount(int(self.Rows_lineEdit.text()))
        self.tableWidget.setColumnCount(int(self.Columns_lineEdit.text()))
        global tableLabels
        tableLabels = np.zeros(100)
        tableDimensions = [int(self.Rows_lineEdit.text()), int(self.Columns_lineEdit.text())]

        ##print("tableDimensions set to:", tableDimensions[0],"R, ", tableDimensions[1],"C")
        if self.checkBox_2.isChecked() == True:
            i=0
            A=str("")
            while i < int(self.Columns_lineEdit.text()):
                j = 1
                while j < int(self.Rows_lineEdit.text())+1:
                    self.tableWidget.setItem(j, i, QtWidgets.QTableWidgetItem(""))
                    j += 1
                i += 1
        col=0
        while col < tableDimensions[1]:
            combo = QtWidgets.QComboBox()
            combo.addItems(["Ignore", "X-axis", "Xerr", "Y-axis", "Yerr"])
            # self.tableWidget.setItem(data.shape[1], data.shape[0], cellinfo)
            self.tableWidget.setCellWidget(0, col, combo)
            col += 1
        if 0 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 0).currentIndexChanged.connect(lambda: self.btn_combobox_index(0))
            self.tableWidget.cellWidget(0, 0).currentIndexChanged.connect(self.btn_combobox_changed)
        if 1 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 1).currentIndexChanged.connect(lambda: self.btn_combobox_index(1))
            self.tableWidget.cellWidget(0, 1).currentIndexChanged.connect(self.btn_combobox_changed)
        if 2 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 2).currentIndexChanged.connect(lambda: self.btn_combobox_index(2))
            self.tableWidget.cellWidget(0, 2).currentIndexChanged.connect(self.btn_combobox_changed)
        if 3 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 3).currentIndexChanged.connect(lambda: self.btn_combobox_index(3))
            self.tableWidget.cellWidget(0, 3).currentIndexChanged.connect(self.btn_combobox_changed)
        if 4 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 4).currentIndexChanged.connect(lambda: self.btn_combobox_index(4))
            self.tableWidget.cellWidget(0, 4).currentIndexChanged.connect(self.btn_combobox_changed)
        if 5 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 5).currentIndexChanged.connect(lambda: self.btn_combobox_index(5))
            self.tableWidget.cellWidget(0, 5).currentIndexChanged.connect(self.btn_combobox_changed)
        if 6 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 6).currentIndexChanged.connect(lambda: self.btn_combobox_index(6))
            self.tableWidget.cellWidget(0, 6).currentIndexChanged.connect(self.btn_combobox_changed)
        if 7 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 7).currentIndexChanged.connect(lambda: self.btn_combobox_index(7))
            self.tableWidget.cellWidget(0, 7).currentIndexChanged.connect(self.btn_combobox_changed)
        if 8 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 8).currentIndexChanged.connect(lambda: self.btn_combobox_index(8))
            self.tableWidget.cellWidget(0, 8).currentIndexChanged.connect(self.btn_combobox_changed)
        if 9 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 9).currentIndexChanged.connect(lambda: self.btn_combobox_index(9))
            self.tableWidget.cellWidget(0, 9).currentIndexChanged.connect(self.btn_combobox_changed)
        if 10 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 10).currentIndexChanged.connect(lambda: self.btn_combobox_index(10))
            self.tableWidget.cellWidget(0, 10).currentIndexChanged.connect(self.btn_combobox_changed)
        if 11 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 11).currentIndexChanged.connect(lambda: self.btn_combobox_index(11))
            self.tableWidget.cellWidget(0, 11).currentIndexChanged.connect(self.btn_combobox_changed)
        if 12 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 12).currentIndexChanged.connect(lambda: self.btn_combobox_index(12))
            self.tableWidget.cellWidget(0, 12).currentIndexChanged.connect(self.btn_combobox_changed)
        if 13 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 13).currentIndexChanged.connect(lambda: self.btn_combobox_index(13))
            self.tableWidget.cellWidget(0, 13).currentIndexChanged.connect(self.btn_combobox_changed)
        if 14 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 14).currentIndexChanged.connect(lambda: self.btn_combobox_index(14))
            self.tableWidget.cellWidget(0, 14).currentIndexChanged.connect(self.btn_combobox_changed)
        if 15 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 15).currentIndexChanged.connect(lambda: self.btn_combobox_index(15))
            self.tableWidget.cellWidget(0, 15).currentIndexChanged.connect(self.btn_combobox_changed)
        if 16 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 16).currentIndexChanged.connect(lambda: self.btn_combobox_index(16))
            self.tableWidget.cellWidget(0, 16).currentIndexChanged.connect(self.btn_combobox_changed)
        if 17 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 17).currentIndexChanged.connect(lambda: self.btn_combobox_index(17))
            self.tableWidget.cellWidget(0, 17).currentIndexChanged.connect(self.btn_combobox_changed)
        if 18 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 18).currentIndexChanged.connect(lambda: self.btn_combobox_index(18))
            self.tableWidget.cellWidget(0, 18).currentIndexChanged.connect(self.btn_combobox_changed)
        if 19 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 19).currentIndexChanged.connect(lambda: self.btn_combobox_index(19))
            self.tableWidget.cellWidget(0, 19).currentIndexChanged.connect(self.btn_combobox_changed)
        if 20 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 20).currentIndexChanged.connect(lambda: self.btn_combobox_index(20))
            self.tableWidget.cellWidget(0, 20).currentIndexChanged.connect(self.btn_combobox_changed)
        if 21 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 21).currentIndexChanged.connect(lambda: self.btn_combobox_index(21))
            self.tableWidget.cellWidget(0, 21).currentIndexChanged.connect(self.btn_combobox_changed)
        if 22 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 22).currentIndexChanged.connect(lambda: self.btn_combobox_index(22))
            self.tableWidget.cellWidget(0, 22).currentIndexChanged.connect(self.btn_combobox_changed)
        if 23 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 23).currentIndexChanged.connect(lambda: self.btn_combobox_index(23))
            self.tableWidget.cellWidget(0, 23).currentIndexChanged.connect(self.btn_combobox_changed)
        if 24 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 24).currentIndexChanged.connect(lambda: self.btn_combobox_index(24))
            self.tableWidget.cellWidget(0, 24).currentIndexChanged.connect(self.btn_combobox_changed)
        if 25 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 25).currentIndexChanged.connect(lambda: self.btn_combobox_index(25))
            self.tableWidget.cellWidget(0, 25).currentIndexChanged.connect(self.btn_combobox_changed)
        if 26 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 26).currentIndexChanged.connect(lambda: self.btn_combobox_index(26))
            self.tableWidget.cellWidget(0, 26).currentIndexChanged.connect(self.btn_combobox_changed)
        if 27 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 27).currentIndexChanged.connect(lambda: self.btn_combobox_index(27))
            self.tableWidget.cellWidget(0, 27).currentIndexChanged.connect(self.btn_combobox_changed)
        if 28 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 28).currentIndexChanged.connect(lambda: self.btn_combobox_index(28))
            self.tableWidget.cellWidget(0, 28).currentIndexChanged.connect(self.btn_combobox_changed)
        if 29 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 29).currentIndexChanged.connect(lambda: self.btn_combobox_index(29))
            self.tableWidget.cellWidget(0, 29).currentIndexChanged.connect(self.btn_combobox_changed)
        if 30 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 30).currentIndexChanged.connect(lambda: self.btn_combobox_index(30))
            self.tableWidget.cellWidget(0, 30).currentIndexChanged.connect(self.btn_combobox_changed)
        if 31 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 31).currentIndexChanged.connect(lambda: self.btn_combobox_index(31))
            self.tableWidget.cellWidget(0, 31).currentIndexChanged.connect(self.btn_combobox_changed)
        if 32 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 32).currentIndexChanged.connect(lambda: self.btn_combobox_index(32))
            self.tableWidget.cellWidget(0, 32).currentIndexChanged.connect(self.btn_combobox_changed)
        if 33 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 33).currentIndexChanged.connect(lambda: self.btn_combobox_index(33))
            self.tableWidget.cellWidget(0, 33).currentIndexChanged.connect(self.btn_combobox_changed)
        if 34 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 34).currentIndexChanged.connect(lambda: self.btn_combobox_index(34))
            self.tableWidget.cellWidget(0, 34).currentIndexChanged.connect(self.btn_combobox_changed)
        if 35 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 35).currentIndexChanged.connect(lambda: self.btn_combobox_index(35))
            self.tableWidget.cellWidget(0, 35).currentIndexChanged.connect(self.btn_combobox_changed)
        if 36 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 36).currentIndexChanged.connect(lambda: self.btn_combobox_index(36))
            self.tableWidget.cellWidget(0, 36).currentIndexChanged.connect(self.btn_combobox_changed)
        if 37 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 37).currentIndexChanged.connect(lambda: self.btn_combobox_index(37))
            self.tableWidget.cellWidget(0, 37).currentIndexChanged.connect(self.btn_combobox_changed)
        if 38 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 38).currentIndexChanged.connect(lambda: self.btn_combobox_index(38))
            self.tableWidget.cellWidget(0, 38).currentIndexChanged.connect(self.btn_combobox_changed)
        if 39 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 39).currentIndexChanged.connect(lambda: self.btn_combobox_index(39))
            self.tableWidget.cellWidget(0, 39).currentIndexChanged.connect(self.btn_combobox_changed)
        if 40 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 40).currentIndexChanged.connect(lambda: self.btn_combobox_index(40))
            self.tableWidget.cellWidget(0, 40).currentIndexChanged.connect(self.btn_combobox_changed)
        if 41 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 41).currentIndexChanged.connect(lambda: self.btn_combobox_index(41))
            self.tableWidget.cellWidget(0, 41).currentIndexChanged.connect(self.btn_combobox_changed)
        if 42 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 42).currentIndexChanged.connect(lambda: self.btn_combobox_index(42))
            self.tableWidget.cellWidget(0, 42).currentIndexChanged.connect(self.btn_combobox_changed)
        if 43 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 43).currentIndexChanged.connect(lambda: self.btn_combobox_index(43))
            self.tableWidget.cellWidget(0, 43).currentIndexChanged.connect(self.btn_combobox_changed)
        if 44 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 44).currentIndexChanged.connect(lambda: self.btn_combobox_index(44))
            self.tableWidget.cellWidget(0, 44).currentIndexChanged.connect(self.btn_combobox_changed)
        if 45 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 45).currentIndexChanged.connect(lambda: self.btn_combobox_index(45))
            self.tableWidget.cellWidget(0, 45).currentIndexChanged.connect(self.btn_combobox_changed)
        if 46 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 46).currentIndexChanged.connect(lambda: self.btn_combobox_index(46))
            self.tableWidget.cellWidget(0, 46).currentIndexChanged.connect(self.btn_combobox_changed)
        if 47 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 47).currentIndexChanged.connect(lambda: self.btn_combobox_index(47))
            self.tableWidget.cellWidget(0, 47).currentIndexChanged.connect(self.btn_combobox_changed)
        if 48 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 48).currentIndexChanged.connect(lambda: self.btn_combobox_index(48))
            self.tableWidget.cellWidget(0, 48).currentIndexChanged.connect(self.btn_combobox_changed)
        if 49 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 49).currentIndexChanged.connect(lambda: self.btn_combobox_index(49))
            self.tableWidget.cellWidget(0, 49).currentIndexChanged.connect(self.btn_combobox_changed)
        if 50 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 50).currentIndexChanged.connect(lambda: self.btn_combobox_index(50))
            self.tableWidget.cellWidget(0, 50).currentIndexChanged.connect(self.btn_combobox_changed)
        if 51 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 51).currentIndexChanged.connect(lambda: self.btn_combobox_index(51))
            self.tableWidget.cellWidget(0, 51).currentIndexChanged.connect(self.btn_combobox_changed)
        if 52 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 52).currentIndexChanged.connect(lambda: self.btn_combobox_index(52))
            self.tableWidget.cellWidget(0, 52).currentIndexChanged.connect(self.btn_combobox_changed)
        if 53 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 53).currentIndexChanged.connect(lambda: self.btn_combobox_index(53))
            self.tableWidget.cellWidget(0, 53).currentIndexChanged.connect(self.btn_combobox_changed)
        if 54 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 54).currentIndexChanged.connect(lambda: self.btn_combobox_index(54))
            self.tableWidget.cellWidget(0, 54).currentIndexChanged.connect(self.btn_combobox_changed)
        if 55 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(lambda: self.btn_combobox_index(55))
            self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(self.btn_combobox_changed)
        if 56 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(lambda: self.btn_combobox_index(56))
            self.tableWidget.cellWidget(0, 55).currentIndexChanged.connect(self.btn_combobox_changed)
        if 57 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 57).currentIndexChanged.connect(lambda: self.btn_combobox_index(57))
            self.tableWidget.cellWidget(0, 57).currentIndexChanged.connect(self.btn_combobox_changed)
        if 58 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 58).currentIndexChanged.connect(lambda: self.btn_combobox_index(58))
            self.tableWidget.cellWidget(0, 58).currentIndexChanged.connect(self.btn_combobox_changed)
        if 59 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 59).currentIndexChanged.connect(lambda: self.btn_combobox_index(59))
            self.tableWidget.cellWidget(0, 59).currentIndexChanged.connect(self.btn_combobox_changed)
        if 60 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 60).currentIndexChanged.connect(lambda: self.btn_combobox_index(60))
            self.tableWidget.cellWidget(0, 60).currentIndexChanged.connect(self.btn_combobox_changed)
        if 61 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 61).currentIndexChanged.connect(lambda: self.btn_combobox_index(61))
            self.tableWidget.cellWidget(0, 61).currentIndexChanged.connect(self.btn_combobox_changed)
        if 62 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 62).currentIndexChanged.connect(lambda: self.btn_combobox_index(62))
            self.tableWidget.cellWidget(0, 62).currentIndexChanged.connect(self.btn_combobox_changed)
        if 63 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 63).currentIndexChanged.connect(lambda: self.btn_combobox_index(63))
            self.tableWidget.cellWidget(0, 63).currentIndexChanged.connect(self.btn_combobox_changed)
        if 64 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 64).currentIndexChanged.connect(lambda: self.btn_combobox_index(64))
            self.tableWidget.cellWidget(0, 64).currentIndexChanged.connect(self.btn_combobox_changed)
        if 65 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 65).currentIndexChanged.connect(lambda: self.btn_combobox_index(65))
            self.tableWidget.cellWidget(0, 65).currentIndexChanged.connect(self.btn_combobox_changed)
        if 66 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 66).currentIndexChanged.connect(lambda: self.btn_combobox_index(66))
            self.tableWidget.cellWidget(0, 66).currentIndexChanged.connect(self.btn_combobox_changed)
        if 67 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 67).currentIndexChanged.connect(lambda: self.btn_combobox_index(67))
            self.tableWidget.cellWidget(0, 67).currentIndexChanged.connect(self.btn_combobox_changed)
        if 68 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 68).currentIndexChanged.connect(lambda: self.btn_combobox_index(68))
            self.tableWidget.cellWidget(0, 68).currentIndexChanged.connect(self.btn_combobox_changed)
        if 69 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 69).currentIndexChanged.connect(lambda: self.btn_combobox_index(69))
            self.tableWidget.cellWidget(0, 69).currentIndexChanged.connect(self.btn_combobox_changed)
        if 70 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 70).currentIndexChanged.connect(lambda: self.btn_combobox_index(70))
            self.tableWidget.cellWidget(0, 70).currentIndexChanged.connect(self.btn_combobox_changed)
        if 71 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 71).currentIndexChanged.connect(lambda: self.btn_combobox_index(71))
            self.tableWidget.cellWidget(0, 71).currentIndexChanged.connect(self.btn_combobox_changed)
        if 72 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 72).currentIndexChanged.connect(lambda: self.btn_combobox_index(72))
            self.tableWidget.cellWidget(0, 72).currentIndexChanged.connect(self.btn_combobox_changed)
        if 73 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 73).currentIndexChanged.connect(lambda: self.btn_combobox_index(73))
            self.tableWidget.cellWidget(0, 73).currentIndexChanged.connect(self.btn_combobox_changed)
        if 74 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 74).currentIndexChanged.connect(lambda: self.btn_combobox_index(74))
            self.tableWidget.cellWidget(0, 74).currentIndexChanged.connect(self.btn_combobox_changed)
        if 75 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 75).currentIndexChanged.connect(lambda: self.btn_combobox_index(75))
            self.tableWidget.cellWidget(0, 75).currentIndexChanged.connect(self.btn_combobox_changed)
        if 76 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 76).currentIndexChanged.connect(lambda: self.btn_combobox_index(76))
            self.tableWidget.cellWidget(0, 76).currentIndexChanged.connect(self.btn_combobox_changed)
        if 77 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 77).currentIndexChanged.connect(lambda: self.btn_combobox_index(77))
            self.tableWidget.cellWidget(0, 77).currentIndexChanged.connect(self.btn_combobox_changed)
        if 78 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 78).currentIndexChanged.connect(lambda: self.btn_combobox_index(78))
            self.tableWidget.cellWidget(0, 78).currentIndexChanged.connect(self.btn_combobox_changed)
        if 79 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 79).currentIndexChanged.connect(lambda: self.btn_combobox_index(79))
            self.tableWidget.cellWidget(0, 79).currentIndexChanged.connect(self.btn_combobox_changed)
        if 80 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 80).currentIndexChanged.connect(lambda: self.btn_combobox_index(80))
            self.tableWidget.cellWidget(0, 80).currentIndexChanged.connect(self.btn_combobox_changed)
        if 81 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 81).currentIndexChanged.connect(lambda: self.btn_combobox_index(81))
            self.tableWidget.cellWidget(0, 81).currentIndexChanged.connect(self.btn_combobox_changed)
        if 82 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 82).currentIndexChanged.connect(lambda: self.btn_combobox_index(82))
            self.tableWidget.cellWidget(0, 82).currentIndexChanged.connect(self.btn_combobox_changed)
        if 83 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 83).currentIndexChanged.connect(lambda: self.btn_combobox_index(83))
            self.tableWidget.cellWidget(0, 83).currentIndexChanged.connect(self.btn_combobox_changed)
        if 84 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 84).currentIndexChanged.connect(lambda: self.btn_combobox_index(84))
            self.tableWidget.cellWidget(0, 84).currentIndexChanged.connect(self.btn_combobox_changed)
        if 85 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 85).currentIndexChanged.connect(lambda: self.btn_combobox_index(85))
            self.tableWidget.cellWidget(0, 85).currentIndexChanged.connect(self.btn_combobox_changed)
        if 86 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 86).currentIndexChanged.connect(lambda: self.btn_combobox_index(86))
            self.tableWidget.cellWidget(0, 86).currentIndexChanged.connect(self.btn_combobox_changed)
        if 87 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 87).currentIndexChanged.connect(lambda: self.btn_combobox_index(87))
            self.tableWidget.cellWidget(0, 87).currentIndexChanged.connect(self.btn_combobox_changed)
        if 88 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 88).currentIndexChanged.connect(lambda: self.btn_combobox_index(88))
            self.tableWidget.cellWidget(0, 88).currentIndexChanged.connect(self.btn_combobox_changed)
        if 89 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 89).currentIndexChanged.connect(lambda: self.btn_combobox_index(89))
            self.tableWidget.cellWidget(0, 89).currentIndexChanged.connect(self.btn_combobox_changed)
        if 90 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 90).currentIndexChanged.connect(lambda: self.btn_combobox_index(90))
            self.tableWidget.cellWidget(0, 90).currentIndexChanged.connect(self.btn_combobox_changed)
        if 91 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 91).currentIndexChanged.connect(lambda: self.btn_combobox_index(91))
            self.tableWidget.cellWidget(0, 91).currentIndexChanged.connect(self.btn_combobox_changed)
        if 92 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 92).currentIndexChanged.connect(lambda: self.btn_combobox_index(92))
            self.tableWidget.cellWidget(0, 92).currentIndexChanged.connect(self.btn_combobox_changed)
        if 93 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 93).currentIndexChanged.connect(lambda: self.btn_combobox_index(93))
            self.tableWidget.cellWidget(0, 93).currentIndexChanged.connect(self.btn_combobox_changed)
        if 94 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 94).currentIndexChanged.connect(lambda: self.btn_combobox_index(94))
            self.tableWidget.cellWidget(0, 94).currentIndexChanged.connect(self.btn_combobox_changed)
        if 95 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 95).currentIndexChanged.connect(lambda: self.btn_combobox_index(95))
            self.tableWidget.cellWidget(0, 95).currentIndexChanged.connect(self.btn_combobox_changed)
        if 96 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 96).currentIndexChanged.connect(lambda: self.btn_combobox_index(96))
            self.tableWidget.cellWidget(0, 96).currentIndexChanged.connect(self.btn_combobox_changed)
        if 97 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 97).currentIndexChanged.connect(lambda: self.btn_combobox_index(97))
            self.tableWidget.cellWidget(0, 97).currentIndexChanged.connect(self.btn_combobox_changed)
        if 98 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 98).currentIndexChanged.connect(lambda: self.btn_combobox_index(98))
            self.tableWidget.cellWidget(0, 98).currentIndexChanged.connect(self.btn_combobox_changed)
        if 99 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 99).currentIndexChanged.connect(lambda: self.btn_combobox_index(99))
            self.tableWidget.cellWidget(0, 99).currentIndexChanged.connect(self.btn_combobox_changed)
        if 100 < int(self.Columns_lineEdit.text()):
            self.tableWidget.cellWidget(0, 100).currentIndexChanged.connect(lambda: self.btn_combobox_index(100))
            self.tableWidget.cellWidget(0, 100).currentIndexChanged.connect(self.btn_combobox_changed)
    def btn_SaveTable(self):
        ##print("Save Table")

        self.readTable()
        SaveFile()


    def readTable(self):
        try:
            global OutPut_Table
            tableDimensions = [int(self.tableWidget.rowCount()), int(self.tableWidget.columnCount())]
            OutPut_Table = np.zeros((tableDimensions[0]-1, tableDimensions[1]))
            i = 0
            while i < tableDimensions[1]:
                j = 0
                while j < tableDimensions[0]-1:
                    a_item = self.tableWidget.item(j+1, i)
                    try:
                        a_name = np.single(a_item.text())
                    except:
                        a_name = np.single(0)
                    OutPut_Table[j, i] = a_name
                    j += 1
                i += 1
            #print(OutPut_Table)
        except Exception as e:
            self.errMessage("Reading Table:", str(e))

    def pltConfigWindow(self):
        self.Ui_ConfigWindow = QtWidgets.QMainWindow()
        self.ui = Ui_ConfigWindow()
        self.ui.setupUiConfigWindow(self.Ui_ConfigWindow)
        self.Ui_ConfigWindow.show()

    def btn_GeneratePlot(self):
        self.readTable()
        try:
            if list(tableLabels == 1).count(True) == 1 and list(tableLabels == 3).count(True) == 1:
                self.pltConfigWindow()
                Plot_Window().show()
            else:
                self.errMessage("The inappropriate combination is selected from the dropdown buttons on the table.", "Possible Solution: Click on 'New Table' button with 'Delete Old Entries' button unchecked and select the proper labels combination.")

        except Exception as e:
            self.errMessage("Generating Plot:", str(e))


    def about_gui_command(self):
        about_gui()
    def open_home_page(self):
        webbrowser.open('https://www.physlab.org/', new=2)

    def errMessage(self,Text,InformativeText):
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('ico.ico'))
        msgBox.setWindowTitle("PhysPlot - Plot Window")
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(Text)
        msgBox.setInformativeText(InformativeText)
        msgBox.setWindowTitle("Warning")
        msgBox.exec_()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setWindowIcon(QtGui.QIcon('ico.ico'))
    MainWindow.show()



    sys.exit(app.exec_())
