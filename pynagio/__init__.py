import argparse
import sys
import os
import re
import time
import getpass
import hashlib
import json
import prefixes


class PynagioCheck(object):

    def __init__(self):
        self.options = []
        self.metrics = {}
        self.metrics_regex = []
        self.thresholds = []
        self.checked_thresholds = []
        self.threshold_regexes = []
        self.filtered_thresholds = []
        self.summary = ["OK"]
        self.output = []
        self.perfdata = []
        self.perfdata_regex = []
        self.rates = {}
        self.rate_regexes = []
        self.filtered_rates = []
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
        self.parser.add_argument("-r", nargs='+', dest="rates",
                                 help="Rates to calculate")
        self.parser.add_argument("-R", nargs='+', dest="rate_regexes",
                                 help="Rates regex to calculate")
        # self.args = self.parser.parse_args()

    def add_option(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def parse_arguments(self):
        self.args = self.parser.parse_args()

    def add_summary(self, summary):
        self.summary.append(summary)

    def add_output(self, output):
        self.output.append((output))

    def add_perfdata(self, label, value):
        self.perfdata.append("{}={}".format(label, value))

    def parse_thresholds(self):
        if self.args.thresholds:
            for threshold in self.args.thresholds:
                parsed_threshold = parse_threshold(threshold)
                self.thresholds.append(parsed_threshold)
                self.args.thresholds.remove(threshold)
        if self.filtered_thresholds:
            for threshold in self.filtered_thresholds:
                parsed_threshold = parse_threshold(threshold)
                self.thresholds.append(parsed_threshold)
                self.filtered_thresholds.remove(threshold)

    def check_thresholds(self, label, value):
        value = float(value)
        if self.thresholds:
            for threshold in self.thresholds:
                if label == threshold['label']:
                    checked_threshold = threshold
                    checked_threshold['value'] = value
                    if 'prefix' in threshold:
                        for name in ['ok', 'crit', 'warn']:
                            if name in threshold:
                                threshold[name][0] = (threshold[name][0]
                                * prefixes.prefixes[threshold['prefix']])
                                threshold[name][1] = (threshold[name][1]
                                * prefixes.prefixes[threshold['prefix']])
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
        if self.args.threshold_regexes:
            for threshold_regex in self.args.threshold_regexes:
                parsed_threshold_regex = parse_threshold_regex(threshold_regex)
                label_regex = parsed_threshold_regex['label_regex']
                rest = parsed_threshold_regex['rest']
                if label_regex.match(label):
                    self.filtered_thresholds.append("metric={},{}".format(label,
                                                                          rest))

    def get_rate(self, label, value):
        calculated_rate = calculate_rate(label, value)
        if self.args.rates:
            if label in self.args.rates and calculated_rate:
                rate_name, rate = calculated_rate
                return rate_name, rate
        if self.filtered_rates:
            if label in self.filtered_rates and calculated_rate:
                rate_name, rate = calculated_rate
                return rate_name, rate
        return False

    def add_metrics(self, metrics):
        self.metrics = metrics
        for label in metrics:
            value = float(metrics[label])
            if self.args.rate_regexes:
                if match_label(self.args.rate_regexes, label):
                    self.filtered_rates.append(label)
        for label in metrics:
            value = float(metrics[label])
            rate_value = self.get_rate(label, value)
            if rate_value:
                rate_name, rate = rate_value
                self.rates[rate_name] = rate
        if self.rates:
            metrics.update(self.rates)
        for label in metrics:
            value = float(metrics[label])
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
        if not self.args.no_perfdata:
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
        if kv[0] == 'prefix':
            parsed_threshold['prefix'] = kv[1]
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


def calculate_rate(label, value):
    time_now = time.time()
    value_now = {label: (value, time_now)}
    user = getpass.getuser()
    script_name = os.path.basename(__file__)
    script_args = "-".join(sys.argv)
    hashname = (hashlib.md5((user + script_name
                             + script_args).encode('utf-8')).hexdigest())
    if user == "root":
        rate_filename = "/var/run/nagios-{}".format(hashname)
    else:
        rate_filename = "/tmp/nagios-{}".format(hashname)
    if os.path.exists(rate_filename):
        with open(rate_filename, "r+") as ratefile:
            try:
                values_from_file = json.load(ratefile)
                if label in values_from_file:
                    delta = value - values_from_file[label][0]
                    time_delta = time_now - values_from_file[label][1]
                    rate = delta / time_delta
                    rate_name = label + "_rate"
                    values_from_file[label] = (value, time_now)
                    with open(rate_filename, "w+") as ratefile:
                        json.dump(values_from_file, ratefile,
                                  ensure_ascii=False, sort_keys=True,
                                  indent=4)
                    return (rate_name, rate)
            except Exception, e:
                print(str(e))
                with open(rate_filename, "w+") as ratefile:
                    json.dump(value_now, ratefile, ensure_ascii=False,
                              sort_keys=True, indent=4)
                return False
    else:
        print("Cannot find rate file.")
        with open(rate_filename, "w+") as ratefile:
            time_now = time.time()
            value_now = {label: (value, time_now)}
            json.dump(value_now, ratefile, ensure_ascii=False,
                      sort_keys=True, indent=4)
        return False


def match_label(regexes, label):
    for regex in regexes:
        compiled_regex = re.compile(regex)
        if compiled_regex.match(label):
            return True
        return False
