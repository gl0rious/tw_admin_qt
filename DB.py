import cx_Oracle
from settings import Settings
import sys
from PyQt5.QtWidgets import QMessageBox
import logging


class DB:
    def __init__(self, username, password, mainWindow):
        self.username = username
        self.password = password
        self.host = Settings.settings['host']
        self.port = Settings.settings['port']
        self.instance = Settings.settings['instance']
        self.mainWindow = mainWindow
        self.logger = logging.getLogger('tw-logger')
        self.check_user_DBA_privilege()

    def log_error_and_exit(self, exc, debug):
        error, = exc.args
        QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                            error.message)
        self.logger.error(error.message)
        sys.exit()

    def connect(self):
        try:
            return cx_Oracle.connect('tw08/pproot08@192.168.2.33:1521/SIT08001')
            # return cx_Oracle.connect('{}/{}@{}:{}/{}'.format(self.username,self.password,self.host,self.port,self.instance))
        except cx_Oracle.Error as exc:
            error, = exc.args
            QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                                error.message)
            self.logger.error(error.message)
            sys.exit()

    def check_user_DBA_privilege(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("""SELECT Count(*) FROM USER_ROLE_PRIVS
                     where granted_role='DBA'""")
        count = c.fetchone()[0]
        if count == 0:
            QMessageBox.warning(
                self.mainWindow,
                'Login error', '"{}" not a DBA user, retry'.format(self.username))
            self.logger.error('User {} : Not a DBA user'.format(self.username))
            conn.close()
            sys.exit()

    def get_users_list(self):
        try:
            conn = self.connect()
            users = []
            c = conn.cursor()
            c.execute(
                "select upper(utilis), nom_utilis from utilisateur_app")
            for row in c:
                users.append((row[0], row[1]))
            c.close()
            conn.close()
            return users
        except cx_Oracle.Error as exc:
            error, = exc.args
            QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                                error.message)
            self.logger.error(error.message)
            sys.exit()

    def get_all_db_roles(self):
        try:
            conn = self.connect()
            perms = []
            c = conn.cursor()
            c.execute("SELECT upper(role) FROM DBA_ROLES")
            for row in c:
                perms.append(row[0])
            perms = perms[34:]
            c.close()
            conn.close()
            return perms
        except cx_Oracle.Error as exc:
            error, = exc.args
            QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                                error.message)
            self.logger.error(error.message)
            sys.exit()

    def get_user_roles(self, user):
        try:
            conn = self.connect()
            perms = []
            c = conn.cursor()
            c.execute(
                """SELECT ROLE_UTILIS
                FROM ROLE_UTILISATEUR WHERE(NOM_UTILIS='{}')""".format(user))
            for row in c:
                perms.append(row[0])
            c.close()
            conn.close()
            return perms
        except cx_Oracle.Error as exc:
            error, = exc.args
            QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                                error.message)
            self.logger.error(error.message)
            sys.exit()

    def grant_user_roles(self, user, perms):
        try:
            sql1 = '''
                    INSERT INTO ROLE_UTILISATEUR
                        VALUES ('{user}','{perm}')
                    '''
            sql2 = 'GRANT {perm} TO {user}'
            conn = self.connect()
            c = conn.cursor()
            for perm in perms:
                c.execute(sql1.format(user=user, perm=perm))
                c.execute(sql2.format(user=user, perm=perm))
            c.close()
            conn.close()
        except cx_Oracle.Error as exc:
            error, = exc.args
            QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                                error.message)
            self.logger.error(error.message)
            sys.exit()

    def revoke_user_roles(self, user, perms):
        try:
            sql1 = """DELETE FROM ROLE_UTILISATEUR
                        WHERE NOM_UTILIS='{user}' and ROLE_UTILIS='{perm}'"""
            sql2 = 'revoke {perm} from {user}'
            conn = self.connect()
            c = conn.cursor()
            for perm in perms:
                c.execute(sql1.format(user=user, perm=perm))
                c.execute(sql2.format(user=user, perm=perm))
            c.close()
            conn.close()
        except cx_Oracle.Error as exc:
            error, = exc.args
            QMessageBox.warning(self.mainWindow, 'Error {}'.format(error.code),
                                error.message)
            self.logger.error(error.message)
            sys.exit()
