import type { ConnectionTarget, TransportSpec, TransportStatus, Unsubscribe } from '@camera.ui/transport';
import type { WsEvent, WsEventHandler, WsHandle, WsHandleSpec, WsTransport } from '@camera.ui/transport/transports/ws';
import type { HomeAssistant } from './types.js';

const TARGET_SEGMENTS: Record<string, string> = {
  '/api/go2rtc': 'go2rtc',
  '/api/proxy': 'rpc',
};

const WS_CLOSE_CONNECT_FAILED = 4000;
const WS_CLOSE_DISPOSED = 4002;

export interface HaTransportHost {
  getHass: () => HomeAssistant | undefined;
  getEntryId: () => string | undefined;
}

interface InternalHandle {
  readonly spec: WsHandleSpec;
  readonly listeners: { [E in WsEvent]: Set<WsEventHandler<E>> };
  ws: WebSocket | null;
  url: string | null;
  disposed: boolean;
}

export function createHaWsTransport(host: HaTransportHost): WsTransport {
  const spec: TransportSpec = { id: 'ha-ws', kind: 'per-resource', phaseGating: false };
  const handles = new Set<InternalHandle>();
  let disposed = false;

  function emitClose(handle: InternalHandle, code: number, reason: string): void {
    for (const fn of [...handle.listeners.close]) fn({ code, reason, wasClean: false });
  }

  async function connect(handle: InternalHandle): Promise<void> {
    try {
      const hass = host.getHass();
      const entryId = host.getEntryId();
      const segment = TARGET_SEGMENTS[handle.spec.path];
      if (!hass || !entryId || !segment) {
        throw new Error(`cannot resolve proxy target for ${handle.spec.path}`);
      }

      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(handle.spec.query ?? {})) {
        if (value !== undefined && value !== null && value !== '') params.set(key, value);
      }
      const query = params.toString();
      const path = `/api/cameraui/ws/${entryId}/${segment}${query ? `?${query}` : ''}`;

      const signed = await hass.callWS<{ path: string }>({ type: 'auth/sign_path', path });
      if (handle.disposed) return;

      const url = 'ws' + hass.hassUrl(signed.path).substring(4);
      const ws = new WebSocket(url, handle.spec.protocols as string | string[] | undefined);
      if (handle.spec.binaryType) ws.binaryType = handle.spec.binaryType;
      handle.ws = ws;
      handle.url = url;

      ws.onopen = () => {
        if (handle.disposed || handle.ws !== ws) return;
        for (const fn of [...handle.listeners.open]) fn();
      };
      ws.onmessage = (event) => {
        if (handle.disposed || handle.ws !== ws) return;
        for (const fn of [...handle.listeners.message]) fn(event);
      };
      ws.onerror = (event) => {
        if (handle.disposed || handle.ws !== ws) return;
        for (const fn of [...handle.listeners.error]) fn(event);
      };
      ws.onclose = (event) => {
        if (handle.ws === ws) {
          handle.ws = null;
          handle.url = null;
        } else {
          return;
        }
        for (const fn of [...handle.listeners.close]) fn({ code: event.code, reason: event.reason, wasClean: event.wasClean });
      };
    } catch (err) {
      if (!handle.disposed) {
        emitClose(handle, WS_CLOSE_CONNECT_FAILED, err instanceof Error ? err.message : String(err));
      }
    }
  }

  function closeWs(handle: InternalHandle, code: number, reason: string): void {
    const ws = handle.ws;
    if (!ws) return;
    handle.ws = null;
    handle.url = null;
    ws.onclose = null;
    ws.onmessage = null;
    ws.onerror = null;
    ws.onopen = null;
    try {
      ws.close(code, reason);
    } catch {
      // ignore
    }
    emitClose(handle, code, reason);
  }

  function open(handleSpec: WsHandleSpec): WsHandle {
    if (disposed) throw new Error('ha-ws-transport disposed');
    const handle: InternalHandle = {
      spec: handleSpec,
      listeners: { open: new Set(), close: new Set(), message: new Set(), error: new Set() },
      ws: null,
      url: null,
      disposed: false,
    };
    handles.add(handle);
    void connect(handle);

    return {
      get readyState() {
        return handle.ws?.readyState ?? WebSocket.CLOSED;
      },
      get url() {
        return handle.url;
      },
      send(data) {
        if (handle.disposed) throw new Error('ws-handle disposed');
        const ws = handle.ws;
        if (!ws) throw new Error('ws-handle: no active socket');
        if (ws.readyState !== WebSocket.OPEN) throw new Error('ws-handle: socket not open');
        ws.send(data as never);
      },
      close(code?: number, reason?: string) {
        closeWs(handle, code ?? 1000, reason ?? '');
      },
      on<E extends WsEvent>(event: E, handler: WsEventHandler<E>): Unsubscribe {
        const set = handle.listeners[event] as Set<WsEventHandler<E>>;
        set.add(handler);
        return () => {
          set.delete(handler);
        };
      },
      dispose() {
        if (handle.disposed) return;
        handle.disposed = true;
        const ws = handle.ws;
        handle.ws = null;
        handle.url = null;
        if (ws) {
          ws.onclose = null;
          ws.onmessage = null;
          ws.onerror = null;
          ws.onopen = null;
          try {
            ws.close(WS_CLOSE_DISPOSED, 'disposed');
          } catch {
            // ignore
          }
        }
        handle.listeners.open.clear();
        handle.listeners.close.clear();
        handle.listeners.message.clear();
        handle.listeners.error.clear();
        handles.delete(handle);
      },
    };
  }

  return {
    get spec() {
      return spec;
    },
    get handleCount() {
      return handles.size;
    },
    async apply(_target: ConnectionTarget | null): Promise<void> {
      // HA owns connectivity, nothing to re-target
    },
    health(): TransportStatus {
      return { up: true };
    },
    on(): Unsubscribe {
      return () => {};
    },
    async dispose(): Promise<void> {
      disposed = true;
      for (const handle of [...handles]) {
        handle.disposed = true;
        closeWs(handle, WS_CLOSE_DISPOSED, 'disposed');
      }
      handles.clear();
    },
    open,
  };
}
