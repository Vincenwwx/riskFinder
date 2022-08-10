from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QColor
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon, QBrush, QPen, QColor, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction, QGraphicsScene, QGraphicsView, QVBoxLayout, \
    QHBoxLayout, QWidget


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
        # Manage roles
        self.settings_action = QAction(QIcon("../material/icons/settings.svg"), "Settings", self)
        self.settings_action.setToolTip("Settings")
        self.settings_action.triggered.connect(self.set_roles)
        # Simulation
        self.simulation_actions["start"] = QAction(QIcon("../material/icons/start.svg"), "Start", self)
        self.simulation_actions["start"].triggered.connect(self.start_simulation)

        self.simulation_actions["pause"] = QAction(QIcon("../material/icons/pause.svg"), "Pause", self)
        self.simulation_actions["pause"].triggered.connect(self.pause_simulation)

        self.simulation_actions["restart"] = QAction(QIcon("../material/icons/restart.svg"), "Restart", self)
        self.simulation_actions["restart"].triggered.connect(self.restart_simulation)

        self.simulation_actions["stop"] = QAction(QIcon("../material/icons/stop.svg"), "Stop", self)
        self.simulation_actions["stop"].triggered.connect(self.stop_simulation)

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False) # Todo: may differs in Mac and linux
        # ====================
        # File menu
        # ====================
        file_menu = menu_bar.addMenu("&File")
        # - Save simulation result
        file_menu.addAction(self.save_simulation_result_action)
        # - System refresh
        file_menu.addAction(self.refresh_system_action)
        # - Exit
        file_menu.addSeparator() # add a separating line
        file_menu.addAction(self.exit_action)

        # ====================
        # Configuration menu
        # ====================
        configuration_menu = menu_bar.addMenu("&Edit")
        # - Set roles
        configuration_menu.addAction(self.settings_action)

        # ====================
        # Simulation menu
        # ====================
        simulation_menu = menu_bar.addMenu("&Simulate")
        # - Start
        simulation_menu.addAction(self.simulation_actions["start"])
        # - Pause
        simulation_menu.addAction(self.simulation_actions["pause"])
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

    def draw_PLU(self, PLU):
        """Draw a PLU on the canvas

        Args:
            PLU (dict): Information of PLU to draw.

        Returns:
            bool: True if succeed, otherwise false
        """
        battery_level = PLU["battery level"]
        position = PLU["position"]
        role = PLU["role"]


    def _createStatusBar(self):
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("System ready...")

    # ------------- Event functions ---------------
    # When set_roles is triggered, a new window will pop out
    def start_simulation(self):
        pass

    def pause_simulation(self):
        pass

    def restart_simulation(self):
        pass

    def stop_simulation(self):
        pass
