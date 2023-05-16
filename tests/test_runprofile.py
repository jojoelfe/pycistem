from pycistem.core import *

rpm = RunProfileManager()
rpm.ImportRunProfilesFromDisk("/groups/elferich/thp1.txt")


rp = rpm.ReturnProfilePointer(1)
print("Test")
print("Test")
rp.SubstituteExecutableName("unblur")

for rc in rp.run_commands:
    print(rc.number_of_copies)
    print(rc.command_to_run)
