import json


class Model:
    def __init__(self, PLUs=None, data_file_path='./roles.db'):
        self.roles = []
        self.load_roles(data_file_path)
        self.PLUs = PLUs or []

    def load_roles(self, data_file_path):
        """ Load roles from a (database) file.

        Args:
            data_file_path (str): Path of the data file.

        Returns:
            bool: True if succeed, otherwise False.
        """
        try:
            with open(data_file_path, 'r') as f:
                self.roles = json.load(f)
        except FileNotFoundError:
            print("[ERROR] Failed to load role data file, please check...")
            exit(1)

    def save_roles(self):
        """
        Save list of roles as a (database) file.

        Returns:
            bool
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

    def update_connection(self):
        """
        Update the connection of the PLUs according to positions of PLUs.

        Returns:
            bool: True if succeed, otherwise False.
        """
        pass
