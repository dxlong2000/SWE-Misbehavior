# -*- coding: utf-8 -*-
# Copyright 2015-2018 Yelp
# Copyright 2019 Yelp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Merging errors, picking the best one, and displaying it."""
import json

from mrjob.util import unique


_PYTHON_TRACEBACK_HEADER = 'Traceback (most recent call last):'


def _pick_error(log_interpretation):
    """Pick most recent error from a dictionary possibly containing
    step, history, and task interpretations. Returns None if there
    are no errors.
    """
    errors = _extract_errors(log_interpretation)

    # no point in merging spark errors, which may not be tied to a container
    # because they're not even necessarily on Hadoop
    spark_errors = _pick_spark_errors(errors)
    if spark_errors:
        return spark_errors[0]

    # otherwise, merge hadoop/task errors and pick the most recent one
    attempt_to_container_id = log_interpretation.get('history', {}).get(
        'attempt_to_container_id', {})

    merged_errors = _merge_and_sort_errors(errors, attempt_to_container_id)
    if merged_errors:
        return merged_errors[0]

    return None


def _extract_errors(log_interpretation):
    """Extract all errors from *log_interpretation*, in no particular order."""
    errors = []

    for log_type in ('step', 'history', 'task'):
        errors.extend(
            log_interpretation.get(log_type, {}).get('errors') or ())

    return errors


def _pick_spark_errors(errors):
    """Pick the shortest Spark error with a traceback."""
    def sort_key(error):
        spark_error = error['spark_error']
        msg = spark_error.get('message') or ''
        num_lines = spark_error.get('num_lines') or 1

        return (
            _PYTHON_TRACEBACK_HEADER in msg,
            num_lines > 1,
            -num_lines,
        )

    return sorted(
        (e for e in errors if e.get('spark_error')),
        key=sort_key, reverse=True)


def _pick_error_attempt_ids(log_interpretation):
    """Pick error attempt IDs from step and history logs, so we know which
    task logs to look at (most relevant first)"""
    errors = _extract_errors(log_interpretation)

    attempt_to_container_id = log_interpretation.get('history', {}).get(
        'attempt_to_container_id', {})

    errors = _merge_and_sort_errors(errors, attempt_to_container_id)

    errors.sort(key=_is_probably_task_error, reverse=True)

    return list(unique(
        error['attempt_id'] for error in errors
        if error.get('attempt_id')))


def _is_probably_task_error(error):
    """Used to identify task errors."""
    return ('subprocess failed' in
            error.get('hadoop_error', {}).get('message', ''))


def _merge_and_sort_errors(errors, attempt_to_container_id=None):
    """This function merges errors from one or more lists of errors and returns them sorted by recency.
    This function first initializes a dictionary to save errors. Then, it iterates through each error in the given list of errors and merge them by container id. If an error does not have container id, it generates a key based on the error's time. Finally it uses a custom key sort function to prioritize task errors and sort the errors based on their keys.
    
    Input-Output Arguments
    :param errors: List of dictionaries. One or more lists of errors to be merged and sorted.
    :param attempt_to_container_id: Dictionary. A dictionary mapping attempt_id to container_id.
    :return: List of dictionaries. The merged and sorted list of errors.
    
    """


def _log_probable_cause_of_failure(log, error):
    """Log "probable cause of failure" log message."""
    log.error('\nProbable cause of failure:\n\n%s\n\n' % _format_error(error))


def _format_error(error):
    """Return string to log/print explaining the given error."""
    # it's just sad if we error while trying to explain an error
    try:
        return _format_error_helper(error)
    except:
        return json.dumps(error, indent=2, sort_keys=True)


def _format_error_helper(error):
    """Return string to log/print explaining the given error."""
    result = ''

    spark_error = error.get('spark_error')
    if spark_error:
        spark_error = _trim_spark_error(spark_error)

        result += spark_error.get('message', '')

        if spark_error.get('path'):
            result += '\n\n(from %s)' % _describe_source(spark_error)

        # spark errors typically include both java and Python stacktraces,
        # so it's not helpful to print hadoop/task errors (and there probably
        # wouldn't be any)
    else:
        hadoop_error = error.get('hadoop_error')
        if hadoop_error:
            result += hadoop_error.get('message', '')

            if hadoop_error.get('path'):
                result += '\n\n(from %s)' % _describe_source(hadoop_error)

        # for practical purposes, there's always a Java error with a message,
        # so don't worry too much about spacing.

        task_error = error.get('task_error')
        if task_error:
            if hadoop_error:
                result += '\n\ncaused by:\n\n%s' % (
                    task_error.get('message', ''))
            else:
                result += task_error.get('message', '')

            if task_error.get('path'):
                result += '\n\n(from %s)' % _describe_source(task_error)

    split = error.get('split')
    if split and split.get('path'):
        result += '\n\nwhile reading input from %s' % _describe_source(split)

    return result


def _describe_source(d):
    """return either '<path>' or 'line N of <path>' or 'lines M-N of <path>'.
    """
    path = d.get('path') or ''

    if 'num_lines' in d and 'start_line' in d:
        if d['num_lines'] == 1:
            return 'line %d of %s' % (d['start_line'] + 1, path)
        else:
            return 'lines %d-%d of %s' % (
                d['start_line'] + 1, d['start_line'] + d['num_lines'], path)
    else:
        return path


def _trim_spark_error(spark_error):
    """If *spark_error* contains a stack trace followed by a blank line,
    trim off the blank line and everything that follows."""
    spark_error = dict(spark_error)

    parts = spark_error['message'].split('\n\n')

    if len(parts) > 1 and _PYTHON_TRACEBACK_HEADER in parts[0]:
        spark_error['message'] = parts[0]
        spark_error['num_lines'] = len(parts[0].split('\n')) + 1

    return spark_error