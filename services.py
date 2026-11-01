import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN


async def async_register_services(
    hass,
):
    manager = hass.data[DOMAIN]["manager"]

    async def add_project(call):
        await manager.add_project(
            call.data["name"]
        )

    async def assign_tag(call):
        await manager.assign_tag(
            call.data["tag_id"],
            call.data["project_id"],
        )

    async def assign_last_scanned_tag(call):
        tag_id = await manager.get_last_unknown_tag()

        if tag_id is None:
            return

        await manager.assign_tag(
            tag_id,
            call.data["project_id"],
        )

    async def assign_current_tag(call):
        await manager.assign_current_tag(
            call.data["project_id"]
        )

    hass.services.async_register(
        DOMAIN,
        "add_project",
        add_project,
        schema=vol.Schema(
            {vol.Required("name"): cv.string}
        ),
    )

    hass.services.async_register(
        DOMAIN,
        "assign_tag",
        assign_tag,
    )

    hass.services.async_register(
        DOMAIN,
        "assign_current_tag",
        assign_current_tag,
)