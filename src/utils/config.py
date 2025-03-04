import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


DEBUG = os.getenv('DEBUG', 'False') in ['True', 'true']
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')

# Sensum Database
SENSUM_DB_USER = os.environ['SENSUM_DB_USER']
SENSUM_DB_PASS = os.environ['SENSUM_DB_PASS']
SENSUM_DB_HOST = os.environ['SENSUM_DB_HOST']
SENSUM_DB_DATABASE = os.environ['SENSUM_DB_DATABASE']
SENSUM_DB_PORT = os.environ['SENSUM_DB_PORT']
