from datetime import datetime

from homeassistant.exceptions import HomeAssistantError


class TrackerManager:
    def __init__(self, storage):
        self._storage = storage
        self._listeners = []

        self.current_project = "No Project"
        self.current_tag = None

    def register_listener(self, callback):
        self._listeners.append(callback)

    def notify_listeners(self):
        for callback in self._listeners:
            callback()

    async def get_data(self):
        return await self._storage.load()

    async def add_project(self, name):
        data = await self.get_data()

        name = " ".join(name.split())
        if not name:
            raise HomeAssistantError(
                "Project name cannot be empty"
            )

        project_id = name.lower().replace(" ", "_")
        if project_id in data["projects"]:
            raise HomeAssistantError(
                "A project with this name already exists"
            )

        data["projects"][project_id] = {
            "name": name,
        }

        await self._storage.save(data)
        self.notify_listeners()

        return project_id

    async def assign_tag(self, tag_id, project_id):
        data = await self.get_data()

        data["tags"][tag_id] = project_id

        await self._storage.save(data)

    async def get_current_project(self):
        return self.current_project

    async def start_session(self, tag_id):
        self.current_tag = tag_id

        self.notify_listeners()

        data = await self.get_data()

        if data["active_session"] is not None:
            return False

        project_id = data["tags"].get(tag_id)

        if not project_id:
            return False

        data["active_session"] = {
            "project_id": project_id,
            "start": datetime.now().isoformat(),
        }

        await self._storage.save(data)

        project = data["projects"].get(project_id)

        self.current_project = project["name"]

        self.notify_listeners()

        return project_id

    async def stop_session(self):
        data = await self.get_data()

        active = data["active_session"]

        if active is None:
            return False

        active["end"] = datetime.now().isoformat()

        data["sessions"].append(active)

        data["active_session"] = None

        await self._storage.save(data)

        self.current_project = "No Project"

        self.current_tag = None

        self.notify_listeners()

        return True

    async def get_current_duration_seconds(self):
        data = await self.get_data()

        active = data["active_session"]

        if active is None:
            return 0

        start = datetime.fromisoformat(
            active["start"]
        )

        duration = datetime.now() - start

        return int(duration.total_seconds())

    async def get_total_time_today_seconds(self):
        data = await self.get_data()

        today = datetime.now().date()

        total = 0

        for session in data["sessions"]:
            start = datetime.fromisoformat(
                session["start"]
            )

            if start.date() != today:
                continue

            end = datetime.fromisoformat(
                session["end"]
            )

            total += int(
                (end - start).total_seconds()
            )

        # Include active session
        active = data["active_session"]

        if active is not None:
            start = datetime.fromisoformat(
                active["start"]
            )

            if start.date() == today:
                total += int(
                    (
                        datetime.now() - start
                    ).total_seconds()
                )

        return total

    async def get_project_names(self):
        data = await self.get_data()

        return {
            k: v["name"]
            for k, v in data["projects"].items()
        }

    async def get_current_tag(self):
        return self.current_tag or "None"

    async def get_projects(self):
        data = await self.get_data()

        return data["projects"]

    async def assign_current_tag(
        self,
        project_id,
        ):
        if not self.current_tag:
            return False

        await self.assign_tag(
            self.current_tag,
            project_id,
        )

        data = await self.get_data()

        project = data["projects"].get(project_id)

        if project:
            self.current_project = project["name"]

            self.notify_listeners()

        return True