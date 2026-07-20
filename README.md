# camera.ui for Home Assistant

Home Assistant integration for [camera.ui](https://github.com/cameraui/camera.ui): cameras, motion and detection sensors, live streams and the camera.ui interface, directly in Home Assistant.

## Installation

Requires [HACS](https://hacs.xyz).

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cameraui&repository=hass-integration&category=integration)

1. In HACS, add this repository as a custom repository (⋮ menu → Custom repositories), category **Integration**. Or use the button above.
2. Install **camera.ui** and restart Home Assistant.
3. Add it under Settings → Devices & services → Add integration → camera.ui, and point it at your camera.ui instance.

## Automations

Each camera is a Home Assistant device. Motion and the camera's sensors show up as entities you can trigger on directly. Detection events also ride the HA event bus.

### Object sensors

Cameras with object detection get four binary sensors: person, vehicle, animal, package. Each is on while that object is in view and turns off when the detection ends.

```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.front_door_person
    to: 'on'
action:
  - service: notify.mobile_app_phone
    data:
      message: Someone is at the front door
```

### Device triggers

In the automation editor every camera offers three triggers: Detection started, Detection ended, Object recognized. "Object recognized" fires when a face, license plate or classifier result is identified during an event.

### The cameraui_event bus event

One event fires for every detection, so you can match on the details. Fields:

- `camera_id`, `camera_name`
- `state`: `start`, `object` (a new object class appeared), `recognized` (a face/plate/classifier result), `end`
- `detection_types`: which detectors fired (motion, object, face, licensePlate, classifier)
- `labels`: object labels seen so far (person, vehicle, ...)
- `faces`, `plates`, `classifications`: recognized values
- `attributes`: the raw list with per-item confidence
- `event_id`

Values like plates and faces are lists, so match them with a template condition:

```yaml
trigger:
  - platform: event
    event_type: cameraui_event
condition:
  - "{{ 'ABC-123' in trigger.event.data.plates }}"
action:
  - service: cover.open_cover
    target:
      entity_id: cover.gate
```

---

_Part of the camera.ui ecosystem - A comprehensive camera management solution._
