"""
Freeze mutes stores information about which servers have inactivated Mr Freeze.

Table structure:
freeze_mutes        server*    INTEGER      Server ID
                    muted      BOOLEAN      Is muted?
"""

from typing import Dict
from typing import Optional

from discord import Guild

from ..helpers import db_create
from ..helpers import db_execute
from ..helpers import failure_print
from ..helpers import success_print


class FreezeMutes:
    """Class for handling the freeze_mutes table."""

    def __init__(self, dbpath: str) -> None:
        self.dbpath = dbpath
        self.module_name = "Freeze Mutes table"
        self.table_name = "freeze_mutes"
        self.freeze_mutes: Optional[Dict[int, bool]] = None

        self.table = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                            server      INTEGER PRIMARY KEY NOT NULL,
                            muted       BOOLEAN NOT NULL);"""

    def initialize(self) -> None:
        """Set up the freeze mutes table, then fetch mutes."""
        db_create(self.dbpath, self.module_name, self.table)
        self.freeze_mutes_from_db()

    def is_freeze_muted(self, server: Guild) -> Optional[bool]:
        """Check freeze mute value for a given server."""
        # Check that current mutes has been fetched.
        # If not refetch it.
        if self.freeze_mutes is None:
            self.freeze_mutes_from_db()

        # Check that it was indeed fetched, otherwise
        # return False as default.
        if self.freeze_mutes is None:
            return None

        # Check if the requested server has an entry,
        # otherwise return False as default.
        if server.id not in self.freeze_mutes:
            return None

        # Finally, return the actual value from the dictionary.
        return self.freeze_mutes[server.id]

    def toggle_freeze_mute(self, server: Guild) -> bool:
        """
        Toggle the freeze mute value for the specified server.

        If the value is unset, set to true.
        If the value is false, set to true.
        If the value is true, set to false.

        Return the new value.
        """
        new_value = not self.is_freeze_muted(server)
        return self.upsert(server, new_value)

    def upsert(self, server: Guild, value: bool) -> bool:
        """Insert or replace the value for `server` with `value`."""
        sql = f"""INSERT INTO {self.table_name} (server, muted) VALUES (?, ?)
              ON CONFLICT(server) DO UPDATE SET muted = ?;"""
        query = db_execute(self.dbpath, sql, (server.id, value, value))

        if query.error is not None:
            failure_print(
                self.module_name,
                f"failed to set {server.name} to {value}\n{query.error}")
            return False

        elif not self.update_dictionary(server.id, value):
            failure_print(
                self.module_name,
                f"failed to update dictionary for {server.name} to {value}\n{query.error}")
            return False

        else:
            success_print(
                self.module_name,
                f"successfully set {server.name} to {value}")
            return True

    def update_dictionary(self, key: int, value: bool) -> bool:
        """Try to update the dictionary with the mute channels."""
        if self.freeze_mutes is None:
            self.freeze_mutes_from_db()

        if self.freeze_mutes is None:
            return False
        else:
            self.freeze_mutes[key] = value
            return True

    def freeze_mutes_from_db(self) -> None:
        """
        Load current freeze mute values from database.

        The values are then stored in a dictionary for quick access.
        Whenever the value is changed, the value in the dictionary and
        the database are updated simultaneously through the
        toggle_freeze_mute method.
        """
        sql = f"SELECT server, muted FROM {self.table_name}"
        query = db_execute(self.dbpath, sql, tuple())

        if query.error is None:
            new_mutes = dict()
            for entry in query.output:
                new_mutes[entry[0]] = bool(entry[1])

            self.freeze_mutes = new_mutes
            success_print(self.module_name, "successfully fetched mutes")
        else:
            self.freeze_mutes = None
            failure_print(self.module_name, f"failed to fetch mutes: {query.error}")