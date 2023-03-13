from PySide6 import QtWidgets
from PySide6.QtCore import Slot


class CategoryWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        modify_button = QtWidgets.QPushButton("Редактировать категории")
        modify_button.clicked.connect(self.modify_categories)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(modify_button)
        self.setLayout(layout)

    @Slot()
    def modify_categories(self):
        modify_form = AddCategoryForm()
        modify_form.exec()


class AddCategoryForm(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QFormLayout()

        parent_label = QtWidgets.QLabel("Категория-родитель")
        self.parent_input = QtWidgets.QLineEdit()
        layout.addRow(parent_label, self.parent_input)

        category_label = QtWidgets.QLabel("Новая категория")
        self.category_input = QtWidgets.QLineEdit()
        layout.addRow(category_label, self.category_input)

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self._register_buttons()
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    @Slot()
    def ok_button_click(self):
        # self.is_ok_clicked = True
        self.accept()

    def _register_buttons(self):
        ok_button = QtWidgets.QDialogButtonBox.StandardButton.Ok
        cancel_button = QtWidgets.QDialogButtonBox.StandardButton.Cancel
        self.buttonBox.addButton(ok_button)
        self.buttonBox.addButton(cancel_button)

        self.buttonBox.accepted.connect(self.ok_button_click)
        self.buttonBox.rejected.connect(self.reject)


class DeleteCategoryForm(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QFormLayout()

        category_label = QtWidgets.QLabel("Категория")
        self.category_input = QtWidgets.QLineEdit()
        layout.addRow(category_label, self.category_input)

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self._register_buttons()
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    @Slot()
    def ok_button_click(self):
        # self.is_ok_clicked = True
        self.accept()

    def _register_buttons(self):
        delete_button = QtWidgets.QDialogButtonBox.StandardButton.Ok
        delete_button.name = 'Удалить'
        cancel_button = QtWidgets.QDialogButtonBox.StandardButton.Cancel
        cancel_button.name = 'Отмена'
        self.buttonBox.addButton(delete_button)
        self.buttonBox.addButton(cancel_button)

        self.buttonBox.accepted.connect(self.ok_button_click)
        self.buttonBox.rejected.connect(self.reject)
