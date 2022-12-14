import json


class PLU:
    """Datastructure to represent a production line unit.

    Each PLU has the following attributes:
        - ID: identical num
        - role_id: the id of the role of the PLU
        - battery_level: current battery level
        - position: 2d tuple (x, y)
    """
    def __init__(self, ID, role_id, ip, battery_level, position=(0, 0, 0, 0)):
        self.id = ID
        self.role = role_id
        self.ip = ip
        self.battery_level = battery_level
        self.position = position


class Model:
    def __init__(self, PLUs=None, data_file_path='./roles.db'):
        # list of roles, each role is represented in a dictionary
        self.data_file_path = data_file_path
        self.roles = []
        self.load_roles()

        # Information of the PLUs that are currently connected to the system.
        # Data is represented as a list of PLU (objects).
        self.PLUs = PLUs or []

    @property
    def num_of_PLUs(self):
        return len(self.PLUs)

    @property
    def num_of_roles(self):
        return len(self.roles)

    @property
    def role_name(self):
        names = []
        for role in self.roles:
            names.append(role["name"])
        return names

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
