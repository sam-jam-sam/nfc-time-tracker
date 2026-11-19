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

    def unregister_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

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
            "archived": False,
        }

        await self._storage.save(data)
        self.notify_listeners()

        return project_id

    async def assign_tag(self, tag_id, project_id):
        data = await self.get_data()

        project = data["projects"].get(project_id)
        if project is None or project.get("archived", False):
            raise HomeAssistantError(
                "Select an active project to assign this tag"
            )

        data["tags"][tag_id] = project_id

        await self._storage.save(data)

    async def get_project_id_by_name(self, name):
        data = await self.get_data()

        return next(
            (
                project_id
                for project_id, project in data["projects"].items()
                if project["name"] == name
            ),
            None,
        )

    async def rename_project(self, project_id, new_name):
        data = await self.get_data()
        project = data["projects"].get(project_id)

        if project is None:
            raise HomeAssistantError("Project not found")

        new_name = " ".join(new_name.split())
        if not new_name:
            raise HomeAssistantError("Project name cannot be empty")

        if any(
            other_id != project_id
            and other["name"].casefold() == new_name.casefold()
            for other_id, other in data["projects"].items()
        ):
            raise HomeAssistantError(
                "A project with this name already exists"
            )

        project["name"] = new_name
        await self._storage.save(data)

        active = data["active_session"]
        if active is not None and active["project_id"] == project_id:
            self.current_project = new_name

        self.notify_listeners()

    async def archive_project(self, project_id):
        data = await self.get_data()
        project = data["projects"].get(project_id)

        if project is None:
            raise HomeAssistantError("Project not found")

        active = data["active_session"]
        if active is not None and active["project_id"] == project_id:
            raise HomeAssistantError(
                "Stop the active session before archiving this project"
            )

        project["archived"] = True
        data["tags"] = {
            tag_id: assigned_project_id
            for tag_id, assigned_project_id in data["tags"].items()
            if assigned_project_id != project_id
        }

        await self._storage.save(data)
        self.notify_listeners()

    async def restore_project(self, project_id):
        data = await self.get_data()
        project = data["projects"].get(project_id)

        if project is None:
            raise HomeAssistantError("Project not found")

        project["archived"] = False
        await self._storage.save(data)
        self.notify_listeners()

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

        project = data["projects"].get(project_id)
        if project is None or project.get("archived", False):
            return False

        data["active_session"] = {
            "project_id": project_id,
            "start": datetime.now().isoformat(),
        }

        await self._storage.save(data)

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

    async def get_project_total_seconds(self, project_id):
        data = await self.get_data()
        total = 0

        for session in data["sessions"]:
            if session["project_id"] != project_id:
                continue

            start = datetime.fromisoformat(session["start"])
            end = datetime.fromisoformat(session["end"])
            total += max(0, int((end - start).total_seconds()))

        active = data["active_session"]
        if active is not None and active["project_id"] == project_id:
            start = datetime.fromisoformat(active["start"])
            total += max(
                0,
                int((datetime.now() - start).total_seconds()),
            )

        return total

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
        changed = False

        for project in data["projects"].values():
            if "archived" not in project:
                project["archived"] = False
                changed = True

        if changed:
            await self._storage.save(data)

        return data["projects"]

    async def assign_current_tag(
        self,
        project_id,
        ):
        if not self.current_tag:
            return False

        project_id = project_id.strip()
        data = await self.get_data()
        project = data["projects"].get(project_id)

        if project is None:
            project_id = next(
                (
                    stored_id
                    for stored_id, stored_project in data["projects"].items()
                    if stored_project["name"].lower().replace(" ", "_")
                    == project_id
                ),
                None,
            )
            if project_id is None:
                return False

            project = data["projects"][project_id]

        if project.get("archived", False):
            return False

        await self.assign_tag(
            self.current_tag,
            project_id,
        )

        if project:
            self.current_project = project["name"]

            self.notify_listeners()

        return True