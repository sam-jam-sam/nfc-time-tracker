from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1
STORAGE_KEY = "nfc_time_tracker"

DEFAULT_DATA = {
    "projects": {},
    "tags": {},
    "sessions": [],
    "active_session": None,
}


class TrackerStorage:
    def __init__(self, hass):
        self._store = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
        )

    async def load(self):
        data = await self._store.async_load()
        return data or DEFAULT_DATA.copy()

    async def save(self, data):
        await self._store.async_save(data)