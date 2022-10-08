import sys, time
import configparser
from PyQt5 import QtWidgets

from control_center.src.view import Window, Assign_role_window, Settings_window
from control_center.src.model import Model
from multiprocessing import Process, Manager
from utils import parse_ip_range, send_http_post, ping_ip


class Controller:
    def __init__(self, http_config):
        self._app = QtWidgets.QApplication(sys.argv)
        ########################
        # init model
        ########################
        self._model = Model()
        self.ips = parse_ip_range(http_config['ip_range'])
        self.delay = http_config["http_requesting_delay"]
        self.get_info_suffix = http_config["get_info_suffix"]

        ########################
        # Init view
        ########################
        self._view = Window()
        self.settings_window = None
        self.assign_role_window = None
        # Create bindings
        self._view.simulation_actions["start"].triggered.connect(self.start_simulation)
        self._view.assign_role_action.triggered.connect(self.assign_role_handle)
        self._view.settings_action.triggered.connect(self.settings_handle)

    def start_simulation(self):
        """
        Change the status of each PLUs by sending POST requests to all live PLUs
        """
        ips = self.detect_PLUs()

        ips = [plu.ip for plu in self._model.PLUs]
        for ip in ips:
            schema = f'http://{ip}/config'
            payload = {'state': 1}
            Process(target=send_http_post, args=(schema, payload)).start()

    def detect_PLUs(self):
        live_ips = Manager().list()
        for ip in self.ips:
            Process(target=ping_ip, args=(ip, live_ips)).start()
            time.sleep(0.4)
        return live_ips

    def assign_role_handle(self):
        if self.assign_role_window is None:
            self.assign_role_window = Assign_role_window(self._model.role_name)
        self.assign_role_window.show()

    def settings_handle(self):
        if self.settings_window is None:
            self.settings_window = Settings_window()
        self.settings_window.show()

    def run(self):
        self._view.show()
        return self._app.exec_()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./../config.ini')
    controller = Controller(config['HTTP'])
    try:
        sys.exit(controller.run())
    except SystemExit:
        print("Closing app...")
