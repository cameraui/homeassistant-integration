import { createHaWsTransport } from './haTransport.js';

import type { CameraUiContext } from '@camera.ui/browser';
import type { RPCClient } from '@camera.ui/rpc';
import type { ConnectionTarget } from '@camera.ui/transport';
import type { HaTransportHost } from './haTransport.js';

export function createHaCameraUiContext(host: HaTransportHost): CameraUiContext {
  const wsTransport = createHaWsTransport(host);

  let cachedTarget: ConnectionTarget | null = null;
  const target = computed<ConnectionTarget | null>(() => {
    const hass = host.getHass();
    if (!hass || !host.getEntryId()) return null;
    cachedTarget ??= { endpoint: { url: hass.hassUrl('/'), mode: 'direct-lan' }, tokens: { access: '' } };
    return cachedTarget;
  });

  return markRaw({
    rpc: shallowRef<RPCClient | undefined>(undefined),
    target,
    isConnected: computed(() => target.value !== null),
    endpoint: computed(() => target.value?.endpoint.url),
    token: computed(() => undefined),
    extraProxyQuery: computed(() => undefined),
    error: ref<Error | undefined>(undefined),
    wsTransport,
    on: () => {},
    off: () => {},
  });
}
