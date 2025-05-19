// [ESLint]: External library imports first
import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import {
  FaPython,
  FaRegClone,
  FaTerminal,
  FaCheck,
  FaPlay,
} from "react-icons/fa";

import { Button, Card, OverlayTrigger, Tooltip, Form } from "react-bootstrap";
import { HiCode } from "react-icons/hi";
import queryString from "query-string";
import { withRouter } from "react-router";

// [ESLint]: Local imports second
import ClipboardToast from "../../Components/ClipboardToast";

import { copyTextToClipboard } from "../../utils";

import ZarrStreamIcon from "../../Icons/ZarrStreamIcon";

import DataBrowserOptionsDropdown from "./DataBrowserOptionsDropdown";

import * as constants from "./constants";

import { prepareSearchParams } from "./utils";

import {
  TIME_RANGE_FILE,
  TIME_RANGE_FLEXIBLE,
  TIME_RANGE_STRICT,
  BBOX_RANGE_FILE,
  BBOX_RANGE_FLEXIBLE,
  BBOX_RANGE_STRICT,
  STREAM_CATALOGUE_MAXIMUM,
} from "./constants";

const Modes = {
  CLI: "CLI",
  PYTHON: "PYTHON",
  API: "API",
};

const DataBrowserOptions = {
  DEFAULT: "data-search",
  INTAKE: "intake-catalogue",
  STAC: "stac-catalogue",
};

function DataBrowserCommandImpl(props) {
  const [showToast, setShowToast] = useState(false);
  const [mode, setMode] = useState(Modes.CLI);
  const [copying, setCopying] = useState(false);
  const hostName = window.location.host;

  const isGuest = !(props.currentUser && props.currentUser.home);
  // read “zarr_stream” right out of Redux: location.query
  const zarrEnabled = !isGuest && props.selectedFacets.zarr_stream === "true";

  const getDataBrowserOption = (activeOption) => {
    switch (activeOption) {
      case "intake":
        return DataBrowserOptions.INTAKE;
      case "stac":
        return DataBrowserOptions.STAC;
      case "search":
      default:
        return DataBrowserOptions.DEFAULT;
    }
  };

  const handleDataBrowserOptionChange = (option) => {
    // handle databrowser option changes from the dropdown

    // This will be passed to the DataBrowserOptionsDropdown component
    // The databrowserOption will be derived from this option when needed
    setActiveOption(option);
  };

  const [activeOption, setActiveOption] = useState("search");
  useEffect(() => {
    // To reset the dropdown, for cases that we are already
    // on intake or stac catalogue and the user clear the
    // all facets and we exceed the maximum number of files
    // for catalogues
    if (
      props.numFiles > STREAM_CATALOGUE_MAXIMUM &&
      activeOption !== "search"
    ) {
      setActiveOption("search");
    }
  }, [props.numFiles, activeOption]);
  const isStac = activeOption === "stac";
  const zarrAllowed = !isStac;
  const databrowserOption = getDataBrowserOption(activeOption);
  // avoid zarr_stream=true from the URL to sneak into any of our MODES
  const selectedFacets = Object.fromEntries(
    Object.entries(props.selectedFacets).filter(([k]) => k !== "zarr_stream")
  );
  function getCliTimeSelector() {
    let dateSelectorToCli;
    const dateSelector = props.dateSelector;
    if (dateSelector === TIME_RANGE_FLEXIBLE) {
      dateSelectorToCli = "flexible";
    } else if (dateSelector === TIME_RANGE_STRICT) {
      dateSelectorToCli = "strict";
    } else if (dateSelector === TIME_RANGE_FILE) {
      dateSelectorToCli = "file";
    }
    return dateSelectorToCli;
  }

  function getCliBBoxSelector() {
    let bboxSelectorToCli;
    const bboxSelector = props.bboxSelector;
    if (bboxSelector === BBOX_RANGE_FLEXIBLE) {
      bboxSelectorToCli = "flexible";
    } else if (bboxSelector === BBOX_RANGE_STRICT) {
      bboxSelectorToCli = "strict";
    } else if (bboxSelector === BBOX_RANGE_FILE) {
      bboxSelectorToCli = "file";
    }
    return bboxSelectorToCli;
  }

  function getFullCliCommand(dateSelectorToCli, bboxSelectorToCli) {
    let command =
      `freva-client databrowser ${databrowserOption} ` +
      `--host ${hostName} ` +
      (props.selectedFlavour !== constants.DEFAULT_FLAVOUR
        ? `--flavour ${props.selectedFlavour} `
        : "") + // don't show the freva flavour if it's the default (freva)
      (props.minDate ? `time=${props.minDate}to${props.maxDate} ` : "") +
      (props.minLon
        ? `bbox=${props.minLon},${props.maxLon},${props.minLat},${props.maxLat} `
        : "") +
      Object.keys(selectedFacets)
        .map((key) => {
          const value = selectedFacets[key];
          return `${props.facetMapping[key]}=${value}`;
        })
        .join(" ") +
      (dateSelectorToCli && props.minDate
        ? ` --time-select ${dateSelectorToCli}`
        : "") +
      (bboxSelectorToCli && props.minLon
        ? ` --bbox-select ${bboxSelectorToCli}`
        : "");

    if (zarrEnabled && zarrAllowed) {
      command += " --zarr";
      command += " --access-token $token";
    }

    return command.trimEnd();
  }

  function handleCopy(textToCopy) {
    copyTextToClipboard(textToCopy, () => setShowToast(true));
    setCopying(true);
    setTimeout(() => setCopying(false), 1000);
  }

  function executeCommand() {
    if (activeOption === "search") {
      //data-search
      if (zarrEnabled && zarrAllowed) {
        // get the same pattern as in FilesPanelImpl
        const currentLocation = window.location.pathname;
        // add zarr_stream=true to the query string
        const query = queryString.stringify({
          ...props.location.query,
          zarr_stream: "true",
        });
        // Use router to navigate to the new URL
        props.router.push(currentLocation + "?" + query);
      } else {
        const base = window.location.pathname;
        const filtered = Object.fromEntries(
          Object.entries(props.location.query).filter(
            ([k]) => k !== "zarr_stream"
          )
        );
        const qs = queryString.stringify(filtered);
        props.router.push(base + (qs ? `?${qs}` : ""));
      }
      return;
    }

    // For catalog options (intake or stac)
    const url = createCatalogLink(activeOption);

    if (zarrEnabled && zarrAllowed) {
      const catalogUrl = new URL(url, window.location.origin);
      catalogUrl.searchParams.set("zarr_stream", "true");
      window.location.href = catalogUrl.toString();
    } else {
      //TODO: would be removed when we add zarr in static STAC
      window.location.href = url;
    }
  }
  // Modify the renderCLICommand function to always show pip install
  function renderCLICommand() {
    const dateSelectorToCli = getCliTimeSelector();
    const bboxSelectorToCli = getCliBBoxSelector();
    const usernameDisplay = props.currentUser
      ? props.currentUser.username
      : "$USERNAME";
    const fullCommand = getFullCliCommand(dateSelectorToCli, bboxSelectorToCli);

    const pipInstallCmd = "pip install freva-client";
    const tokenCmd =
      zarrEnabled && zarrAllowed
        ? `token=$(freva-client auth -u ${usernameDisplay} --host ${hostName} | jq -r .access_token)`
        : "";

    // Combine commands (for the sake of better copy functionality)
    const combinedCmd =
      zarrEnabled && zarrAllowed
        ? [pipInstallCmd, tokenCmd, fullCommand].filter(Boolean).join("\n\n")
        : [pipInstallCmd, fullCommand].join("\n\n");

    return (
      <div className="position-relative">
        <div className="mb-3">
          <div className="fw-bold small text-muted mb-1">CLI Command:</div>
          <pre
            className="mb-5 command-terminal"
            style={{ whiteSpace: "pre-wrap" }}
          >
            {/* always shows pip install */}
            <span className="command-prompt">$ </span>
            <span className="command-param">pip install freva-client</span>
            <br />
            <br />
            {zarrEnabled && zarrAllowed && (
              <React.Fragment>
                <span className="command-prompt">$ </span>
                <span className="command-param">
                  token=$(freva-client auth -u {usernameDisplay} --host{" "}
                  {hostName} | jq -r .access_token)
                </span>
                <br />
                <br />
              </React.Fragment>
            )}

            {/* essensial commands */}
            <span className="command-prompt">$ </span>
            <span className="command-option">
              freva-client databrowser {databrowserOption}
            </span>
            {props.selectedFlavour !== constants.DEFAULT_FLAVOUR && (
              <React.Fragment>
                <span className="command-option"> --flavour </span>
                <span className="command-param">{props.selectedFlavour}</span>
              </React.Fragment>
            )}
            {props.minDate && (
              <React.Fragment>
                &nbsp;<span className="command-param">time=</span>
                <span className="fw-bold">
                  {`${props.minDate}to${props.maxDate}`}
                </span>
              </React.Fragment>
            )}
            {props.minLon && (
              <React.Fragment>
                &nbsp;<span className="command-param">bbox=</span>
                <span className="fw-bold">
                  {`${props.minLon},${props.maxLon},${props.minLat},${props.maxLat}`}
                </span>
              </React.Fragment>
            )}
            {Object.keys(selectedFacets).map((key) => {
              const value = selectedFacets[key];
              return (
                <React.Fragment key={`command-${key}`}>
                  {" "}
                  <span className="command-param">
                    {props.facetMapping[key]}=
                  </span>
                  <strong>{value}</strong>
                </React.Fragment>
              );
            })}
            {dateSelectorToCli && props.minDate && (
              <React.Fragment>
                <span className="command-option"> --time-select </span>
                <span className="fw-bold">{dateSelectorToCli}</span>
              </React.Fragment>
            )}
            {bboxSelectorToCli && props.minLon && (
              <React.Fragment>
                <span className="command-option"> --bbox-select </span>
                <span className="fw-bold">{bboxSelectorToCli}</span>
              </React.Fragment>
            )}
            <React.Fragment>
              <span className="command-option"> --host </span>
              <span className="command-param">{hostName}</span>
            </React.Fragment>
            {zarrEnabled && zarrAllowed && (
              <React.Fragment>
                <span className="command-option"> --zarr</span>
                <span className="command-option"> --access-token </span>
                <span className="fw-bold">$token</span>
              </React.Fragment>
            )}
          </pre>
          <Button
            size="sm"
            variant="outline-secondary"
            className="position-absolute"
            style={{ top: "-2px", right: "2px", padding: "0.1rem 0.3rem" }}
            onClick={() => handleCopy(combinedCmd)}
          >
            {copying ? <FaCheck size={12} /> : <FaRegClone size={12} />}
          </Button>
        </div>
        <Button
          variant="primary"
          className="position-absolute d-flex align-items-center"
          style={{ bottom: "-35px", right: "2px", padding: "0.1rem 0.3rem" }}
          onClick={executeCommand}
        >
          <FaPlay className="me-1" /> Execute Command
        </Button>
      </div>
    );
  }

  function getFullPythonCommand(dateSelectorToCli, bboxSelectorToCli) {
    let args = [];
    args.push(`host="${hostName}"`);
    if (props.selectedFlavour !== constants.DEFAULT_FLAVOUR) {
      args.push(`flavour="${props.selectedFlavour}"`);
    }

    args = [
      ...args,
      ...Object.keys(selectedFacets).map((key) => {
        const value = selectedFacets[key];
        return `${props.facetMapping[key]}="${value}"`;
      }),
    ];

    if (props.minDate) {
      args.push(`time="${props.minDate} to ${props.maxDate}"`);
      if (dateSelectorToCli) {
        args.push(`time_select="${dateSelectorToCli}"`);
      }
    }

    if (props.minLon) {
      args.push(
        `bbox="${props.minLon} ${props.maxLon} ${props.minLat} ${props.maxLat}"`
      );
      if (bboxSelectorToCli) {
        args.push(`bbox_select="${bboxSelectorToCli}"`);
      }
    }
    if (databrowserOption === DataBrowserOptions.DEFAULT && zarrEnabled) {
      args.push("zarr_stream=True");
      return `databrowser(${args.join(", ")})`;
    } else if (databrowserOption === DataBrowserOptions.INTAKE) {
      const dbCall = `db = databrowser(${args.join(", ")})`;
      if (zarrEnabled) {
        return `${dbCall}\ncat = db.intake_catalogue(stream_zarr=True)\nprint(cat.df)`;
      }
      return `${dbCall}\ncat = db.intake_catalogue()\nprint(cat.df)`;
    } else if (databrowserOption === DataBrowserOptions.STAC) {
      // TODO: would be removed in the future
      // STAC catalogue: zarr streaming not supported
      const dbCall = `db = databrowser(${args.join(", ")})`;
      return `${dbCall}\ndb.stac_catalogue()`;
    }
    return `databrowser(${args.join(", ")})`;
  }

  function renderPythonCommand() {
    const dateSelectorToCli = getCliTimeSelector();
    const bboxSelectorToCli = getCliBBoxSelector();
    const usernameDisplay = props.currentUser
      ? props.currentUser.username
      : "$USERNAME";
    const fullCommand = getFullPythonCommand(
      dateSelectorToCli,
      bboxSelectorToCli
    );

    let importStatement;
    if (zarrEnabled && zarrAllowed) {
      importStatement = `from freva_client import authenticate, databrowser\n\n# Authenticate to get token for Zarr streaming\ntoken_info = authenticate(username="${usernameDisplay}", host="${hostName}")\n\n`;
    } else {
      importStatement = "from freva_client import databrowser\n\n";
    }

    const completeCommand = importStatement + fullCommand;

    return (
      <div className="position-relative jupyter-notebook">
        <div className="fw-bold small text-muted mb-1 mt-3">
          {" "}
          Python Command:
        </div>
        <div className="jupyter-cell">
          <div className="jupyter-prompt">In [1]:</div>
          <div className="jupyter-content">
            <div className="jupyter-code">
              <span className="command-option">from freva_client import </span>
              {zarrEnabled && zarrAllowed ? (
                <span className="command-param">authenticate, databrowser</span>
              ) : (
                <span className="command-param">databrowser</span>
              )}
            </div>
          </div>
        </div>

        {zarrEnabled && zarrAllowed && (
          <div className="jupyter-cell">
            <div className="jupyter-prompt">In [2]:</div>
            <div className="jupyter-content">
              <div className="jupyter-code">
                <span className="command-prompt">
                  # Authenticate to get token for Zarr streaming
                </span>
                <br />
                <span className="fw-bold">token_info </span>
                <span className="command-option">= </span>
                <span className="command-param">authenticate</span>
                <span>(username=</span>
                <span className="command-param">{`"${usernameDisplay}"`}</span>
                <span>, host=</span>
                <span className="command-param">{`"${hostName}"`}</span>
                <span>)</span>
              </div>
            </div>
          </div>
        )}

        {databrowserOption === DataBrowserOptions.DEFAULT && (
          <div className="jupyter-cell">
            <div className="jupyter-prompt">
              In [{zarrEnabled ? "3" : "2"}]:
            </div>
            <div className="jupyter-content">
              <div className="jupyter-code">
                <span className="command-param">databrowser</span>
                <span>(</span>
                {props.selectedFlavour !== constants.DEFAULT_FLAVOUR && (
                  <span>
                    <span className="command-option">flavour=</span>
                    <span className="command-param">{`"${props.selectedFlavour}"`}</span>
                    ,{" "}
                  </span>
                )}

                {Object.keys(selectedFacets).map((key) => {
                  const value = selectedFacets[key];
                  return (
                    <React.Fragment key={`python-cmd-${key}`}>
                      <span className="command-option">
                        {props.facetMapping[key]}=
                      </span>
                      <span className="command-param">{`"${value}"`}</span>
                      {<span>, </span>}
                    </React.Fragment>
                  );
                })}

                {props.minDate && (
                  <React.Fragment>
                    <span className="command-option">time=</span>
                    <span className="command-param">{`"${props.minDate} to ${props.maxDate}"`}</span>
                    {(dateSelectorToCli || props.minLon || zarrEnabled) && (
                      <span>, </span>
                    )}
                  </React.Fragment>
                )}

                {dateSelectorToCli && props.minDate && (
                  <React.Fragment>
                    <span className="command-option">time_select=</span>
                    <span className="command-param">{`"${dateSelectorToCli}"`}</span>
                    {(props.minLon || zarrEnabled) && <span>, </span>}
                  </React.Fragment>
                )}

                {props.minLon && (
                  <React.Fragment>
                    <span className="command-option">bbox=</span>
                    <span className="command-param">{`"${props.minLon} ${props.maxLon} ${props.minLat} ${props.maxLat}"`}</span>
                    {(bboxSelectorToCli || zarrEnabled) && <span>, </span>}
                  </React.Fragment>
                )}

                {bboxSelectorToCli && props.minLon && (
                  <React.Fragment>
                    <span className="command-option">bbox_select=</span>
                    <span className="command-param">{`"${bboxSelectorToCli}"`}</span>
                    {zarrEnabled && <span>, </span>}
                  </React.Fragment>
                )}

                {zarrEnabled && (
                  <React.Fragment>
                    <span className="command-option">zarr_stream=</span>
                    <span className="fw-bold">True</span>
                    <span>, </span>
                  </React.Fragment>
                )}
                <React.Fragment>
                  <span className="command-option">host=</span>
                  <span className="fw-bold">{`"${hostName}"`}</span>
                </React.Fragment>
                <span>)</span>
              </div>
            </div>
          </div>
        )}

        {(databrowserOption === DataBrowserOptions.INTAKE ||
          databrowserOption === DataBrowserOptions.STAC) && (
          <>
            <div className="jupyter-cell">
              <div className="jupyter-prompt">
                In [{zarrEnabled ? "3" : "2"}]:
              </div>
              <div className="jupyter-content">
                <div className="jupyter-code">
                  <span className="fw-bold">db </span>
                  <span className="command-option">= </span>
                  <span className="command-param">databrowser</span>
                  <span>(</span>
                  {props.selectedFlavour !== constants.DEFAULT_FLAVOUR && (
                    <span>
                      <span className="command-option">flavour=</span>
                      <span className="command-param">{`"${props.selectedFlavour}"`}</span>
                      ,{" "}
                    </span>
                  )}

                  {Object.keys(selectedFacets).map((key, index) => {
                    const value = selectedFacets[key];
                    const isLast =
                      index === Object.keys(selectedFacets).length - 1 &&
                      !props.minDate &&
                      !props.minLon;
                    return (
                      <React.Fragment key={`python-cmd-${key}`}>
                        <span className="command-option">
                          {props.facetMapping[key]}=
                        </span>
                        <span className="command-param">{`"${value}"`}</span>
                        {!isLast && <span>, </span>}
                      </React.Fragment>
                    );
                  })}

                  {props.minDate && (
                    <React.Fragment>
                      <span className="command-option">time=</span>
                      <span className="command-param">{`"${props.minDate} to ${props.maxDate}"`}</span>
                      {(dateSelectorToCli || props.minLon) && <span>, </span>}
                    </React.Fragment>
                  )}

                  {dateSelectorToCli && props.minDate && (
                    <React.Fragment>
                      <span className="command-option">time_select=</span>
                      <span className="command-param">{`"${dateSelectorToCli}"`}</span>
                      {props.minLon && <span>, </span>}
                    </React.Fragment>
                  )}

                  {props.minLon && (
                    <React.Fragment>
                      <span className="command-option">bbox=</span>
                      <span className="command-param">{`"${props.minLon} ${props.maxLon} ${props.minLat} ${props.maxLat}"`}</span>
                      {bboxSelectorToCli && <span>, </span>}
                    </React.Fragment>
                  )}

                  {bboxSelectorToCli && props.minLon && (
                    <React.Fragment>
                      <span className="command-option">bbox_select=</span>
                      <span className="command-param">{`"${bboxSelectorToCli}"`}</span>
                    </React.Fragment>
                  )}
                  <span>, </span>
                  <React.Fragment>
                    <span className="command-option">host=</span>
                    <span className="command-param">{`"${hostName}"`}</span>
                  </React.Fragment>
                  <span>)</span>
                </div>
              </div>
            </div>

            <div className="jupyter-cell">
              <div className="jupyter-prompt">
                In [{zarrEnabled ? "4" : "3"}]:
              </div>
              <div className="jupyter-content">
                <div className="jupyter-code">
                  {databrowserOption === DataBrowserOptions.INTAKE ? (
                    <>
                      <span className="fw-bold">cat </span>
                      <span className="command-option">= </span>
                      <span className="command-param">db.intake_catalogue</span>
                      <span>(</span>
                      {zarrEnabled && (
                        <React.Fragment>
                          <span className="command-option">stream_zarr=</span>
                          <span className="fw-bold">True</span>
                        </React.Fragment>
                      )}
                      <span>)</span>
                    </>
                  ) : (
                    // TODO: Add STAC. Currently STAC never gets a stream_zarr flag
                    <span className="command-param">db.stac_catalogue()</span>
                  )}
                </div>
              </div>
            </div>

            {databrowserOption === DataBrowserOptions.INTAKE && (
              <div className="jupyter-cell">
                <div className="jupyter-prompt">
                  In [{zarrEnabled ? "5" : "4"}]:
                </div>
                <div className="jupyter-content">
                  <div className="jupyter-code">
                    <span className="command-option">print</span>
                    <span>(</span>
                    <span className="command-param">cat.df</span>
                    <span>)</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div style={{ marginBottom: "40px" }}></div>
        <Button
          size="sm"
          variant="outline-secondary"
          className="position-absolute"
          style={{ top: "-2px", right: "2px", padding: "0.1rem 0.3rem" }}
          onClick={() => handleCopy(completeCommand)}
        >
          {copying ? <FaCheck size={12} /> : <FaRegClone size={12} />}
        </Button>
        <Button
          variant="primary"
          className="position-absolute d-flex align-items-center"
          style={{ bottom: "-35px", right: "2px", padding: "0.1rem 0.3rem" }}
          onClick={executeCommand}
        >
          <FaPlay className="me-1" /> Execute Command
        </Button>
      </div>
    );
  }

  function getFullApiCommand(dateSelectorToCli, bboxSelectorToCli) {
    const queryParams = [];

    Object.keys(selectedFacets).forEach((key) => {
      const value = selectedFacets[key];
      queryParams.push(
        `${props.facetMapping[key]}=${encodeURIComponent(value)}`
      );
    });

    if (props.minDate) {
      queryParams.push(`time=${props.minDate}to${props.maxDate}`);
      if (dateSelectorToCli) {
        queryParams.push(`time_select=${dateSelectorToCli}`);
      }
    }

    if (props.minLon) {
      queryParams.push(
        `bbox=${props.minLon},${props.maxLon},${props.minLat},${props.maxLat}`
      );
      if (bboxSelectorToCli) {
        queryParams.push(`bbox_select=${bboxSelectorToCli}`);
      }
    }

    const flavourPath =
      props.selectedFlavour !== constants.DEFAULT_FLAVOUR
        ? `/${props.selectedFlavour}`
        : `/${constants.DEFAULT_FLAVOUR}`;

    let endpoint = "";
    if (databrowserOption === DataBrowserOptions.DEFAULT) {
      endpoint = `/api/freva-nextgen/data-search${flavourPath}/file`;
      if (zarrEnabled && zarrAllowed) {
        endpoint = `/api/freva-nextgen/load${flavourPath}`;
      }
    } else if (databrowserOption === DataBrowserOptions.INTAKE) {
      endpoint = `/api/freva-nextgen/intake-catalogue${flavourPath}/file`;
      if (zarrEnabled && zarrAllowed) {
        endpoint = `/api/freva-nextgen/load${flavourPath}`;
        queryParams.push("catalogue-type=intake");
      }
    } else if (databrowserOption === DataBrowserOptions.STAC) {
      // TODO: STAC would be added in the future
      endpoint = `/api/freva-nextgen/stac-catalogue${flavourPath}/file`;
    }

    return `${endpoint}?${queryParams.join("&")}`;
  }

  function getCurlCommand(apiUrl) {
    const usernameDisplay = props.currentUser
      ? props.currentUser.username
      : "$USERNAME";

    if (zarrEnabled && zarrAllowed) {
      return `# First get authentication token\ncurl -X POST /api/freva-nextgen/auth/v2/token \\\n  -d "username=${usernameDisplay}" \\\n  -d "password=YOUR_PASSWORD"\n\n# Then use the token with the API\ncurl -X GET "${apiUrl}" \\\n  -H "accept: application/json" \\\n  -H "Authorization: Bearer {access_token}"`;
    }
    return `curl -X GET "${apiUrl}" -H "accept: application/json"`;
  }

  function renderApiCommand() {
    const dateSelectorToCli = getCliTimeSelector();
    const bboxSelectorToCli = getCliBBoxSelector();

    const apiUrl = getFullApiCommand(dateSelectorToCli, bboxSelectorToCli);
    const curlCommand = getCurlCommand(apiUrl);
    const usernameDisplay = props.currentUser
      ? props.currentUser.username
      : "$USERNAME";

    return (
      <div className="position-relative">
        <div className="mb-4">
          <div className="fw-bold small text-muted mb-1 mt-3">
            API Endpoint:
          </div>
          <pre
            className="mb-5 command-terminal"
            style={{ whiteSpace: "pre-wrap" }}
          >
            {zarrEnabled && zarrAllowed ? (
              <React.Fragment>
                <span className="command-prompt">
                  # First get authentication token
                </span>
                <br />
                <span className="command-prompt">$ </span>
                <span className="command-option">curl -X POST </span>
                <span className="command-param">
                  /api/freva-nextgen/auth/v2/token{" "}
                </span>
                <span>\</span>
                <br />
                <span> -d </span>
                <span className="command-param">
                  &quot;username={usernameDisplay}&quot;{" "}
                </span>
                <span>\</span>
                <br />
                <span> -d </span>
                <span className="command-param">
                  &quot;password=$PASSWORD&quot;
                </span>
                <br />
                <br />
                <span className="command-prompt">
                  # Then use the token with the API
                </span>
                <br />
                <span className="command-prompt">$ </span>
                <span className="command-option">curl -X GET </span>
                <span className="command-param">&quot;{apiUrl}&quot; </span>
                <span>\</span>
                <br />
                <span> -H </span>
                <span className="command-param">
                  &quot;accept: application/json&quot;{" "}
                </span>
                <span>\</span>
                <br />
                <span> -H </span>
                <span className="command-param">
                  &quot;Authorization: Bearer {"{"}
                  {"{"}access_token{"}"}
                  {"}"}&quot;
                </span>
              </React.Fragment>
            ) : (
              <React.Fragment>
                <span className="command-prompt">$ </span>
                <span className="command-option">curl -X GET </span>
                <span className="command-param">&quot;{apiUrl}&quot; </span>
                <span>-H </span>
                <span className="command-param">
                  &quot;accept: application/json&quot;
                </span>
              </React.Fragment>
            )}
          </pre>
        </div>
        <Button
          size="sm"
          variant="outline-secondary"
          className="position-absolute"
          style={{ top: "-2px", right: "2px", padding: "0.1rem 0.3rem" }}
          onClick={() => handleCopy(curlCommand)}
        >
          {copying ? <FaCheck size={12} /> : <FaRegClone size={12} />}
        </Button>
        <Button
          variant="primary"
          className="position-absolute d-flex align-items-center"
          style={{ bottom: "-35px", right: "2px", padding: "0.1rem 0.3rem" }}
          onClick={executeCommand}
        >
          <FaPlay className="me-1" /> Execute Command
        </Button>
      </div>
    );
  }
  const dateSelectorToCli = getCliTimeSelector();
  const bboxSelectorToCli = getCliBBoxSelector();

  // For the catalog dropdown createCatalogLink function
  function createCatalogLink(type) {
    // figure out flavour path
    const flavour =
      props.selectedFlavour !== constants.DEFAULT_FLAVOUR
        ? props.selectedFlavour
        : constants.DEFAULT_FLAVOUR;

    // we need a uniq_key for the path-based endpoints:
    const locationObj = {
      pathname: window.location.pathname,
      query: {
        flavour,
        ...selectedFacets,
        minDate: props.minDate,
        maxDate: props.maxDate,
        dateSelector: dateSelectorToCli,
        minLon: props.minLon,
        maxLon: props.maxLon,
        minLat: props.minLat,
        maxLat: props.maxLat,
        bboxSelector: bboxSelectorToCli,
      },
    };
    const uniq_key = prepareSearchParams(locationObj, "translate=false");

    if (type === "intake") {
      if (zarrEnabled && zarrAllowed) {
        // it's always constant for the API
        const queryParams = [`catalogue-type=intake`];

        // add search parameters to load endpoint
        // other search parameters
        Object.keys(selectedFacets).forEach((key) => {
          queryParams.push(
            `${props.facetMapping[key]}=${encodeURIComponent(selectedFacets[key])}`
          );
        });

        // date and bbox parameters if they exist
        if (props.minDate) {
          queryParams.push(`time=${props.minDate}to${props.maxDate}`);
          if (dateSelectorToCli) {
            queryParams.push(`time_select=${dateSelectorToCli}`);
          }
        }

        if (props.minLon) {
          queryParams.push(
            `bbox=${props.minLon},${props.maxLon},${props.minLat},${props.maxLat}`
          );
          if (bboxSelectorToCli) {
            queryParams.push(`bbox_select=${bboxSelectorToCli}`);
          }
        }

        return `/api/freva-nextgen/databrowser/load/${flavour}?${queryParams.join("&")}`;
      } else {
        // intake-catalogue without zarr
        return `/api/freva-nextgen/databrowser/intake-catalogue/${uniq_key}`;
      }
    }

    if (type === "stac") {
      // always path‐based, no zarr
      return `/api/freva-nextgen/databrowser/stac-catalogue/${uniq_key}`;
    }

    // fallback (should never hit for catalog dropdown)
    return "#";
  }

  return (
    <React.Fragment>
      {/* TODO: we probably have to move this style to a proper place in the future */}
      <style>
        {`
          .form-switch .form-check-input {
            cursor: pointer;
          }
          .form-switch .form-check-input:checked {
            background-color: #0d6efd;
            border-color: #0d6efd;
          }
          .zarr-toggle-wrapper {
            transition: all 0.3s ease;
          }
          .zarr-toggle-wrapper:hover {
            background-color: #f8f9fa;
            border-radius: 4px;
          }
          .command-terminal {
            background-color: #1e1e1e;
            color: #f0f0f0;
            border-radius: 4px;
            padding: 12px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          }
          
          .command-terminal .command-prompt {
            color: #5eadf5;
            font-weight: bold;
          }
          
          .command-terminal .command-param {
            color: #ce9178;
          }
          
          .command-terminal .command-option {
            color: #dcdcaa;
          }
          
          .command-terminal .fw-bold {
            color: #9cdcfe;
          }
          
          .command-terminal .text-primary {
            color: #6a9955 !important;
          }
          
          .command-auth {
            background-color: #252526;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 15px;
            border-left: 3px solid #0d6efd;
          }
          .jupyter-notebook {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin-bottom: 20px;
          }
          .jupyter-notebook .position-absolute.d-flex.align-items-center {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 1rem;
            font-weight: 400;
          }
          .jupyter-cell {
            display: flex;
            margin-bottom: 8px;
            position: relative;
          }
          
          .jupyter-prompt {
            width: 80px;
            text-align: right;
            color: #4e90c9;
            font-weight: bold;
            padding: 8px 8px 8px 0;
            user-select: none;
          }
          
          .jupyter-content {
            flex: 1;
            border: 1px solid #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
          }
          
          .jupyter-code {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            background-color: #f7f7f7;
            color: #333333;
            padding: 8px 10px;
            white-space: pre-wrap;
          }
          
          .jupyter-code .command-option {
            color: #9c5d27;
          }
          
          .jupyter-code .command-param {
            color: #2c85f7;
          }
          
          .jupyter-code .fw-bold {
            color: #208b4c;
          }
          
          .jupyter-code .command-prompt {
            color: #888888;
            font-style: italic;
          }
          .trigger-button {
            width: 36px;
            height: 36px;
            cursor: pointer;
          }
          .catalogue-type-select {
            min-width: 140px;
            margin-right: 8px;
          }
        `}
      </style>
      <Card className={"p-3 py-2 d-block shadow-sm " + props.className}>
        <div className="fw-bold d-flex flex-wrap justify-content-between align-items-center border-bottom pb-2 mb-2">
          <div className="me-2 mb-2">Freva databrowser</div>
          <div className="d-flex flex-wrap align-items-center">
            {!isStac && (
              <div className="zarr-toggle-wrapper px-2 py-1 me-2 mb-2 d-flex flex-column align-items-center justify-content-center">
                <OverlayTrigger
                  overlay={
                    <Tooltip>
                      {isGuest
                        ? "Zarr streaming is not available for guest users"
                        : "Enable Zarr streaming for cloud-optimized data access"}
                    </Tooltip>
                  }
                >
                  <span
                    className={
                      zarrEnabled
                        ? "text-primary fw-bold mb-1"
                        : isGuest
                          ? "text-muted opacity-50 mb-1"
                          : "text-muted mb-1"
                    }
                    style={{ cursor: "help" }}
                  >
                    <ZarrStreamIcon />
                  </span>
                </OverlayTrigger>
                <Form.Check
                  type="switch"
                  id="zarr-streaming-toggle"
                  checked={zarrEnabled}
                  disabled={isGuest}
                  onChange={() => {
                    const next = !zarrEnabled;
                    // write or remove ?zarr_stream=true
                    const base = window.location.pathname;
                    const q = { ...props.location.query };
                    if (next) {
                      q.zarr_stream = "true";
                    } else {
                      delete q.zarr_stream;
                    }
                    props.router.push(
                      base +
                        (queryString.stringify(q)
                          ? `?${queryString.stringify(q)}`
                          : "")
                    );
                  }}
                  style={{
                    marginBottom: 0,
                    marginTop: "-15px",
                    marginLeft: "6px",
                  }}
                />
              </div>
            )}
            <DataBrowserOptionsDropdown
              disabled={props.numFiles > STREAM_CATALOGUE_MAXIMUM}
              createCatalogLink={props.createCatalogLink || createCatalogLink}
              numFiles={props.numFiles}
              maxFiles={STREAM_CATALOGUE_MAXIMUM}
              className="me-2 mb-2"
              onOptionChange={handleDataBrowserOptionChange}
              activeOption={activeOption}
            />
            <OverlayTrigger overlay={<Tooltip>Show CLI command</Tooltip>}>
              <Button
                className="trigger-button me-1 mb-2 d-flex align-items-center justify-content-center"
                active={mode === Modes.CLI}
                variant="outline-secondary"
                onClick={() => setMode(Modes.CLI)}
              >
                <div>
                  <FaTerminal className="fs-5" />
                </div>
              </Button>
            </OverlayTrigger>

            <OverlayTrigger overlay={<Tooltip>Show Python command</Tooltip>}>
              <Button
                className="trigger-button me-1 mb-2 d-flex align-items-center justify-content-center"
                active={mode === Modes.PYTHON}
                variant="outline-secondary"
                onClick={() => setMode(Modes.PYTHON)}
              >
                <div>
                  <FaPython className="fs-5" />
                </div>
              </Button>
            </OverlayTrigger>

            <OverlayTrigger overlay={<Tooltip>Show API endpoint</Tooltip>}>
              <Button
                className="trigger-button me-1 mb-2 d-flex align-items-center justify-content-center"
                active={mode === Modes.API}
                variant="outline-secondary"
                onClick={() => setMode(Modes.API)}
              >
                <div>
                  <HiCode className="fs-5" />
                </div>
              </Button>
            </OverlayTrigger>
          </div>
        </div>
        {mode === Modes.CLI && renderCLICommand()}
        {mode === Modes.PYTHON && renderPythonCommand()}
        {mode === Modes.API && renderApiCommand()}
      </Card>
      <ClipboardToast show={showToast} setShow={setShowToast} />
    </React.Fragment>
  );
}

DataBrowserCommandImpl.propTypes = {
  className: PropTypes.string,
  selectedFacets: PropTypes.object,
  dateSelector: PropTypes.string,
  minDate: PropTypes.string,
  maxDate: PropTypes.string,
  bboxSelector: PropTypes.string,
  minLon: PropTypes.string,
  maxLon: PropTypes.string,
  minLat: PropTypes.string,
  maxLat: PropTypes.string,
  selectedFlavour: PropTypes.string,
  facetMapping: PropTypes.object,
  numFiles: PropTypes.number,
  createCatalogLink: PropTypes.func,
  location: PropTypes.object,
  router: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }),
  currentUser: PropTypes.shape({
    id: PropTypes.number,
    username: PropTypes.string,
    email: PropTypes.string,
    home: PropTypes.string,
    scratch: PropTypes.string,
  }),
};

const mapStateToProps = (state) => ({
  selectedFacets: state.databrowserReducer.selectedFacets,
  dateSelector: state.databrowserReducer.dateSelector,
  minDate: state.databrowserReducer.minDate,
  maxDate: state.databrowserReducer.maxDate,
  bboxSelector: state.databrowserReducer.bboxSelector,
  minLon: state.databrowserReducer.minLon,
  maxLon: state.databrowserReducer.maxLon,
  minLat: state.databrowserReducer.minLat,
  maxLat: state.databrowserReducer.maxLat,
  facetMapping: state.databrowserReducer.facetMapping,
  selectedFlavour: state.databrowserReducer.selectedFlavour,
  numFiles: state.databrowserReducer.numFiles,
  currentUser: state.appReducer.currentUser,
});

export default withRouter(connect(mapStateToProps)(DataBrowserCommandImpl));
