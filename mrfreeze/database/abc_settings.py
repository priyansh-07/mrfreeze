"""Abstract base class for settings."""

from abc import ABCMeta
from typing import Dict
from typing import Optional
from typing import Union

from discord import Guild
from discord import Role
from discord import TextChannel

from .helpers import db_create
from .helpers import db_execute
from .helpers import failure_print
from .helpers import success_print


class ABCSetting(metaclass=ABCMeta):
    """
    Abstract base class for Settings.

    This class defines a number of properties that every settings submodule
    needs to be able to interface properly with the rest of the system.
    """

    # General properties
    name: str
    table_name: str
    dict: Optional[Dict[int, Union[bool, int]]]
    dbpath: str

    # SQL commands
    select_all: str
    insert: str
    table: str

    def create_table(self) -> None:
        """Create the table for a given module."""
        db_create(self.dbpath, self.name, self.table)

    def load_from_db(self) -> None:
        """
        Load the values of a given modules from database into memory.

        Each module has a dictionary called self.dict into which the values
        are all loaded. This function generalises this process so it doesn't
        have to be implemented into all the cogs individually.
        """
        query = db_execute(self.dbpath, self.select_all, tuple())

        if query.error is None:
            new_dict = dict()
            for entry in query.output:
                new_dict[entry[0]] = entry[1]

            self.dict = new_dict
            success_print(self.name, f"successfully fetched {self.name}")
        else:
            failure_print(self.name, f"failed to fetch {self.name}: {query.error}")
            self.dict = None

    def get(self, server: Guild) -> Optional[int]:
        """Get the value from a given module for a given server."""
        # Check that values are loaded, if not try again.
        if self.dict is None:
            self.load_from_db()

        # Check that they loaded properly, otherwise return None.
        if self.dict is None:
            return None

        # Check if requested server has an entry, otherwise return None.
        if server.id not in self.dict:
            return None

        # Finally, return the actual value from the dictionary.
        return self.dict[server.id]

    def update_dictionary(self, key: int, value: Union[int, bool]) -> bool:
        """Update the dictionary for a given module."""
        if self.dict is None:
            self.load_from_db()

        if self.dict is None:
            return False
        else:
            self.dict[key] = value
            return True

    def set(self, object: Union[TextChannel, Role]) -> bool:
        """Set the value using a TextChannel or Role object."""
        return self.upsert(object.guild, object.id)

    def set_by_id(self, server: Guild, value: Union[bool, int]) -> bool:
        """Set the value using a Guild object and a value."""
        return self.upsert(server, value)

    def upsert(self, server: Guild, value: Union[int, bool]) -> bool:
        """Insert or update the value for `server.id` with `value`."""
        query = db_execute(self.dbpath, self.insert, (server.id, value, value))

        if query.error is not None:
            failure_print(
                self.name,
                f"failed to set {server.name} to {value}\n{query.error}")
            return False
        elif not self.update_dictionary(server.id, value):
            failure_print(
                self.name,
                f"failed to update dictionary for {server.name} to {value}\n{query.error}")
            return False
        else:
            success_print(
                self.name,
                f"successfully set {server.name} to {value}")
            return True
