import logging

from homeassistant.core import callback
from .const import DOMAIN, PLATFORMS
from .manager import TrackerManager
from .storage import TrackerStorage
from .services import (
    async_register_services,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    _LOGGER.warning("NFC TIME TRACKER LOADED")

    storage = TrackerStorage(hass)
    manager = TrackerManager(storage)

    hass.data[DOMAIN] = {
        "storage": storage,
        "manager": manager,
    }

    await async_register_services(
        hass
    )

    async def process_tag_present(tag_id):
        await manager.start_session(tag_id)

    async def process_tag_removed():
        await manager.stop_session()

    @callback
    def handle_tag_present(event):
        hass.async_create_task(
            process_tag_present(
                event.data["tag_id"]
            )
        )

    @callback
    def handle_tag_removed(event):
        hass.async_create_task(
            process_tag_removed()
        )

    hass.bus.async_listen(
        "esphome.nfc_tag_present",
        handle_tag_present,
    )

    hass.bus.async_listen(
        "esphome.nfc_tag_removed",
        handle_tag_removed,
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )