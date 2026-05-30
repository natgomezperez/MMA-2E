import pytest

import datetime as dt
from swarmpal.io import PalDataItem, create_paldata
from swarmpal_mma.pal_processes import MMA_SHA_2E

def get_paldatatime_vires_config(
    collection=None, start_time=None, end_time=None, model=None
):
    """Set of options which are passed through to viresclient
    For options, see https://swarmpal.readthedocs.io/en/latest/api/io.html#swarmpal.io.PalDataItem.from_vires
    """
    SAMPLING_STEP = "PT25S"
    VIRES_AUXILIARIES = ["MLT", "QDLat", "Dst", "QDBasis", "DipoleAxisVector"]
    return dict(
        collection=collection,
        measurements=["B_NEC"],
        models=[model],
        auxiliaries=VIRES_AUXILIARIES,
        sampling_step=SAMPLING_STEP,
        start_time=start_time,
        end_time=end_time,
        server_url="https://vires.services/ows",
        options=dict(asynchronous=False, show_progress=False),
    )

@pytest.fixture()
def vires_test_data():
    # Global parameters (should always remain the same)
    MODEL = "'Model' = 'CHAOS-Core' + 'CHAOS-Static'"
    MODEL_WITH_IONO = "'Model' = 'CHAOS-Core' + 'CHAOS-Static' + 'MIO_SHA_2C'"
    AVAILABLE_DATASETS = {"Swarm-A": "SW_OPER_MAGA_LR_1B", "Swarm-B": "SW_OPER_MAGB_LR_1B"}
    
    # Tunable parameters
    #PARAMS = {"LT_limit": 6, "min_gm_lat": 0, "max_gm_lat": 65}
    # TODO: See what should be included here from MMA_2E/utils/Config.py
    
    # Local settings (changes with each run) - these determine what external data is used
    START_TIME = dt.datetime(2024, 1, 1)
    END_TIME = dt.datetime(2024, 1, 7)
    time_delta = END_TIME - START_TIME
    three_hours_in_days = 3/24
    expected_num_time_bins = time_delta.days / three_hours_in_days
    # START_TIME = dt.datetime(2024, 10, 1)
    # END_TIME = dt.datetime(2024, 10, 2)
    SPACECRAFTS_TO_USE = ["Swarm-A", "Swarm-B"]  # corresponds to AVAILABLE_DATASETS 

    start_time = START_TIME
    end_time = END_TIME
    model = MODEL
    data_config = {
        spacecraft: get_paldatatime_vires_config(
            collection=AVAILABLE_DATASETS.get(spacecraft),
            start_time=start_time,
            end_time=end_time,
            model=model,
        )
        for spacecraft in SPACECRAFTS_TO_USE
    }
    return (
        expected_num_time_bins,
        create_paldata(
            **{
                label: PalDataItem.from_vires(**data_params)
                for label, data_params in data_config.items()
            }
        )
    )

def test_vires(vires_test_data):
    mma_process = MMA_SHA_2E()
    mma_process.set_config()
    expected_num_time_bins, data_in = vires_test_data
    data_out = mma_process(data_in)

    # Check that the output dataset exists
    assert '/MMA_SHA_2E' in data_out.groups

    # Check that all the output variables exist
    output_variables = list(data_out['MMA_SHA_2E'].keys())
    expected_variables = {'qs', 'gh', 'R2_e', 'R2_i', 'data_per_bin', 'Cm_cond_e', 'Cm_cond_i', 'MSER_i', 'MSER_e'}
    assert len(expected_variables) == len(output_variables)
    for expected_variable in expected_variables:
        assert expected_variable in output_variables

        # Check that each output variable has the expected shape
        if expected_variable in {'qs', 'gh'}:
            assert data_out['MMA_SHA_2E'][expected_variable].shape == (expected_num_time_bins, 15)
        else:
            assert data_out['MMA_SHA_2E'][expected_variable].shape == (expected_num_time_bins,)
