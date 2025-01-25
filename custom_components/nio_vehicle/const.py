"""Constants for the NIO Vehicle integration."""
from datetime import timedelta

DOMAIN = "nio_vehicle"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

# Configuration
CONF_VEHICLE_ID = "vehicle_id"
CONF_ACCESS_TOKEN = "access_token"
CONF_APP_VERSION = "app_version"
CONF_DEVICE_ID = "device_id"
CONF_SIGN = "sign"
CONF_TIMESTAMP = "timestamp"

# API Constants
API_BASE_URL = "https://icar.nio.com/api/2/rvs/vehicle"
API_HEADERS = {
    "Host": "icar.nio.com",
    "Connection": "keep-alive",
    "Accept": "application/json,text/json,text/plain",
    "User-Agent": "NextevCar/5.36.1 (com.do1.WeiLaiApp; build:2291; iOS 18.3.0) Alamofire/5.9.1",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
}

# Device Info
MANUFACTURER = "NIO"
MODEL = "Electric Vehicle"

# Default API Parameters
DEFAULT_APP_ID = "10002"
DEFAULT_APP_VERSION = "5.36.1"
DEFAULT_LANGUAGE = "zh-CN"
DEFAULT_REGION = "cn"
