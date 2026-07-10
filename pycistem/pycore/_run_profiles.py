"""Pure-Python reimplementation of RunCommand/RunProfile/RunProfileManager.

Ported from cisTEM/src/core/run_command.h, run_profile.{h,cpp}, and
run_profile_manager.{h,cpp}. These are plain data containers describing
how to launch cisTEM worker processes on a cluster/queue; no FFT/physics
involved, so this is a straightforward line-for-line port.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunCommand:
    command_to_run: str = ""
    number_of_copies: int = 0
    number_of_threads_per_copy: int = 0
    override_total_copies: bool = False
    overriden_number_of_copies: int = 0
    delay_time_in_ms: int = 0

    def SetCommand(
        self,
        wanted_command,
        wanted_number_of_copies,
        wanted_number_of_threads_per_copy,
        wanted_override_total_copies,
        wanted_overriden_number_of_copies,
        wanted_delay_time_in_ms,
    ):
        self.command_to_run = wanted_command
        self.number_of_copies = wanted_number_of_copies
        self.number_of_threads_per_copy = wanted_number_of_threads_per_copy
        self.override_total_copies = wanted_override_total_copies
        self.overriden_number_of_copies = wanted_overriden_number_of_copies
        self.delay_time_in_ms = wanted_delay_time_in_ms


class RunProfile:
    def __init__(self):
        self.id = 1
        self.name = ""
        self.manager_command = "$command"
        self.gui_address = ""
        self.controller_address = ""
        self.executable_name = ""
        self.run_commands = []

    @property
    def number_of_run_commands(self):
        return len(self.run_commands)

    def AddCommand(self, *args):
        if len(args) == 1 and isinstance(args[0], RunCommand):
            self.run_commands.append(args[0])
            return
        (
            wanted_command,
            wanted_number_of_copies,
            wanted_number_of_threads_per_copy,
            wanted_override_total_copies,
            wanted_overriden_number_of_copies,
            wanted_delay_time_in_ms,
        ) = args
        self.run_commands.append(
            RunCommand(
                command_to_run=wanted_command,
                number_of_copies=wanted_number_of_copies,
                number_of_threads_per_copy=wanted_number_of_threads_per_copy,
                override_total_copies=wanted_override_total_copies,
                overriden_number_of_copies=wanted_overriden_number_of_copies,
                delay_time_in_ms=wanted_delay_time_in_ms,
            )
        )

    def RemoveCommand(self, number_to_remove):
        del self.run_commands[number_to_remove]

    def RemoveAll(self):
        self.run_commands = []

    def ReturnTotalJobs(self):
        total_jobs = 0
        for command in self.run_commands:
            if command.override_total_copies:
                total_jobs += command.overriden_number_of_copies
            else:
                total_jobs += command.number_of_copies
        return total_jobs

    def SubstituteExecutableName(self, executable_name):
        for command in self.run_commands:
            command.command_to_run = command.command_to_run.replace("$command", executable_name)

    def __eq__(self, other):
        if not isinstance(other, RunProfile):
            return NotImplemented
        return (
            self.name == other.name
            and self.manager_command == other.manager_command
            and self.executable_name == other.executable_name
            and self.gui_address == other.gui_address
            and self.controller_address == other.controller_address
            and self.run_commands == other.run_commands
        )


class RunProfileManager:
    def __init__(self):
        self.current_id_number = 0
        self.run_profiles = []

    @property
    def number_of_run_profiles(self):
        return len(self.run_profiles)

    def AddProfile(self, profile_to_add):
        self.run_profiles.append(profile_to_add)
        if profile_to_add.id > self.current_id_number:
            self.current_id_number = profile_to_add.id

    def AddBlankProfile(self):
        self.current_id_number += 1
        profile = RunProfile()
        profile.id = self.current_id_number
        profile.name = "New Profile"
        profile.manager_command = "$command"
        profile.AddCommand("$command", 2, 1, False, 0, 10)
        self.run_profiles.append(profile)

    def AddDefaultLocalProfile(self):
        import os

        execution_command = str(Path(os.sys.executable).parent / "$command")

        self.current_id_number += 1
        profile = RunProfile()
        profile.id = self.current_id_number
        profile.name = "Default Local"
        profile.manager_command = execution_command

        number_of_cores = os.cpu_count() or 1
        number_of_cores += 1

        profile.AddCommand(execution_command, number_of_cores, 1, False, 0, 10)
        self.run_profiles.append(profile)

    def RemoveProfile(self, number_to_remove):
        del self.run_profiles[number_to_remove]

    def RemoveAllProfiles(self):
        self.run_profiles = []

    def ReturnLastProfilePointer(self):
        return self.run_profiles[-1]

    def ReturnProfilePointer(self, wanted_profile):
        return self.run_profiles[wanted_profile]

    def ReturnProfileName(self, wanted_profile):
        return self.run_profiles[wanted_profile].name

    def ReturnProfileID(self, wanted_profile):
        return self.run_profiles[wanted_profile].id

    def ReturnTotalJobs(self, wanted_profile):
        return self.run_profiles[wanted_profile].ReturnTotalJobs()

    def WriteRunProfilesToDisk(self, filename, profile_ids):
        lines = [f"number_of_profiles={len(profile_ids)}"]
        for profile_counter, profile_id in enumerate(profile_ids):
            profile = self.run_profiles[profile_id]
            lines.append(f'profile_{profile_counter}_name="{profile.name}"')
            lines.append(f'profile_{profile_counter}_manager_command="{profile.manager_command}"')
            lines.append(f'profile_{profile_counter}_gui_address="{profile.gui_address}"')
            lines.append(f'profile_{profile_counter}_controller_address="{profile.controller_address}"')
            lines.append(f"profile_{profile_counter}_number_of_run_commands={profile.number_of_run_commands}")
            for command_counter, command in enumerate(profile.run_commands):
                prefix = f"profile_{profile_counter}_command_{command_counter}"
                lines.append(f'{prefix}_command_to_run="{command.command_to_run}"')
                lines.append(f"{prefix}_number_of_copies={command.number_of_copies}")
                lines.append(f"{prefix}_number_of_threads_per_copy={command.number_of_threads_per_copy}")
                lines.append(f"{prefix}_should_override_total_number_of_copies={int(command.override_total_copies)}")
                lines.append(f"{prefix}_overriden_total_number_of_copies={command.overriden_number_of_copies}")
                lines.append(f"{prefix}_delay_time_in_ms={command.delay_time_in_ms}")
        Path(filename).write_text("\n".join(lines) + "\n")

    def ImportRunProfilesFromDisk(self, filename):
        path = Path(filename)
        if not path.exists():
            return False

        lines = path.read_text().splitlines()
        line_iter = iter(lines)

        def next_value(prefix):
            line = next(line_iter)
            if not line.startswith(prefix):
                raise ValueError(f"Expected line starting with {prefix!r}, got {line!r}")
            return line[len(prefix) :]

        def next_quoted(prefix):
            return next_value(prefix).strip('"')

        number_of_profiles = int(next_value("number_of_profiles="))

        profiles_buffer = []
        for profile_counter in range(number_of_profiles):
            profile = RunProfile()
            profile.name = next_quoted(f"profile_{profile_counter}_name=")
            profile.manager_command = next_quoted(f"profile_{profile_counter}_manager_command=")
            profile.gui_address = next_quoted(f"profile_{profile_counter}_gui_address=")
            profile.controller_address = next_quoted(f"profile_{profile_counter}_controller_address=")
            number_of_run_commands = int(next_value(f"profile_{profile_counter}_number_of_run_commands="))

            for command_counter in range(number_of_run_commands):
                prefix = f"profile_{profile_counter}_command_{command_counter}"
                command_to_run = next_quoted(f"{prefix}_command_to_run=")
                number_of_copies = int(next_value(f"{prefix}_number_of_copies="))
                number_of_threads = int(next_value(f"{prefix}_number_of_threads_per_copy="))
                override_total_jobs = bool(int(next_value(f"{prefix}_should_override_total_number_of_copies=")))
                overriden_total_jobs = int(next_value(f"{prefix}_overriden_total_number_of_copies="))
                delay_time_in_ms = int(next_value(f"{prefix}_delay_time_in_ms="))
                profile.AddCommand(
                    command_to_run,
                    number_of_copies,
                    number_of_threads,
                    override_total_jobs,
                    overriden_total_jobs,
                    delay_time_in_ms,
                )
            profiles_buffer.append(profile)

        for profile in profiles_buffer:
            profile.id = self.current_id_number
            self.AddProfile(profile)
            profile.id = self.current_id_number
            self.current_id_number += 1

        return True
