import json


class PLU:
    """Datastructure to represent a production line unit.

    Each PLU has the following attributes:
        - ID: identical num
        - role_id: the id of the role of the PLU
        - battery_level: current battery level
        - position: 2d tuple (x, y)
        - connection: list of two lists (the first list contains the IDs of the input,
                      and the second contains IDs of the output PLU.
    """
    def __init__(self, ID, role_id, battery_level, position, connection=None):
        self.id = ID
        self.role = role_id
        self.battery_level = battery_level
        self.position = position
        self.connection = connection or []


class Model:
    def __init__(self, PLUs=None, data_file_path='./roles.db'):
        # list of roles, each role is represented in a dictionary
        self.data_file_path = data_file_path
        self.roles = []
        self.load_roles()

        # Information of the PLUs that are currently connected to the system.
        # Data is represented as a list of PLU (objects).
        self.PLUs = PLUs or []

    def load_roles(self):
        """ Load roles from a (database) file. """
        try:
            with open(self.data_file_path, 'r') as f:
                self.roles = json.load(f)
                print("Successfully load roles.")
        except FileNotFoundError:
            print("[ERROR] Failed to load role data file, please check...")
            exit(1)

    def save_roles(self):
        """ Save list of roles as a (database) file.

        If the file doesn't exist, then create a new one.

        Returns:
            bool: True if succeed, otherwise False.
        """
        with open(self.data_file_path, 'w') as f:
            json.dump(self.roles, f)

    def update_connection(self):
        """Recalculate the connection of the PLUs based on the positions of PLUs.

        Returns:
            bool: True if succeed, otherwise False.
        """
        pass

    def name_to_id(self, name):
        """Convert role name to id."""
        if self.roles:
            for role in self.roles:
                if name == role["name"]:
                    return role["id"]
        else:
            print("[WARNING] Empty role list.")

    def id_to_name(self, id_num):
        """Convert role id to name."""
        if self.roles:
            for role in self.roles:
                if id_num == role["id"]:
                    return role["name"]
        else:
            print("[WARNING] Empty role list.")
