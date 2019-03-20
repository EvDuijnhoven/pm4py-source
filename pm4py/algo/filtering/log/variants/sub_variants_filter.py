from pm4py.algo.filtering.common import filtering_constants
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, admitted_sub_variants, parameters=None):
    """
    Filter log keeping/removing only provided variants

    Parameters
    -----------
    log
        Log object
    admitted_sub_variants
        Admitted sub variants
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            positive -> Indicate if events should be kept/removed
    """

    if parameters is None:
        parameters = {}
    positive = parameters["positive"] if "positive" in parameters else True
    sub_variants = get_sub_variants(log, parameters)
    log = EventLog()
    for sub_variant in sub_variants:
        if (positive and sub_variant in admitted_sub_variants) or (not positive and sub_variant not in admitted_sub_variants):
            for trace in sub_variants[sub_variant]:
                log.append(trace)
    return log


def get_sub_variants(log, parameters=None):
    """
    Gets a dictionary whose key is the sub_variant and as value there
    is the list of traces that share the sub_variant

    Parameters
    ----------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            sub_variant_length -> Length of the sub variants
            count_unique_traces -> If true, only count unique traces

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """

    sub_variants_trace_idx = get_sub_variants_from_log_trace_idx(log, parameters)

    return convert_variants_trace_idx_to_trace_obj(log, sub_variants_trace_idx)


def get_sub_variants_from_log_trace_idx(log, parameters=None):
    """
    Gets a dictionary whose key is the sub_variant and as value there
    is the list of traces indexes that share the sub_variant

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            sub_variant_length -> Length of the sub variants
            count_unique_traces -> If true, only count unique traces

    Returns
    ----------
    sub_variants
        Dictionary with sub_variant as the key and the list of traces indexes as the value
    """
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    sub_variant_length = parameters['sub_variant_length'] if 'sub_variant_length' in parameters else 3
    count_unique_traces = parameters['count_unique_traces'] if 'count_unique_traces' in parameters else True

    sub_variants = {}
    for trace_idx, trace in enumerate(log):
        for i in range(len(trace)-sub_variant_length):
            sub_variant = ",".join([x[attribute_key] for x in trace[i:(i+sub_variant_length)] if attribute_key in x])
            if sub_variant not in sub_variants:
                sub_variants[sub_variant] = []
            if trace_idx not in sub_variants[sub_variant] or not count_unique_traces:
                sub_variants[sub_variant].append(trace_idx)

    return sub_variants


def convert_variants_trace_idx_to_trace_obj(log, sub_variants_trace_idx):
    """
    Converts sub_variants expressed as trace indexes to trace objects

    Parameters
    -----------
    log
        Trace log object
    sub_variants_trace_idx
        Variants associated to a list of belonging indexes

    Returns
    -----------
    sub_variants
        Sub Variants associated to a list of belonging traces
    """
    sub_variants = {}

    for key in sub_variants_trace_idx:
        sub_variants[key] = []
        for value in sub_variants_trace_idx[key]:
            sub_variants[key].append(log[value])

    return sub_variants
