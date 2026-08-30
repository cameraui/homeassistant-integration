# Changelog

## 0.4.0

- **camera.ui cards for dashboards.** A camera card with the snapshot tile or the full live player, a camview view as a widget with drag and drop, and the recent events strip. A click opens the camera.ui dialog with the timeline. The cards are served by the camera.ui server (2.1.13 or newer) and keep working from a local copy while it is down. Access is admins only by default; the integration options open it to all users, with an optional viewer token.
- **Recordings in the Home Assistant media browser.** Events with a recording appear under camera.ui, by camera and day, with thumbnails. A click plays the clip right away, and every entry can be sent to a media player. Clips use the sub stream by default, switchable to the main stream in the options.
- An outdated camera.ui server now shows a repair issue naming the minimum version instead of silently missing features.
- **The old built-in cards are replaced.** `custom:cameraui-card` keeps its name and switches to the new card by itself; its old options (`title`, `source`, `mode`, `autostart`, `snapshot_interval`) no longer apply, pick the new ones in the card editor. `custom:cameraui-grid-card` is gone: dashboards using it show "Custom element doesn't exist" until you rebuild them with the new `custom:cameraui-view-card` or a sections view.
