import queryString from "query-string";

import * as constants from "./constants";

export function prepareSearchParams(location, additionalParams = "") {
  let params = "";
  let flavourValue = constants.DEFAULT_FLAVOUR;

  if (location) {
    const queryObject = location.query;
    const {
      dateSelector,
      minDate,
      maxDate,
      bboxSelector,
      minLon,
      maxLon,
      minLat,
      maxLat,
      flavour,
      ...facets
    } = queryObject;

    flavourValue = flavour ?? flavourValue;
    params = queryString.stringify(facets);

    if (params && additionalParams) {
      params = "&" + params;
    }

    const isDateSelected = !!minDate;
    if (isDateSelected) {
      params += `&time_select=${dateSelector}&time=${minDate} TO ${maxDate}`;
    }

    const isBBoxSelected = !!(minLon && maxLon && minLat && maxLat);
    if (isBBoxSelected) {
      params += `&bbox_select=${bboxSelector}&bbox=${minLon},${maxLon},${minLat},${maxLat}`;
    }
  }

  return `${flavourValue}/file?${additionalParams}${params}`;
}
