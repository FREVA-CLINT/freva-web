import { combineReducers } from 'redux'
import * as constants from './constants';
import _ from 'lodash';

const databrowserInitialState = {
    facets: [],
    selectedFacets: {}
};

export const databrowserReducer = (state = databrowserInitialState, action) => {
    switch (action.type) {
        case constants.LOAD_FACETS:
            return {...state, facets: action.payload.data};
        case constants.SELECT_FACET:
            let selectedFacets = {...state.selectedFacets};
            selectedFacets[action.facet] = action.value;
            return {...state, selectedFacets};
        case constants.CLEAR_FACET:
            let newFacets = {...state.selectedFacets};
            newFacets = _.omit(newFacets, action.facet);
            return {...state, selectedFacets: newFacets};
        default:
            return state
    }
};