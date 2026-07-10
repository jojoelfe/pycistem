import pytest

from pycistem.pycore import RunCommand as PyRunCommand
from pycistem.pycore import RunProfile as PyRunProfile
from pycistem.pycore import RunProfileManager as PyRunProfileManager

core = pytest.importorskip("pycistem.core")
from pycistem.core import RunCommand as CoreRunCommand  # noqa: E402
from pycistem.core import RunProfile as CoreRunProfile  # noqa: E402
from pycistem.core import RunProfileManager as CoreRunProfileManager  # noqa: E402

# NOTE: pycistem.core's RunCommand binds `command_to_run` with
# `.def_readonly(...)`, which round-trips through a custom wxString
# type_caster that is defined separately (non-`inline`) in both
# euler_search.cpp and run_profiles.cpp -- a likely ODR violation once both
# translation units are linked into the same .so. Reading `command_to_run`
# from a compiled-core RunCommand is confirmed to both return corrupted
# data (e.g. "echo hi" read back as "write") and segfault the interpreter
# shortly after, reproducible with no pycore code involved at all:
#     c = pycistem.core.RunCommand(); c.SetCommand("echo hi", ...)
#     c.command_to_run  # -> "write", then segfaults on interpreter exit
# tests/test_core.py::test_run_profiles already has a TODO documenting the
# same class of bug for `run_commands[i].command_to_run`. Since the
# reference value itself is wrong, it can't be used as a correctness
# oracle -- so below we compare everything *except* command_to_run against
# the compiled core, and verify command_to_run correctness only against
# pycore's own (simple, easily-inspected) string formatting.


def test_run_command_set_command():
    py_cmd = PyRunCommand()
    core_cmd = CoreRunCommand()
    py_cmd.SetCommand("echo hi", 2, 1, False, 0, 10)
    core_cmd.SetCommand("echo hi", 2, 1, False, 0, 10)

    assert py_cmd.command_to_run == "echo hi"
    assert py_cmd.number_of_copies == core_cmd.number_of_copies == 2


def test_run_profile_add_command_and_totals():
    hosts = ["host1", "host2", "host3"]
    num_threads = 2
    delay = 100

    def build(run_profile_cls):
        profile = run_profile_cls()
        profile.name = "64GPUs"
        profile.manager_command = "/software/CISTEM/$command"
        profile.RemoveAll()
        for host in hosts:
            for igpu in range(8):
                profile.AddCommand(
                    f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && /software/CISTEM/$command"',
                    1,
                    num_threads,
                    False,
                    0,
                    delay,
                )
        return profile

    py_profile = build(PyRunProfile)
    core_profile = build(CoreRunProfile)

    assert py_profile.name == core_profile.name == "64GPUs"
    assert py_profile.manager_command == core_profile.manager_command
    assert len(py_profile.run_commands) == len(core_profile.run_commands) == 24
    assert py_profile.ReturnTotalJobs() == core_profile.ReturnTotalJobs()
    for i, (host, igpu) in enumerate((h, g) for h in hosts for g in range(8)):
        expected = f'ssh -f {host} "unset CUDA_VISIBLE_DEVICES && export CUDA_VISIBLE_DEVICES={igpu} && /software/CISTEM/$command"'
        assert py_profile.run_commands[i].command_to_run == expected
        assert py_profile.run_commands[i].number_of_copies == 1


def test_run_profile_substitute_executable_name():
    py_profile = PyRunProfile()
    py_profile.AddCommand("$command --arg 1", 1, 1, False, 0, 0)
    py_profile.SubstituteExecutableName("my_program")
    assert py_profile.run_commands[0].command_to_run == "my_program --arg 1"


def test_run_profile_manager_add_blank_profile():
    py_manager = PyRunProfileManager()
    core_manager = CoreRunProfileManager()

    py_manager.AddBlankProfile()
    core_manager.AddBlankProfile()

    assert py_manager.run_profiles[0].name == core_manager.run_profiles[0].name
    assert py_manager.run_profiles[0].manager_command == core_manager.run_profiles[0].manager_command
    assert len(py_manager.run_profiles[0].run_commands) == len(core_manager.run_profiles[0].run_commands)


def test_run_profile_manager_write_and_import_round_trip(tmp_path):
    def populate(manager_cls):
        manager = manager_cls()
        manager.AddBlankProfile()
        manager.run_profiles[0].name = "Profile A"
        manager.AddBlankProfile()
        manager.run_profiles[1].name = "Profile B"
        return manager

    py_manager = populate(PyRunProfileManager)
    core_manager = populate(CoreRunProfileManager)

    py_file = tmp_path / "py_profiles.txt"
    core_file = tmp_path / "core_profiles.txt"

    py_manager.WriteRunProfilesToDisk(str(py_file), [0, 1])
    core_manager.WriteRunProfilesToDisk(str(core_file), [0, 1])

    assert py_file.read_text() == core_file.read_text()

    py_manager2 = PyRunProfileManager()
    core_manager2 = CoreRunProfileManager()
    assert py_manager2.ImportRunProfilesFromDisk(str(py_file)) == core_manager2.ImportRunProfilesFromDisk(
        str(core_file)
    )
    assert py_manager2.run_profiles[0].name == core_manager2.run_profiles[0].name
    assert py_manager2.run_profiles[1].name == core_manager2.run_profiles[1].name
