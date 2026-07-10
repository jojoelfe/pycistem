import sqlite3
from pathlib import Path

import pytest

from pycistem.pycore import Project as PyProject

core = pytest.importorskip("pycistem.core.core")
from pycistem.core import Project as CoreProject  # noqa: E402


def _schema(db_path):
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return {name: sql for name, sql in rows}


def test_create_new_project_schema_matches_compiled_core(tmp_path):
    # Mirrors pycistem.database.create_project(), which mkdir()s the
    # project directory itself before calling CreateNewProject -- neither
    # the compiled Project::CreateNewProject nor pycore's version creates
    # that top-level directory (only the Assets/* subdirs beneath it).
    py_dir = tmp_path / "py_project"
    core_dir = tmp_path / "core_project"
    py_dir.mkdir()
    core_dir.mkdir()

    py_project = PyProject()
    assert py_project.CreateNewProject(str(py_dir / "py_project.db"), str(py_dir), "py_project")

    core_project = CoreProject()
    assert core_project.CreateNewProject(str(core_dir / "core_project.db"), str(core_dir), "core_project")

    py_schema = _schema(py_dir / "py_project.db")
    core_schema = _schema(core_dir / "core_project.db")

    assert set(py_schema.keys()) == set(core_schema.keys())
    for table_name in core_schema:
        assert py_schema[table_name] == core_schema[table_name], f"schema mismatch for {table_name}"

    py_project.Close(True, True)
    core_project.Close(True, True)


def test_create_new_project_directory_layout_matches(tmp_path):
    py_dir = tmp_path / "py_project"
    core_dir = tmp_path / "core_project"
    py_dir.mkdir()
    core_dir.mkdir()

    py_project = PyProject()
    py_project.CreateNewProject(str(py_dir / "proj.db"), str(py_dir), "proj")
    core_project = CoreProject()
    core_project.CreateNewProject(str(core_dir / "proj.db"), str(core_dir), "proj")

    py_subdirs = {p.relative_to(py_dir) for p in py_dir.rglob("*") if p.is_dir()}
    core_subdirs = {p.relative_to(core_dir) for p in core_dir.rglob("*") if p.is_dir()}
    assert py_subdirs == core_subdirs

    py_project.Close(True, True)
    core_project.Close(True, True)


def test_open_project_from_file_round_trip(tmp_path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    db_path = project_dir / "proj.db"

    core_project = CoreProject()
    core_project.CreateNewProject(str(db_path), str(project_dir), "proj")
    core_project.Close(True, True)

    py_project = PyProject()
    assert py_project.OpenProjectFromFile(str(db_path))
    assert py_project.project_name == "proj"
    assert Path(py_project.project_directory) == project_dir
    py_project.Close(True, True)


def test_project_master_settings_row_matches(tmp_path):
    py_dir = tmp_path / "py_project"
    core_dir = tmp_path / "core_project"
    py_dir.mkdir()
    core_dir.mkdir()

    py_project = PyProject()
    py_project.CreateNewProject(str(py_dir / "proj.db"), str(py_dir), "proj")
    core_project = CoreProject()
    core_project.CreateNewProject(str(core_dir / "proj.db"), str(core_dir), "proj")

    with sqlite3.connect(py_dir / "proj.db") as con:
        py_row = con.execute("SELECT PROJECT_NAME, CURRENT_VERSION, TOTAL_CPU_HOURS, TOTAL_JOBS_RUN FROM MASTER_SETTINGS").fetchone()
    with sqlite3.connect(core_dir / "proj.db") as con:
        core_row = con.execute("SELECT PROJECT_NAME, CURRENT_VERSION, TOTAL_CPU_HOURS, TOTAL_JOBS_RUN FROM MASTER_SETTINGS").fetchone()

    assert py_row == core_row

    py_project.Close(True, True)
    core_project.Close(True, True)


def test_database_execute_and_query_roundtrip(tmp_path):
    py_dir = tmp_path / "py_project"
    py_dir.mkdir()
    py_project = PyProject()
    py_project.CreateNewProject(str(py_dir / "proj.db"), str(py_dir), "proj")

    py_project.database.ExecuteSQL(
        "INSERT INTO MOVIE_ASSETS (MOVIE_ASSET_ID, NAME, FILENAME) VALUES (1, 'test', 'test.tif')"
    )
    count = py_project.database.ReturnSingleLongFromSelectCommand("SELECT COUNT(*) FROM MOVIE_ASSETS")
    assert count == 1
    py_project.Close(True, True)


def test_database_movie_asset_batch_insert(tmp_path):
    py_dir = tmp_path / "py_project"
    py_dir.mkdir()
    py_project = PyProject()
    py_project.CreateNewProject(str(py_dir / "proj.db"), str(py_dir), "proj")

    py_project.database.BeginMovieAssetInsert()
    for i in range(3):
        py_project.database.AddNextMovieAsset(
            i + 1, f"movie{i}", f"movie{i}.tif", 0, 11520, 8184, 34, 300, 1.0, 1.0, 2.7,
            "gain.dm4", "", 1.0, 0, 0, 1.0, 1.0, 0, 1, 25,
        )
    py_project.database.EndMovieAssetInsert()

    count = py_project.database.ReturnSingleLongFromSelectCommand("SELECT COUNT(*) FROM MOVIE_ASSETS")
    assert count == 3
    py_project.Close(True, True)
