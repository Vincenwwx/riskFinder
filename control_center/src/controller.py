import os.path
import sys, shutil, requests, json, time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal

from control_center.src.view import Window
from control_center.src.model import Model, PLU


class Detector_HTTP(QThread):
    """Detector periodically broadcasts HTTP requests to detect status of
    all connected PLUs.

    The status include ID, role and battery level.
    """
    def __init__(self, ip_range, delay=3):
        super().__init__()
        self.ip_range = self.parseIpRange(ip_range)
        # Holder of PLUs'id, which will be used to figure out if there is newly
        # joining PLU.
        self.online_ips = []
        # Signal with parameters:
        #   - PLU id (int)
        #   - Role id (int)
        #   - Battery level (int)
        self.detect_new_PLU_signal = pyqtSignal(int, int, int, name="detect_new_PLU")
        self.delay = delay

    def run(self):
        while (True):
            for ip in self.ip_range:
                schema = f'http://{ip}/info'
                try:
                    res = requests.get(schema)
                    if res.status_code == 200 and ip not in self.online_ips : # if PLU is alive and new
                        data = json.loads(res.text)
                        print(f"[Detector] New PLU found: "
                              f"id={data['id']}, "
                              f"role={data['role']}, "
                              f"battery level={data['batLel']}")
                        self.detect_new_PLU_signal.emit(data['id'], data['role'], data['batLel'])
                except:
                    pass
            time.sleep(self.delay)

    @staticmethod
    def parseIpRange(ip_range):
        """Parse ip range to list of ips.

        Example:
            '192.1.1.0-20' is parsed to ['192.1.1.0', '192.1.1.1', ..., '192.1.1.20']
        """
        tmp, end = ip_range.split('-')
        base, start = tmp.rsplit('.', 1)
        start = int(start)
        end = int(end) + 1

        res = []
        for i in range(start, end):
            res.append(f'{base}.{i}')
        return res


class Vision(QThread):
    """Camera captures the physical layout of PLUs.

    The process includes init Pi Camera, captures frames, use OpenCV to recognize
    PLUs and return the positions.
    """
    def __init__(self):
        super(Vision, self).__init__()
        # Holder of PLUs'id, which will be used to figure out if there is newly
        # joining PLU.
        id_nums = []
        see_new_PLU_signal = pyqtSignal(int, tuple)
        # TODO: init Pi Camera

    def run(self) -> None:
        #while (True):
        pass

    def get_position(self, id_num):
        """Get the position of a PLU.

        Args:
            id_num (id): the id of the target PLU.

        Returns:
            tuple: if the PLU stays in the scene, the coordinate of it will be
                   returned, otherwise None.
        """
        pass


class Controller:
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self.model = Model()  # 初始化模型
        self.detector_http = Detector_HTTP()
        self.vision = Vision()
        self._view = Window()  # 初始化视图

        self.saved_dir = "./../material/figures/"

    def create_new_role(self,
                        id_num: int,
                        role_id: int,
                        battery_level: int,
                        position: tuple,
                        figure_file_path: str):
        """Add new roles to the list.

        Args:
            id_num (int): id of new PLU.
            role_id (int): id of new PLU's role.
            battery_level (int): range from 0 to 100.
            position (tuple): coordinate of PLU.
            figure_file_path (str): path of figure file.

        Returns:
            bool: True if succeed, otherwise False.
        """
        self.model.roles.append(PLU(id_num, role_id, battery_level, position, []))
        self.model.update_connection()

        # Copy figure file to local path and rename
        saved_figure_dir = os.path.join(os.path.dirname(os.getcwd()), "material", "figures")
        if not os.path.exists(saved_figure_dir):
            print(f'Folder "{saved_figure_dir}" doesn\'t exist, create a new one.')
            os.makedirs(saved_figure_dir)
        _, extension = os.path.splitext(figure_file_path)
        save_figure_file_path = os.path.join(saved_figure_dir,
                                             f'{self.model.id_to_name(role_id)}.{extension}')
        shutil.copy(figure_file_path, save_figure_file_path)

    def delete_role(self, role_name: str):
        """Delete roles from the stored list of roles.

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

    def edit_role(self, role_name, new_role_name=None, new_figure_file_path=None):
        """ Edit existing role.

        User can either edit role's name, figure. To update figure, the program
        will firstly delete the obsolete figure file from the directory and then
        copy the new figure file and rename it.

        Args:
            role_name (str): Existent role to edit.
            new_role_name (str): Optional, if user want to rename the role, then
                                 new role name should be provided.
            new_figure_file_path (str): Optional, if user want to change the figure
                                 of a role.

        Returns:
            bool: True if successfully add a new PLU, otherwise False.
        """
        pass

    def append_new_PLU(self, PLU: dict):
        """Add a new detected PLU to the list.

        Args:
            PLU (dict): Information of PLU to add.

        Returns:
            bool: True if successfully add a new PLU, otherwise False.
        """
        pass

    def delete_PLU(self, PLU_id: int):
        """
        Delete a PLU from the list.

        Args:
            PLU_id (int): Id of the PLU to delete.

        Returns:
            bool: True if succeed, otherwise False.
        """
        pass

    def update_PLU_status(self, PLU_id, battery_level=None, position=None):
        """
        Update the status of a PLU, i.e., battery level, position.

        Args:
            PLU_id (int): Id of the PLU to update.
            battery_level (int, optional): New battery level.
            position (tuple of (int, int), optional): New position.

        Returns:
            bool: True if succeed, otherwise False.
        """
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