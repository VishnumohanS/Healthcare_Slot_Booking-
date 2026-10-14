# health_sdk.AppointmentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**book_appointment**](AppointmentsApi.md#book_appointment) | **POST** /appointments/ | Book an appointment
[**cancel_appointment**](AppointmentsApi.md#cancel_appointment) | **DELETE** /appointments/{appointment_id} | Cancel an appointment
[**get_appointment**](AppointmentsApi.md#get_appointment) | **GET** /appointments/{appointment_id} | Get an appointment by ID
[**list_appointments**](AppointmentsApi.md#list_appointments) | **GET** /appointments/ | List appointments


# **book_appointment**
> AppointmentRead book_appointment(appointment_create)

Book an appointment

Books one fixed-length slot (default 30 minutes) with a doctor.

* `404` - the doctor does not exist
* `409` - the doctor already has an active appointment at that slot
* `422` - malformed input, slot not on a boundary, or outside the doctor's working hours

### Example


```python
import health_sdk
from health_sdk.models.appointment_create import AppointmentCreate
from health_sdk.models.appointment_read import AppointmentRead
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
    api_instance = health_sdk.AppointmentsApi(api_client)
    appointment_create = health_sdk.AppointmentCreate() # AppointmentCreate | 

    try:
        # Book an appointment
        api_response = api_instance.book_appointment(appointment_create)
        print("The response of AppointmentsApi->book_appointment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppointmentsApi->book_appointment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **appointment_create** | [**AppointmentCreate**](AppointmentCreate.md)|  | 

### Return type

[**AppointmentRead**](AppointmentRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**404** | Doctor not found |  -  |
**409** | Slot already booked |  -  |
**422** | Validation error / outside working hours |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_appointment**
> AppointmentRead cancel_appointment(appointment_id)

Cancel an appointment

Marks the appointment `cancelled` and frees the slot. Returns the cancelled appointment.

### Example


```python
import health_sdk
from health_sdk.models.appointment_read import AppointmentRead
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
    api_instance = health_sdk.AppointmentsApi(api_client)
    appointment_id = 56 # int | 

    try:
        # Cancel an appointment
        api_response = api_instance.cancel_appointment(appointment_id)
        print("The response of AppointmentsApi->cancel_appointment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppointmentsApi->cancel_appointment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **appointment_id** | **int**|  | 

### Return type

[**AppointmentRead**](AppointmentRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Appointment not found |  -  |
**409** | Appointment already cancelled |  -  |
**422** | Invalid appointment ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_appointment**
> AppointmentRead get_appointment(appointment_id)

Get an appointment by ID

### Example


```python
import health_sdk
from health_sdk.models.appointment_read import AppointmentRead
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
    api_instance = health_sdk.AppointmentsApi(api_client)
    appointment_id = 56 # int | 

    try:
        # Get an appointment by ID
        api_response = api_instance.get_appointment(appointment_id)
        print("The response of AppointmentsApi->get_appointment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppointmentsApi->get_appointment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **appointment_id** | **int**|  | 

### Return type

[**AppointmentRead**](AppointmentRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Appointment not found |  -  |
**422** | Invalid appointment ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_appointments**
> List[AppointmentRead] list_appointments(doctor_id=doctor_id, var_date=var_date, include_cancelled=include_cancelled)

List appointments

Active appointments ordered by time. Filter by doctor and/or calendar date (`YYYY-MM-DD`).

### Example


```python
import health_sdk
from health_sdk.models.appointment_read import AppointmentRead
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
    api_instance = health_sdk.AppointmentsApi(api_client)
    doctor_id = 56 # int | Only this doctor's appointments (optional)
    var_date = '2013-10-20' # date | Only appointments on this date (YYYY-MM-DD) (optional)
    include_cancelled = False # bool | Also return cancelled appointments (optional) (default to False)

    try:
        # List appointments
        api_response = api_instance.list_appointments(doctor_id=doctor_id, var_date=var_date, include_cancelled=include_cancelled)
        print("The response of AppointmentsApi->list_appointments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppointmentsApi->list_appointments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **doctor_id** | **int**| Only this doctor&#39;s appointments | [optional] 
 **var_date** | **date**| Only appointments on this date (YYYY-MM-DD) | [optional] 
 **include_cancelled** | **bool**| Also return cancelled appointments | [optional] [default to False]

### Return type

[**List[AppointmentRead]**](AppointmentRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid filter value |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

