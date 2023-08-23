# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\pulse_generate.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PulseSignal(object):
    def setupUi(self, PulseSignal):
        PulseSignal.setObjectName("PulseSignal")
        PulseSignal.resize(176, 199)
        self.verticalLayout = QtWidgets.QVBoxLayout(PulseSignal)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(PulseSignal)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.Layout_freq = QtWidgets.QHBoxLayout()
        self.Layout_freq.setObjectName("Layout_freq")
        self.label_freq = QtWidgets.QLabel(PulseSignal)
        self.label_freq.setAlignment(QtCore.Qt.AlignCenter)
        self.label_freq.setObjectName("label_freq")
        self.Layout_freq.addWidget(self.label_freq)
        self.freq = QtWidgets.QSpinBox(PulseSignal)
        self.freq.setMaximum(40000)
        self.freq.setObjectName("freq")
        self.Layout_freq.addWidget(self.freq)
        self.verticalLayout.addLayout(self.Layout_freq)
        self.Layout_duration = QtWidgets.QHBoxLayout()
        self.Layout_duration.setObjectName("Layout_duration")
        self.label_duration = QtWidgets.QLabel(PulseSignal)
        self.label_duration.setAlignment(QtCore.Qt.AlignCenter)
        self.label_duration.setObjectName("label_duration")
        self.Layout_duration.addWidget(self.label_duration)
        self.duration = QtWidgets.QDoubleSpinBox(PulseSignal)
        self.duration.setDecimals(2)
        self.duration.setMaximum(999.99)
        self.duration.setSingleStep(0.01)
        self.duration.setObjectName("duration")
        self.Layout_duration.addWidget(self.duration)
        self.verticalLayout.addLayout(self.Layout_duration)
        self.Layout_samplerate = QtWidgets.QHBoxLayout()
        self.Layout_samplerate.setObjectName("Layout_samplerate")
        self.label_samplerate = QtWidgets.QLabel(PulseSignal)
        self.label_samplerate.setAlignment(QtCore.Qt.AlignCenter)
        self.label_samplerate.setObjectName("label_samplerate")
        self.Layout_samplerate.addWidget(self.label_samplerate)
        self.samplerate = QtWidgets.QSpinBox(PulseSignal)
        self.samplerate.setMinimum(1)
        self.samplerate.setMaximum(99999)
        self.samplerate.setObjectName("samplerate")
        self.Layout_samplerate.addWidget(self.samplerate)
        self.verticalLayout.addLayout(self.Layout_samplerate)
        self.buttonBox = QtWidgets.QDialogButtonBox(PulseSignal)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(1, 2)
        self.verticalLayout.setStretch(2, 2)
        self.verticalLayout.setStretch(3, 2)
        self.verticalLayout.setStretch(4, 2)

        self.retranslateUi(PulseSignal)
        self.buttonBox.accepted.connect(PulseSignal.accept) # type: ignore
        self.buttonBox.rejected.connect(PulseSignal.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(PulseSignal)

    def retranslateUi(self, PulseSignal):
        _translate = QtCore.QCoreApplication.translate
        PulseSignal.setWindowTitle(_translate("PulseSignal", "脉冲信号生成"))
        self.label.setText(_translate("PulseSignal", "请设置您的参数"))
        self.label_freq.setText(_translate("PulseSignal", "频率（hz）："))
        self.label_duration.setText(_translate("PulseSignal", "持续时间（s）："))
        self.label_samplerate.setText(_translate("PulseSignal", "采样率（hz）："))