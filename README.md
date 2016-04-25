# pynagio
Super simple nagios check python library

For now calling add_metrics() with python dictionary (label = value) as an argument works. Check examples directory.

## Features:
  - It can check thresholds (-t). Subset of nagios-plugins new threshold syntax (https://nagios-plugins.org/doc/new-threshold-syntax.html) has been implemented.
  - Metric name can be specified as regex (-T)
  - Rates (per second) from counters can be calculated (-r)
