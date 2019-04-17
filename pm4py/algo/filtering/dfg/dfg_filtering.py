from pm4py.algo.discovery.dfg.utils.dfg_utils import get_max_activity_count, get_activities_from_dfg,\
    sum_ingoutg_val_activ, get_outgoing_edges, get_ingoing_edges, get_utility_value_edge

from pm4py.algo.filtering.common import filtering_constants


def clean_dfg_based_on_noise_thresh(dfg, activities, noise_threshold):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    ----------
    dfg
        Directly-Follows graph
    activities
        Activities in the DFG graph
    noise_threshold
        Noise threshold

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """

    new_dfg = None
    activ_max_count = {}
    for act in activities:
        activ_max_count[act] = get_max_activity_count(dfg, act)

    for el in dfg:
        if type(el[0]) is str:
            if new_dfg is None:
                new_dfg = {}
            act1 = el[0]
            act2 = el[1]
            val = dfg[el]
        else:
            if new_dfg is None:
                new_dfg = []
            act1 = el[0][0]
            act2 = el[0][1]
            val = el[1]

        if val < max(activ_max_count[act1] * noise_threshold, activ_max_count[act2] * noise_threshold):
            pass
        else:
            if type(el[0]) is str:
                new_dfg[el] = dfg[el]
                pass
            else:
                new_dfg.append(el)
                pass

    return new_dfg


def clean_dfg_conflict_resolution(dfg, preserve_threshold=0, ratio_threshold=0):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    ----------
    dfg
        Directly-Follows graph
    preserve_threshold
        Preserve threshold
    ratio_threshold
        Ratio threshold

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """

    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    new_dfg = None
    for el in dfg:
        if type(el[0]) is str:
            act1 = el[0]
            act2 = el[1]
            val = dfg[el]
        else:
            act1 = el[0][0]
            act2 = el[0][1]
            val = el[1]
        if act1 in ingoing and act2 in ingoing[act1]:
            rel_significance = val/(2*sum_ingoutg_val_activ(outgoing, act1)) + val/(2*sum_ingoutg_val_activ(ingoing, act2))
            if rel_significance < preserve_threshold:
                continue
            else:
                val2 = ingoing[act1][act2]
                rel_significance2 = val2 / (2 * sum_ingoutg_val_activ(outgoing, act2)) + val2 / (
                            2 * sum_ingoutg_val_activ(ingoing, act1))
                if rel_significance2 < preserve_threshold and abs(rel_significance - rel_significance2) < ratio_threshold:
                    continue
        if type(el[0]) is str:
            if new_dfg is None:
                new_dfg = {}
            new_dfg[el] = dfg[el]
        else:
            if new_dfg is None:
                new_dfg = []
            new_dfg.append(el)
    return new_dfg


def clean_dfg_edge_filtering(dfg, edge_cutoff=1):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    ----------
    dfg
        Directly-Follows graph
    edge_cutoff
        Paths percentage

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    new_dfg = None
    for el in dfg:
        if type(el[0]) is str:
            act1 = el[0]
            act2 = el[1]
            val = dfg[el]
        else:
            act1 = el[0][0]
            act2 = el[0][1]
            val = el[1]

        ingoing_utility_value = get_utility_value_edge(ingoing, act2, val)
        outgoing_utility_value = get_utility_value_edge(outgoing, act1, val)

        if max(ingoing_utility_value, outgoing_utility_value) < edge_cutoff:
            pass
        else:
            if type(el[0]) is str:
                if new_dfg is None:
                    new_dfg = {}
                new_dfg[el] = dfg[el]
                pass
            else:
                if new_dfg is None:
                    new_dfg = []
                new_dfg.append(el)
                pass
    return new_dfg


def apply(dfg, parameters=None):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    -----------
    dfg
        Directly-Follows graph
    parameters
        Possible parameters of the algorithm, including:
            noiseThreshold -> Threshold of noise in the algorithm

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """
    if parameters is None:
        parameters = {}
    noise_threshold = parameters[
        "noiseThreshold"] if "noiseThreshold" in parameters else filtering_constants.DEFAULT_NOISE_THRESH_DF

    activities = get_activities_from_dfg(dfg)

    return clean_dfg_based_on_noise_thresh(dfg, activities, noise_threshold)
