from utils.database import DatabaseClient
from utils.config import SENSUM_DB_DATABASE, SENSUM_DB_USER, SENSUM_DB_PASS, SENSUM_DB_HOST, SENSUM_DB_PORT


def get_db_client():
    return DatabaseClient(SENSUM_DB_DATABASE, SENSUM_DB_USER, SENSUM_DB_PASS, SENSUM_DB_HOST, SENSUM_DB_PORT)
