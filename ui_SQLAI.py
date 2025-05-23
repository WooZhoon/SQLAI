# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_SQLAI.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import os
from dotenv import load_dotenv
from PyQt5 import QtCore, QtGui, QtWidgets

# 환경 정보를 불러옴
dotenv_path = ".env"
load_dotenv(dotenv_path)

HOST = os.getenv("HOST","127.0.0.1")
PORT = os.getenv("PORT","3306")
USER = os.getenv("USER","root")
PASS = os.getenv("PASS","1111")

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(523, 414)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_HOST = QtWidgets.QLabel(self.centralwidget)
        self.label_HOST.setMinimumSize(QtCore.QSize(0, 40))
        self.label_HOST.setMaximumSize(QtCore.QSize(261, 40))
        self.label_HOST.setObjectName("label_HOST")
        self.gridLayout_3.addWidget(self.label_HOST, 0, 0, 1, 1)
        self.label_PASS = QtWidgets.QLabel(self.centralwidget)
        self.label_PASS.setMinimumSize(QtCore.QSize(0, 40))
        self.label_PASS.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_PASS.setObjectName("label_PASS")
        self.gridLayout_3.addWidget(self.label_PASS, 3, 0, 1, 1)
        self.USER_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.USER_edit.setMinimumSize(QtCore.QSize(180, 40))
        self.USER_edit.setMaximumSize(QtCore.QSize(16777215, 40))
        self.USER_edit.setObjectName("USER_edit")
        self.gridLayout_3.addWidget(self.USER_edit, 2, 2, 1, 1)
        self.PASS_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.PASS_edit.setMinimumSize(QtCore.QSize(180, 40))
        self.PASS_edit.setMaximumSize(QtCore.QSize(16777215, 40))
        self.PASS_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.PASS_edit.setObjectName("PASS_edit")
        self.gridLayout_3.addWidget(self.PASS_edit, 3, 2, 1, 1)
        self.label_USER = QtWidgets.QLabel(self.centralwidget)
        self.label_USER.setMinimumSize(QtCore.QSize(0, 40))
        self.label_USER.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_USER.setObjectName("label_USER")
        self.gridLayout_3.addWidget(self.label_USER, 2, 0, 1, 1)
        self.label_PORT = QtWidgets.QLabel(self.centralwidget)
        self.label_PORT.setMinimumSize(QtCore.QSize(0, 40))
        self.label_PORT.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_PORT.setObjectName("label_PORT")
        self.gridLayout_3.addWidget(self.label_PORT, 1, 0, 1, 1)
        self.PORT_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.PORT_edit.setMinimumSize(QtCore.QSize(180, 40))
        self.PORT_edit.setMaximumSize(QtCore.QSize(16777215, 40))
        self.PORT_edit.setObjectName("PORT_edit")
        self.gridLayout_3.addWidget(self.PORT_edit, 1, 2, 1, 1)
        self.HOST_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.HOST_edit.setEnabled(True)
        self.HOST_edit.setMinimumSize(QtCore.QSize(180, 40))
        self.HOST_edit.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setKerning(True)
        self.HOST_edit.setFont(font)
        self.HOST_edit.setFrame(True)
        self.HOST_edit.setObjectName("HOST_edit")
        self.gridLayout_3.addWidget(self.HOST_edit, 0, 2, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setMinimumSize(QtCore.QSize(99, 0))
        self.label_5.setMaximumSize(QtCore.QSize(16777215, 30))
        self.label_5.setObjectName("label_5")
        self.gridLayout_5.addWidget(self.label_5, 0, 0, 1, 1)
        self.DB_combo = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DB_combo.sizePolicy().hasHeightForWidth())
        self.DB_combo.setSizePolicy(sizePolicy)
        self.DB_combo.setMinimumSize(QtCore.QSize(200, 40))
        self.DB_combo.setMaximumSize(QtCore.QSize(16777215, 40))
        self.DB_combo.setObjectName("DB_combo")
        self.gridLayout_5.addWidget(self.DB_combo, 1, 0, 1, 1)
        self.Conn_push = QtWidgets.QPushButton(self.centralwidget)
        self.Conn_push.setMinimumSize(QtCore.QSize(200, 40))
        self.Conn_push.setMaximumSize(QtCore.QSize(16777215, 40))
        self.Conn_push.setObjectName("Conn_push")
        self.gridLayout_5.addWidget(self.Conn_push, 2, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_5, 0, 3, 1, 1)
        self.Load_push = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Load_push.sizePolicy().hasHeightForWidth())
        self.Load_push.setSizePolicy(sizePolicy)
        self.Load_push.setMinimumSize(QtCore.QSize(80, 120))
        self.Load_push.setMaximumSize(QtCore.QSize(100, 120))
        self.Load_push.setObjectName("Load_push")
        self.gridLayout_4.addWidget(self.Load_push, 0, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_4)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 120))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 496, 132))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.Output_text = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.Output_text.setMinimumSize(QtCore.QSize(0, 120))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        font.setKerning(False)
        self.Output_text.setFont(font)
        self.Output_text.setAutoFillBackground(False)
        self.Output_text.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Output_text.setLineWidth(40)
        self.Output_text.setMidLineWidth(40)
        self.Output_text.setOpenExternalLinks(True)
        self.Output_text.setOpenLinks(True)
        self.Output_text.setObjectName("Output_text")
        self.gridLayout_2.addWidget(self.Output_text, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Input_edit = QtWidgets.QTextEdit(self.centralwidget)
        self.Input_edit.setMinimumSize(QtCore.QSize(0, 60))
        self.Input_edit.setMaximumSize(QtCore.QSize(16777215, 80))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Input_edit.setFont(font)
        self.Input_edit.setObjectName("Input_edit")
        self.horizontalLayout_2.addWidget(self.Input_edit)
        self.Send_push = QtWidgets.QPushButton(self.centralwidget)
        self.Send_push.setMinimumSize(QtCore.QSize(0, 60))
        self.Send_push.setMaximumSize(QtCore.QSize(16777215, 80))
        self.Send_push.setObjectName("Send_push")
        self.horizontalLayout_2.addWidget(self.Send_push)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 523, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SQLAI"))
        self.label_HOST.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">HOST</span></p></body></html>"))
        self.label_PASS.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">PASS</span></p></body></html>"))
        self.USER_edit.setText(_translate("MainWindow", USER))
        self.PASS_edit.setText(_translate("MainWindow", PASS))
        self.label_USER.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">USER</span></p></body></html>"))
        self.label_PORT.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">PORT</span></p></body></html>"))
        self.PORT_edit.setText(_translate("MainWindow", PORT))
        self.HOST_edit.setText(_translate("MainWindow", HOST))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Select DB to use.</span></p></body></html>"))
        self.Conn_push.setText(_translate("MainWindow", "Connect"))
        self.Load_push.setText(_translate("MainWindow", "Load DB"))
        self.Send_push.setText(_translate("MainWindow", "send"))
