from django.test import TestCase
import json

import pytest

from ..models import JSONReformTaxCalculator, TaxSaveInputs
from ..forms import TaxBrainForm
from ...test_assets.test_models import TaxBrainTableResults, TaxBrainFieldsTest


@pytest.mark.django_db
class TestTaxBrainJSONReformModel(object):
    """Test taxbrain JSONReformTaxCalculator."""

    test_string = "".join(["1" for x in range(100000)])

    def test_create_reforms(self):
        self.reforms = JSONReformTaxCalculator.objects.create(
            reform_text=TestTaxBrainJSONReformModel.test_string,
            raw_reform_text=TestTaxBrainJSONReformModel.test_string,
            assumption_text=TestTaxBrainJSONReformModel.test_string,
            raw_assumption_text=TestTaxBrainJSONReformModel.test_string
        )

    def test_get_errors_warnings_pre_PB_160(self):
        """
        Test get old errors/warnings
        """
        pre_PB_160 = {
            'errors': {
                '1900': 'test'}, 'warnings': {
                '1770': 'test2'}}
        reform = JSONReformTaxCalculator(
            errors_warnings_text=json.dumps(pre_PB_160)
        )
        assert reform.get_errors_warnings() == {'policy': pre_PB_160}

    def test_get_errors_warnings_post_PB_160(self):
        """
        Test get old errors/warnings
        """
        post_PB_160 = {
            'project': {
                'errors': {'1900': 'test'},
                'warnings': {'1770': 'test2'}
            }
        }
        reform = JSONReformTaxCalculator(
            errors_warnings_text=json.dumps(post_PB_160)
        )
        assert reform.get_errors_warnings() == post_PB_160


class TestTaxBrainStaticResults(TaxBrainTableResults):

    def test_static_tc_lt_0130(self, test_coverage_fields, skelaton_res_lt_0130,
                               skelaton_res_gt_0130):
        self.tc_table_backcompat(test_coverage_fields, skelaton_res_lt_0130,
                                 skelaton_res_gt_0130,
                                 taxcalc_vers="0.10.2.abc",
                                 webapp_vers="1.1.1")

    def test_static_tc_gt_0130(self, test_coverage_fields,
                               skelaton_res_gt_0130):
        self.tc_table_backcompat(test_coverage_fields, skelaton_res_gt_0130,
                                 skelaton_res_gt_0130,
                                 taxcalc_vers="0.13.0",
                                 webapp_vers="1.2.0")


class TestTaxBrainStaticFields(TaxBrainFieldsTest):

    def test_set_fields(self, test_coverage_gui_fields):
        start_year = 2017
        fields = test_coverage_gui_fields.copy()
        fields['first_year'] = start_year

        self.parse_fields(start_year, fields, Form=TaxBrainForm)

    def test_old_runs(self):
        """
        Test that the fields JSON objects can be generated dyanamically
        """
        start_year = 2017
        tsi = TaxSaveInputs(
            ID_AmountCap_Switch_0='True',
            FICA_ss_trt='0.10',
            STD_cpi='True',
            SS_Earnings_c_cpi=True,
            first_year=start_year
        )
        tsi.save()
        tsi.set_fields()
        assert tsi.input_fields['_FICA_ss_trt'] == [0.10]
        assert tsi.input_fields['_STD_cpi']
        assert tsi.input_fields['_SS_Earnings_c_cpi']
        assert tsi.input_fields['_ID_AmountCap_Switch_medical'] == [True]

    def test_deprecated_fields(self):
        """
        Test that deprecated fields are added correctly
        """
        start_year = 2017
        tsi = TaxSaveInputs(
            raw_input_fields={
                'FICA_ss_trt': '0.10',
                'ID_BenefitSurtax_Switch_0': 'True',
                'STD_cpi': 'True',
                'deprecated_param': '1000'
            },
            first_year=start_year
        )
        tsi.set_fields()
        assert tsi.deprecated_fields == ['deprecated_param']
        tsi.raw_input_fields['yet_another_deprecated_param'] = '1001'
        tsi.set_fields()
        assert tsi.deprecated_fields == ['deprecated_param',
                                         'yet_another_deprecated_param']
        assert tsi.raw_input_fields['deprecated_param'] == '1000'
        assert tsi.raw_input_fields['yet_another_deprecated_param'] == '1001'
        assert 'deprecated_param' not in tsi.input_fields
        assert 'yet_another_deprecated_param' not in tsi.input_fields

    def test_data_source_puf(self, test_coverage_gui_fields):
        start_year = 2017
        fields = test_coverage_gui_fields.copy()
        fields['first_year'] = start_year
        fields['data_source'] = 'PUF'
        model = self.parse_fields(start_year, fields,
                                  use_puf_not_cps=True)

        assert model.use_puf_not_cps

    def test_data_source_cps(self, test_coverage_gui_fields):
        start_year = 2017
        fields = test_coverage_gui_fields.copy()
        fields['first_year'] = start_year
        fields['data_source'] = 'CPS'
        model = self.parse_fields(start_year, fields,
                                  use_puf_not_cps=False)

        assert not model.use_puf_not_cps
