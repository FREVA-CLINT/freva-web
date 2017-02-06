import * as constants from './constants';
import fetch from 'isomorphic-fetch'

export const exportPlugin = (path) => (dispatch) => {
    let url = `/api/plugins/export/?export_file=${path}`;
    return fetch(url)
        .then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.EXPORT_PLUGIN
            });
            return json;
        })
        .then(json => dispatch(loadPlugins()))
};

export const loadPlugins = () => (dispatch) => {

    let url = `/api/plugins/list/`;
    return fetch(url)
        .then(response => response.json())
        .then(json => dispatch({
            type: constants.LOAD_PLUGINS,
            payload: json
        }))
};