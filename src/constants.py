from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_0_URL = 'https://peps.python.org/'
OUTPUT_FORMAT_PRETTY_TABLE = 'pretty'
OUTPUT_FORMAT_FILE = 'file'
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'
LOGGING_DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOGS_DIR_NAME = 'logs'
BASE_DIR = Path(__file__).parent
FILE_OUTPUT_DT_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': 'Deferred',
    'F': 'Final',
    'P': 'Provisional',
    'R': 'Rejected',
    'S': 'Superseded',
    'W': 'Withdrawn',
    'empty': ('Draft', 'Active'),
}
