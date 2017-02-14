import * as constants from './constants'
import fetch from 'isomorphic-fetch'
import {getCookie} from '../../utils'
import _ from 'lodash';

export const selectFacet = (facet, value) => dispatch => {
    dispatch({
        type: constants.SELECT_FACET,
        facet,
        value
    });
    dispatch(setActiveFacet(facet));
    dispatch(loadFacets());
    dispatch(loadFiles());
};

export const clearFacet = (facet) => dispatch => {
    dispatch({
        type: constants.CLEAR_FACET,
        facet
    });
    dispatch(loadFacets());
    dispatch(loadFiles());
};

export const setMetadata = (metadata) => ({
    type: constants.SET_METADATA,
    metadata
});

export const clearAllFacets = (facet) => dispatch => {
    dispatch({
        type: constants.CLEAR_ALL_FACETS,
        facet
    });
    dispatch(loadFacets());
    dispatch(loadFiles());
};

export const setActiveFacet = (facet) => ({
    type: constants.SET_ACTIVE_FACET,
    facet
});

export const loadFacets = () => (dispatch, getState) => {

    const {selectedFacets} = getState().databrowserReducer;
    let params = '';
    _.map(selectedFacets, (value, key) => {
        params += `&${key}=${value};`
    });
    let url = `/solr/solr-search/?facet=*${params}`;

    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }}
        ).then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.LOAD_FACETS,
                payload: json
            });
        })
};

export const loadFiles = () => (dispatch, getState) => {

    const {selectedFacets} = getState().databrowserReducer;
    let params = '';
    _.map(selectedFacets, (value, key) => {
        params += `&${key}=${value};`
    });
    let url = `/solr/solr-search/?start=0&rows=100${params}`;

    return fetch(url, {
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }}
        ).then(response => response.json())
        .then(json => {
            dispatch({
                type: constants.LOAD_FILES,
                payload: json
            });
        })
};