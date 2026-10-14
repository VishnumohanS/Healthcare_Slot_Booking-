# AppointmentRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**doctor_id** | **int** |  | 
**patient_name** | **str** |  | 
**slot** | **datetime** |  | 
**status** | **str** |  | 

## Example

```python
from health_sdk.models.appointment_read import AppointmentRead

# TODO update the JSON string below
json = "{}"
# create an instance of AppointmentRead from a JSON string
appointment_read_instance = AppointmentRead.from_json(json)
# print the JSON string representation of the object
print(AppointmentRead.to_json())

# convert the object into a dict
appointment_read_dict = appointment_read_instance.to_dict()
# create an instance of AppointmentRead from a dict
appointment_read_from_dict = AppointmentRead.from_dict(appointment_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


