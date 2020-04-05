import sys
import time
from concurrent.futures import ThreadPoolExecutor

from config import conf

from server.controllers import user_info_pool, satellite_pool, satellite_database
from server.models.objects import *
from server.models.status_code import *
from utilities.utils import Utils
from utilities.concurrent_task import ConcurrentTask, ConcurrentTaskPool
from server.services.satellite_location_service import fetch_satellite_info


