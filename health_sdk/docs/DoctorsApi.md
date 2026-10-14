# health_sdk.DoctorsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_doctor**](DoctorsApi.md#create_doctor) | **POST** /doctors/ | Create a doctor
[**get_doctor**](DoctorsApi.md#get_doctor) | **GET** /doctors/{doctor_id} | Get a doctor by ID
[**list_doctors**](DoctorsApi.md#list_doctors) | **GET** /doctors/ | List all doctors


# **create_doctor**
> DoctorRead create_doctor(doctor_create)

Create a doctor

Registers a doctor with working hours. `end_hour` must be later than `start_hour`.

### Example


```python
import health_sdk
from health_sdk.models.doctor_create import DoctorCreate
from health_sdk.models.doctor_read import DoctorRead
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
    api_instance = health_sdk.DoctorsApi(api_client)
    doctor_create = health_sdk.DoctorCreate() # DoctorCreate | 

    try:
        # Create a doctor
        api_response = api_instance.create_doctor(doctor_create)
        print("The response of DoctorsApi->create_doctor:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DoctorsApi->create_doctor: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **doctor_create** | [**DoctorCreate**](DoctorCreate.md)|  | 

### Return type

[**DoctorRead**](DoctorRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_doctor**
> DoctorRead get_doctor(doctor_id)

Get a doctor by ID

### Example


```python
import health_sdk
from health_sdk.models.doctor_read import DoctorRead
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
    api_instance = health_sdk.DoctorsApi(api_client)
    doctor_id = 56 # int | Doctor ID

    try:
        # Get a doctor by ID
        api_response = api_instance.get_doctor(doctor_id)
        print("The response of DoctorsApi->get_doctor:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DoctorsApi->get_doctor: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **doctor_id** | **int**| Doctor ID | 

### Return type

[**DoctorRead**](DoctorRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Doctor not found |  -  |
**422** | Invalid doctor ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_doctors**
> List[DoctorRead] list_doctors()

List all doctors

### Example


```python
import health_sdk
from health_sdk.models.doctor_read import DoctorRead
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
    api_instance = health_sdk.DoctorsApi(api_client)

    try:
        # List all doctors
        api_response = api_instance.list_doctors()
        print("The response of DoctorsApi->list_doctors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DoctorsApi->list_doctors: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[DoctorRead]**](DoctorRead.md)

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

