#!/usr/bin/env python


import pynagio
import glob
import fileinput


# Function to get a dictionay out of sth - metric_name: metric_value
def get_data():
    files = glob.glob('/sys/class/net/*/statistics/*')

    metrics = {}
    for line in fileinput.input(files):
        metric_name = fileinput.filename().replace(
            '/sys/class/net/', '').replace('/statistics/', '_')
        metrics[metric_name] = line.strip()
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
