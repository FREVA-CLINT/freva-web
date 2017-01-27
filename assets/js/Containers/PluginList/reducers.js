import * as constants from './constants';

const pluginListInitialState = {
    plugins: [],
    exported: null
};

export const pluginListReducer = (state = pluginListInitialState, action) => {
    switch (action.type) {
        case constants.LOAD_PLUGINS:
            let exported = false;
            action.payload.map(v => {
                if (v[1].user_exported)
                    exported = v[1].plugin_module;
            })
            return {...state, plugins: action.payload, exported};
        default:
            return state
    }
};