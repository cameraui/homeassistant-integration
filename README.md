# camera.ui for Home Assistant

Home Assistant integration for [camera.ui](https://github.com/cameraui/camera.ui): cameras, sensors and detection events as entities, the full camera.ui interface in the sidebar, and dashboard cards with the camera.ui player and event dialog.

## Installation

Requires [HACS](https://hacs.xyz).

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cameraui&repository=homeassistant-integration&category=integration)

1. In HACS, add this repository as a custom repository (⋮ menu → Custom repositories), category **Integration**. Or use the button above.
2. Install **camera.ui** and restart Home Assistant.
3. Add it under Settings → Devices & services → Add integration → camera.ui. camera.ui servers on the local network are discovered automatically; otherwise enter host and port.
4. Enter an API token. Create one in camera.ui under Settings → Account → API tokens, signed in as an admin: controlling sensors (locks, lights, PTZ and the rest) needs admin rights, a viewer token can only watch. The token stays on the Home Assistant server, the browser never sees it.

## What you get

### Entities

Each camera is a device with a camera entity (snapshot and RTSP stream) and, depending on the camera, entities for motion, object detection (person, vehicle, animal), faces, license plates and classifications. Standalone sensors from camera.ui (switches, lights, sirens, locks, covers, alarm panels) show up as their own entities and can be controlled from Home Assistant.

An update entity per server shows available camera.ui updates and installs them.

### Sidebar panel

The full camera.ui interface opens inside Home Assistant as a sidebar entry, for admins. It follows the Home Assistant theme and language and needs no extra login. Works remotely through Nabu Casa too; only WebRTC falls back to MSE when the camera.ui server is not reachable directly.

### Dashboard cards

The cards are the camera.ui components themselves, served by your camera.ui server (2.1.13 or newer) and registered automatically. They render inside the box you give them in the sections view and follow the Home Assistant theme.

**Camera** (`custom:cameraui-card`)

```yaml
type: custom:cameraui-card
entity: camera.front_door
mode: snapshot          # snapshot (default) or live
click: popup            # popup (camera.ui dialog with timeline), ha (open the sidebar panel on this camera), none
fit: contain            # contain (black bars) or cover (crop)
controls: true          # player controls, live mode
toolbar: true           # name, snapshot, detection toggle, shortcuts; live mode
detection_indicator: true
```

Snapshot mode is the tile from the camera.ui home view: current snapshot with its age, refreshed when the server pushes a new one. Live mode is the camera.ui player with WebRTC/MSE, H.265, two-way audio and PTZ.

**View** (`custom:cameraui-view-card`)

```yaml
type: custom:cameraui-view-card
view: Living room        # a camview view from camera.ui, the editor lists them
rearrange: true          # show the rearrange button inside the widget
```

A saved camera.ui camview view as a widget: the same camera grid with drag and drop and card sizes. Rearranging inside the widget is shared with the sidebar panel. With several camera.ui servers the editor also offers a server picker.

**Events** (`custom:cameraui-events-card`)

```yaml
type: custom:cameraui-events-card
entities:               # optional, default: all camera.ui cameras
  - camera.front_door
```

The recent-events strip from the camera.ui home view. A click opens the camera.ui dialog at that event, with the timeline.

Card access is limited to Home Assistant administrators by default. Open Settings → Devices & services → camera.ui → Configure to allow all Home Assistant users. Administrators use the integration's API token. For everyone else you can store a viewer token there (create a user with the viewer role in camera.ui and an API token for it); without one, other users fall back to the integration token and its rights.

Several camera.ui servers can live on one dashboard, each card follows the server of its entity.

If the camera.ui server is unreachable, the cards keep working from a local copy and show the camera.ui offline state until the server is back.

### Media browser

Recorded events with a detection (person, vehicle, face, ...; motion alone does not count) show up in the Home Assistant media browser under **camera.ui**: one folder per camera plus "All cameras", then the days with recordings, then the events of that day with their thumbnail. A click plays the clip in the Home Assistant player, and every entry can be sent to a media player:

```yaml
action: media_player.play_media
target:
  entity_id: media_player.living_room_tv
data:
  media_content_type: video
  media_content_id: media-source://cameraui/<entry id>/<camera id>/2026-08-30/<event id>
```

Clips come from the sub stream by default, which keeps them small over remote connections; switch to the main stream under Settings → Devices & services → camera.ui → Configure. They are served as recorded, so H.265 recordings play only where the player can decode them. Needs the NVR plugin; the folder says so when it is missing.

### PTZ action

Moving a camera by hand happens in the card. For automations and scripts there is the `cameraui.ptz` action: target a camera entity and pass `action` (`continuous`, `stop`, `move`, `absolute`, `preset`, `home`) with `pan`, `tilt`, `zoom` (-1 to 1) or `preset`. For example, point the camera at the gate whenever the gate opens:

```yaml
action: cameraui.ptz
target:
  entity_id: camera.front_door
data:
  action: preset
  preset: Gate
```

## Automations

Motion and the camera's sensors are entities you can trigger on directly. Detection events also ride the Home Assistant event bus.

### Object sensors

Cameras with object detection get binary sensors for person, vehicle and animal. Each is on while that object is in view and turns off when the detection ends.

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
