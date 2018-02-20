import * as constants from './constants';
import _ from 'lodash';

const resultbrowserInitialState = {
    facets: [],
    files: [],
    numResults: null,
    selectedFacets: {},
    activeFacet: 'results',
    metadata: {},
    caption: [],
    page: 1,
    limit: 25,
    sortName: 'timestamp',
    sortOrder:'desc',
    searchText: ''
};

export const resultbrowserReducer = (state = resultbrowserInitialState, action) => {
    switch (action.type) {
        case constants.LOAD_RESULT_FACETS:
            return {...state, facets: action.payload.data};
        case constants.SELECT_RESULT_FACET:
            let selectedFacets = {...state.selectedFacets};
            selectedFacets[action.facet] = action.value;
            return {...state, selectedFacets};
        case constants.CLEAR_RESULT_FACET:
            let newFacets = {...state.selectedFacets};
            newFacets = _.omit(newFacets, action.facet);
            return {...state, selectedFacets: newFacets};
        case constants.CLEAR_ALL_RESULT_FACETS:
            return {...state, selectedFacets: {}};
        case constants.SET_ACTIVE_RESULT_FACET:
            if (state.activeFacet === action.facet)
                return {...state, activeFacet: resultbrowserInitialState.activeFacet};
            return {...state, activeFacet: action.facet};
        case constants.SET_METADATA:
            return {...state, metadata: action.metadata};
        case constants.LOAD_RESULT_FILES:
            return {...state, results: action.payload.data,
                numResults: action.payload.metadata.numFound};
        case constants.SELECT_ACTIVE_PAGE:
            return {...state, page: action.page};
        case constants.SORT_ACTIVE_PAGE:
            return {...state, sortName: action.sortName, sortOrder: action.sortOrder};
        case constants.ON_SEARCH:
            return {...state, searchText: action.searchText}
        default:
            return state
    }
};


