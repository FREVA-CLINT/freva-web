import fetch from "isomorphic-fetch";

import { getCookie } from "../../utils";

import * as constants from "./constants";

export const updateCategoryFilter = (category) => dispatch => {
  dispatch({
    type: constants.UPDATE_CATEGORY_FILTER,
    category
  });
  return dispatch({
    type: constants.FILTER_PLUGINS
  });
};

export const updateTagFilter = (tag) => dispatch => {
  dispatch({
    type: constants.UPDATE_TAG_FILTER,
    tag
  });
  return dispatch({
    type: constants.FILTER_PLUGINS
  });
};


export const updateSearchFilter = (value) => dispatch => {
  dispatch({
    type: constants.UPDATE_SEARCH_FILTER,
    value
  });
  return dispatch({
    type: constants.FILTER_PLUGINS
  });
};

export const exportPlugin = (path) => (dispatch) => {
  const url = "/api/plugins/export/";
  return fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      export_file: path
    })
  })
    .then(response => response.json())
    .then(json => {
      dispatch({
        type: constants.EXPORT_PLUGIN
      });
      return json;
    })
    .then(() => dispatch(loadPlugins()));
};

export const loadPlugins = () => (dispatch) => {

  const url = "/api/plugins/list/";
  return fetch(url, {
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
  })
    .then(response => response.json())
    .then(json => dispatch({
      type: constants.LOAD_PLUGINS,
      payload: json
    }));
};