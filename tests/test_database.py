from pathlib import Path
from pycistem.database import create_project, import_movies
from pycistem.core import Project

import pytest

def test_create_project(tmp_path):
    project_name = "test_project"
    output_dir = tmp_path
    project_dir = Path(output_dir, project_name)

    # Call the function to create the project
    create_project(project_name, output_dir)

    # Check that the project directory was created
    assert project_dir.exists()

    # Check that the project was created successfully
    project_db = Path(project_dir, f"{project_name}.db")
    assert project_db.exists()
    project = Project()
    success = project.OpenProjectFromFile(project_db.as_posix())
    assert success
    project.Close(True,True)


@pytest.fixture
def new_cistem_project(tmp_path):
    project_name = "test_project"
    output_dir = tmp_path
    project_dir = Path(output_dir, project_name)

    # Call the function to create the project
    create_project(project_name, output_dir)
    return Path(project_dir, f"{project_name}.db")



@pytest.mark.parametrize("movies, gain, pattern, expected_num", [
    ("/tmp/movie1.tif", "/tmp/movie.dm4", None, 1),
    ("/tmp/movie1.tif", True, None, 1),
    (["/tmp/movie1.tif", "/tmp/movie2.tif"], "/tmp/movie.dm4", None, 2),
    ("/tmp", True, "*.tif", 2),
    ("/tmp", False, "*.tif", 2)
    ])
def test_import_movies(new_cistem_project, movies, pattern, gain, expected_num):
    num_imported = import_movies(new_cistem_project, movies=movies, pattern=pattern, gain=gain)
    assert num_imported == expected_num
