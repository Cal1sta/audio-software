# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\single_generate.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SingleSignal(object):
    def setupUi(self, SingleSignal):
        SingleSignal.setObjectName("SingleSignal")
        SingleSignal.resize(229, 210)
        self.verticalLayout = QtWidgets.QVBoxLayout(SingleSignal)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SingleSignal)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.Layout_type = QtWidgets.QHBoxLayout()
        self.Layout_type.setObjectName("Layout_type")
        self.label_type = QtWidgets.QLabel(SingleSignal)
        self.label_type.setAlignment(QtCore.Qt.AlignCenter)
        self.label_type.setObjectName("label_type")
        self.Layout_type.addWidget(self.label_type)
        self.type = QtWidgets.QComboBox(SingleSignal)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.type.sizePolicy().hasHeightForWidth())
        self.type.setSizePolicy(sizePolicy)
        self.type.setObjectName("type")
        self.type.addItem("")
        self.type.addItem("")
        self.type.addItem("")
        self.Layout_type.addWidget(self.type)
        self.Layout_type.setStretch(0, 1)
        self.Layout_type.setStretch(1, 1)
        self.verticalLayout.addLayout(self.Layout_type)
        self.Layout_freq = QtWidgets.QHBoxLayout()
        self.Layout_freq.setObjectName("Layout_freq")
        self.label_freq = QtWidgets.QLabel(SingleSignal)
        self.label_freq.setAlignment(QtCore.Qt.AlignCenter)
        self.label_freq.setObjectName("label_freq")
        self.Layout_freq.addWidget(self.label_freq)
        self.freq = QtWidgets.QSpinBox(SingleSignal)
        self.freq.setMaximum(40000)
        self.freq.setObjectName("freq")
        self.Layout_freq.addWidget(self.freq)
        self.verticalLayout.addLayout(self.Layout_freq)
        self.Layout_amp = QtWidgets.QHBoxLayout()
        self.Layout_amp.setObjectName("Layout_amp")
        self.label_amp = QtWidgets.QLabel(SingleSignal)
        self.label_amp.setAlignment(QtCore.Qt.AlignCenter)
        self.label_amp.setObjectName("label_amp")
        self.Layout_amp.addWidget(self.label_amp)
        self.amp = QtWidgets.QSpinBox(SingleSignal)
        self.amp.setObjectName("amp")
        self.Layout_amp.addWidget(self.amp)
        self.verticalLayout.addLayout(self.Layout_amp)
        self.Layout_offset = QtWidgets.QHBoxLayout()
        self.Layout_offset.setObjectName("Layout_offset")
        self.label_offset = QtWidgets.QLabel(SingleSignal)
        self.label_offset.setAlignment(QtCore.Qt.AlignCenter)
        self.label_offset.setObjectName("label_offset")
        self.Layout_offset.addWidget(self.label_offset)
        self.offset = QtWidgets.QSpinBox(SingleSignal)
        self.offset.setMaximum(360)
        self.offset.setSingleStep(1)
        self.offset.setObjectName("offset")
        self.Layout_offset.addWidget(self.offset)
        self.verticalLayout.addLayout(self.Layout_offset)
        self.buttonBox = QtWidgets.QDialogButtonBox(SingleSignal)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SingleSignal)
        self.type.setCurrentIndex(0)
        self.buttonBox.accepted.connect(SingleSignal.accept) # type: ignore
        self.buttonBox.rejected.connect(SingleSignal.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(SingleSignal)

    def retranslateUi(self, SingleSignal):
        _translate = QtCore.QCoreApplication.translate
        SingleSignal.setWindowTitle(_translate("SingleSignal", "单频信号生成"))
        self.label.setText(_translate("SingleSignal", "请设置您的参数"))
        self.label_type.setText(_translate("SingleSignal", "类型："))
        self.type.setItemText(0, _translate("SingleSignal", "正弦波"))
        self.type.setItemText(1, _translate("SingleSignal", "矩形波"))
        self.type.setItemText(2, _translate("SingleSignal", "脉冲波"))
        self.label_freq.setText(_translate("SingleSignal", "频率（hz）"))
        self.label_amp.setText(_translate("SingleSignal", "振幅()"))
        self.label_offset.setText(_translate("SingleSignal", "相位(°)"))