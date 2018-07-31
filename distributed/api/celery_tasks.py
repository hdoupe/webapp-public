import json
import os

from celery import Celery

import btax
from btax.front_end_util import runner_json_tables
import taxcalc


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                   'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'redis://localhost:6379')

celery_app = Celery('tasks2', broker=CELERY_BROKER_URL,
                    backend=CELERY_RESULT_BACKEND)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['msgpack', 'json'],
)


def dropq_task(year_n, user_mods, first_budget_year, use_puf_not_cps=True,
               use_full_sample=True):
    print(
        'keywords to dropq',
        dict(
            year_n=year_n,
            start_year=int(first_budget_year),
            use_puf_not_cps=use_puf_not_cps,
            use_full_sample=use_full_sample,
            user_mods=user_mods
        )
    )

    results, pdfs = taxcalc.tbi.run_nth_year_taxcalc_model(
        year_n=year_n,
        start_year=int(first_budget_year),
        use_puf_not_cps=use_puf_not_cps,
        use_full_sample=use_full_sample,
        user_mods=user_mods
    )

    # Add taxcalc version to results
    vinfo = taxcalc._version.get_versions()
    results['taxcalc_version'] = vinfo['version']
    # TODO: Make this the distributed app version, not the TC version
    results['dropq_version'] = vinfo['version']

    return results, pdfs


@celery_app.task(name='api.celery_tasks.aggregate_yearly_results')
def aggregate_yearly_results(ans):
    results = {'outputs': []}
    all_pdfs_to_aggregate = {key: [] for key in ('aggr_d', 'aggr_1', 'aggr_2')}
    for formatted_result, pdfs_to_aggregate in ans:
        for key in formatted_result:
            if key == 'outputs':
                results['outputs'] += result['outputs']
            else:
                results[key] = result[key]
        # for key, value in pdfs_to_aggregate.items():
        #     all_pdfs_to_aggregate[key].append(value)
    results['aggr_outputs'] = taxcalc.tbi.run_taxcalc_years_aggregation(
        all_pdfs_to_aggregate)
    return json.dumps(results)


@celery_app.task(name='api.celery_tasks.dropq_task_async')
def dropq_task_async(year, user_mods, first_budget_year, use_puf_not_cps=True):
    return dropq_task(year, user_mods, first_budget_year,
                      use_puf_not_cps=use_puf_not_cps, use_full_sample=True)


@celery_app.task(name='api.celery_tasks.dropq_task_small_async')
def dropq_task_small_async(year, user_mods, first_budget_year,
                           use_puf_not_cps=True):
    return dropq_task(year, user_mods, first_budget_year,
                      use_puf_not_cps=use_puf_not_cps, use_full_sample=False)


@celery_app.task(name='api.celery_tasks.elasticity_gdp_task_async')
def elasticity_gdp_task_async(year_n, user_mods, first_budget_year,
                              gdp_elasticity, use_puf_not_cps=True):
    print("kw to dropq", dict(
        year_n=year_n,
        start_year=int(first_budget_year),
        use_puf_not_cps=use_puf_not_cps,
        use_full_sample=True,
        user_mods=user_mods,
        gdp_elasticity=gdp_elasticity
    ))

    gdp_elast_i = taxcalc.tbi.run_nth_year_gdp_elast_model(
        year_n=year_n,
        start_year=int(first_budget_year),
        use_puf_not_cps=use_puf_not_cps,
        use_full_sample=True,
        user_mods=user_mods,
        gdp_elasticity=gdp_elasticity
    )

    results = {'elasticity_gdp': gdp_elast_i}
    # Add taxcalc version to results
    vinfo = taxcalc._version.get_versions()
    results['taxcalc_version'] = vinfo['version']
    # TODO: Make this the distributed app version, not the TC version
    results['dropq_version'] = vinfo['version']

    json_res = json.dumps(results)
    return json_res


# @celery_app.task(name='api.celery_tasks.ogusa_async')
# def ogusa_async(user_mods, ogusa_params, guid):
#     pass

@celery_app.task(name='api.celery_tasks.btax_async')
def btax_async(user_mods, start_year):
    print("user mods: ", user_mods)
    user_mods['start_year'] = start_year
    print("submitting btax data: ", user_mods)
    results = {}
    tables = json.loads(runner_json_tables(**user_mods))
    if tables.get("json_table"):
        results.update(tables["json_table"])
        if tables.get("dataframes"):
            dataframes = json.loads(tables["dataframes"])
            for x, y in list(dataframes.items()):
                dataframes[x] = json.loads(y)
            results["dataframes"] = dataframes
    else:
        results.update(tables)
    vinfo = taxcalc._version.get_versions()
    results['taxcalc_version'] = vinfo['version']
    # TODO: Make this the distributed app version, not the TC version
    results['dropq_version'] = vinfo['version']
    binfo = btax._version.get_versions()
    results['btax_version'] = binfo['version']
    json_res = json.dumps(results)
    return json_res
