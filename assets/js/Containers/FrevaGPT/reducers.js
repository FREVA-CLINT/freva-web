import * as constants from "./constants";

const frevaGPTInitialState = {
  conversation: [],
  thread: "",
};

export const frevaGPTReducer = (state = frevaGPTInitialState, action) => {
  switch (action.type) {
    case constants.SET_CONVERSATION:
      return { ...state, conversation: action.payload };
    case constants.SET_THREAD:
      return { ...state, thread: action.payload };
    case constants.ADD_ELEMENT:
      return {
        ...state,
        conversation: [...state.conversation, action.payload],
      };
    default:
      return state;
  }
};
