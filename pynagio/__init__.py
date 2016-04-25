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
        self.threshold_regexes = []
        self.summary = ["OK"]
        self.output = []
        self.perfdata = []
        self.perfdata_regex = []
        self.rates = []
        self.rates_regex = []
        self.exitcode = 0
        self.critical_on = []
        self.warning_on = []

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-t", nargs='+', dest="thresholds",
                                 help="Threshold(s) to check")
        self.parser.add_argument("-T", nargs='+', dest="threshold_regexes",
                                 help="Threshold regex(es) to check")
        self.parser.add_argument("--no-perfdata", "--np", action='store_true',
                                 help="Threshold regex(es) to check")
        self.args = self.parser.parse_args()

        print(dir(self.args))
        # self.parse_thresholds()

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

    def parse_thresholds(self):
        if self.args.thresholds:
            for threshold in self.args.thresholds:
                parsed_threshold = parse_threshold(threshold)
                self.thresholds.append(parsed_threshold)
                self.args.thresholds.remove(threshold)

    def check_thresholds(self, label, value):
        value = float(value)
        if self.thresholds:
            for threshold in self.thresholds:
                if label == threshold['label']:
                    checked_threshold = threshold
                    checked_threshold['value'] = value
                    if 'ok' in threshold:
                        if threshold['ok'][0] < value <= threshold['ok'][1]:
                            checked_threshold['exitcode'] = 0
                            self.checked_thresholds.append(checked_threshold)
                            break
                    if 'crit' in threshold:
                        if threshold['crit'][0] < value <= threshold['crit'][1]:
                            checked_threshold['exitcode'] = 2
                            self.checked_thresholds.append(checked_threshold)
                            break
                    if 'warn' in threshold:
                        if threshold['warn'][0] < value <= threshold['warn'][1]:
                            checked_threshold['exitcode'] = 1
                            self.checked_thresholds.append(checked_threshold)
                            break
                    if 'ok' in threshold:
                        checked_threshold['exitcode'] = 2
                        self.checked_thresholds.append(checked_threshold)
                        break
                    checked_threshold['exitcode'] = 0
                    self.checked_thresholds.append(checked_threshold)

    def filter_threshold_regexes(self, label):
        for threshold_regex in self.args.threshold_regexes:
            parsed_threshold_regex = parse_threshold_regex(threshold_regex)
            label_regex = parsed_threshold_regex['label_regex']
            rest = parsed_threshold_regex['rest']
            if label_regex.match(label):
                self.args.thresholds.append("metric={},{}".format(label, rest))

    def add_metrics(self, metrics):
        self.metrics = metrics
        for label in metrics:
            value = metrics[label]
            self.add_perfdata(label, value)
            self.filter_threshold_regexes(label)
            self.parse_thresholds()
            self.check_thresholds(label, value)

    def exit(self):
        if self.checked_thresholds:
            for threshold in self.checked_thresholds:
                if threshold['exitcode'] == 2:
                    self.exitcode = 2
                    self.summary[0] = "CRITICAL"
                    break
            if self.exitcode != 2:
                for threshold in self.checked_thresholds:
                    if threshold['exitcode'] == 1:
                        self.exitcode = 1
                        self.summary[0] = "WARNING"
                        break
            for threshold in self.checked_thresholds:
                if threshold['exitcode'] == 2:
                    self.critical_on.append("{} = {}".format(
                        threshold['label'], threshold['value']))
                if threshold['exitcode'] == 1:
                    self.warning_on.append("{} = {}".format(
                        threshold['label'], threshold['value']))
        summary_line = ""
        if self.summary:
            summary_line += " ".join(self.summary) + " "
        if self.critical_on:
            summary_line += "Critical on" + " " + " ".join(
                self.critical_on) + " "
        if self.warning_on:
            summary_line += "Warning on" + " " + " ".join(
                self.warning_on) + " "
        print(summary_line)
        if self.output:
            print(self.output)
        else:
            for label in self.metrics:
                print("{} = {}".format(label, self.metrics[label]))
        if self.args.np_perfdata:
            if self.perfdata:
                print(" | ")
                print("\n".join(self.perfdata))
        sys.exit(self.exitcode)


def parse_threshold(threshold):
    parsed_threshold = {}
    for kv in [part.split("=") for part in threshold.split(",")]:
        if kv[0] == 'metric':
            parsed_threshold['label'] = kv[1]
        if kv[0] in ['ok', 'crit', 'warn']:
            parsed_threshold[kv[0]] = [float(x) for x
                                       in kv[1].split("..")]
    return parsed_threshold


def parse_threshold_regex(threshold_regex):
    parsed_threshold_regex = {}
    parsed_threshold_regex['rest'] = ""
    for kv in threshold_regex.split(","):
        if kv.split("=")[0] == "metric":
            parsed_threshold_regex['label_regex'] = re.compile(kv.split("=")[1])
        else:
            parsed_threshold_regex['rest'] += "," + kv
    return parsed_threshold_regex
