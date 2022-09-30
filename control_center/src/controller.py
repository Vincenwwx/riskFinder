import os.path
import sys, shutil, requests, json, time
import configparser
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal

from control_center.src.view import Window
from control_center.src.model import Model, PLU


class Detector_HTTP(QThread):
    """Detector periodically broadcasts HTTP requests to detect status of
    all connected PLUs.

    The status include ID, role and battery level.
    """

    # Signal with parameters:
    #   - PLU id (int)
    #   - Role id (int)
    #   - Battery level (int)
    #detect_PLU_joins_signal = pyqtSignal(int, int, int, name="detect_new_PLU_joins")
    #detect_PLU_leaves_signal = pyqtSignal(int, name="detect_PLU_leaves")
    detected_PLU_signal = pyqtSignal(list)

    def __init__(self, http_config):  # Send an HTTP request every {delay}/s
        super().__init__()
        self.ip_range = self.parse_ip_range(http_config["ip_range"])
        # TODO: or just a list?
        self.online_PLUs = []  # dict in form of 'ip': PLU_id
        self.delay = http_config["http_requesting_delay"]
        self.get_info_suffix = http_config["get_info_suffix"]

    def run(self):
        """
        Test the existence of PLUs by sending HTTP requests to every ip in the
        list for every {delay} seconds.
        """
        while(True):
            online_PLUs = []
            for ip in self.ip_range:
                schema = f'http://{ip}/{self.get_info_suffix}'
                try:
                    res = requests.get(schema)

                    if res.status_code == 200:  # target is connected
                        data = json.loads(res.text)
                        print(f"[Detector] New PLU found: "
                              f"id={data['id']}, "
                              f"role={data['role']}, "
                              f"battery level={data['batLel']}")
                        # TODO: What to do after detecting a new PLU?
                        online_PLUs.append([data['id'], data['role'], data['batLel']])
                        """
                        if ip not in self.online_PLUs:  # if target is new
                            self.detect_PLU_joins_signal.emit(data['id'], data['role'], data['batLel'])
                        """

                except ConnectionError:         # target is not connected
                    pass
                    """
                    if ip in self.online_PLUs:  # but once connected
                        del self.online_PLUs[ip]
                        print(f"[Detector] PLU with ip {ip} leaves")
                        self.detect_PLU_leaves_signal(self.online_PLUs[ip])
                    """
            self.detected_PLU_signal.emit(online_PLUs)
            time.sleep(self.delay)

    @staticmethod
    def parse_ip_range(ip_range):
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
        # while (True):
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
    def __init__(self, ip_range):
        self._app = QtWidgets.QApplication(sys.argv)
        # init model
        self.model = Model()

        # Init view
        self._view = Window()
"""
        # Init HTTP detector (thread)
        self.detector_http = Detector_HTTP(ip_range)
        self.detector_http.detect_PLU_joins_signal.connect(self.append_new_PLU)
        self.detector_http.detect_PLU_leaves_signal.connect(self.delete_PLU)
        # Init vision (thread)
        self.vision = Vision()

        self.saved_dir = "./../material/figures/"
"""

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

    def detector_handler(self, data):
        pass

    def append_new_PLU(self, PLU_id: int, role_id: int, battery_level: int):
        """Add a new detected PLU to the list.

        Args:
            PLU_id (int): Id of PLU to add.
            role_id (int): Id of PLU's role.
            battery_level (int): percentage of battery level.

        Returns:
            bool: True if successfully add a new PLU, otherwise False.
        """
        self.model.PLUs.append(PLU(ID=PLU_id,
                                   role_id=role_id,
                                   battery_level=battery_level))

    def delete_PLU(self, PLU_id: int):
        """
        Delete a PLU from the list.

        Args:
            PLU_id (int): Id of the PLU to delete.

        Returns:
            bool: True if succeed, otherwise False.
        """
        for i in range(self.model.num_of_PLUs-1):
            if self.model.PLUs[i].id == PLU_id:
                del self.model.PLUs[i]

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
        for PLU in self.model.PLUs:
            if PLU.id == PLU_id:
                if battery_level:
                    PLU.battery_level = battery_level
                if position:
                    PLU.position = position

    def run(self):
        self._view.show()
        return self._app.exec_()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./../config.ini')
    controller = Controller(config['Basic']['ip_range'])
    try:
        sys.exit(controller.run())
    except SystemExit:
        print("Closing app...")
