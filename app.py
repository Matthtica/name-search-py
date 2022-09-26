import sys
import pandas as pd
import re
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import json

from MainWindow import Ui_MainWindow

CONFIG_JSON = 'name_search_config.json'
SEARCH_COLUMN = 'Customer Name'
DATA_FILE = 'Data Refresh Sample Data.xlsx'

width_index = 0
height_index = 1
dir_index = 2

class TableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.config = [0] * 10
        self.load()
        ran = QAction("an action")
        self.subMenu.addAction(ran)
        self.search.setPlaceholderText("Type here to search quickly!")
        self.df = pd.read_excel(DATA_FILE)
        self.model = TableModel(self.df)
        self.table.setModel(self.model)
        self.search.textChanged.connect(self.text_changed)
        self.open_new.triggered.connect(self.openNew)

    def text_changed(self, s: str):
        if s:
            self.model._data = self.df[self.df[SEARCH_COLUMN].str.contains(s, flags=re.IGNORECASE)]
        else:
            self.model._data = self.df
        self.model.layoutChanged.emit()
    
    def resizeEvent(self, event: QResizeEvent):
        self.config[width_index] = event.size().width()
        self.config[height_index] = event.size().height()
        self.save()

    def load(self):
        try:
            with open(CONFIG_JSON, 'r') as f:
                self.config = json.load(f)
            self.resize(QSize(self.config[width_index], self.config[height_index]))
            self.updateRecentFiles()

        except Exception:
            pass
    
    def updateRecentFiles(self):
        self.action_ref = []
        self.subMenu.clear()
        for f in self.config[dir_index]:
            value = f.split('/')[-1]
            act = QAction(value)
            act.setData(f)
            act.triggered.connect(self.openRecent)
            self.subMenu.addAction(act)
            self.action_ref.append(act)

    def save(self):
        with open(CONFIG_JSON, 'w') as f:
            json.dump(self.config, f)

    def openNew(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("*.xlsx")
        if dlg.exec():
            fileNames = dlg.selectedFiles()
            df = None
            try:
                df = pd.read_excel(fileNames[0])
            except Exception:
                pass
            self.model._data = df
            self.model.layoutChanged.emit()
            if isinstance(self.config[dir_index], int):
                self.config[dir_index] = fileNames
            elif len(self.config[dir_index]) > 5:
                self.config[dir_index].pop()
                self.config[dir_index].insert(0, fileNames[0])
            else:
                self.config[dir_index].insert(0, fileNames[0])
            self.updateRecentFiles()
            self.save()

    def openRecent(self):
        f = self.sender().data()
        print(f)
        self.df = pd.read_excel(f)
        self.model._data = self.df
        self.model.layoutChanged.emit()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()