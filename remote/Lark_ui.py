# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'larkClient.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(382, 299)
        self.C_Bt = QtWidgets.QPushButton(Dialog)
        self.C_Bt.setGeometry(QtCore.QRect(10, 30, 101, 51))
        self.C_Bt.setObjectName("C_Bt")
        self.R_Bt = QtWidgets.QPushButton(Dialog)
        self.R_Bt.setGeometry(QtCore.QRect(140, 30, 101, 51))
        self.R_Bt.setObjectName("R_Bt")
        self.log = QtWidgets.QLabel(Dialog)
        self.log.setGeometry(QtCore.QRect(10, 100, 81, 16))
        self.log.setObjectName("log")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(10, 130, 361, 161))
        self.textEdit.setObjectName("textEdit")
        self.W_Bt = QtWidgets.QPushButton(Dialog)
        self.W_Bt.setGeometry(QtCore.QRect(270, 30, 101, 51))
        self.W_Bt.setObjectName("W_Bt")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "远程桌面"))
        self.C_Bt.setText(_translate("Dialog", "启动远程电脑"))
        self.R_Bt.setText(_translate("Dialog", "连接远程电脑"))
        self.log.setText(_translate("Dialog", "状态窗口："))
        self.W_Bt.setText(_translate("Dialog", "关闭远程电脑"))

