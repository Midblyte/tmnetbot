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

from functools import partial

from plate import Plate
from pyrogram.scaffold import Scaffold


plate = Plate(Scaffold.PARENT_DIR / '..' / 'locales')


def translator(*group, **kwargs):
    def _translate(key: str, locale: str = None, *, count: int = None, **kws) -> str:
        if locale is not None and locale not in plate.locales:
            matching_locales = filter(lambda lang_tag: lang_tag.startswith(locale), plate.locales)

            allowed_translations = map(lambda lang_tag: _translate(key, lang_tag, count=count, **kws), matching_locales)

            default_translation = plate('.'.join([*group, key]), locale=None, count=count, **kws)

            matching_translations = list(filter(lambda text: text != default_translation, allowed_translations))

            return matching_translations[0] if len(matching_translations) > 0 else default_translation

        return plate('.'.join([*group, key]), locale, count=count, **kws)

    return partial(_translate, **kwargs)
