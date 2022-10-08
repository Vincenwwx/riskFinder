from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QPixmap, QIntValidator
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction, QGraphicsScene, QGraphicsView, QVBoxLayout, \
    QHBoxLayout, QWidget, QLineEdit, QComboBox, QPushButton
from utils import send_http_post


class Scene(QLabel):
    def __init__(self, parent):
        super(Scene, self).__init__()
        self.parent = parent
        width, height = parent.width(), parent.height()
        # Setup background
        self.pixmap = QPixmap(width, height)
        self.pixmap.fill(QColor(120, 120, 120))
        self.setPixmap(self.pixmap)

    def paintEvent(self, event):
        pass


""" 
Main window
"""
class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Emulator")
        self.resize(800, 600)

        self.simulation_actions = {}
        self.settings_window = None
        self.assign_role_window = None

        self._initActions()
        self._createMenuBar()
        self._createToolbars()
        self._createScene()
        self._createStatusBar()

    def _initActions(self):
        # Save simulation result
        self.save_simulation_result_action = QAction("Save simulation result", self)
        self.save_simulation_result_action.setShortcut(QKeySequence('Shift+Ctrl+S'))
        # Refresh system status
        self.refresh_system_action = QAction("Refresh system", self)
        # Exit
        self.exit_action = QAction(QIcon("../material/icons/exit.svg"), '&Exit', self)
        self.exit_action.setShortcut(QKeySequence('Ctrl+Esc'))
        self.exit_action.triggered.connect(self.close)
        # Edit
        #  - Set role
        self.assign_role_action = QAction("Assign role", self)
        self.assign_role_action.setToolTip("Assign role to PLU")
        #  - Settings
        self.settings_action = QAction(QIcon("../material/icons/settings.svg"), "Settings", self)
        self.settings_action.setToolTip("Settings")
        # Simulation
        #  - start
        self.simulation_actions["start"] = QAction(QIcon("../material/icons/start.svg"), "Start", self)
        #self.simulation_actions["start"].triggered.connect(self.start_simulation)
        #  - restart
        self.simulation_actions["restart"] = QAction(QIcon("../material/icons/restart.svg"), "Restart", self)
        #self.simulation_actions["restart"].triggered.connect(self.restart_simulation)
        #  - stop
        self.simulation_actions["stop"] = QAction(QIcon("../material/icons/stop.svg"), "Stop", self)
        #self.simulation_actions["stop"].triggered.connect(self.stop_simulation)

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)  # Todo: may differs in Mac and linux
        # ====================
        # File menu
        # ====================
        file_menu = menu_bar.addMenu("&File")
        # - Save simulation result
        file_menu.addAction(self.save_simulation_result_action)
        # - System refresh
        file_menu.addAction(self.refresh_system_action)
        # - Exit
        file_menu.addSeparator()  # add a separating line
        file_menu.addAction(self.exit_action)

        # ====================
        # Edit menu
        # ====================
        configuration_menu = menu_bar.addMenu("&Edit")
        # - Assign role
        configuration_menu.addAction(self.assign_role_action)
        configuration_menu.addSeparator()  # add a separating line
        # - Settings
        configuration_menu.addAction(self.settings_action)

        # ====================
        # Simulation menu
        # ====================
        simulation_menu = menu_bar.addMenu("&Simulate")
        # - Start
        simulation_menu.addAction(self.simulation_actions["start"])
        # - Restart
        simulation_menu.addAction(self.simulation_actions["restart"])
        # - Stop
        simulation_menu.addAction(self.simulation_actions["stop"])

    # The toolbars should look like:
    #   Set roles | Start | Pause | Stop | restart | Exit
    def _createToolbars(self):
        # Edit toolbar
        edit_toolbar = self.addToolBar("toolbar")
        edit_toolbar.setMovable(False)
        edit_toolbar.addAction(self.settings_action)
        # Simulation actions
        for _, v in self.simulation_actions.items():
            edit_toolbar.addAction(v)
        # Exit actions
        edit_toolbar.addAction(self.exit_action)

    def _createContextMenu(self):
        self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.centralWidget.addAction(self.refresh_system_action)

    def _createScene(self):
        """ Create scene composing of stage and connection
        """
        self.canvas = Scene(self)
        self.setCentralWidget(self.canvas)

    def draw_PLUs(self, PLUs):
        """Draw PLUs on the canvas

        Args:
            PLU (dict): Information of PLU to draw.

        Returns:
            bool: True if succeed, otherwise false
        """
        pass

    def _createStatusBar(self):
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("System ready...")


class Settings_window(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Settings")
        layout.addWidget(self.label)
        self.setLayout(layout)


class Assign_role_window(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, roles, ip_prefix="192.168.22"):
        super().__init__()
        self.setWindowTitle("Assign role")
        self.ip_prefix = ip_prefix
        layout = QVBoxLayout()
        layout_1 = QHBoxLayout()
        layout_2 = QHBoxLayout()
        self.label_0 = QLabel("Assign PLU ")
        self.label_1 = QLabel("with role")

        self.id_text = QLineEdit()
        self.id_text.setValidator(QIntValidator())
        self.id_text.setMaxLength(12)
        self.id_text.setText("(IP prefix)")
        self.id_text.setAlignment(Qt.AlignLeft)

        self.cb = QComboBox()
        for role in roles:
            self.cb.addItem(role)

        confirm_button = QPushButton(self)
        confirm_button.setText("confirm")
        confirm_button.clicked.connect(self.set_role)

        ok_button = QPushButton(self)
        ok_button.setText("ok")
        ok_button.clicked.connect(self.close)

        layout_1.addWidget(self.label_0)
        layout_1.addWidget(self.id_text)
        layout_1.addWidget(self.label_1)
        layout_1.addWidget(self.cb)
        layout_2.addWidget(confirm_button)
        layout_2.addWidget(ok_button)
        layout.addLayout(layout_1)
        layout.addLayout(layout_2)
        self.setLayout(layout)

    def set_role(self):
        ip_suffix = self.id_text.text()
        scheme = f'http://{self.ip_prefix}.{ip_suffix}/config'
        payload = {"role": self.cb.currentText(), "state": 0}
        send_http_post(scheme, payload)