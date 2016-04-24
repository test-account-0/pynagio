import argparse
import sys
import re


class PynagioCheck(object):

    def __init__(self):
        self.options = []
        self.metrics = []
        self.metrics_regex = []
        self.thresholds = []
        self.checked_thresholds = []
        self.thresholds_regex = []
        self.summary = []
        self.output = []
        self.perfdata = []
        self.perfdata_regex = []
        self.rates = []
        self.rates_regex = []
        self.exitcode = 0

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-t", nargs='+', dest="thresholds",
                                 help="Threshold(s) to check")
        self.args = self.parser.parse_args()

    def add_option(self, *args):
        self.parser.add_argument(*args)

    def add_summary(self, summary):
        self.summary.append(summary)

    def add_output(self, output):
        self.output.append((output))

    def add_perfdata(self, label, value):
        self.perfdata.append("{}={}".format(label, value))

    def add_rate(self, metric, *filename):
        pass

    def check_threshold(self, label, value, threshold):
        pass

    def add_metrics(self, metrics):
        self.metrics = metrics
        threshold = "TODO"
        for label in metrics:
            value = metrics[label]
            self.add_perfdata(label, value)
            self.check_threshold(label, value, threshold)

    def exit(self):
        if self.summary:
            print(" ".join(self.summary))
        else:
            print("OK")
        if self.output:
            print(self.output)
        else:
            for label in self.metrics:
                print("{} = {}".format(label, self.metrics[label]))
        if self.perfdata:
            print(" | ")
            print("\n".join(self.perfdata))
        sys.exit(self.exitcode)


# for future use
def match_label(regexes, label):
    for regex in regexes:
        compiled_regex = re.compile(regex)
        if compiled_regex.match(label):
            return True
        return False
