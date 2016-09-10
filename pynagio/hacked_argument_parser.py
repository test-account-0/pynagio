import argparse
import sys
from gettext import gettext as _

class HackedArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(3, _('%(prog)s: error: %(message)s\n') % args)
