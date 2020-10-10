from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class UserTableView(QTableWidget):
    def __init__(self, user_data, *args):
        self.data = user_data
        QTableWidget.__init__(self, len(self.data), 2)
        self.setupData()
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.sortByColumn(1, Qt.AscendingOrder)

    def setupData(self):
        headers = ['nom', 'user']
        self.setHorizontalHeaderLabels(headers)
        for i, user in enumerate(self.data):
            user_item = QTableWidgetItem(user[0])
            self.setItem(i, 0, user_item)
            name_item = QTableWidgetItem(user[1])
            self.setItem(i, 1, name_item)
