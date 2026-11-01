from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.helpers.event import (
    async_track_time_interval,
)

from datetime import timedelta

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    manager = hass.data[DOMAIN]["manager"]

    async_add_entities(
        [
            CurrentProjectSensor(manager),
            CurrentSessionDurationSensor(manager),
            TotalTimeTodaySensor(manager),
            CurrentTagSensor(manager),
            ProjectsSensor(manager),
        ]
    )


class CurrentProjectSensor(SensorEntity):
    _attr_name = "Current Project"
    _attr_unique_id = "nfc_time_tracker_current_project"

    def __init__(self, manager):
        self.manager = manager

        self._attr_native_value = (
            manager.current_project
        )

    async def async_added_to_hass(self):
        self.manager.register_listener(
            self._handle_manager_update
        )

    @callback
    def _handle_manager_update(self):
        self._attr_native_value = (
            self.manager.current_project
        )

        self.async_write_ha_state()

class CurrentSessionDurationSensor(
    SensorEntity
):
    _attr_name = "Current Session Duration"
    _attr_unique_id = (
        "nfc_time_tracker_current_session_duration"
    )

    _attr_device_class = (
        SensorDeviceClass.DURATION
    )

    _attr_native_unit_of_measurement = "s"

    _attr_state_class = (
        SensorStateClass.MEASUREMENT
    )

    def __init__(self, manager):
        self.manager = manager
        self._attr_native_value = 0

    async def async_added_to_hass(self):
        self.manager.register_listener(
            self._handle_manager_update
        )

        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._timer_update,
                timedelta(seconds=1),
            )
        )

    @callback
    def _handle_manager_update(self):
        self.async_schedule_update_ha_state(
            True
        )

    async def _timer_update(self, now):
        self.async_schedule_update_ha_state(
            True
        )

    async def async_update(self):
        self._attr_native_value = (
            await self.manager
            .get_current_duration_seconds()
        )

class TotalTimeTodaySensor(
    SensorEntity
):
    _attr_name = "Total Time Today"
    _attr_unique_id = (
        "nfc_time_tracker_total_time_today"
    )

    _attr_device_class = (
        SensorDeviceClass.DURATION
    )

    _attr_native_unit_of_measurement = "s"

    _attr_state_class = (
        SensorStateClass.MEASUREMENT
    )

    def __init__(self, manager):
        self.manager = manager
        self._attr_native_value = 0

    async def async_added_to_hass(self):
        self.manager.register_listener(
            self._handle_manager_update
        )

        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._timer_update,
                timedelta(seconds=30),
            )
        )

    @callback
    def _handle_manager_update(self):
        self.async_schedule_update_ha_state(
            True
        )

    async def _timer_update(self, now):
        self.async_schedule_update_ha_state(
            True
        )

    async def async_update(self):
        self._attr_native_value = (
            await self.manager
            .get_total_time_today_seconds()
        )

class CurrentTagSensor(SensorEntity):
    _attr_name = "Current Tag"
    _attr_unique_id = (
        "nfc_time_tracker_current_tag"
    )

    def __init__(self, manager):
        self.manager = manager

        self._attr_native_value = (
            manager.current_tag or "None"
        )

    async def async_added_to_hass(self):
        self.manager.register_listener(
            self._handle_manager_update
        )

    @callback
    def _handle_manager_update(self):
        self._attr_native_value = (
            self.manager.current_tag
            or "None"
        )

        self.async_write_ha_state()

class ProjectsSensor(SensorEntity):
    _attr_name = "Projects"
    _attr_unique_id = (
        "nfc_time_tracker_projects"
    )

    def __init__(self, manager):
        self.manager = manager

        self._attr_native_value = 0
        self._attr_extra_state_attributes = {
            "projects": {}
        }

    async def async_added_to_hass(self):
        self.manager.register_listener(
            self._handle_manager_update
        )

        await self.async_update()

    @callback
    def _handle_manager_update(self):
        self.async_schedule_update_ha_state(
            True
        )

    async def async_update(self):
        projects = await self.manager.get_projects()

        self._attr_native_value = len(projects)

        self._attr_extra_state_attributes = projects