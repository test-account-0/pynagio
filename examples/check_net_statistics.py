#!/usr/bin/env python


import pynagio
import glob
import fileinput


def get_data():
    files = glob.glob('/sys/class/net/*/statistics/*')

    metrics = {}
    for line in fileinput.input(files):
        metric_name = fileinput.filename().replace(
            '/sys/class/net/', '').replace('/statistics/', '_')
        metrics[metric_name] = line.strip()
    return metrics


def main():
    metrics = get_data()

    check = pynagio.PynagioCheck()
    check.add_metrics(metrics)
    check.exit()


if __name__ == '__main__':
    main()
