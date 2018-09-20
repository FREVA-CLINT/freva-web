import * as constants from './constants';


const appReducerInitialState = {
    currentUser: undefined,
    table : window.table
};

export const appReducer = (state = appReducerInitialState, action) => {
    switch (action.type) {
        case constants.GET_CURRENT_USER_SUCCESS:
            return {...state, currentUser: action.payload};
        default:
            return state
    }
};
