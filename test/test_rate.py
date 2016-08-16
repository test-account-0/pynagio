#!/usr/bin/env python


import pynagio
import os


def get_data():
    if os.path.isfile("/tmp/lastrate.txt"):
        with open("/tmp/lastrate.txt", "r+") as lastratefile:
            lastrate = int(lastratefile.read())
            lastratefile.seek(0)
            lastratefile.truncate()
            lastratefile.write(str(lastrate + 10))
            metrics = {
                'lastrate': lastrate + 10
            }
    else:
        with open("/tmp/lastrate.txt", "w+") as lastratefile:
            lastrate = 0
            lastratefile.write("0")
            metrics = {
                'lastrate': 0
            }
    return metrics


def main():
    # it needs to be a dictionary
    metrics = get_data()

    # Common lines to every script
    check = pynagio.PynagioCheck()
    check.parse_arguments()
    check.add_metrics(metrics)
    check.exit()


if __name__ == '__main__':
    main()
