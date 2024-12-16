import * as constants from "./constants";

export function setThread(thread_id) {
  return {
    type: "SET_THREAD",
    payload: thread_id,
  };
}

export function setConversation(conversation) {
  return {
    type: "SET_CONVERSATION",
    payload: conversation,
  };
}

export const addElement = (element) => (dispatch) => {
  dispatch({
    type: constants.ADD_ELEMENT,
    payload: element,
  });
};
