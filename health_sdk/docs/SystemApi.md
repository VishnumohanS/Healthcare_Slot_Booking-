# health_sdk.SystemApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_scheduling_config**](SystemApi.md#get_scheduling_config) | **GET** /config/scheduling | Scheduling configuration
[**health_check**](SystemApi.md#health_check) | **GET** /health | Liveness and database check


# **get_scheduling_config**
> SchedulingConfig get_scheduling_config()

Scheduling configuration

Lets clients (e.g. the React app) derive slots with the same duration the server enforces.

### Example


```python
import health_sdk
from health_sdk.models.scheduling_config import SchedulingConfig
from health_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = health_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with health_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = health_sdk.SystemApi(api_client)

    try:
        # Scheduling configuration
        api_response = api_instance.get_scheduling_config()
        print("The response of SystemApi->get_scheduling_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->get_scheduling_config: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**SchedulingConfig**](SchedulingConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_check**
> HealthResponse health_check()

Liveness and database check

### Example


```python
import health_sdk
from health_sdk.models.health_response import HealthResponse
from health_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = health_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with health_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = health_sdk.SystemApi(api_client)

    try:
        # Liveness and database check
        api_response = api_instance.health_check()
        print("The response of SystemApi->health_check:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->health_check: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthResponse**](HealthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

