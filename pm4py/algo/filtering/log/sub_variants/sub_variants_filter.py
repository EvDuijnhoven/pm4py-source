from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.algo.filtering.log.variants import variants_filter


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
    variants = variants_filter.get_variants(log, parameters)
    log = EventLog()
    for variant in variants:
        if any(x in variant for x in admitted_sub_variants) == positive:
            for trace in variants[variant]:
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
            sub_variant_lengths -> the lengths of the sub_variants
            count_unique_traces -> If true, only count unique traces
            sub_variant_activities -> The activities the sub_variant should contain
            sub_variant_start_activities -> The activities the sub_variant should start with
            sub_variant_end_activities -> The activities the sub_variant should end on

    Returns
    ----------
    sub_variants
        Dictionary with sub_variant as the key and the list of traces indexes as the value
    """
    if parameters is None:
        parameters = {}

    sub_variant_lengths = parameters['sub_variant_lengths'] if 'sub_variant_lengths' in parameters else [5]
    count_unique_traces = parameters['count_unique_traces'] if 'count_unique_traces' in parameters else True

    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    sub_variant_activities = parameters[
        'sub_variant_activities'] if 'sub_variant_activities' in parameters else False
    sub_variant_start_activities = parameters[
        'sub_variant_start_activities'] if 'sub_variant_start_activities' in parameters else False
    sub_variant_end_activities = parameters[
        'sub_variant_end_activities'] if 'sub_variant_end_activities' in parameters else False

    sub_variants = {}
    for trace_idx, trace in enumerate(log):
        for sub_variant_length in sub_variant_lengths:
            for i in range(len(trace) - sub_variant_length + 1):
                sub_trace_attributes = create_sub_trace_attributes_array(
                    trace[i:(i + sub_variant_length)],
                    attribute_key,
                    sub_variant_activities,
                    sub_variant_start_activities,
                    sub_variant_end_activities)
                if sub_trace_attributes:
                    sub_variant = ",".join(sub_trace_attributes)
                    if sub_variant not in sub_variants:
                        sub_variants[sub_variant] = []
                    if trace_idx not in sub_variants[sub_variant] or not count_unique_traces:
                        sub_variants[sub_variant].append(trace_idx)

    return sub_variants


def create_sub_trace_attributes_array(
        sub_trace,
        attribute_key,
        sub_variant_activities,
        sub_variant_start_activities,
        sub_variant_end_activities):
    """
    Returns the sub_trace_attributes whenever it meets the citeria

    Parameters
    ----------
    sub_trace
        Sub trace
    attribute_key
        Attribute identifying the activity in the log
    sub_variant_activities
        The activities the sub_variant should contain
    sub_variant_start_activities
        The activities the sub_variant should start with
    sub_variant_end_activities
        The activities the sub_variant should end on

    Returns
    ----------
    sub_trace_attributes
        Array of strings of the attribute_key
    """
    sub_trace_attributes = [x[attribute_key] for x in sub_trace if
                            attribute_key in x]

    return sub_trace_attributes if (
            (not sub_variant_start_activities or any(
                sub_variant_start_activity == sub_trace_attributes[0] for sub_variant_start_activity in
                sub_variant_start_activities)) and
            (not sub_variant_end_activities or any(
                sub_variant_end_activity == sub_trace_attributes[-1] for sub_variant_end_activity in
                sub_variant_end_activities)) and
            (not sub_variant_activities or any(
                sub_variant_activity in sub_trace_attributes for sub_variant_activity in
                sub_variant_activities))
        ) else []


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
