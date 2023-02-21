import * as constants from "./constants";

const appReducerInitialState = {
  currentUser: null,
  error: "",
};

export const appReducer = (state = appReducerInitialState, action) => {
  switch (action.type) {
    case constants.GET_CURRENT_USER_SUCCESS:
      return { ...state, currentUser: action.payload, error: "" };
    case constants.SET_ERROR:
      return { ...state, error: action.payload };
    default:
      // In our default case we reset the error on
      // every new state change if the error has not been
      // set.
      return { ...state, error: "" };
  }
};
