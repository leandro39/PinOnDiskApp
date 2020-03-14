from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(516, 516)
        MainWindow.setMinimumSize(QtCore.QSize(516, 516))
        MainWindow.setMaximumSize(QtCore.QSize(516, 516))
        MainWindow.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        MainWindow.setAcceptDrops(False)
        MainWindow.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(16, 4, 481, 59))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.gridLayout = QtWidgets.QGridLayout(self.horizontalLayoutWidget_3)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.portCombo = QtWidgets.QComboBox(self.horizontalLayoutWidget_3)
        self.portCombo.setObjectName("portCombo")
        self.gridLayout.addWidget(self.portCombo, 1, 0, 1, 4)
        
        self.labelNotConnected = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.labelNotConnected.setMaximumHeight(26)
        self.labelNotConnected.setMaximumWidth(26)
        self.labelNotConnected.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelNotConnected.setText = ""
        self.labelNotConnected.setScaledContents(True)
        self.labelNotConnected.setObjectName("labelNotConnected")
        self.gridLayout.addWidget(self.labelNotConnected, 1, 12, 1, 4)

        self.labelConnected = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.labelConnected.setMaximumHeight(26)
        self.labelConnected.setMaximumWidth(26)
        self.labelConnected.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelConnected.setText = ""
        self.labelConnected.setScaledContents(True)
        self.labelConnected.setObjectName("labelConnected")
        self.gridLayout.addWidget(self.labelConnected, 1, 12, 1, 4)
        self.labelConnected.hide()

        self.label_3 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.conectarBtn = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.conectarBtn.setObjectName("conectarBtn")
        self.gridLayout.addWidget(self.conectarBtn, 1, 5, 1, 4)
        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 2)
        self.gridLayout.setColumnStretch(2, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setEnabled(False)
        self.groupBox.setGeometry(QtCore.QRect(8, 88, 493, 325))
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.groupBox)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(8, 24, 481, 285))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.experimentNameInput = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.experimentNameInput.setObjectName("experimentNameInput")
        self.verticalLayout_3.addWidget(self.experimentNameInput)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pathInput = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.pathInput.setEnabled(False)
        self.pathInput.setReadOnly(True)
        self.pathInput.setObjectName("pathInput")
        self.horizontalLayout_2.addWidget(self.pathInput)
        self.pathBrowseBtn = QtWidgets.QToolButton(self.verticalLayoutWidget_2)
        self.pathBrowseBtn.setObjectName("pathBrowseBtn")
        self.horizontalLayout_2.addWidget(self.pathBrowseBtn)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.distanciaInput = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.distanciaInput.setObjectName("distanciaInput")
        self.horizontalLayout.addWidget(self.distanciaInput)
        self.label_6 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.label_5 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_3.addWidget(self.label_5)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.radioCombo = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        self.radioCombo.setObjectName("radioCombo")
        self.horizontalLayout_3.addWidget(self.radioCombo)
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.label_8 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_3.addWidget(self.label_8)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.cargaInput = QtWidgets.QLineEdit(self.verticalLayoutWidget_2)
        self.cargaInput.setObjectName("cargaInput")
        self.horizontalLayout_5.addWidget(self.cargaInput)
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_5.addWidget(self.label_9)
        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayoutWidget_5 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_5.setGeometry(QtCore.QRect(12, 404, 485, 73))
        self.horizontalLayoutWidget_5.setObjectName("horizontalLayoutWidget_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_5)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.startBtn = QtWidgets.QPushButton(self.horizontalLayoutWidget_5)
        self.startBtn.setEnabled(False)
        self.startBtn.setObjectName("startBtn")
        self.horizontalLayout_4.addWidget(self.startBtn)
        self.pauseBtn = QtWidgets.QPushButton(self.horizontalLayoutWidget_5)
        self.pauseBtn.setEnabled(False)
        self.pauseBtn.setObjectName("pauseBtn")
        self.horizontalLayout_4.addWidget(self.pauseBtn)
        self.stopBtn = QtWidgets.QPushButton(self.horizontalLayoutWidget_5)
        self.stopBtn.setEnabled(False)
        self.stopBtn.setObjectName("stopBtn")
        self.horizontalLayout_4.addWidget(self.stopBtn)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 516, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "POD App"))
        self.label_3.setText(_translate("MainWindow", "Seleccione puerto del controlador"))
        self.conectarBtn.setText(_translate("MainWindow", "Conectar"))
        self.groupBox.setTitle(_translate("MainWindow", "Configuración de experimento"))
        self.label_2.setText(_translate("MainWindow", "Nombre del experimento"))
        self.label.setText(_translate("MainWindow", "Seleccione carpeta de destino para guardar datos del ensayo:"))
        self.pathBrowseBtn.setText(_translate("MainWindow", "..."))
        self.label_4.setText(_translate("MainWindow", "Distancia"))
        self.label_6.setText(_translate("MainWindow", "m"))
        self.label_5.setText(_translate("MainWindow", "Radio"))
        self.label_7.setText(_translate("MainWindow", "mm"))
        self.label_8.setText(_translate("MainWindow", "Carga"))
        self.label_9.setText(_translate("MainWindow", "N"))
        self.startBtn.setText(_translate("MainWindow", "Empezar"))
        self.pauseBtn.setText(_translate("MainWindow", "Pausar"))
        self.stopBtn.setText(_translate("MainWindow", "Detener"))
