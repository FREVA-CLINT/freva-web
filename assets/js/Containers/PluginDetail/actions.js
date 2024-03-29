import fetch from "isomorphic-fetch";

import { getCookie } from "../../utils";

import * as constants from "./constants";

export const resetPlugin = () => {
  return {
    type: constants.RESET_PLUGIN,
  };
};

export const loadPlugin = (pluginName) => (dispatch) => {
  const url = `/api/plugins/${pluginName}/`;
  return fetch(url, {
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.status >= 400) {
        throw new Error(response.statusText);
      }
      return response.json();
    })
    .then((json) => {
      dispatch({
        type: constants.LOAD_PLUGIN,
        payload: json,
      });
      return json;
    })
    .catch((error) => {
      dispatch({
        type: constants.LOAD_PLUGIN_ERROR,
        errorMessage: "Error occured while loading plugin: " + error.message,
      });
    });
};

export const sendDeveloperMail = (text, toolName) => () => {
  const url = "/api/utils/mail-to-developer/";
  return fetch(url, {
    credentials: "same-origin",
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      tool_name: toolName,
    }),
  });
};
