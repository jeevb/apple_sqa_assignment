import datetime
import functools
import json
import os
import re

from fnmatch import filter
from collections import defaultdict
from pprint import pprint

def to_date(s, fmt=None):
    args = [s]
    if fmt is not None:
        args.append(fmt)

    return datetime.datetime.strptime(*args)


class LogEntry(dict):
    """Extension of dict class with an extra attribute to store
    a raw log string.
    """
    def __init__(self, *args, **kwargs):
        super(LogEntry, self).__init__(*args, **kwargs)
        self.raw = None


class LogContainer(object):
    """Container to store and manipulate log entries.

    Arguments:
    log_fmt -- regex pattern to define fields for logs to be extracted.
    field_types -- dict defining rules for explicit coercion of specified
    fields. Keys correspond to the name of the field to coerce. Values
    correspond to the type of object to coerce the field to. Values must be
    one of the following: integer, float, date, character.

    Keyword arguments:
    date_fmt -- format of date fields. If not specified, dates will be
    retained as characters (default None).
    """
    def __init__(self, log_fmt, field_types, date_fmt=None):
        super(LogContainer, self).__init__()
        self._log_fmt = re.compile(log_fmt)
        self._fields = self._log_fmt.groupindex.keys()
        self._field_types = field_types

        # Define field conversion functions
        self._type_cast_funcs = {
            'integer': int,
            'float': float,
            'date': functools.partial(to_date, fmt=date_fmt)
        }

        # Validation of initial state
        self._validate()

        self._logs = []

    @property
    def logs(self):
        return self._logs

    @property
    def fields(self):
        return self._fields

    def _validate(self):
        """Check if fields (regex named groups) have been specified
        in the log format, and check if fields to be explicitly coerced
        are valid and defined in the log format.
        """
        if not self._fields:
            raise ValueError('No fields specified in log format.')
        self._validate_fields(self._field_types.iterkeys())

    def _validate_fields(self, fields):
        """Check if specified field is valid and defined in log format."""
        for field in fields:
            if field not in self._fields:
                raise ValueError('Unknown field found: %r' % field)

    def _format(self, val, field):
        """Explicitly coerce specified fields to integer, float, or date.
        """
        if field not in self._field_types:
            return val

        try:
            fmt = self._field_types[field]
            f = self._type_cast_funcs[fmt]
        except KeyError:
            raise TypeError(
                'Invalid type specification %r for field %r.' % (fmt, field)
            )
        else:
            return f(val)

    def _parse_log_file(self, f):
        """Parse specified log file, extract field information, coerce
        fields if necessary, and create and store LogEntry objects. Each
        LogEntry object corresponds to one line in a log file.

        Arguments:
        f -- file to parse.
        """
        for log in open(f).xreadlines():
            _log = log.strip()

            # Match log entry to specified regex pattern and extract fields
            match = self._log_fmt.match(_log)
            if match:
                entry = LogEntry(
                    (field, self._format(val, field))
                    for field, val in match.groupdict().iteritems()
                )
                # Store raw log string as an attribute of the log entry dict
                entry.raw = _log
                self._logs.append(entry)

    def parse(self, path, pattern):
        """Recursively traverse specified path and parse files that
        have names matching a given pattern.

        Arguments:
        path -- path to directory to search for log files.
        pattern -- pattern of filenames to parse.
        """
        for root, dirs, files in os.walk(path):
            for f in filter(files, pattern):
                self._parse_log_file(os.path.join(root, f))

    def order(self, *args, **kwargs):
        """Sort logs by specified fields. Arguments are fields to sort by.
        Keyword argument 'decreasing' enforces sort order.
        """
        self._validate_fields(args)
        self._logs.sort(key=lambda k: tuple(k[field] for field in args),
                       reverse=kwargs.get('decreasing', False))

    def summarize(self, val, by, funcs, var=None, print_result=False):
        """Summarize values from one field by another categorical field.

        Arguments:
        val -- name of field to summarize
        by -- categorical variable to summarize values by
        funcs -- list of functions to use for value summarization

        Keyword arguments:
        var -- filter to specify categorical variables to summarize by
        (default None).
        print_result -- switch to print a pretty dictionary of summary
        statistics to console (default False).
        """
        self._validate_fields([val, by])

        to_summarize = defaultdict(list)
        for log in self._logs:
            key = log[by]
            if (var is None or var == key or
                    (hasattr(var, '__iter__') and key in var)):
                to_summarize[key].append(log[val])

        _funcs = funcs if hasattr(funcs, '__iter__') else [funcs]
        summary = {
            key: {f.__name__: f(vals) for f in _funcs}
            for key, vals in to_summarize.iteritems()
        }
        if print_result:
            print json.dumps(summary, indent=4)

        return summary

    def write_to(self, output):
        """Write logs in container to specified file.

        Arguments:
        output -- path of file to write logs to.
        """
        with open(output, 'w') as handle:
            handle.writelines(x.raw + '\n' for x in self._logs)
