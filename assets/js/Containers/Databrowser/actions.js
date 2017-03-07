import * as constants from './constants'
import fetch from 'isomorphic-fetch'
import {getCookie} from '../../utils'
import _ from 'lodash';
import $ from 'jquery';

export const selectFacet = (facet, value) => dispatch => {
    $('html').addClass('wait');
    setTimeout(function(){


    dispatch({
        type: constants.SELECT_FACET,
        facet,
        value
    });
    dispatch(setActiveFacet(facet));
    dispatch(loadFacets());
    dispatch(loadFiles());
    },50);

};

export const clearFacet = (facet) => dispatch => {
    $('html').addClass('wait');
    dispatch({
        type: constants.CLEAR_FACET,
        facet
    });
    dispatch(loadFacets());
    dispatch(loadFiles());
};

export const resetNcdump = () => ({
    type: constants.RESET_NCDUMP
})

export const setMetadata = (metadata) => ({
    type: constants.SET_METADATA,
    metadata
});

export const clearAllFacets = (facet) => dispatch => {
    $('html').addClass('wait');
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
            $('html').removeClass('wait');
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

export const loadNcdump = (fn, pw) => dispatch => {
    let url = `/api/solr/ncdump/`;
    dispatch({type: constants.LOAD_NCDUMP, fn});
    return fetch(url, {
        credentials: 'same-origin',
        method: 'POST',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pass: pw,
            file: fn
        })
    }).then(resp => {

        if (!resp.ok) {
            throw Error([resp.status, resp.statusText]);
        }
        return resp.json();
    }).then(json => dispatch({type: constants.LOAD_NCDUMP_SUCCESS, payload: json})
    ).catch(error => dispatch({type: constants.LOAD_NCDUMP_ERROR}));
};