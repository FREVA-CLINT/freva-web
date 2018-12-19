import * as constants from './constants'
import _ from 'lodash';

export const selectMenuItem = (params, data) => ({
    type: constants.CHANGE_PARAM,
    params,
    data
});

export const cacheData = (key, data) => ({
    type: constants.CACHE_DATA,
    key,
    data
});

export const getHindcastData = (params) => (dispatch, getState) => {
    const {metric, variable, reference, hindcastSet, leadtime, region} = params
    if (metric && variable && reference && hindcastSet && leadtime && region) {
        let url = `/api/hindcast-frontend/get-hindcast-data/?leadtime=${leadtime}&metric=${metric.value}&type=map&variable=${variable.value}&reference=${reference.value}&hindcastset=${hindcastSet.value}&region=${region.value}`;
        const {cache} = getState().hindcastFrontendReducer.settingsReducer;

        if (cache[url]) {
            return new Promise((resolve) => resolve()).then(() => cache[url])
        }

        return fetch(url, {
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(json => {
                dispatch(cacheData(url, json));
                return json
            })
    }
};


export const getHindcastTimeseriesData = (params) => (dispatch, getState) => {
    const {metric, variable, reference, hindcastSet, region}= params;
    if (metric && variable && reference && hindcastSet && region) {

        let url = `/api/hindcast-frontend/get-hindcast-data/?metric=${metric.value}&type=fieldmean&variable=${variable.value}&reference=${reference.value}&hindcastset=${hindcastSet.value}&region=${region.value}`;
        const {cache} = getState().hindcastFrontendReducer.settingsReducer;

        if (cache[url]) {
            return new Promise((resolve) => resolve()).then(() => cache[url])
        }
        
        return fetch(url, {
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        })
            .then(response => response.json())
            .then(json => {
                dispatch(cacheData(url, json));
                return  json
            })
    }
};

export const changeParamAsync = (params) => (dispatch, getState) => {
    const {metric, variable, reference, hindcastSet, leadtime, region} = getState().hindcastFrontendReducer.selectMenuReducer;
    const newParams = {metric: metric.selected, variable: variable.selected, reference: reference.selected,
        hindcastSet: hindcastSet.selected, leadtime: leadtime.selected, region: region.selected, ...params};
    return Promise.all([
        dispatch(getHindcastData(newParams)),
        dispatch(getHindcastTimeseriesData(newParams))
    ]).then((data) => {
        dispatch(selectMenuItem(params, data));
    })
};

export const loadOptions = (facet) => (dispatch, getState) => {
    const {metric, variable, reference, hindcastSet, leadtime, region} = getState().hindcastFrontendReducer.selectMenuReducer;
    const params = {metric, variable, reference, hindcastSet, region};
    let url = `/api/hindcast-frontend/get-hindcast-facets?facet=${facet}`;
    _.map(params, (val, key) => {
        if (val.selected && key !== facet) {
            url += `&${key}=${val.selected.value}`;
        }
    });

    dispatch({
        type: 'LOAD_OPTIONS',
        facet
    });

    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        }).then(response => response.json())
        .then(json => {
            dispatch({
                type: 'LOAD_OPTIONS_SUCCESS',
                facet,
                json
            })
        })

};
