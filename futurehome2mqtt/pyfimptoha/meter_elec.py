import json


def new_sensor(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    """
    Creates meter_elec sensors in Home Assistant based on FIMP services
    """

    sup_units: list = device["services"][service_name]["props"]["sup_units"]
    identifier_for_unit = identifier
    statuses = []

    for unit in sup_units:
        identifier = f"{identifier_for_unit}_{unit}"

        if unit == "kWh":
            unit_of_measurement = "kWh"
            kwh_component = {
                "name": "(energi)",
                "device_class": "energy",
                "state_class": "total_increasing",
                "unit_of_measurement": unit_of_measurement,
                "value_template": f"""
                    {{% if value_json.props.unit == "{unit_of_measurement}" %}}
                        {{{{ value_json.val | round(1) }}}}
                    {{% endif %}}
                """,
                "object_id": identifier,
                "unique_id": identifier
            }

            # Merge default_component with elec_component
            merged_component = {**default_component, **kwh_component}

            payload = json.dumps(merged_component)
            mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

            # Queue statuses
            payload = queue_status(
                param="energy",
                device=device,
                props={"unit": "kWh"},
                serv="meter_elec",
                typ="evt.meter.report",
                val_t="float"
            )
            if payload:
                statuses.append((state_topic, payload))

        elif unit == "W":
            unit_of_measurement = "W"
            w_component = {
                "name": "(forbruk)",
                "device_class": "power",
                "state_class": "measurement",
                "unit_of_measurement": unit_of_measurement,
                "value_template": f"""
                    {{% if value_json.props.unit == "{unit_of_measurement}" %}}
                        {{{{ value_json.val | round(1) }}}}
                    {{% endif %}}
                """,
                "object_id": identifier,
                "unique_id": identifier
            }

            # Merge default_component with w_component
            merged_component = {**default_component, **w_component}

            payload = json.dumps(merged_component)
            mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

            # Queue statuses
            payload = queue_status(
                param="wattage",
                device=device,
                props={"unit": "W"},
                serv="meter_elec",
                typ="evt.meter.report",
                val_t="float"
            )
            if payload:
                statuses.append((state_topic, payload))

        elif unit == "V":
            unit_of_measurement = "V"
            v_component = {
                "name": "(volt)",
                "device_class": "voltage",
                "state_class": "measurement",
                "unit_of_measurement": unit_of_measurement,
                "value_template": f"""
                    {{% if value_json.props.unit == "{unit_of_measurement}" %}}
                        {{{{ value_json.val | round(0) }}}}
                    {{% endif %}}
                """,
                "object_id": identifier,
                "unique_id": identifier
            }

            # Merge default_component with v_component
            merged_component = {**default_component, **v_component}

            payload = json.dumps(merged_component)
            mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

        # Queue statuses
        # TODO: Status will be 'unknown' until first report.

        elif unit == "A":
            unit_of_measurement = "A"
            a_component = {
                "name": "(amp)",
                "device_class": "current",
                "state_class": "measurement",
                "unit_of_measurement": unit_of_measurement,
                "value_template": f"""
                    {{% if value_json.props.unit == "{unit_of_measurement}" %}}
                        {{{{ value_json.val | round(0) }}}}
                    {{% endif %}}
                """,
                "object_id": identifier,
                "unique_id": identifier
            }

            # Merge default_component with a_component
            merged_component = {**default_component, **a_component}

            payload = json.dumps(merged_component)
            mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

        # Queue statuses
        # TODO: Status will be 'unknown' until first report.

    return statuses


def queue_status(param, device, props, serv, typ, val_t):
    payload = None
    if device.get("param") and device["param"].get(f"{param}"):
        value = device["param"][f"{param}"]
        data = {
            "props": props,
            "serv": f"{serv}",
            "type": f"{typ}",
            "val": float(value),
            "val_t": val_t,
            "src": "homeassistant"
        }

        payload = json.dumps(data)
    return payload
