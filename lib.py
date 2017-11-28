import logging
import requests
import sys
import time
from datetime import datetime


MAX_RETRIES = 4
DEFAULT_LOG_LEVEL=logging.WARNING  # change to DEBUG for more detail


def get_default_logger():
  logging.basicConfig(level=DEFAULT_LOG_LEVEL)
  logger = logging.getLogger(__name__)
  stderr_handler = logging.StreamHandler()
  logger.addHandler(stderr_handler)
  return logger


def get_access_token(api_host, user_email, user_password, logger=None):
  retry_count = 0
  if not logger:
    logger = get_default_logger()
  while retry_count < MAX_RETRIES:
    login = requests.post('https://' + api_host + '/login',
                          data = {"email": user_email, "password": user_password})
    if login.status_code == 200:
      return login.json()['data']['accessToken']
    else:
      logger.warning("Error in get_access_token: {}\n".format(login))
    retry_count += 1
  raise Exception("Giving up on get_access_token after {0} tries.".format(retry_count))


def get_data(url, headers, params=None, logger=None):
  base_log_record = dict(route=url, params=params)
  retry_count = 0
  if not logger:
    logger = get_default_logger()
  while retry_count < MAX_RETRIES:
    start_time = time.time()
    data = requests.get(url, params=params, headers=headers, timeout=None)
    elapsed_time = time.time() - start_time
    log_record = dict(base_log_record)
    log_record['elapsed_time_in_ms'] = 1000 * elapsed_time
    log_record['retry_count'] = retry_count
    log_record['status_code'] = data.status_code
    if data.status_code == 200:
      logger.debug(log_record)
      return data
    retry_count += 1
    log_record['tag'] = 'failed_gro_api_request'
    log_record['message'] = data.text  
    if retry_count < MAX_RETRIES:
      logger.warning(log_record)
    else:
      logger.error(log_record)
  raise Exception(data.text)


def get_available(access_token, api_host, entity_type):
  """Given an entity_type, which is one of 'items', 'metrics',
    'regions', returns a JSON dict with the list of available entities
    of the given type.
    """
  url = '/'.join(['https:', '', api_host, 'v2/available', entity_type])
  headers = {'authorization': 'Bearer ' + access_token}
  resp = get_data(url, headers)
  return resp.json()


def list_available(access_token, api_host, selected_entities):
  """List available entities given some selected entities. Given a dict
    of selected entity ids of the form { <entity_type>: <entity_id>,
    ...}, returns a list of dictionaries representing available {
    item_id: ..., metric_id: ... , region_id: ... ,} for which data
    series are available which satisfy the input selection.
    """
  url = '/'.join(['https:', '', api_host, 'v2/entities/list'])
  headers = {'authorization': 'Bearer ' + access_token}
  resp = get_data(url, headers, selected_entities)
  try:
    return resp.json()['data']
  except KeyError as e:
    raise Exception(resp.text)


def lookup(access_token, api_host, entity_type, entity_id):
  """Given an entity_type, which is one of 'items', 'metrics',
    'regions', 'units', or 'sources', returns a JSON dict with the
    list of available entities of the given type.
  """
  url = '/'.join(['https:', '', api_host, 'v2', entity_type, str(entity_id)])
  headers = {'authorization': 'Bearer ' + access_token}
  resp = get_data(url, headers)
  try:
    return resp.json()['data']
  except KeyError as e:
    raise Exception(resp.text)


def get_data_series(access_token, api_host, item_id, metric_id, region_id):
  """Get data series records for the given selected entities."""
  url = '/'.join(['https:', '', api_host, 'v2/data_series/list'])
  headers = {'authorization': 'Bearer ' + access_token}
  params = { }
  if region_id:
    params['regionId'] = region_id
  if item_id:
    params['itemId'] = item_id
  if metric_id:
    params['metricId'] =  metric_id
  resp = get_data(url, headers, params)
  try:
    return resp.json()['data']
  except KeyError as e:
    raise Exception(resp.text)


def get_data_points(access_token, api_host,
                    item_id, metric_id, region_id, frequency_id, source_id):
  url = '/'.join(['https:', '', api_host, 'v2/data'])
  headers = {'authorization': 'Bearer ' + access_token }
  params = {'regionId': region_id, 'itemId': item_id, 'metricId': metric_id,
            'frequencyId': frequency_id, 'sourceId': source_id}
  resp = get_data(url, headers, params)
  try:
    return resp.json()['data']
  except KeyError as e:
    raise Exception(resp.text)


def search(access_token, api_host,
           entity_type, search_terms):
  """Given an entity_type, which is one of 'items', 'metrics',
  'regions', performs a search for the given terms.
  """
  url = '/'.join(['https:', '', api_host, 'v2/search', entity_type])
  headers = {'authorization': 'Bearer ' + access_token }
  resp = get_data(url, headers, {'q': search_terms})
  return resp.json()
