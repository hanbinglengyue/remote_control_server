# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Server_ui.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.log = QtWidgets.QLabel(Dialog)
        self.log.setGeometry(QtCore.QRect(10, 10, 101, 21))
        self.log.setObjectName("log")
        self.L_Date = QtWidgets.QTextEdit(Dialog)
        self.L_Date.setGeometry(QtCore.QRect(10, 30, 381, 261))
        self.L_Date.setObjectName("L_Date")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "GFD_Windows"))
        self.log.setText(_translate("Dialog", "状态窗口:"))
