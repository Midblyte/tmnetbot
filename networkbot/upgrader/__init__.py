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

from collections import OrderedDict

from ..mongo import networkdb, options_collection, options


def v0_1_0():
    pass


def v0_2_0():
    networkdb["admins"].update_many({}, {"$set": {"admin": True, "notifications": True}})
    networkdb["admins"].rename("users")


jobs = OrderedDict([
    ("0.1.0", v0_1_0),
    ("0.2.0", v0_2_0)
])


def upgrade():
    from .. import __version__

    upgrade_from = options("__version__") or "0.1.0"
    upgrade_to = __version__

    versions, calls = map(list, (jobs.keys(), jobs.values(),))

    for call in calls[versions.index(upgrade_from)+1:versions.index(upgrade_to)+1]:
        call()

    options_collection.find_one_and_update({}, {"$set": {"__version__": __version__}})
