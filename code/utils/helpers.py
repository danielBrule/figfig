import requests
from requests.exceptions import RequestException
from contextlib import closing
import time
import urllib3

from utils.log import logger


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Mobile Safari/537.36'
}



def is_good_response(resp):
    return resp.status_code == 200

def simple_get(url: str,
               user_agent: {} = None,
               sleep_time: int = 1,
               stop_if_url_different: bool = False,
               verify=True,
               proxy=None,
               timeout=5):
    time.sleep(sleep_time)
    try:
        with closing(requests.get(url, stream=True, headers=user_agent, verify=verify,
                                  proxies=proxy, auth=None, timeout=timeout)) as resp:
            if is_good_response(resp):
                if stop_if_url_different and resp.url != url:
                    return None
                return resp.content
            else:
                return None

    except RequestException as e:
        logger.error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def get_url_redirection(url: str,
                        user_agent: {} = None,
                        sleep_time: int = 1,
                        verify=True):
    time.sleep(sleep_time)

    try:
        with closing(requests.get(url, stream=True, headers=user_agent, verify=verify)) as resp:
            if is_good_response(resp):
                return resp.url
            else:
                return None
    except RequestException as e:
        logger.error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def simple_requests_json(url: str, user_agent: {}, json: {} = {}, data: {} = {},
                         sleep_time: int = 1, method: str = "POST", verify=False):
    time.sleep(sleep_time)
    header = user_agent
    try:
        with closing(requests.request(method=method, url=url, json=json, stream=True, headers=header,
                                      data=data, verify=verify)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        logger.error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
