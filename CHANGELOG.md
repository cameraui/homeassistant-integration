# Changelog

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
