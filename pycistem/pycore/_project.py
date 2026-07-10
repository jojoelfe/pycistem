"""Pure-Python reimplementation of the cisTEM Project class.

Ported from cisTEM/src/core/project.cpp. Only CreateNewProject,
OpenProjectFromFile, and Close are used from Python (see
pycistem/database/__init__.py); the EXPERIMENTAL TemplateMatching asset
directory that cisTEM guards behind #ifdef EXPERIMENTAL is created
unconditionally here since pycistem's own database helpers assume it
exists (see ensure_template_is_a_volume_asset / match_template.py).
"""

from pathlib import Path

from pycistem.pycore._database import CISTEM_VERSION_TEXT, Database, INTEGER_DATABASE_VERSION

_ASSET_SUBDIRS = [
    "Assets/Movies",
    "Assets/Images",
    "Assets/Volumes",
    "Assets/TemplateMatching",
    "Assets/PhaseDifferenceImages",
    "Assets/CTF",
    "Assets/ParticlePosition",
    "Assets/ParticleStacks",
    "Assets/ClassAverages",
    "Assets/Parameters",
    "Scratch",
    "Assets/Images/Spectra",
    "Assets/Images/Scaled",
    "Assets/Volumes/OrthViews",
]


class Project:
    def __init__(self):
        self.is_open = False
        self.total_cpu_hours = 0.0
        self.total_jobs_run = 0
        self.project_name = ""
        self.project_directory = ""
        self.database = Database()

    def CreateNewProject(self, wanted_database_file, wanted_project_directory, wanted_project_name):
        if self.is_open:
            raise RuntimeError("Attempting to create a new project, but there is already an open project")
        if not wanted_project_name:
            raise ValueError("Attempting to create a new project, but the project name is blank")
        if not wanted_project_directory:
            raise ValueError("Attempting to create a new project, but the project dir is blank")

        self.database.CreateNewDatabase(wanted_database_file)
        self.database.CreateAllTables()

        self.project_name = wanted_project_name
        self.project_directory = wanted_project_directory

        for subdir in _ASSET_SUBDIRS:
            Path(self.project_directory, subdir).mkdir(parents=True, exist_ok=True)

        self.total_cpu_hours = 0.0
        self.total_jobs_run = 0

        # Database.ExecuteSQL mirrors Database::ExecuteSQL (a fire-and-forget
        # string exec with no parameter binding), so bind parameters directly
        # against the underlying connection here instead.
        self.database.connection.execute(
            "INSERT OR REPLACE INTO MASTER_SETTINGS "
            "(NUMBER, PROJECT_DIRECTORY, PROJECT_NAME, CURRENT_VERSION, TOTAL_CPU_HOURS, TOTAL_JOBS_RUN, CISTEM_VERSION_TEXT) "
            "VALUES (1, ?, ?, ?, ?, ?, ?)",
            (
                str(self.project_directory),
                self.project_name,
                INTEGER_DATABASE_VERSION,
                self.total_cpu_hours,
                self.total_jobs_run,
                CISTEM_VERSION_TEXT,
            ),
        )

        self.is_open = True
        return True

    def OpenProjectFromFile(self, file_to_open):
        if self.is_open:
            raise RuntimeError("Attempting to create a new project, but there is already an open project")

        self.database.Open(file_to_open)
        settings = self.database.GetMasterSettings()
        if settings is None:
            return False

        self.project_directory = settings["project_directory"]
        self.project_name = settings["project_name"]
        self.total_cpu_hours = settings["total_cpu_hours"]
        self.total_jobs_run = settings["total_jobs_run"]

        for subdir in _ASSET_SUBDIRS:
            Path(self.project_directory, subdir).mkdir(parents=True, exist_ok=True)

        self.is_open = True
        return True

    def Close(self, remove_lock=True, update_statistics=True):
        if update_statistics:
            self.database.ExecuteSQL(
                f"UPDATE MASTER_SETTINGS SET TOTAL_JOBS_RUN = {int(self.total_jobs_run)}, "
                f"TOTAL_CPU_HOURS = {float(self.total_cpu_hours)}, "
                f"CISTEM_VERSION_TEXT = '{CISTEM_VERSION_TEXT}'"
            )
        self.database.ExecuteSQL(
            f"UPDATE MASTER_SETTINGS SET CURRENT_VERSION = {INTEGER_DATABASE_VERSION}, "
            f"CISTEM_VERSION_TEXT = '{CISTEM_VERSION_TEXT}'"
        )
        self.database.Close(remove_lock)

        self.is_open = False
        self.total_cpu_hours = 0.0
        self.total_jobs_run = 0
        self.project_name = ""
        self.project_directory = ""
