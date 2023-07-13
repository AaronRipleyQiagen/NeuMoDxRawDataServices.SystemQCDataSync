from .dependencies import *

manage_runset_sample_exclusions = ManageRunsetSampleExclusions(
    aio_id="run-review-manage-runset-sample-exclusions"
)

excluded_samples_content = dbc.Card(
    dbc.CardBody([manage_runset_sample_exclusions]),
    className="mt-3",
)
