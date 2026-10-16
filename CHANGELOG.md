# Changelog

## 0.4.4

**Needs Home Assistant 2026.3 or newer.** Update Home Assistant first, HACS does not offer this version to older installations.

- **The media browser lists every recording of a day.** A day that started during a running event stopped after the first page and listed that event twice. Needs NVR 1.5.1.
- **Detections no longer stay on after the connection to camera.ui drops.** Motion and object sensors turn off and `cameraui_event` fires `end`, so automations waiting for it no longer hang. With camera.ui 2.3.1, detections that are still running stay on and only those that ended during the outage end.
- **Two camera.ui servers in one Home Assistant no longer mix up their entities.** Connection changes and new sensors of one server reached the entities of the other.
- **Reloading or disabling the integration finishes promptly.** It no longer leaves a connection to camera.ui running, and an unreachable server no longer holds the reload for half a minute.
- **The media browser and the dashboard cards give up sooner on an unreachable camera.ui.** Cards fall back to their local copy instead of waiting five minutes.
- **Live view in Home Assistant reacts correctly when camera.ui refuses or drops the stream**, instead of treating every end as a normal close.
- **The integration token stays out of the Home Assistant log.**
- **Clips in the media browser start sooner.** A clip that is already exported or exporting plays without asking camera.ui again, seeking no longer looks up the whole day each time, and thumbnails load only the picture they show.
- **Several people can watch the same clip.** Seeking in one no longer stops the export for everyone, and a clip being exported no longer sits in Home Assistant's memory.
- **On days with more than 600 events, the older clips play too.**
- **Live video through Home Assistant needs less CPU.**
- **The camera.ui panel and the dashboard cards load faster on slow connections.** Replies from camera.ui reach the browser compressed. Needs camera.ui 2.3.1.
- **A server update that camera.ui refuses shows the reason**, for example a worker that would no longer connect to the new version, instead of only an error code.

## 0.4.3

- Dependency updates.

## 0.4.2

- **Update entities follow the server right away.** A plugin or server updated from the camera.ui interface no longer stays listed as pending in Home Assistant for hours, and the install button no longer reinstalls the version that is already running. The server pushes the change over the event socket, the poll behind it runs hourly instead of every six hours.

## 0.4.1

- **Backup before a server update.** The install dialog of the server update entity offers "Create backup before updating"; the backup lands in the camera.ui scheduled-backup folder and a failed backup stops the update. The release notes now say that the update replaces the camera.ui server itself, not just the integration.
- **Updates from Home Assistant can be turned off.** A new option in the integration settings keeps the update entities visible without an install button.
- **The panel's own top bar is gone.** The Home Assistant menu button moves into the camera.ui app: top left on phones, and a "Home Assistant" entry at the bottom of the camera.ui sidebar on desktop when the Home Assistant sidebar is hidden. Needs camera.ui 2.1.16.
- **Status bar and home indicator are handled by camera.ui.** The app's bars now run edge to edge in the Home Assistant app, in camera.ui's colors, without doubled spacing or a band in the wrong theme color.

## 0.4.0

- **camera.ui cards for dashboards.** A camera card with the snapshot tile or the full live player, a camview view as a widget with drag and drop, and the recent events strip. A click opens the camera.ui dialog with the timeline. The cards are served by the camera.ui server (2.1.13 or newer) and keep working from a local copy while it is down. Access is admins only by default; the integration options open it to all users, with an optional viewer token.
- **Recordings in the Home Assistant media browser.** Events with a recording appear under camera.ui, by camera and day, with thumbnails. A click plays the clip right away, and every entry can be sent to a media player. Clips use the sub stream by default, switchable to the main stream in the options.
- An outdated camera.ui server now shows a repair issue naming the minimum version instead of silently missing features.
- Notification pictures sent through the camera.ui Home Assistant plugin load via Home Assistant now, so they show on the phone away from home too. Needs the plugin 1.0.12.
- **The old built-in cards are replaced.** `custom:cameraui-card` keeps its name and switches to the new card by itself; its old options (`title`, `source`, `mode`, `autostart`, `snapshot_interval`) no longer apply, pick the new ones in the card editor. `custom:cameraui-grid-card` is gone: dashboards using it show "Custom element doesn't exist" until you rebuild them with the new `custom:cameraui-view-card` or a sections view.
