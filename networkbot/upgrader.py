# tmnetbot - Telegram bot
# Copyright (C) 2020 Midblyte <https://github.com/Midblyte>
#
# This file is part of tmnetbot.
#
# tmnetbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tmnetbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tmnetbot.  If not, see <https://www.gnu.org/licenses/>.


from itertools import islice

from .mongo import networkdb


def v0_1_0():
    pass


def v0_2_0():
    networkdb["admins"].update_many({}, {"$set": {
        "admin": True,
        "notifications": {k: True for k in ("scheduling", "sending", "cooldown")}
    }})
    networkdb["admins"].rename("users")


jobs = {
    "0.1.0": v0_1_0,
    "0.2.0": v0_2_0
}


def upgrade():
    from . import __version__

    upgrade_from = networkdb.options.find_one({}, projection=["__version__"]).get("__version__") or "0.1.0"
    upgrade_from_index = list(jobs.keys()).index(upgrade_from) + 1

    for current_version in islice(jobs, upgrade_from_index, len(jobs)):
        print(f"Upgrading to version {current_version} ...")
        jobs[current_version]()

    networkdb.options.find_one_and_update({}, {"$set": {"__version__": __version__}})
