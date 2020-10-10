
from PyQt5.QtWidgets import (
    QMainWindow, QShortcut, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QWidget, QTabWidget, QDialog, QDialogButtonBox, QLineEdit,
    QMessageBox, QScrollArea, QGroupBox, QCheckBox)
from PyQt5.QtGui import QKeySequence, QFont, QIcon
from PyQt5.QtCore import Qt
from UserTableView import UserTableView
from settings import Settings
from DB import DB
import sys
import logging


class MainWindow(QMainWindow):

    def __init__(self, *args):
        super(QMainWindow, self).__init__()
        self.setWindowIcon(QIcon("icon.png"))
        self.init_logger()
        Settings.load(self)
        self.connectDialog()
        self.find_roles()

        shortcut1 = QShortcut(QKeySequence("Ctrl+A"), self)
        shortcut1.activated.connect(self.select_all)
        shortcut2 = QShortcut(QKeySequence("Ctrl+Z"), self)
        shortcut2.activated.connect(self.unselect_all)

        self.editing = False
        self.resize(1100, 600)

        mainLayout = QHBoxLayout()
        self.table = UserTableView(self.db.get_users_list())
        self.table.itemSelectionChanged.connect(self.select_user)
        mainLayout.addWidget(self.table)
        self.user_label = QLabel()
        font = QFont('sans-serif', 12, QFont.Bold)
        self.user_label.setFont(font)

        self.tabs = QTabWidget()
        self.init_ui_tabs()

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.btn_edit = QPushButton("Edit")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_save = QPushButton("Save")
        self.btn_copy = QPushButton("Copy from")

        line = QFrame()
        line.setFrameShape(QFrame.VLine)

        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.btn_copy.setEnabled(False)

        self.btn_edit.clicked.connect(self.btn_edit_clicked)
        self.btn_cancel.clicked.connect(self.btn_cancel_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.btn_copy.clicked.connect(self.btn_copy_clicked)
        hbox.addWidget(self.btn_edit)
        hbox.addWidget(self.btn_cancel)
        hbox.addWidget(self.btn_save)
        hbox.addWidget(line)
        hbox.addWidget(self.btn_copy)
        vbox.addLayout(hbox)
        vbox.addWidget(self.user_label)
        vbox.addWidget(self.tabs)
        mainLayout.addLayout(vbox)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)
        self.setWindowTitle("TW Users Admin - ["+self.db.username+"]")
        self.table.setCurrentCell(0, 0)

    def onError(self, title, message):
        self.logger.warning(message)
        QMessageBox.warning(self, title, message)
		#setWindowIcon(QIcon("icon.png"))
        sys.exit()

    def init_logger(self):
        logging.basicConfig(
            filename='admin_app.log',
            format='%(asctime)s,%(msecs)d %(levelname)-8s '
            + '[%(filename)s:%(lineno)d:%(funcName)s] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.DEBUG)
        self.logger = logging.getLogger('tw-logger')

    def select_all(self):
        if self.editing:
            for tab in self.tabs.tabs:
                for checkBox in tab.checkBoxList:
                    checkBox.setChecked(True)

    def unselect_all(self):
        if self.editing:
            for tab in self.tabs.tabs:
                for checkBox in tab.checkBoxList:
                    checkBox.setChecked(False)

    def connectDialog(self):
        if 'user' in Settings.settings and 'password' in Settings.settings:
            self.db = DB(Settings.settings['user'],
                         Settings.settings['password'], self)
            return
        d = QDialog()
        d.setWindowTitle("Connect user")
        d.setWindowModality(Qt.ApplicationModal)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        d.buttonBox = QDialogButtonBox(QBtn)
        d.buttonBox.accepted.connect(d.accept)
        d.buttonBox.rejected.connect(d.reject)

        d.layout = QVBoxLayout()
        d.layout.addWidget(QLabel('Username:'))
        usernameEdit = QLineEdit()
        d.layout.addWidget(usernameEdit)
        d.layout.addWidget(QLabel('Password:'))
        passwordEdit = QLineEdit()
        d.layout.addWidget(passwordEdit)
        passwordEdit.setEchoMode(QLineEdit.Password)
        d.layout.addWidget(d.buttonBox)
        d.setLayout(d.layout)
        if 'user' in Settings.settings:
            usernameEdit.setText(Settings.settings['user'])
            passwordEdit.setFocus(True)
        if d.exec_():
            username = usernameEdit.text()
            password = passwordEdit.text()
            self.db = DB(username, password, self)
        else:
            sys.exit()

    def btn_edit_clicked(self):
        self.btn_edit.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_copy.setEnabled(True)
        self.table.setEnabled(False)
        self.reset_options()
        self.set_editing_enabled(True)

    def btn_cancel_clicked(self):
        self.btn_edit.setEnabled(True)
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.btn_copy.setEnabled(False)
        self.table.setEnabled(True)
        self.reset_options()
        self.set_editing_enabled(False)

    def btn_save_clicked(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure!")
        msg.setInformativeText('Save changes to "'+self.user_name+'" ?')
        msg.setWindowTitle("Save Changes")
        msg.setWindowIcon(QIcon("icon.png"))
        msg.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)

        if msg.exec_() == QMessageBox.Save:
            self.save_user_roles()
            self.btn_cancel_clicked()

    def save_user_roles(self):
        granted_roles = (role for role in self.user_roles_mod if role not in
                         self.user_roles)
        revoked_roles = (role for role in self.user_roles if role not in
                         self.user_roles_mod)
        self.db.grant_user_roles(self.user_name, granted_roles)
        self.db.revoke_user_roles(self.user_name, revoked_roles)
        self.user_roles = self.user_roles_mod

    def btn_copy_clicked(self):
        d = QDialog()
        d.setWindowTitle("Copy from")
        d.setWindowModality(Qt.ApplicationModal)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        d.buttonBox = QDialogButtonBox(QBtn)
        d.buttonBox.accepted.connect(d.accept)
        d.buttonBox.rejected.connect(d.reject)

        d.layout = QVBoxLayout()
        d.layout.addWidget(QLabel('select other user:'))
        userList = [user for user in self.db.get_users_list() if user[1]
                    != self.user_name]
        d.table = UserTableView(userList)
        d.layout.addWidget(d.table)
        d.layout.addWidget(d.buttonBox)
        d.setLayout(d.layout)
        d.table.setCurrentCell(0, 0)
        if d.exec_():
            selectedUser = d.table.selectedItems()[1].text()
            self.user_roles_mod = self.db.get_user_roles(selectedUser)
            for tab in self.tabs.tabs:
                for checkbox in tab.checkBoxList:
                    checkbox.setChecked(
                        checkbox.roleName in self.user_roles_mod)

    def reset_options(self):
        self.user_roles_mod = self.user_roles.copy()
        for tab in self.tabs.tabs:
            for cb in tab.checkBoxList:
                cb.setStyleSheet("color: black")
                cb.setChecked(cb.roleName in self.user_roles)
        self.update_tab_names()

    def set_editing_enabled(self, enabled):
        self.editing = enabled
        for tab in self.tabs.tabs:
            for cb in tab.checkBoxList:
                cb.setEnabled(enabled)

    def setup_tab(self, name, groups):
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        tab.checkBoxList = []
        tabContent = QWidget()
        vbox = QVBoxLayout(tabContent)
        role_count = 0
        for groupName, groupRoles in groups.items():
            groupbox = QGroupBox(groupName)
            hbox = QHBoxLayout(groupbox)
            vbox1 = QVBoxLayout()
            vbox1.setAlignment(Qt.AlignTop)
            vbox2 = QVBoxLayout()
            vbox2.setAlignment(Qt.AlignTop)
            roles_info = ((role[0].upper(), role[1])
                          for role in groupRoles.items())
            roles = [role for role in roles_info
                     if role[0] in self.valid_roles]
            sortedRoles = sorted(roles, key=lambda role: role[1])
            role_count += len(roles)
            for i, (roleName, roleTitle) in enumerate(sortedRoles):
                cb = QCheckBox(roleTitle, tab)
                cb.stateChanged.connect(self.option_checked)
                cb.setEnabled(False)
                cb.roleName = roleName
                tab.checkBoxList.append(cb)
                if i < len(roles)/2:
                    vbox1.addWidget(cb)
                else:
                    vbox2.addWidget(cb)
            hbox.addLayout(vbox1)
            hbox.addLayout(vbox2)
            vbox.addWidget(groupbox)
        tab.setWidget(tabContent)
        tab.name = name
        self.tabs.addTab(tab, '{} ({})'.format(name,role_count))
        self.tabs.tabs.append(tab)

    def option_checked(self, state):
        checkbox = self.sender()
        if not checkbox.isEnabled():
            return
        role = checkbox.roleName
        if role in self.user_roles_mod and state == Qt.Unchecked:
            self.user_roles_mod.remove(role)
        elif role not in self.user_roles_mod and state == Qt.Checked:
            self.user_roles_mod.append(role)
        if role in self.user_roles_mod and role not in self.user_roles:
            checkbox.setStyleSheet("color: green")
        elif role not in self.user_roles_mod and role in self.user_roles:
            checkbox.setStyleSheet("color: red")
        else:
            checkbox.setStyleSheet("color: black")
        self.update_tab_names()
        self.check_for_save()

    def check_for_save(self):
        edited_options = sum(role not in self.user_roles
                             for role in self.user_roles_mod)
        edited_options += sum(role not in self.user_roles_mod
                              for role in self.user_roles)
        self.need_save = edited_options > 0
        self.btn_save.setEnabled(self.need_save)

    def init_ui_tabs(self):
        self.tabs.tabs = []
        for tab_name, tab in Settings.app_roles.items():
            self.setup_tab(tab_name, tab)

    def select_user(self):
        self.user = self.table.selectedItems()[0].text()
        self.user_name = self.table.selectedItems()[1].text()
        self.user_label.setText(self.user_name+' : '+self.user)
        self.user_roles = self.db.get_user_roles(self.user_name)
        self.reset_options()
        self.update_tab_names()

    def update_tab_names(self):
        for tabi in range(self.tabs.count()):
            widget = self.tabs.widget(tabi)
            role_count = len(widget.checkBoxList)
            user_role_count = sum(cb.roleName in self.user_roles_mod
                                  for cb in widget.checkBoxList)
            self.tabs.setTabText(
                tabi, '{} ({}/{})'.format(widget.name,user_role_count,role_count))

    def find_roles(self):
        set_forms = set(Settings.form_roles)
        set_db = set(self.db.get_all_db_roles())

        self.valid_roles = list(set_forms.intersection(set_db))
        invalid_roles = list(set_forms.difference(set_db))

        if invalid_roles:
            roles = ','.join(invalid_roles)
            self.onError('Invalid DB roles', 'invalid DB roles : '+roles)
