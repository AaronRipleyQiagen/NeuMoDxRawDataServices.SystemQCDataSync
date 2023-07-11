from .initialize import *
from .issues_defintion import *
from .pcrdata import *
from .active_issues import *
from .remediation_actions import *
from .cartridge_pictures import *
from .tadm_pictures import *
from .comments import *
from .misc_files import *
from .runset_review import *
from .sample_exclusion import *


def get_run_review_callbacks(app):
    get_initialization_callbacks(app)
    get_issue_definition_callbacks(app)
    get_pcr_data_callbacks(app)
    get_active_issue_callbacks(app)
    get_remediation_action_callbacks(app)
    get_cartridge_picture_callbacks(app)
    get_tadm_picture_callbacks(app)
    get_comment_callbacks(app)
    get_misc_file_callbacks(app)
    get_runset_review_callbacks(app)
    get_sample_exclusion_callbacks(app)
