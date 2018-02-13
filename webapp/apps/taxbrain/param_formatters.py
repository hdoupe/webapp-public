from collections import defaultdict, namedtuple
import six
import json
import ast

import taxcalc

from helpers import (INPUTS_META, BOOL_PARAMS, is_reverse, is_wildcard,
                     make_bool, convert_val, TRUE_REGEX, FALSE_REGEX)


MetaParam = namedtuple("MetaParam", ["param_name", "param_meta"])


def benefit_switch_fixup(fields, model, name="ID_BenefitSurtax_Switch"):
    """
    Take the incoming POST, the user reform, and the TaxSaveInputs
    model and fixup the switches _0, ..., _6 to one array of
    bools. Also set the model values correctly based on incoming
    POST
    """
    # Django forms needs switches to be True/False but in the interest of
    # ensuring that reforms created from a file or the GUI interface are the
    # same (down to the data type) the reform data are set to 1.0/0.0
    # _ids = [name + '_' + str(i) for i in range(7)]
    # values_from_model = [[fields[_id][0] for _id in _ids if _id in fields]]
    # final_values = [[True if _id in fields else False for (fields, _id) in zip(values_from_model[0], _ids)]]
    # for _id, val in zip(_ids, final_values[0]):
    #     fields[_id] = [1 if val else 0]
    #     setattr(model, _id, unicode(val))
    return fields


def amt_fixup(request, reform, model):
    """
    Take the regular tax captial gains parameters from the user reform
    and set them as the equivalent Alternative Minimum Tax capital
    gains parameters
    """
    cap_gains_params = ["CG_rt1", "CG_brk1_0", "CG_brk1_1",
                        "CG_brk1_2", "CG_brk1_3", "CG_brk1_cpi",
                        "CG_rt2", "CG_brk2_0", "CG_brk2_1",
                        "CG_brk2_2", "CG_brk2_3", "CG_brk2_cpi",
                        "CG_rt3"]

    for cgparam in cap_gains_params:
        if cgparam in reform:
            reform['AMT_' + cgparam] = reform[cgparam]
            if cgparam.endswith("_cpi"):
                setattr(model, 'AMT_' + cgparam, reform[cgparam])
            else:
                setattr(model, 'AMT_' + cgparam, reform[cgparam][0])

    return reform


def growth_fixup(mod):
    # if mod['growth_choice']:
    #     if mod['growth_choice'] == 'factor_adjustment':
    #         del mod['factor_target']
    #     if mod['growth_choice'] == 'factor_target':
    #         del mod['factor_adjustment']
    # else:
    #     if 'factor_adjustment' in mod:
    #         del mod['factor_adjustment']
    #     if 'factor_target' in mod:
    #         del mod['factor_target']
    #
    # del mod['growth_choice']

    return mod


def switch_fixup(taxbrain_data, fields, taxbrain_model):
    growth_fixup(taxbrain_data)
    benefit_names = ["ID_BenefitSurtax_Switch", "ID_BenefitCap_Switch",
                     "ID_AmountCap_Switch"]
    for benefit_name in benefit_names:
        benefit_switch_fixup(fields,
                             taxbrain_model,
                             name=benefit_name)

    amt_fixup(fields,
              taxbrain_data,
              taxbrain_model)


def parse_value(value, meta_param):
    """
    Parse the value to the type that the upstream package specification
    requires, but we let the upstream package deal with creating error messages

    returns: parsed value
    """
    # expecting a string
    assert isinstance(value, six.string_types)

    value = value.strip()

    # if value is wildcard or reverse operator, then return it
    if is_wildcard(value) or is_reverse(value):
        return value.strip()

    # get type requirements from model specification
    boolean_value = meta_param.param_meta["boolean_value"]
    if not boolean_value:
        integer_value = meta_param.param_meta["integer_value"]
    else:
        integer_value = False
    float_value = not(boolean_value or integer_value)

    # Try to parse case-insensitive True/False strings
    if TRUE_REGEX.match(value, endpos=4):
        prepped = "True"
    elif FALSE_REGEX.match(value, endpos=5):
        prepped = "False"
    else:
        # ast.literal_eval won't parse negative numbers
        negate = 1
        if value.rfind("-") == 0:
            negate = -1
            prepped = value[1:]
        else:
            prepped = value

    # value is not an integer, float, or boolean string
    try:
        parsed = ast.literal_eval(prepped)
    except ValueError:
        return parsed

    # Use information given to us by upstream specs to convert this value
    # into desired type or fail silently
    if isinstance(parsed, bool):
        return parsed
    elif isinstance(parsed, int):
        if boolean_value:
            return True if parsed else False
        elif float_value:
            return negate * float(parsed)
        else:
            return negate * parsed
    elif isinstance(parsed, float):
        if boolean_value:
            return True if parsed else False
        elif integer_value:
            # Don't want to lose info when we cast the float down to int
            # Note: 5.0 % 1.0 == 0.0 but 5.2 % 1.0 == 0.2
            if parsed % 1.0 > 0:
                return negate * parsed
            else:
                return negate * int(parsed)
        else:
            return negate * parsed
    else:
        return parsed

def parse_fields(param_dict, default_params):
    """
    Parses the raw GUI input into the correct types and maps the names to the
    appropriate default names

    returns: dictionary with parsed data
    """
    parsed = {}
    for k, v in param_dict.items():
        # user did not specify a value for this param
        if not v:
            continue

        # get upstream package parameter name and meta info
        meta_param = get_default_policy_param(k, default_params)
        values = []
        for item in v.split(","):
             values.append(parse_value(item, meta_param))
        parsed[meta_param.param_name] = values

    return parsed


def get_default_policy_param(param, default_params):
    """
    Map TaxBrain field name to Tax-Calculator parameter name
    For example: STD_0 maps to _STD_single

    returns: named tuple with taxcalc param name and metadata
    """
    if '_' + param in default_params: # ex. EITC_indiv --> _EITC_indiv
        return MetaParam('_' + param, default_params['_' + param])
    param_pieces = param.split('_')
    end_piece = param_pieces[-1]
    no_suffix = '_' + '_'.join(param_pieces[:-1])
    if end_piece == 'cpi': # ex. SS_Earnings_c_cpi --> _SS_Earnings_c_cpi
        if no_suffix in default_params:
            return MetaParam('_' + param, default_params[no_suffix])
        else:
            msg = "Received unexpected parameter: {}"
            raise ValueError(msg.format(param))
    if no_suffix in default_params: # ex. STD_0 --> _STD_single
        try:
            ix = int(end_piece)
        except ValueError:
            msg = "Parsing {}: Expected integer for index but got {}"
            raise ValueError(msg.format(param, end_piece))
        num_columns = len(default_params[no_suffix]['col_label'])
        if ix < 0 or ix >= num_columns:
            msg = "Parsing {}: Index {} not in range ({}, {})"
            raise IndexError(msg.format(param, ix, 0, num_columns))
        col_label = default_params[no_suffix]['col_label'][ix]
        return MetaParam(no_suffix + '_' + col_label, default_params[no_suffix])
    msg = "Received unexpected parameter: {}"
    raise ValueError(msg.format(param))


def to_json_reform(fields, start_year, cls=taxcalc.Policy):
    """
    Convert fields style dictionary to json reform style dictionary
    For example:
    fields = {'_state': <django.db.models.base.ModelState object at 0x10c764950>,
              'creation_date': datetime.datetime(2015, 1, 1, 0, 0), 'id': 64,
              'ID_ps_cpi': True, 'quick_calc': False,
              'FICA_ss_trt': [u'*', 0.1, u'*', 0.2], 'first_year': 2017,
              'ID_BenefitSurtax_Switch_0': [True], 'ID_Charity_c_cpi': True,
              'EITC_rt_2': [1.0]}
    to
    reform = {'_CG_nodiff': {'2017': [False]},
              '_FICA_ss_trt': {'2020': [0.2], '2018': [0.1]},
              '_ID_Charity_c_cpi': {'2017': True},
              '_EITC_rt_2kids': {'2017': [1.0]}}

    returns json style reform
    """
    map_back_to_tb = {}
    number_reverse_operators = 1
    default_params = cls.default_data(start_year=start_year,
                                      metadata=True)
    ignore = INPUTS_META

    reform = {}
    for param in fields:
        if param not in ignore:
            meta_param = get_default_policy_param(param, default_params)
            param_name = meta_param.param_name
            map_back_to_tb[param_name] = param
            reform[param_name] = {}
            if not isinstance(fields[param], list):
                assert isinstance(fields[param], bool) and param.endswith('_cpi')
                reform[param_name][str(start_year)] = fields[param]
                continue
            i = 0
            while i < len(fields[param]):
                if is_wildcard(fields[param][i]):
                    # may need to do something here
                    pass
                elif is_reverse(fields[param][i]):
                    # only the first character can be a reverse char
                    # and there must be a following character
                    assert len(fields[param]) > 1
                    # set value for parameter in start_year - 1
                    assert (isinstance(fields[param][i + 1], (int, float)) or
                            isinstance(fields[param][i + 1], bool))
                    reform[param_name][str(start_year - 1)] = \
                        [fields[param][i + 1]]

                    # realign year and parameter indices
                    for op in (0, number_reverse_operators + 1):
                        fields[param].pop(0)
                    continue
                else:
                    assert (isinstance(fields[param][i], (int, float)) or
                            isinstance(fields[param][i], bool))
                    reform[param_name][str(start_year + i)] = \
                        [fields[param][i]]

                i += 1

    return reform, map_back_to_tb


def append_errors_warnings(errors_warnings, append_func):
    """
    Appends warning/error messages to some object, append_obj, according to
    the provided function, append_func
    """
    for action in ['warnings', 'errors']:
        for param in errors_warnings[action]:
            for year in sorted(
                errors_warnings[action][param].keys(),
                key=lambda x: int(x)
            ):
                msg = errors_warnings[action][param][year]
                append_func(param, msg)


def parse_errors_warnings(errors_warnings, map_back_to_tb):
    """
    Parse error messages so that they can be mapped to Taxbrain param ID. This
    allows the messages to be displayed under the field where the value is
    entered.

    returns: dictionary 'parsed' with keys: 'errors' and 'warnings'
        parsed['errors/warnings'] = {year: {tb_param_name: 'error message'}}
    """
    parsed = {'errors': defaultdict(dict), 'warnings': defaultdict(dict)}
    for action in errors_warnings:
        msgs = errors_warnings[action]
        if len(msgs) == 0:
            continue
        for msg in msgs.split('\n'):
            if len(msg) == 0: # new line
                continue
            msg_spl = msg.split()
            msg_action = msg_spl[0]
            year = msg_spl[1]
            curr_id = msg_spl[2][1:]
            msg_parse = msg_spl[2:]
            parsed[action][curr_id][year] = ' '.join([msg_action] + msg_parse +
                                                         ['for', year])

    return parsed


def read_json_reform(reform, assumptions, map_back_to_tb={}):
    """
    Read reform and parse errors

    returns reform and assumption dictionaries that are compatible with
            taxcalc.Policy.implement_reform
            parsed warning and error messsages to be displayed on input page
            if necessary
    """
    policy_dict = taxcalc.Calculator.read_json_param_objects(
        reform,
        assumptions,
    )
    # get errors and warnings on parameters that do not cause ValueErrors
    errors_warnings = taxcalc.tbi.reform_warnings_errors(policy_dict)
    errors_warnings = parse_errors_warnings(errors_warnings,
                                            map_back_to_tb)
    # separate reform and assumptions
    reform_dict = policy_dict["policy"]
    assumptions_dict = {k: v for k, v in policy_dict.items() if k != "policy"}

    return reform_dict, assumptions_dict, errors_warnings


def get_reform_from_file(request_files, reform_text=None,
                         assumptions_text=None):
    """
    Parse files from request object and collect errors_warnings

    returns reform and assumptions dictionaries that are compatible with
            taxcalc.Policy.implement_reform
            raw reform and assumptions text
            parsed warning and error messsages to be displayed on input page
            if necessary
    """
    if "docfile" in request_files:
        inmemfile_reform = request_files['docfile']
        reform_text = inmemfile_reform.read()
    if 'assumpfile' in files:
        inmemfile_assumption = request_files['assumpfile']
        assumptions_text = inmemfile_assumption.read()

    (reform_dict, assumptions_dict,
        errors_warnings) = read_json_reform(reform_text,
                                            assumptions_text)

    assumptions_text = assumptions_text or ""

    return (reform_dict, assumptions_dict, reform_text, assumptions_text,
            errors_warnings)


def get_reform_from_gui(fields, taxbrain_model=None, behavior_model=None,
                        stored_errors=None):
    """
    Parse request and model objects and collect reforms and warnings
    This function is also called by dynamic/views.behavior_model.  In the
    future, this could be used as a generic GUI parameter parsing function.

    returns reform and assumptions dictionaries that are compatible with
            taxcalc.Policy.implement_reform
            raw reform and assumptions text
            parsed warning and error messsages to be displayed on input page
            if necessary
    """
    if taxbrain_model is not None:
        start_year = taxbrain_model.start_year
    elif behavior_model is not None:
        start_year = behavior_model.start_year
    else:
        raise ValueError("Neither taxbrain_model nor behavior_model was given")

    taxbrain_data = {}
    assumptions_data = {}
    map_back_to_tb = {}

    policy_dict_json = {}
    assumptions_dict_json = {}

    # prepare taxcalc params from TaxSaveInputs model
    if taxbrain_model is not None:
        default_params = taxcalc.Policy.default_data(start_year=start_year,
                                                     metadata=True)
        taxbrain_data = taxbrain_model.raw_fields
        taxbrain_data = parse_fields(taxbrain_data, default_params)
        switch_fixup(taxbrain_data, fields, taxbrain_model)
        # convert GUI input to json style taxcalc reform
        policy_dict_json, map_back_to_tb = to_json_reform(taxbrain_data,
                                                          int(start_year))
    if behavior_model is not None:
        assumptions_data = dict(behavior_model.__dict__)
        assumptions_data = parse_fields(assumptions_data)
        (assumptions_dict_json,
            map_back_assump) = to_json_reform(assumptions_data,
                                              int(start_year),
                                              cls=taxcalc.Behavior)
        map_back_to_tb.update(map_back_assump)

    policy_dict_json = {"policy": policy_dict_json}

    policy_dict_json = json.dumps(policy_dict_json)

    assumptions_dict_json = {"behavior": assumptions_dict_json,
                             "growdiff_response": {},
                             "consumption": {},
                             "growdiff_baseline": {}}
    assumptions_dict_json = json.dumps(assumptions_dict_json)

    (reform_dict, assumptions_dict,
        errors_warnings) = read_json_reform(policy_dict_json,
                                            assumptions_dict_json,
                                            map_back_to_tb)

    return (reform_dict, assumptions_dict, "", "", errors_warnings)