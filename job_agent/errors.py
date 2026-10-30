"""The two ways a run stops on purpose. The command line turns them into exit codes 3 and 2."""


class Refused(Exception):
    """Something CONTRACT.md refuses (Refuses 1 and 2). Raised before any connection opens."""


class BrokenInput(Exception):
    """An input the run cannot use (CONTRACT.md, In: "Broken input stops the run and changes no state")."""
