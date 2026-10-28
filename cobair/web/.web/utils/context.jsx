import { useContext, useMemo, useReducer, useRef, useState, createElement, useEffect, useLayoutEffect } from "react"
import { applyDelta, ReflexEvent, hydrateClientStorage, useEventLoop, refs } from "$/utils/state"
import { ColorModeContext, UploadFilesContext, DispatchContext, EventLoopContext, getStateContext, registerApp, eventLoop } from "$/utils/context-registry"
import { jsx } from "@emotion/react";

export { ColorModeContext, UploadFilesContext, DispatchContext, EventLoopContext };
export const initialState = {"reflex___state____state": {"is_hydrated_rx_state_": false, "rx_router_headers_rx_state_": {"host": "", "origin": "", "upgrade": "", "connection": "", "pragma": "", "cache_control": "", "user_agent": "", "sec_websocket_version": "", "sec_websocket_key": "", "sec_websocket_extensions": "", "accept_encoding": "", "accept_language": "", "raw_headers": {}}, "rx_router_page_rx_state_": {"host": "", "path": "", "raw_path": "", "full_path": "", "full_raw_path": "", "params": {}}, "rx_router_route_id_rx_state_": "", "rx_router_session_rx_state_": {"client_token": "", "client_ip": "", "session_id": ""}, "rx_router_url_rx_state_": {"scheme": "", "netloc": "", "origin": "://", "path": "", "query": "", "query_parameters": {}, "fragment": "", "href": ""}}, "reflex___state____state.cobair___web___state____editor_state": {"can_redo_rx_state_": false, "can_undo_rx_state_": false, "combined_rx_state_": [], "combined_dialog_open_rx_state_": false, "combined_error_rx_state_": "", "combined_intention_rx_state_": "0", "combined_parts_rx_state_": [], "combined_value_rx_state_": "5", "context_dialog_error_rx_state_": "", "context_dialog_index_rx_state_": -1, "context_dialog_name_rx_state_": "", "context_dialog_open_rx_state_": false, "context_dialog_rows_rx_state_": [], "contexts_rx_state_": [], "decision_threshold_rx_state_": "0.0", "dirty_rx_state_": false, "draft_rx_state_": "", "error_rx_state_": "", "evidence_rx_state_": [], "expanded_contexts_rx_state_": [], "file_name_rx_state_": "", "graph_edges_rx_state_": [], "graph_key_rx_state_": "", "graph_nodes_rx_state_": [], "inference_error_rx_state_": "", "influence_context_rx_state_": "0", "influence_rows_rx_state_": [], "info_rx_state_": "", "intention_dialog_error_rx_state_": "", "intention_dialog_index_rx_state_": -1, "intention_dialog_name_rx_state_": "", "intention_dialog_open_rx_state_": false, "intentions_rx_state_": [], "local_file_rx_state_": "", "problems_rx_state_": [], "recognized_rx_state_": "", "results_rx_state_": [], "revision_rx_state_": 0, "selected_intention_rx_state_": -1, "tab_rx_state_": "editor", "threshold_percent_rx_state_": 0.0}, "reflex___state____state.reflex___istate___shared____shared_state_base_internal": {}, "reflex___state____state.reflex___state____frontend_event_exception_state": {}, "reflex___state____state.reflex___state____on_load_internal_state": {}, "reflex___state____state.reflex___state____update_vars_internal_state": {}}
export const initialStateHashes = ["5b898815fe7fbeea", "d029e8db883816fc", "270b660d53b34e24", "bf21a9e8fbc5a384", "bf21a9e8fbc5a384", "bf21a9e8fbc5a384", "bf21a9e8fbc5a384"]

export const defaultColorMode = "system"
export const StateContexts = {reflex___state____state: getStateContext("reflex___state____state"),reflex___state____state__cobair___web___state____editor_state: getStateContext("reflex___state____state.cobair___web___state____editor_state"),reflex___state____state__reflex___istate___shared____shared_state_base_internal: getStateContext("reflex___state____state.reflex___istate___shared____shared_state_base_internal"),reflex___state____state__reflex___state____frontend_event_exception_state: getStateContext("reflex___state____state.reflex___state____frontend_event_exception_state"),reflex___state____state__reflex___state____on_load_internal_state: getStateContext("reflex___state____state.reflex___state____on_load_internal_state"),reflex___state____state__reflex___state____update_vars_internal_state: getStateContext("reflex___state____state.reflex___state____update_vars_internal_state"),};
export const clientStorage = {"cookies": {}, "local_storage": {"reflex___state____state.cobair___web___state____editor_state.draft_rx_state_": {"name": "cobair_draft", "sync": false}}, "session_storage": {}}


export const state_name = "reflex___state____state"

export const exception_state_name = "reflex___state____state.reflex___state____frontend_event_exception_state"

// Tracked cookie and local storage vars set in the browser, or undefined if none.
const clientStorageVars = () => {
    const client_storage_vars = hydrateClientStorage(clientStorage);
    if (client_storage_vars && Object.keys(client_storage_vars).length !== 0) {
        return client_storage_vars;
    }
    return undefined;
}

// These events are triggered on each client-side page navigation.
export const onLoadInternalEvent = () => {
    const internal_events = [];

    // Only send the client storage vars if any are actually set in the browser.
    const client_storage_vars = clientStorageVars();
    if (client_storage_vars !== undefined) {
        internal_events.push(
            ReflexEvent(
                'reflex___state____state.reflex___state____update_vars_internal_state.update_vars_internal',
                {vars: client_storage_vars},
            ),
        );
    }

    // `on_load_internal` triggers the correct on_load event(s) for the current page.
    // If the page does not define any on_load event, this will just set `is_hydrated = true`.
    internal_events.push(ReflexEvent('reflex___state____state.reflex___state____on_load_internal_state.on_load_internal'));

    return internal_events;
}

// The single event sent when the websocket connects or reconnects: it resets and
// applies client storage, sends the state, and queues the page's on_load events.
// On the first connect the frontend still holds the compiled defaults, so it
// sends their hashes and the backend only returns the vars that differ; any
// later (re)hydrate gets the full state.
export const initialEvents = (first = false) => {
    const client_storage_vars = clientStorageVars();
    const payload = {};
    if (client_storage_vars !== undefined) {
        payload["vars"] = client_storage_vars;
    }
    if (first) {
        payload["hashes"] = initialStateHashes;
    }
    return [ReflexEvent('reflex___state____state.hydrate_and_load', payload)];
}
    

export const isDevMode = false;

// The static runtime reads these through the registry, so this module is the
// only one Vite re-executes when they change.
registerApp({
  initialState,
  clientStorage,
  state_name,
  exception_state_name,
  onLoadInternalEvent,
  initialEvents,
  isDevMode,
  defaultColorMode,
});

export function addEvents(events, args, event_actions) {
  return eventLoop.addEvents(events, args, event_actions);
}

export function getConnectErrors() {
  return eventLoop.connectErrors;
}

export function UploadFilesProvider({ children }) {
  const [filesById, setFilesById] = useState({})
  refs["__clear_selected_files"] = (id) => setFilesById(filesById => {
    const newFilesById = {...filesById}
    delete newFilesById[id]
    return newFilesById
  })
  return createElement(
    UploadFilesContext.Provider,
    { value: [filesById, setFilesById] },
    children
  );
}

// ``displayName`` is what React DevTools shows for the wrapper; without it
// every client-only component in the tree renders as ``Anonymous``.
export function ClientSide(component, name) {
  function ClientSideComponent({ children, ...props }) {
    const [Component, setComponent] = useState(null);
    useEffect(() => {
      async function load() {
        const comp = await component();
        setComponent(() => comp);
      }
      load();
    }, []);
    return Component ? jsx(Component, props, children) : null;
  }
  ClientSideComponent.displayName = name ? `ClientSide(${name})` : "ClientSide";
  return ClientSideComponent;
}

export function EventLoopProvider({ children }) {
  const dispatch = useContext(DispatchContext)
  const [addEventsLocal, connectErrors] = useEventLoop(
    dispatch,
    initialEvents,
    clientStorage,
  )
  // Publish the dispatchers so JSX literals constructed outside the
  // React-tree path (e.g. ``ErrorBoundary.onError``) can call ``addEvents``.
  eventLoop.addEvents = addEventsLocal;
  eventLoop.connectErrors = connectErrors;
  return useMemo(
    () =>
      createElement(
        EventLoopContext.Provider,
        { value: [addEventsLocal, connectErrors] },
        children
      ),
    [addEventsLocal, connectErrors, children],
  );
}

// ``useLayoutEffect`` warns when rendered on the server, where no effect runs
// at all, so fall back to ``useEffect`` there.
const useIsomorphicLayoutEffect =
  typeof document !== "undefined" ? useLayoutEffect : useEffect;

// Holds the mutable substate -> dispatch registry that ``SubstateProvider``
// writes into and ``EventLoopProvider`` reads. The registry object identity is
// stable for the lifetime of the tree, so neither adding a dispatcher nor
// updating a substate re-renders the consumers of ``DispatchContext``.
const DispatchProvider = ({ children }) => {
  const dispatchers = useRef({});
  return useMemo(
    () =>
      createElement(DispatchContext, { value: dispatchers.current }, children),
    [children],
  );
};

// One provider per substate: each owns its own reducer, so a delta for one
// substate only re-renders its provider instead of recreating every provider.
const SubstateProvider = ({ children, substateName, contextName }) => {
  const dispatchers = useContext(DispatchContext);
  const [state, dispatchSubstate] = useReducer(
    applyDelta,
    initialState[substateName],
  );
  // A layout effect, not a passive one: layout effects for the whole commit
  // run before any passive effect, so every dispatcher is registered before
  // ``EventLoopProvider`` (mounted below this provider) connects the socket.
  // A delta naming an unregistered substate is a fatal state mismatch.
  useIsomorphicLayoutEffect(() => {
    dispatchers[substateName] = dispatchSubstate;
    return () => {
      delete dispatchers[substateName];
    };
  }, [dispatchers, dispatchSubstate, substateName]);
  return useMemo(
    () => createElement(StateContexts[contextName], { value: state }, children),
    [children, state, contextName],
  );
};

// ``[substateName, contextName]`` for every substate, outermost first.
const SUBSTATES = [
  ['reflex___state____state', 'reflex___state____state'],
  ['reflex___state____state.cobair___web___state____editor_state', 'reflex___state____state__cobair___web___state____editor_state'],
  ['reflex___state____state.reflex___istate___shared____shared_state_base_internal', 'reflex___state____state__reflex___istate___shared____shared_state_base_internal'],
  ['reflex___state____state.reflex___state____frontend_event_exception_state', 'reflex___state____state__reflex___state____frontend_event_exception_state'],
  ['reflex___state____state.reflex___state____on_load_internal_state', 'reflex___state____state__reflex___state____on_load_internal_state'],
  ['reflex___state____state.reflex___state____update_vars_internal_state', 'reflex___state____state__reflex___state____update_vars_internal_state'],
];

function ClientStateProvider({ children }) {
  return useMemo(() => {
    let tree = children;
    for (let i = SUBSTATES.length - 1; i >= 0; i--) {
      const [substateName, contextName] = SUBSTATES[i];
      tree = createElement(SubstateProvider, { substateName, contextName }, tree);
    }
    return createElement(DispatchProvider, {}, tree);
  }, [children]);
}

// The server renders once and never applies a delta, so it provides the
// initial state through bare context providers. ``SubstateProvider`` would add
// a second render level per substate, and the server renderer recurses once per
// level, so with many substates rendering a page can exhaust the stack.
function ServerStateProvider({ children }) {
  let tree = children;
  for (let i = SUBSTATES.length - 1; i >= 0; i--) {
    const [substateName, contextName] = SUBSTATES[i];
    tree = createElement(
      StateContexts[contextName],
      { value: initialState[substateName] },
      tree,
    );
  }
  return createElement(DispatchContext, { value: {} }, tree);
}

export const StateProvider =
  typeof document === "undefined" ? ServerStateProvider : ClientStateProvider;