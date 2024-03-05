from PyQt5.QtWidgets import (
    QStyle, QFileDialog, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QApplication,
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QTableWidgetItem,
    QHeaderView, QAction, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
import csv
import json

def update_totals_from_file(self, file_path):
    total_value = 0.0
    total_quantity = 0
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip the header
        for row in reader:
            if row:
                price = float(row[2]) if row[2] else 0
                quantity = int(row[3]) if row[3] else 0
                total_value += price * quantity
                total_quantity += quantity
    self.totalValueLabel.setText(f"Celková hodnota: {total_value:.2f} Kč")
    self.totalQuantityLabel.setText(f"Celkový počet kusů: {total_quantity}")

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Přidat Položku")

        self.layout = QFormLayout(self)

        self.ean = QLineEdit(self)
        self.layout.addRow("EAN:", self.ean)

        self.name = QLineEdit(self)
        self.layout.addRow("Název:", self.name)

        self.price = QLineEdit(self)
        self.layout.addRow("Cena:", self.price)

        self.quantity = QLineEdit(self)
        self.layout.addRow("Počet Kusů:", self.quantity)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.validateInput)
        self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)

    def validateInput(self):
        if self.ean.text() and self.name.text() and self.price.text() and self.quantity.text():
            try:
                price = float(self.price.text())
                quantity = int(self.quantity.text())
                if price < 0 or quantity < 0:
                    raise ValueError
                self.accept()
            except ValueError:
                QMessageBox.warning(self, 'Validation Error', 'Price must be a valid positive number and Quantity must be a valid positive integer')
        else:
            QMessageBox.warning(self, 'Validation Error', 'All fields must be filled')

    def getValues(self):
        return self.ean.text(), self.name.text(), self.price.text(), self.quantity.text()
class SkladovkaApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Vytvořil Amarox s.r.o. Všechna práva vyhrazena
        self.copyrightLabel = QLabel("Vytvořil Amarox s.r.o. Všechna práva vyhrazena", self)
        self.copyrightLabel.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.statusBar().addPermanentWidget(self.copyrightLabel)
        self.setWindowTitle("Skladový systém Jolanda")
        self.setGeometry(100, 100, 1024, 768)
        self.setCentralWidget(SkladTab())

def setButtonStyle(button):
    button.setStyleSheet("QPushButton {\nfont: bold;\nborder: 2px solid #0056b3;\nborder-radius: 5px;\npadding: 5px;\nmargin: 4px 2px;\n}"
                         "background-color: #007BFF;"
                         "border-radius: 5px;"
                         "color: white;"
                         "padding: 6px;"
                         "margin: 4px 2px}"
                         "QPushButton::hover {"
                         "background-color: #0056b3}")

class SkladTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Zadejte klíčové slovo pro hledání")
        self.search_field.textChanged.connect(self.filterTable)
        layout.addWidget(QLabel("Vyhledávání:"))
        layout.addWidget(self.search_field)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["EAN", "Název", "Cena", "Počet kusů"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.addButton = QPushButton(QIcon.fromTheme('document-new'), "Přidat položku")
        self.addButton.clicked.connect(self.addTestItem)
        setButtonStyle(self.addButton)
        button_layout.addWidget(self.addButton)
        self.clearButton = QPushButton(QIcon.fromTheme('edit-clear'), "Clear Table")
        self.clearButton.clicked.connect(self.clearTable)
        setButtonStyle(self.clearButton)
        button_layout.addWidget(self.clearButton)

        self.saveButton = QPushButton(QIcon.fromTheme('document-save'), "Save Data")
        self.saveButton.clicked.connect(self.saveData)
        setButtonStyle(self.saveButton)
        button_layout.addWidget(self.saveButton)

        self.loadButton = QPushButton(QIcon.fromTheme('document-open'), "Load Data")
        self.loadButton.clicked.connect(self.loadData)
        setButtonStyle(self.loadButton)
        button_layout.addWidget(self.loadButton)

        layout.addLayout(button_layout)

        self.setupTableContextMenu()

        self.totalValueLabel = QLabel("Celková hodnota: 0 Kč")
        self.totalQuantityLabel = QLabel("Celkový počet kusů: 0")
        layout.addWidget(self.totalValueLabel)
        layout.addWidget(self.totalQuantityLabel)
    def calculate_totals(self):
        total_value = 0.0
        total_quantity = 0
        for row in range(self.table.rowCount()):
            price_item = self.table.item(row, 2)
            quantity_item = self.table.item(row, 3)
            if price_item and quantity_item:
                try:
                    price = float(price_item.text())
                    quantity = int(quantity_item.text())
                    total_value += price * quantity
                    total_quantity += quantity
                except ValueError:
                    pass  # Ignore rows with invalid data
        self.totalValueLabel.setText(f"Celková hodnota: {total_value:.2f} Kč")
        self.totalQuantityLabel.setText(f"Celkový počet kusů: {total_quantity}")

    def update_dashboard(self):
        self.calculate_totals()

    def setupTableContextMenu(self):
        self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
        editAction = QAction("Edit", self)
        editAction.triggered.connect(self.editItem)
        self.table.addAction(editAction)

        deleteAction = QAction("Delete", self)
        deleteAction.triggered.connect(self.deleteItem)
        self.table.addAction(deleteAction)
    def addTestItem(self):
        dialog = AddItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            ean, name, price, quantity = dialog.getValues()
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(ean))
            self.table.setItem(row_count, 1, QTableWidgetItem(name))
            self.table.setItem(row_count, 2, QTableWidgetItem(price))
            self.table.setItem(row_count, 3, QTableWidgetItem(quantity))
            self.update_dashboard()  # Update totals after adding a new item

    def clearTable(self):
        self.table.setRowCount(0)
        self.update_dashboard()  # Update totals after clearing the table

    def saveData(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w') as csv_file:
                writer = csv.writer(csv_file)
                for row in range(self.table.rowCount()):
                    row_data = []
                    for column in range(self.table.columnCount()):
                        item = self.table.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    writer.writerow(row_data)
    def loadData(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)")
        if path:
            self.table.setRowCount(0)  # Clear the table
            with open(path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    row_data = [QTableWidgetItem(field) for field in row]
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    for i in range(len(row_data)):
                        self.table.setItem(row_position, i, row_data[i])
            self.update_dashboard()  # Update totals after loading data

    def editItem(self):
        selected = self.table.currentRow()
        if selected >= 0:
            ean, name, price, quantity = [self.table.item(selected, i).text() for i in range(4)]
            dialog = AddItemDialog(self)
            dialog.ean.setText(ean)
            dialog.name.setText(name)
            dialog.price.setText(price)
            dialog.quantity.setText(quantity)
            if dialog.exec_() == QDialog.Accepted:
                new_ean, new_name, new_price, new_quantity = dialog.getValues()
                self.table.setItem(selected, 0, QTableWidgetItem(new_ean))
                self.table.setItem(selected, 1, QTableWidgetItem(new_name))
                self.table.setItem(selected, 2, QTableWidgetItem(new_price))
                self.table.setItem(selected, 3, QTableWidgetItem(new_quantity))
                self.update_dashboard()  # Update totals after editing an item
    def deleteItem(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)
            self.update_dashboard()  # Update totals after deleting an item

    def filterTable(self):
        search_text = self.search_field.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

def main():
    app = QApplication(sys.argv)
    main_window = SkladovkaApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# Přidání funkce pro export dat
def export_data(self, data, export_file_path):
    # Export dat do CSV souboru
    data.to_csv(export_file_path, index=False)

# Příklad použití exportu
data = self.load_data('some_file.xls')  # Načtení dat
processed_data = self.process_data(data)  # Zpracování dat
self.export_data(processed_data, 'exported_data.csv')  # Export dat

# Vytvořil Amarox s.r.o. Všechna práva vyhrazena