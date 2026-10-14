# SchedulingConfig


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**slot_duration_minutes** | **int** | Length of every appointment slot. | 

## Example

```python
from health_sdk.models.scheduling_config import SchedulingConfig

# TODO update the JSON string below
json = "{}"
# create an instance of SchedulingConfig from a JSON string
scheduling_config_instance = SchedulingConfig.from_json(json)
# print the JSON string representation of the object
print(SchedulingConfig.to_json())

# convert the object into a dict
scheduling_config_dict = scheduling_config_instance.to_dict()
# create an instance of SchedulingConfig from a dict
scheduling_config_from_dict = SchedulingConfig.from_dict(scheduling_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


