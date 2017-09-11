from taxcalc.records import Records
from taxcalc.calculate import Calculator
from taxcalc.policy import Policy
from taxcalc.utils import multiyear_diagnostic_table
import pandas as pd
import numpy as np
import json

import traceback

def format_reform(reform):
    formatted = {"policy": {}}
    for param in reform:
        formatted["policy"][param] = {"2017": reform[param]}

    return formatted


def get_default_reform():
    dd = Policy.default_data(metadata=False, start_year=2017)

    reform = format_reform(dd)

    return reform


def assert_reforms_equal(local, taxbrain):
    default_reform = get_default_reform()["policy"]
    local_keys = list(local.keys())
    taxbrain_keys = list(taxbrain.keys())
    params = set(local_keys + taxbrain_keys)
    for param in params:
        if param not in local_keys or param not in taxbrain_keys:
            assert (param not in local_keys and param in taxbrain_keys)
            np.testing.assert_equal(taxbrain[param], default_reform[param]["2017"])
            continue
        try:
            np.testing.assert_equal(local[param], taxbrain[param])
        except AssertionError as ae:
            print("PARAMETER:\t", param)
            print("EXPECTED:\t", local[param])
            print("ACTUAL:\t\t", taxbrain[param])
            traceback.print_exc()


def taxbrain_param_processing():
    # actual data posted to taxbrain
    local_all = {u'_ACTC_ChildNum': [4.0],
         u'_ACTC_Income_thd': [3500.0],
         u'_ACTC_rt': [0.1],
         u'_ACTC_rt_bonus_under5family': [0.01],
         u'_AGI_surtax_thd': [[175000, 350000, 175000, 350000, 9e+99]],
         u'_AGI_surtax_trt': [0.1],
         u'_ALD_Alimony_hc': [0.15],
         u'_ALD_Dependents_Child_c': [7156.0],
         u'_ALD_Dependents_Elder_c': [5000.0],
         u'_ALD_Dependents_hc': [0.1],
         u'_ALD_Dependents_thd': [[250000, 500000, 250001, 250002, 0.0]],
         u'_ALD_DomesticProduction_hc': [0.19],
         u'_ALD_EarlyWithdraw_hc': [0.14],
         u'_ALD_EducatorExpenses_hc': [0.16],
         u'_ALD_HSADeduction_hc': [0.17],
         u'_ALD_IRAContributions_hc': [0.18],
         u'_ALD_InvInc_ec_base_RyanBrady': [True],
         u'_ALD_InvInc_ec_rt': [0.08],
         u'_ALD_KEOGH_SEP_hc': [0.13],
         u'_ALD_SelfEmp_HealthIns_hc': [0.12],
         u'_ALD_SelfEmploymentTax_hc': [0.11],
         u'_ALD_StudentLoan_hc': [0.1],
         u'_ALD_Tuition_hc': [0.2],
         u'_AMEDT_ec': [[100000, 150000, 95000, 100001, 200000.0]],
         u'_AMEDT_rt': [0.015],
         u'_AMT_CG_brk1': [[27950, 55900, 27950, 40800, 75900.0]],
         u'_AMT_CG_brk2': [[218400, 270700, 135350, 244550, 470700.0]],
         u'_AMT_CG_brk3': [[818400, 870700, 535350, 844550, 9e+99]],
         u'_AMT_CG_rt1': [0.11],
         u'_AMT_CG_rt2': [0.21],
         u'_AMT_CG_rt3': [0.36],
         u'_AMT_CG_rt4': [0.51],
         u'_AMT_brk1': [177800.0],
         u'_AMT_em': [[44300, 74500, 32250, 44300, 84500.0]],
         u'_AMT_em_ps': [[100700, 140900, 70450, 100701, 160900.0]],
         u'_AMT_prt': [0.4],
         u'_AMT_rt1': [0.3],
         u'_AMT_rt2': [0.1],
         u'_CDCC_c': [2500.0],
         u'_CDCC_crt': [30.0],
         u'_CDCC_ps': [10000.0],
         u'_CG_brk1': [[27950, 55900, 27950, 40800, 75900.0]],
         u'_CG_brk2': [[218400, 270700, 135350, 244550, 470700.0]],
         u'_CG_brk3': [[818400, 870700, 535350, 844550, 9e+99]],
         u'_CG_ec': [0.01],
         u'_CG_nodiff': [True],
         u'_CG_reinvest_ec_rt': [0.01],
         u'_CG_rt1': [0.1],
         u'_CG_rt2': [0.2],
         u'_CG_rt3': [0.35],
         u'_CG_rt4': [0.5],
         u'_CR_AmOppNonRefundable_hc': [0.16],
         u'_CR_AmOppRefundable_hc': [0.15],
         u'_CR_Education_hc': [0.19],
         u'_CR_ForeignTax_hc': [0.11],
         u'_CR_GeneralBusiness_hc': [0.13],
         u'_CR_MinimumTax_hc': [0.14],
         u'_CR_OtherCredits_hc': [0.18],
         u'_CR_ResidentialEnergy_hc': [0.12],
         u'_CR_RetirementSavings_hc': [0.1],
         u'_CR_SchR_hc': [0.17],
         u'_CTC_c': [800.0],
         u'_CTC_c_under5_bonus': [0.01],
         u'_CTC_new_c': [100.0],
         u'_CTC_new_c_under5_bonus': [100.0],
         u'_CTC_new_prt': [0.2],
         u'_CTC_new_ps': [[10000, 20000, 10001, 20001, 0.0]],
         u'_CTC_new_refund_limit_payroll_rt': [0.2],
         u'_CTC_new_refund_limited': [True],
         u'_CTC_new_rt': [0.1],
         u'_CTC_prt': [0.1],
         u'_CTC_ps': [[70000, 100000, 50000, 65000, 75000.0]],
         u'_DependentCredit_c': [0.01],
         u'_EITC_InvestIncome_c': [3050.0],
         u'_EITC_MaxEligAge': [50.0],
         u'_EITC_MinEligAge': [26.0],
         u'_EITC_c': [[410, 3000, 5016, 6018]],
         u'_EITC_indiv': [True],
         u'_EITC_prt': [[0.08, 0.2, 0.25, 0.23]],
         u'_EITC_ps': [[8040, 15340, 15341, 15342]],
         u'_EITC_ps_MarriedJ': [[5090, 5090, 5090, 5090]],
         u'_EITC_rt': [[0.07, 0.3, 0.35, 0.4]],
         u'_FICA_mc_trt': [0.05],
         u'_FICA_ss_trt': [0.15],
         u'_FST_AGI_thd_hi': [[980000, 980001, 498000, 980002, 2000000.0]],
         u'_FST_AGI_thd_lo': [[900000, 900001, 490000, 900002, 1000000.0]],
         u'_FST_AGI_trt': [0.1],
         u'_ID_BenefitCap_Switch': [[True, True, True, True, 0.0, 1.0, 1.0]],
         u'_ID_BenefitCap_rt': [0.8],
         u'_ID_BenefitSurtax_Switch': [[True, True, True, True, True, False, True]],
         u'_ID_BenefitSurtax_crt': [0.8],
         u'_ID_BenefitSurtax_em': [[1000, 2000, 1001, 1002, 0.0]],
         u'_ID_BenefitSurtax_trt': [0.5],
         u'_ID_Casualty_c': [[100020, 200006, 100021, 100022, 9e+99]],
         u'_ID_Casualty_frt': [0.3],
         u'_ID_Casualty_hc': [0.15],
         u'_ID_Charity_c': [[100016, 200005, 100017, 100018, 9e+99]],
         u'_ID_Charity_crt_all': [0.35],
         u'_ID_Charity_crt_noncash': [0.2],
         u'_ID_Charity_frt': [0.01],
         u'_ID_Charity_hc': [0.13],
         u'_ID_InterestPaid_c': [[100012, 200004, 100013, 100014, 9e+99]],
         u'_ID_InterestPaid_hc': [0.13],
         u'_ID_Medical_c': [[100000, 200000, 100001, 100002, 9e+99]],
         u'_ID_Medical_frt': [0.15],
         u'_ID_Medical_frt_add4aged': [0.00],
         u'_ID_Medical_hc': [0.1],
         u'_ID_Miscellaneous_c': [[100024, 200007, 100025, 100026, 9e+99]],
         u'_ID_Miscellaneous_frt': [0.2],
         u'_ID_Miscellaneous_hc': [0.16],
         u'_ID_RealEstate_c': [[100008, 200003, 100009, 100010, 9e+99]],
         u'_ID_RealEstate_hc': [0.12],
         u'_ID_StateLocalTax_c': [[100004, 200001, 100005, 100006, 9e+99]],
         u'_ID_StateLocalTax_hc': [0.11],
         u'_ID_c': [[20000, 40000, 20001, 20002, 9e+99]],
         u'_ID_crt': [0.9],
         u'_ID_prt': [0.4],
         u'_ID_ps': [[100000, 200000, 100001, 100002, 313800.0]],
         u'_II_brk1': [[8325, 17650, 8326, 12350, 18650.0]],
         u'_II_brk2': [[35950, 73900, 35951, 49800, 75900.0]],
         u'_II_brk3': [[81900, 143100, 70550, 121200, 153100.0]],
         u'_II_brk4': [[151650, 203350, 106675, 202500, 233350.0]],
         u'_II_brk5': [[400700, 400701, 200350, 400702, 416700.0]],
         u'_II_brk6': [[417700, 446700, 228350, 426700, 470700.0]],
         u'_II_brk7': [[710400, 950700, 725350, 834550, 9e+99]],
         u'_II_credit': [[1000, 2000, 1001, 1002, 0.0]],
         u'_II_credit_nr': [[500, 1000, 501, 502, 0.0]],
         u'_II_credit_nr_prt': [0.1],
         u'_II_credit_prt': [0.1],
         u'_II_em': [2000.0],
         u'_II_no_em_nu18': [True],
         u'_II_prt': [0.1],
         u'_II_rt1': [0.15],
         u'_II_rt2': [0.2],
         u'_II_rt3': [0.35],
         u'_II_rt4': [0.4],
         u'_II_rt5': [0.5],
         u'_II_rt6': [0.6],
         u'_II_rt7': [0.7],
         u'_II_rt8': [0.75],
         u'_LST': [50.0],
         u'_NIIT_PT_taxed': [True],
         u'_NIIT_rt': [0.1],
         u'_NIIT_thd': [[190000, 240000, 115000, 190001, 250000.0]],
         u'_PT_brk1': [[8325, 17650, 8326, 12350, 18650.0]],
         u'_PT_brk2': [[35950, 73900, 35951, 49800, 75900.0]],
         u'_PT_brk3': [[81900, 143100, 70550, 121200, 153100.0]],
         u'_PT_brk4': [[151650, 203350, 106675, 202500, 233350.0]],
         u'_PT_brk5': [[400700, 400701, 200350, 400702, 416700.0]],
         u'_PT_brk6': [[417700, 446700, 228350, 426700, 470700.0]],
         u'_PT_brk7': [[710400, 950700, 725350, 834550, 9e+99]],
         u'_PT_rt1': [0.15],
         u'_PT_rt2': [0.2],
         u'_PT_rt3': [0.35],
         u'_PT_rt4': [0.4],
         u'_PT_rt5': [0.5],
         u'_PT_rt6': [0.6],
         u'_PT_rt7': [0.7],
         u'_PT_rt8': [0.75],
         u'_SS_Earnings_c': [130000.0],
         u'_SS_thd50': [[20000, 27000, 20001, 20002, 25000.0]],
         u'_SS_thd85': [[30000, 40000, 30000, 30000, 34000.0]],
         u'_STD': [[7350, 13700, 7351, 10350, 12700.0]],
         u'_STD_Aged': [[2400, 2200, 2100, 2401, 1550.0]]}

    # copied and pasted from keywords to dropq
    taxbrain_all = {'start_year': 2017, 'user_mods': {u'growdiff_response': {}, u'consumption': {}, u'growdiff_baseline': {}, u'behavior': {}, u'policy': {2017: {u'_ID_c': [[20000, 40000, 20001, 20002, 9e+99]], u'_ID_Miscellaneous_c': [[100024, 200007, 100025, 100026, 9e+99]], u'_CTC_c': [800.0], u'_CDCC_crt': [30.0], u'_FST_AGI_thd_hi': [[980000, 980001, 498000, 980002, 2000000.0]], u'_EITC_prt': [[0.08, 0.2, 0.25, 0.23]], u'_EITC_rt': [[0.07, 0.3, 0.35, 0.4]], u'_ID_prt': [0.4], u'_CTC_new_prt': [0.2], u'_ALD_IRAContributions_hc': [0.18], u'_ID_BenefitSurtax_crt': [0.8], u'_ID_Charity_c': [[100016, 200005, 100017, 100018, 9e+99]], u'_ALD_SelfEmp_HealthIns_hc': [0.12], u'_EITC_MinEligAge': [26.0], u'_ALD_KEOGH_SEP_hc': [0.13], u'_EITC_ps_MarriedJ': [[5090, 5090, 5090, 5090]], u'_AGI_surtax_thd': [[175000, 350000, 175000, 350000, 9e+99]], u'_ID_BenefitCap_rt': [0.8], u'_LST': [50.0], u'_ALD_StudentLoan_hc': [0.1], u'_ALD_Tuition_hc': [0.2], u'_ALD_Dependents_Child_c': [7156.0], u'_CG_nodiff': [True], u'_ID_Casualty_frt': [0.3], u'_AMT_em': [[44300, 74500, 32250, 44300, 84500.0]], u'_CR_OtherCredits_hc': [0.18], u'_PT_rt8': [0.75], u'_ID_Miscellaneous_hc': [0.16], u'_PT_rt3': [0.35], u'_PT_rt2': [0.2], u'_PT_rt1': [0.15], u'_STD_Aged': [[2400, 2200, 2100, 2401, 1550.0]], u'_PT_rt7': [0.7], u'_PT_rt6': [0.6], u'_PT_rt5': [0.5], u'_PT_rt4': [0.4], u'_CDCC_ps': [10000.0], u'_II_prt': [0.1], u'_PT_brk7': [[710400, 950700, 725350, 834550, 9e+99]], u'_PT_brk6': [[417700, 446700, 228350, 426700, 470700.0]], u'_PT_brk5': [[400700, 400701, 200350, 400702, 416700.0]], u'_PT_brk4': [[151650, 203350, 106675, 202500, 233350.0]], u'_PT_brk3': [[81900, 143100, 70550, 121200, 153100.0]], u'_PT_brk2': [[35950, 73900, 35951, 49800, 75900.0]], u'_PT_brk1': [[8325, 17650, 8326, 12350, 18650.0]], u'_ACTC_ChildNum': [4.0], u'_SS_thd85': [[30000, 40000, 30000, 30000, 34000.0]], u'_ID_Medical_frt': [0.15], u'_ALD_EducatorExpenses_hc': [0.16], u'_CR_AmOppNonRefundable_hc': [0.16], u'_ID_RealEstate_c': [[100008, 200003, 100009, 100010, 9e+99]], u'_CTC_prt': [0.1], u'_ALD_HSADeduction_hc': [0.17], u'_ID_BenefitSurtax_trt': [0.5], u'_ALD_Dependents_thd': [[250000, 500000, 250001, 250002, 0.0]], u'_ID_Miscellaneous_frt': [0.2], u'_ID_InterestPaid_c': [[100012, 200004, 100013, 100014, 9e+99]], u'_II_no_em_nu18': [True], u'_CTC_new_c': [100.0], u'_DependentCredit_c': [0.01], u'_CG_rt1': [0.1], u'_CG_rt3': [0.35], u'_CG_rt2': [0.2], u'_CG_rt4': [0.5], u'_CR_GeneralBusiness_hc': [0.13], u'_ALD_EarlyWithdraw_hc': [0.14], u'_ID_Medical_hc': [0.1], u'_AMT_CG_rt1': [0.1], u'_AMT_CG_rt2': [0.2], u'_AMT_CG_rt3': [0.35], u'_AMT_CG_rt4': [0.51], u'_II_credit_nr': [[500, 1000, 501, 502, 0.0]], u'_II_credit_prt': [0.1], u'_II_em': [2000.0], u'_ID_Charity_crt_all': [0.35], u'_EITC_MaxEligAge': [50.0], u'_AMEDT_ec': [[100000, 150000, 95000, 100001, 200000.0]], u'_CR_ResidentialEnergy_hc': [0.12], u'_AMT_em_ps': [[100700, 140900, 70450, 100701, 160900.0]], u'_CTC_new_refund_limited': [True], u'_ALD_SelfEmploymentTax_hc': [0.11], u'_CTC_c_under5_bonus': [0.01], u'_CR_AmOppRefundable_hc': [0.15], u'_ID_crt': [0.9], u'_II_brk3': [[81900, 143100, 70550, 121200, 153100.0]], u'_CR_SchR_hc': [0.17], u'_ALD_Alimony_hc': [0.15], u'_ID_BenefitSurtax_Switch': [[True, True, True, True, False, False, False]], u'_II_credit_nr_prt': [0.1], u'_EITC_c': [[410, 3000, 5016, 6018]], u'_CTC_new_rt': [0.1], u'_ID_ps': [[100000, 200000, 100001, 100002, 313800.0]], u'_EITC_indiv': [True], u'_CG_ec': [0.01], u'_CR_MinimumTax_hc': [0.14], u'_ID_Medical_c': [[100000, 200000, 100001, 100002, 9e+99]], u'_SS_Earnings_c': [130000.0], u'_ALD_InvInc_ec_rt': [0.08], u'_ID_BenefitSurtax_em': [[1000, 2000, 1001, 1002, 0.0]], u'_CTC_ps': [[70000, 100000, 50000, 65000, 75000.0]], u'_II_rt6': [0.6], u'_ID_RealEstate_hc': [0.12], u'_ALD_Dependents_hc': [0.1], u'_ID_StateLocalTax_c': [[100004, 200001, 100005, 100006, 9e+99]], u'_ID_StateLocalTax_hc': [0.11], u'_ID_Charity_hc': [0.13], u'_CG_reinvest_ec_rt': [0.01], u'_II_credit': [[1000, 2000, 1001, 1002, 0.0]], u'_FICA_ss_trt': [0.15], u'_ID_Charity_frt': [0.01], u'_AMT_prt': [0.4], u'_ACTC_rt_bonus_under5family': [0.01], u'_STD': [[7350, 13700, 7351, 10350, 12700.0]], u'_ID_InterestPaid_hc': [0.13], u'_NIIT_PT_taxed': [True], u'_AGI_surtax_trt': [0.1], u'_CR_Education_hc': [0.19], u'_AMT_CG_brk2': [[218400, 270700, 135350, 244550, 470700.0]], u'_AMT_CG_brk3': [[818400, 870700, 535350, 844550, 9e+99]], u'_AMT_CG_brk1': [[27950, 55900, 27950, 40800, 75900.0]], u'_II_brk5': [[400700, 400701, 200350, 400702, 416700.0]], u'_II_brk4': [[151650, 203350, 106675, 202500, 233350.0]], u'_II_brk7': [[710400, 950700, 725350, 834550, 9e+99]], u'_II_brk6': [[417700, 446700, 228350, 426700, 470700.0]], u'_II_brk1': [[8325, 17650, 8326, 12350, 18650.0]], u'_EITC_ps': [[8040, 15340, 15341, 15342]], u'_II_brk2': [[35950, 73900, 35951, 49800, 75900.0]], u'_ID_Casualty_hc': [0.15], u'_CG_brk1': [[27950, 55900, 27950, 40800, 75900.0]], u'_CTC_new_ps': [[10000, 20000, 10001, 20001, 0.0]], u'_CG_brk3': [[818400, 870700, 535350, 844550, 9e+99]], u'_CG_brk2': [[218400, 270700, 135350, 244550, 470700.0]], u'_ALD_InvInc_ec_base_RyanBrady': [True], u'_II_rt1': [0.15], u'_II_rt3': [0.35], u'_II_rt2': [0.2], u'_II_rt5': [0.5], u'_II_rt4': [0.4], u'_II_rt7': [0.7], u'_NIIT_thd': [[190000, 240000, 115000, 190001, 250000.0]], u'_II_rt8': [0.75], u'_FST_AGI_trt': [0.1], u'_ALD_DomesticProduction_hc': [0.19], u'_ID_Casualty_c': [[100020, 200006, 100021, 100022, 9e+99]], u'_SS_thd50': [[20000, 27000, 20001, 20002, 25000.0]], u'_AMT_brk1': [177800.0], u'_CDCC_c': [2500.0], u'_ID_Medical_frt_add4aged': [0.0], u'_ACTC_Income_thd': [3500.0], u'_CTC_new_c_under5_bonus': [100.0], u'_AMT_rt1': [0.3], u'_AMT_rt2': [0.1], u'_AMEDT_rt': [0.015], u'_CTC_new_refund_limit_payroll_rt': [0.2], u'_CR_ForeignTax_hc': [0.11], u'_ALD_Dependents_Elder_c': [5000.0], u'_FICA_mc_trt': [0.05], u'_CR_RetirementSavings_hc': [0.1], u'_NIIT_rt': [0.1], u'_ACTC_rt': [0.1], u'_FST_AGI_thd_lo': [[900000, 900001, 490000, 900002, 1000000.0]], u'_ID_BenefitCap_Switch': [[True, True, True, True, 1.0, 1.0, 1.0]], u'_ID_Charity_crt_noncash': [0.2], u'_EITC_InvestIncome_c': [3050.0]}}, u'gdp_elasticity': {}}, 'year_n': 5}

    taxbrain_reform_all = taxbrain_all['user_mods']['policy']

    assert_reforms_equal(local_all, taxbrain_reform_all[2017])