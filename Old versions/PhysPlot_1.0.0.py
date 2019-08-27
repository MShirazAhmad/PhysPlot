'''
    File name: PhysPlot.py
    Authors: Muhammad Shiraz Ahmad and Sabieh Anwar
    Date created: 8/20/2019
    Date last modified: 8/20/2019
    Script Version: 1.0.0
    Python Version: 3.7.3
'''

from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QApplication, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import webbrowser
import os

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
        #delayCmd.delay(self)

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
            self.errMessage("Generating Plot:", str(e))


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
        message = "<p><strong>PhysPlot<br /></strong>Version: 1.0.0 (8/20/2019)</p><p><strong>Created by:</strong> <a href='mailto:shiraz.phy@gmail.com'>Muhammad Shiraz Ahmad</a> and <a href='mailto:sabieh@gmail.com'>Muhammad Sabieh Anwar</a></p><p><strong>Important Links: </strong><a href='https://www.physlab.org/'>PhysLab.org</a>, <a href='https://www.qosain.pk/'>Qosain.pk</a></p><p><strong>License:</strong> <a href='https://www.gnu.org/licenses/gpl-3.0.en.html'>GNU General Public License v3.0</a></p><p>Copyright &copy; 2019, all rights reserved.</p>"
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
                                                "Text Files (*.txt);;All Files (*)", options=options)


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
                                                  "All Files (*);;Text Files (*.txt)")
        if fileName:
            global exportFilePath
            exportFilePath = fileName
            np.savetxt(exportFilePath, np.around(np.single(OutPut_Table), decimals=3), delimiter='\t', fmt='%.3f')


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
                    print(popt)
                    if plt_LableData[10, 1] == True:
                        Label = ""
                    if plt_LableData[10, 3] == True:
                        Label = Label_lineEdit_crvft_11
                    if plt_LableData[10, 2] == True:
                        Label = 'fit: A={B[0]:2.2g}, b={B[1]:2.2g}'.format(B=popt)
                    plt.plot(x, funcGaus(x, *popt), label=Label)
            except Exception as e:
                self.errMessage("A*exp(-b Fit):", str(e))
            print(plt_LableData)
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
       # MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(446, 577)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        MainWindow.setFocusPolicy(QtCore.Qt.ClickFocus)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setAutoFillBackground(True)
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
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
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
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        #self.tableWidget.setAutoFillBackground(True)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        brush = QtGui.QBrush(QtGui.QColor(204, 204, 204))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.Dense4Pattern)
        item.setForeground(brush)
        self.tableWidget.setItem(0, 0, item)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_6.addWidget(self.tableWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.clicked.connect(self.btn_LoadData)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_5.addWidget(self.pushButton)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.btn_SaveTable)
        self.verticalLayout_5.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_5.addWidget(self.pushButton_4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.clicked.connect(self.btn_ClearTable)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.verticalLayout_3.addWidget(self.pushButton_5)
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setChecked(True)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_2.sizePolicy().hasHeightForWidth())
        self.checkBox_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Rows_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Rows_label.setFont(font)
        self.Rows_label.setObjectName("Rows_label")
        self.verticalLayout_2.addWidget(self.Rows_label)
        self.Columns_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Columns_label.setFont(font)
        self.Columns_label.setObjectName("Columns_label")
        self.verticalLayout_2.addWidget(self.Columns_label)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Rows_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.Rows_lineEdit.setMaximumSize(QtCore.QSize(101, 16777215))
        self.Rows_lineEdit.setObjectName("Rows_lineEdit")
        self.verticalLayout.addWidget(self.Rows_lineEdit)
        self.Columns_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.Columns_lineEdit.setMaximumSize(QtCore.QSize(101, 16777215))
        self.Columns_lineEdit.setObjectName("Columns_lineEdit")



        self.Rows_lineEdit.setText("10")
        self.Columns_lineEdit.setText("4")

        self.verticalLayout.addWidget(self.Columns_lineEdit)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_6, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 446, 21))
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
        self.pushButton_4.clicked.connect(self.btn_GeneratePlot)
        self.menuABC.addAction(self.actionHome_Page)
        self.actionHome_Page.triggered.connect(self.about_gui_command)
        self.menuABC.addAction(self.actionHome_Page_2)
        self.menubar.addAction(self.menuABC.menuAction())
        self.actionHome_Page_3 = QtWidgets.QAction(MainWindow)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PhysPlot"))
        self.tableWidget.setSortingEnabled(False)
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.pushButton.setText(_translate("MainWindow", "Import Data"))
#        self.checkBox.setText(_translate("MainWindow", "Append to Table"))
        self.pushButton_5.setText(_translate("MainWindow", "New Table"))
        self.checkBox_2.setText(_translate("MainWindow", "Delete old Entries"))
        self.Rows_label.setText(_translate("MainWindow", "Rows:"))
        self.Columns_label.setText(_translate("MainWindow", "Columns:"))
        #self.pushButton_2.setText(_translate("MainWindow", "Optimize Table"))
        self.pushButton_3.setText(_translate("MainWindow", "Export Data"))
        self.pushButton_4.setText(_translate("MainWindow", "Generate Plot"))

        self.menuABC.setTitle(_translate("MainWindow", "Help"))
        self.actionHome_Page.setText(_translate("MainWindow", "About"))
        self.actionHome_Page_2.setText(_translate("MainWindow", "Home Page"))

        global xIndex
        global uxIndex
        global yIndex
        global uyIndex
        self.btn_ClearTable()

    def btn_LoadData(self):
        try:
            pick_file_to_append()
            import numpy as np
            global data
            try:
                data = np.loadtxt(files)
                self.printTOTable()
            except Exception as e:
                self.errMessage("Loading data to Variable:", str(e))
        except Exception as e:
            pass

    def printTOTable(self): #Prints data file to table
        try:
            import numpy as np
            #print("Loaded Data:", data.shape[0], "R, ", data.shape[1], "C")
            global tableDimensions
            tableDimensions = [int(data.shape[0]) + 1, int(data.shape[1])]
            #print("tableDimensions set to:", tableDimensions[0], "R, ", tableDimensions[1], "C")
            self.tableWidget.setRowCount(data.shape[0] + 1)
            self.tableWidget.setColumnCount(data.shape[1])
            global tableLabels
            tableLabels = np.zeros(data.shape[1])
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

            i = 0
            while i < data.shape[1]:
                j = 0
                while j < data.shape[0]:
                    j += 1
                    A = []
                    # #print(data[j,i])
                    A = str(data[j - 1, i])
                    cellinfo = QTableWidgetItem(A)
                    self.tableWidget.setItem(j, i, cellinfo)
                i += 1
        except Exception as e:
            self.errMessage("Printing to Table:", str(e))


    def btn_combobox_index(self, value):
        try:
            global plot_AxisIndex
            plot_AxisIndex=value
        except Exception as e:
            self.errMessage("Combo Box Index:", str(e))

    def btn_combobox_changed(self, value):
        try:
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
        except Exception as e:
            self.errMessage("ComboBox Values:", str(e))


    def btn_ClearTable(self):

        #print("Clear Table")
    #    self.Rows_lineEdit.text()
    #    self.Columns_lineEdit.text()
        import numpy as np
        self.tableWidget.setRowCount(int(self.Rows_lineEdit.text())+1)
        self.tableWidget.setColumnCount(int(self.Columns_lineEdit.text()))
        global tableDimensions
        tableDimensions = [int(self.Rows_lineEdit.text())+1, int(self.Columns_lineEdit.text())]

        #print("tableDimensions set to:", tableDimensions[0],"R, ", tableDimensions[1],"C")
        global tableLabels
        tableLabels = np.zeros(tableDimensions[1])
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

    def btn_SaveTable(self):
        #print("Save Table")

        self.readTable()
        SaveFile()


    def readTable(self):
        try:
            global OutPut_Table
            OutPut_Table = np.zeros((tableDimensions[0]-1, tableDimensions[1]))
            i = 0
            while i < tableDimensions[1]:
                j = 0
                while j < tableDimensions[0]-1:
                    a_item = self.tableWidget.item(j+1, i)
                    a_name = np.single(a_item.text())
                    OutPut_Table[j, i] = a_name
                    j += 1
                i += 1
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
                self.errMessage("Labels on Dropdown:", "The inappropriate combination is selected from the dropdown buttons on the table.")

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
