# DoctorRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**specialization** | **str** |  | 
**start_hour** | **int** |  | 
**end_hour** | **int** |  | 

## Example

```python
from health_sdk.models.doctor_read import DoctorRead

# TODO update the JSON string below
json = "{}"
# create an instance of DoctorRead from a JSON string
doctor_read_instance = DoctorRead.from_json(json)
# print the JSON string representation of the object
print(DoctorRead.to_json())

# convert the object into a dict
doctor_read_dict = doctor_read_instance.to_dict()
# create an instance of DoctorRead from a dict
doctor_read_from_dict = DoctorRead.from_dict(doctor_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


