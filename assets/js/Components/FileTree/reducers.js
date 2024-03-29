import * as constants from "./constants";

const pushEntry = (needle, n, newChild) => {
  for (let i = 0; i < n.length; i++) {
    if (n[i].path === needle) {
      n[i].childNodes = newChild;
      return true;
    } else if (n[i].childNodes) {
      const c = pushEntry(needle, n[i].childNodes, newChild);
      if (c) {
        return c;
      }
    }
  }
  return false;
};

const fileTreeInitialState = {
  nodes: [],
  root: { id: "r", path: "/" },
  errorMessage: "",
};

export const fileTreeReducer = (state = fileTreeInitialState, action) => {
  switch (action.type) {
    case constants.FETCH_DIR_SUCCESS:
      if (state.nodes.length === 0) {
        return { ...state, nodes: action.payload.folders };
      } else {
        const newNodes = [...state.nodes];
        pushEntry(action.path, newNodes, action.payload.folders);
        return { ...state, nodes: newNodes };
      }
    case constants.FETCH_DIR_ERROR:
      return {
        ...state,
        nodes: action.payload.folders,
        error: action.payload.status,
      };
    case constants.CHANGE_ROOT:
      return { ...state, nodes: [], root: action.root };
    case constants.CLOSE_DIR: {
      const newNodes = [...state.nodes];
      pushEntry(action.path, newNodes, null);
      return { ...state, nodes: newNodes };
    }
    default:
      return state;
  }
};
