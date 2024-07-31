import json
import typing


def new_sensor(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    """
    Creates sensors in Home Assistant based on FIMP services
    """

    if service_name == "battery":
        return battery(**locals())

    elif service_name == "sensor_lumin":
        return sensor_lumin(**locals())

    elif service_name == "sensor_presence":
        return sensor_presence(**locals())

    elif service_name == "sensor_temp":
        return sensor_temp(**locals())

    elif service_name == "sensor_humid":
        return sensor_humid(**locals())

    else:
        print("Failed to create sensor")
        return


def battery(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    unit_of_measurement = "%"
    battery_component = {
        "name": "(batteri)",
        "device_class": "battery",
        # "entity_category": "diagnostic",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(0) }}"
    }

    # Merge default_component with battery_component
    merged_component = {**default_component, **battery_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="batteryPercentage",
        device=device,
        props={},
        serv="battery",
        typ="evt.lvl.report",
        val_t="int"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_lumin(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    unit_of_measurement = "lx"
    lumin_component = {
        "name": "(belysningsstyrke)",
        "device_class": "illuminance",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(0) }}"
    }

    # Merge default_component with lumin_component
    merged_component = {**default_component, **lumin_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="illuminance",
        device=device,
        props={"unit": "Lux"},
        serv="sensor_lumin",
        typ="evt.sensor.report",
        val_t="float"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_presence(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
    ):
    presence_component = {
        "name": "(bevegelse)",
        "device_class": "motion",
        "payload_off": False,
        "payload_on": True,
        "value_template": "{{ value_json.val }}",
    }

    # Merge default_component with presence_component
    merged_component = {**default_component, **presence_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/binary_sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="presence",
        device=device,
        props={},
        serv="sensor_presence",
        typ="evt.presence.report",
        val_t="bool"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_temp(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
    ):

    unit_of_measurement = "°C"
    temp_component = {
        "name": "(temperatur)",
        "device_class": "temperature",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(1) }}",
        # "json_attributes_topic": f"homeassistant/sensor/{identifier}/attributes",
        # "json_attributes_template": "{{ value_json | tojson }}",
        # "force_update": True
    }

    # Merge default_component with temp_component
    merged_component = {**default_component, **temp_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # print(device)
    # # Add attribute for main thing_role if present (used for current_temp in thermostats)
    # if device["services"]["sensor_temp"]["props"].get("thing_role") and \
    #             device["services"]["sensor_temp"]["props"]["thing_role"] == "main":
    #     # ! DEBUG
    #     print("Found it")
    #     attribute = {
    #         "thing_role_main":{
    #         "address": default_component["device"]["identifiers"],
    #         "topic": f"pt:j1/mt:evt{device['services']['sensor_temp']['addr']}"
    #         }
    #     }
    #     attribute_json = json.dumps(attribute)
    #     mqtt.publish(f"homeassistant/sensor/{identifier}/attributes", attribute_json)

    # Queue statuses
    status = None
    payload = queue_status(
        param="temperature",
        device=device,
        props={"unit": "C"},
        serv="sensor_temp",
        typ="evt.sensor.report",
        val_t="float"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_humid(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
    ):
    unit_of_measurement = "%"
    humid_component = {
        "name": "(luftfuktighet)",
        "device_class": "humidity",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(0) }}"
    }

    # Merge default_compontent with humid_component
    merged_component = {**default_component, **humid_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="humidity",
        device=device,
        props={"unit": unit_of_measurement},
        serv="sensor_humid",
        typ="evt.sensor.report",
        val_t="string"
    )
    if payload:
        status = (state_topic, payload)
    return status


def queue_status(param, device, props, serv, typ, val_t):
    payload = None
    if device.get("param") and device["param"].get(f"{param}"):
        value = device["param"][f"{param}"]
        data = {
            "props": props,
            "serv": f"{serv}",
            "type": f"{typ}",
            "val": value,
            "val_t": val_t,
            "src": "homeassistant"
        }

        payload = json.dumps(data)
    return payload
