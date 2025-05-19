import * as constants from "./constants";

const databrowserInitialState = {
  facets: null,
  files: [],
  numFiles: 0,
  start: 0,
  selectedFacets: {},
  minDate: "",
  maxDate: "",
  minLon: "",
  maxLon: "",
  minLat: "",
  maxLat: "",
  dateSelector: constants.TIME_RANGE_FLEXIBLE,
  bboxSelector: constants.BBOX_RANGE_FLEXIBLE,
  metadata: {},
  facetLoading: false,
  fileLoading: false,
  flavours: ["freva"],
  selectedFlavour: constants.DEFAULT_FLAVOUR,
  // zarr_stream is a special case for the Zarr streaming toggle
  facetMapping: {
    zarr_stream: "zarr_stream",
  },
};

export const databrowserReducer = (state = databrowserInitialState, action) => {
  switch (action.type) {
    case constants.SET_FILE_LOADING:
      return { ...state, fileLoading: true };
    case constants.LOAD_FACETS:
      return {
        ...state,
        error: "",
        facets: action.payload.data,
        facetLoading: false,
      };
    case constants.UPDATE_FACET_SELECTION: {
      const {
        minDate,
        maxDate,
        dateSelector,
        minLon,
        maxLon,
        minLat,
        maxLat,
        bboxSelector,
        start,
        flavour,
        ...queryObject
      } = action.queryObject;
      let myMinDate = minDate;
      let myMaxDate = maxDate;
      let myDateSelector = dateSelector;
      let myMinLon = minLon;
      let myMaxLon = maxLon;
      let myMinLat = minLat;
      let myMaxLat = maxLat;
      let myBBoxSelector = bboxSelector;
      if (!dateSelector || !minDate || !maxDate) {
        myDateSelector = databrowserInitialState.dateSelector;
        myMinDate = databrowserInitialState.minDate;
        myMaxDate = databrowserInitialState.maxDate;
      }

      if (!bboxSelector || !minLon || !maxLon || !minLat || !maxLat) {
        myBBoxSelector = databrowserInitialState.bboxSelector;
        myMinLon = databrowserInitialState.minLon;
        myMaxLon = databrowserInitialState.maxLon;
        myMinLat = databrowserInitialState.minLat;
        myMaxLat = databrowserInitialState.maxLat;
      }
      return {
        ...state,
        selectedFacets: { ...queryObject },
        start: start !== undefined ? parseInt(start) : 0,
        dateSelector: myDateSelector,
        minDate: myMinDate,
        maxDate: myMaxDate,
        bboxSelector: myBBoxSelector,
        minLon: myMinLon,
        maxLon: myMaxLon,
        minLat: myMinLat,
        maxLat: myMaxLat,
        selectedFlavour: flavour || databrowserInitialState.selectedFlavour,
      };
    }
    case constants.SET_METADATA:
      return { ...state, metadata: action.metadata };
    case constants.SET_FLAVOURS:
      return { ...state, flavours: action.payload.flavours };
    case constants.LOAD_FILES:
      return {
        ...state,
        facets: action.payload.facets,
        primaryFacets: action.payload.primary_facets,
        facetMapping: {
          ...action.payload.facet_mapping,
          zarr_stream: "zarr_stream",
        },
        files: action.payload.search_results.map((x) => x.file),
        numFiles: action.payload.total_count,
        fileLoading: false,
        start: parseInt(action.payload.start),
        selectedFlavour: action.payload.flavour,
      };
    default:
      return state;
  }
};
