import math
import random

import PyQt5
import qdarkstyle
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QGridLayout,
                             QHBoxLayout, QHeaderView, QLabel, QPushButton,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QTabWidget, QVBoxLayout, QWidget)

import backend.processOptions as opts
import backend.timeFilesManager as timeManager

tabsObject = None

currentTable = None
lastSelectedRow = None


def startGUI():
    app = QApplication([])
    app.setStyle('Fusion')
    if opts.timeclockOpts["darkTheme"]:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = QWidget()
    window.setWindowTitle(opts.timeclockOpts["title"])
    window.setWindowIcon(QtGui.QIcon(
        "../data/assets/" + opts.timeclockOpts["logo"]))
    mainLayout = QVBoxLayout()
    mainLayout.setSpacing(20)

    mainLayout.addLayout(makeTitle())

    global tabsObject
    tabsObject = makeNameArea()
    mainLayout.addWidget(tabsObject)
    updateNamesTable()

    mainLayout.addLayout(makeActions(app))

    window.setLayout(mainLayout)
    window.showFullScreen()
    app.exec_()


def makeTitle():
    titleLayout = QHBoxLayout()
    # titleLayout.setSpacing(42)
    titleFont = QtGui.QFont("Times", 32, QtGui.QFont.Bold)

    title = QLabel(opts.timeclockOpts["title"])
    title.setFixedWidth(820)
    title.setFont(titleFont)

    logo = QLabel()
    logoImage = QtGui.QPixmap("../data/assets/" + opts.timeclockOpts["logo"])
    logoImage = logoImage.scaled(QtCore.QSize(100, 100))
    logo.setPixmap(logoImage)
    if opts.timeclockOpts["darkTheme"]:
        logo.setStyleSheet("QLabel {background:white}")

    titleLayout.addWidget(title)
    titleLayout.addStretch()
    titleLayout.addWidget(logo)
    return titleLayout


def makeNameArea():
    tabs = QTabWidget()
    tabs.setStyleSheet(
        "QTabBar::tab {width: 130px; height:40px} QTabBar::scroller{width:50px;}")

    for i in opts.timeclockOpts["teams"]:
        currentNames = []
        for j in timeManager.nameList:
            if i in timeManager.getJobs(j):
                currentNames.append(j)
        tab = makeNamelist(currentNames)
        if i == opts.timeclockOpts["teams"][0]:
            global currentTable
            currentTable = tab
        tabs.addTab(tab, i)

    def setCurrentTable():
        global currentTable
        global lastSelectedRow
        if lastSelectedRow != None:
            for i in range(currentTable.columnCount()):
                currentTable.item(lastSelectedRow, i).setSelected(False)
        lastSelectedRow = None
        currentTable = tabs.currentWidget()
    tabs.currentChanged.connect(setCurrentTable)

    return tabs


def makeTableItem(text):
    text = str(text)
    item = QTableWidgetItem()
    item.setText(text)
    item.setFlags(Qt.ItemIsEnabled)
    item.setFlags(Qt.ItemIsSelectable)
    return item


def makeNamelist(names):
    namesTable = QTableWidget()
    namesTable.setFixedSize(994, 450)  # 451
    namesTable.setRowCount(len(names))  # NAMES
    namesTable.setColumnCount(4)
    namesTable.setShowGrid(False)
    scroller = namesTable.verticalScrollBar()
    scroller.setStyleSheet("QScrollBar:vertical{width: 50px;}")
    # QScrollBar::left-arrow:vertical, QScrollBar::right-arrow:vertical{height:100px;}
    namesTable.verticalHeader().hide()
    ntPalette = namesTable.palette()
    if opts.timeclockOpts["darkTheme"]:
        ntPalette.setColor(QtGui.QPalette.Text, Qt.white)
    else:
        ntPalette.setColor(QtGui.QPalette.Text, Qt.black)
    namesTable.setPalette(ntPalette)

    def setLastRow(r, *args):
        global lastSelectedRow
        for i in range(namesTable.columnCount()):
            if lastSelectedRow != None:
                namesTable.item(lastSelectedRow, i).setSelected(False)
            namesTable.item(r, i).setSelected(True)
        lastSelectedRow = r
    namesTable.cellClicked.connect(setLastRow)

    headers = ["Name", "Graph", "Hours", "I/O"]
    for header in range(len(headers)):
        headItem = QTableWidgetItem()
        headItem.setText(headers[header])
        namesTable.setHorizontalHeaderItem(header, headItem)

    for i in range(namesTable.rowCount()):
        nameItem = makeTableItem(names[i])
        namesTable.setItem(i, 0, nameItem)
        #
        graphItem = makeTableItem("")
        graphFont = graphItem.font()
        graphFont.setStretch(25)
        graphFont.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 0)
        graphItem.setFont(graphFont)
        namesTable.setItem(i, 1, graphItem)
        #
        hoursItem = makeTableItem("")
        namesTable.setItem(i, 2, hoursItem)
        #
        ioItem = makeTableItem("")
        ioFont = QtGui.QFont("Courier New", 14)
        ioFont.setBold(True)
        ioItem.setFont(ioFont)
        ioItem.setTextAlignment(Qt.AlignRight)
        namesTable.setItem(i, 3, ioItem)

    namesTable.setVisible(False)
    namesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    namesTable.setColumnWidth(1, 100)
    namesTable.resizeColumnToContents(2)
    namesTable.resizeColumnToContents(3)
    namesTable.setVisible(True)
    return namesTable


def updateNamesTable():
    global tabsObject
    for i in range(tabsObject.count()):
        table = tabsObject.widget(i)
        for j in range(table.rowCount()):
            name = table.item(j, 0).text()

            table.item(j, 1).setText("█" * 0)

            hours = timeManager.getHours(name)
            hoursInt = math.floor(hours)
            hourString = str(hoursInt)
            minuteInt = math.floor((hours - hoursInt) * 60)
            minuteString = str(minuteInt)
            table.item(j, 2).setText(hourString + ":" + ("" if minuteInt > 9 else "0") + minuteString)

            ioItem = table.item(j, 3)
            ioItem.setText(timeManager.getCurrentIO(name))
            if ioItem.text() == "i":
                ioItem.setForeground(QtGui.QBrush(Qt.darkGreen))
            elif ioItem.text() == "o":
                ioItem.setForeground(QtGui.QBrush(Qt.black))
            elif ioItem.text() == "a":
                ioItem.setForeground(QtGui.QBrush(Qt.red))
            else:
                ioItem.setForeground(QtGui.QBrush(Qt.yellow))


def makeActions(app):
    actionsLayout = QGridLayout()
    actionsLayout.setVerticalSpacing(5)

    actionsLayout.setRowMinimumHeight(0, 30)
    actionsLayout.setRowMinimumHeight(1, 18)
    actionsLayout.setRowMinimumHeight(2, 50)

    signI = QPushButton("IN")
    signO = QPushButton("OUT")
    signI.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    signI.setStyleSheet(
        'QPushButton {background-color: green; color: white; font-size: 28pt; font-weight: bold}')
    signO.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    signO.setStyleSheet(
        'QPushButton {background-color: red; color: white; font-size: 28pt; font-weight: bold}')

    def doIO(io):
        if currentTable != None and lastSelectedRow != None:
            timeManager.signIO(currentTable.item(
                lastSelectedRow, 0).text(), io)
        else:
            print("No item", currentTable != None, lastSelectedRow != None)
        updateNamesTable()

    signI.clicked.connect(lambda: doIO("i"))
    signO.clicked.connect(lambda: doIO("o"))

    more = QPushButton("More user information")
    newUser = QPushButton("New User")
    graph = QPushButton("Graph")
    update = QPushButton("Update")
    quit = QPushButton("Quit")
    more.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
    newUser.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
    graph.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
    update.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
    quit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
    quit.setStyleSheet('QPushButton {color: red}')

    update.clicked.connect(updateNamesTable)
    quit.clicked.connect(lambda: app.closeAllWindows())

    actionsLayout.addWidget(signI, 0, 0, 3, 2)
    actionsLayout.addWidget(signO, 0, 2, 3, 2)
    actionsLayout.addWidget(more, 0, 4, 2, 1)
    actionsLayout.addWidget(newUser, 2, 4)
    actionsLayout.addWidget(graph, 0, 5)
    actionsLayout.addWidget(update, 1, 5)
    actionsLayout.addWidget(quit, 2, 5)
    return actionsLayout
