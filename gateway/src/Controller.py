import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread

from view import Window
from model import Model


class Http_requester(QThread):
    def __init__(self):
        super().__init__()


class Controller:
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self.model = Model()  # 初始化模型
        self.http_requester = Http_requester()
        #self.http_requester.http_signal.connect()
        self._view = Window()  # 初始化视图
        self.init()

    def init(self):
        self._view.verifySignal.connect(self.verify_credentials)

    def append_new_role(self, role_name: str):
        """
        Add new roles to the list.

        Returns:
            bool: True if succeed, otherwise False.
        """
        pass

    def delete_role(self, role_name: str):
        """
        Delete roles from the list.

        Args:
            role_name (string): name of role to delete.

        Returns:
            bool: True if succeed, otherwise False.
        """
        pass

    def delete_roles(self, roles: list):
        """
        Delete a bunch of roles.

        Args:
            roles (list): list of roles to delete.

        Returns:
            bool: True if succeed, otherwise False.
        """
        if roles:
            for role in roles:
                self.delete_role(role)

    def edit_role(self, role_name: str):
        pass

    def run(self):
        self._view.show()
        return self._app.exec_()


if __name__ == '__main__':
    controller = Controller()
    try:
        sys.exit(controller.run())
    except SystemExit:
        print("Closing app...")