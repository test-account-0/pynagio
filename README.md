# pynagio
Super simple nagios check python library

For now calling add_metrics() with python dictionary (label = value) as an argument works. Check examples directory.

## Features:
  - It can check thresholds (-t). Subset of nagios-plugins new threshold syntax (https://nagios-plugins.org/doc/new-threshold-syntax.html) has been implemented.
  - Metric name can be specified as regex (-T)
  - Rates (per second) from counters can be calculated (-r)
  - Blacklist metrics (-B)

## Examples

```
$ ./examples/check_net_statistics.py -h
usage: check_net_statistics.py [-h] [-t THRESHOLDS [THRESHOLDS ...]]
                               [-T THRESHOLD_REGEXES [THRESHOLD_REGEXES ...]]
                               [--no-perfdata] [--no-long-output]
                               [-r RATES [RATES ...]]
                               [-R RATE_REGEXES [RATE_REGEXES ...]]
                               [-B BLACKLIST_REGEXES [BLACKLIST_REGEXES ...]]

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLDS [THRESHOLDS ...]
                        Threshold(s) to check
  -T THRESHOLD_REGEXES [THRESHOLD_REGEXES ...]
                        Threshold regex(es) to check
  --no-perfdata, --np   Do not print perfdata
  --no-long-output, --nl
                        Do not print long output
  -r RATES [RATES ...]  Rates to calculate
  -R RATE_REGEXES [RATE_REGEXES ...]
                        Rates regex to calculate
  -B BLACKLIST_REGEXES [BLACKLIST_REGEXES ...]
                        Blacklist regexes
```

```
$ ./examples/check_net_statistics.py -t 'metric=eth1_tx_packets,crit=2000..3000,warn=3001..inf' 'metric=br0_tx_packets,crit=207651..207652,warn=207666..inf,ok=0..1000' -T 'metric=.*_bytes,crit=207651..207652,warn=207666..inf,ok=0..1000' -r 'br0_tx_bytes' 'br0_rx_bytes' -B 
```

```
$ ./examples/check_net_statistics.py -t 'metric=wlp3s0_tx_packets,crit=2..3,warn=4..inf,prefix=k'
```

