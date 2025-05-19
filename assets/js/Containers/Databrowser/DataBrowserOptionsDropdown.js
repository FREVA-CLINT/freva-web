import React from "react";
import PropTypes from "prop-types";
import { OverlayTrigger, Tooltip, Dropdown } from "react-bootstrap";

import IntakeIcon from "../../Icons/IntakeIcon";
import STACIcon from "../../Icons/STACIcon";
import FrevaIcon from "../../Icons/FrevaIcon";

const CustomToggle = React.forwardRef(
  ({ children, onClick, disabled, className }, ref) => (
    <button
      type="button"
      className={`btn btn-outline-secondary d-inline-flex align-items-center ${className}`}
      ref={ref}
      onClick={(e) => {
        e.preventDefault();
        onClick(e);
      }}
      disabled={disabled}
    >
      {children}
    </button>
  )
);

CustomToggle.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  className: PropTypes.string,
};

CustomToggle.displayName = "CustomToggle";

const DropdownItemContent = ({ icon: Icon, children }) => (
  <div className="d-flex align-items-center">
    <div
      className="d-flex align-items-center justify-content-center"
      style={{ width: "40px" }}
    >
      <Icon className="me-2" />
    </div>
    <span>{children}</span>
  </div>
);

DropdownItemContent.propTypes = {
  icon: PropTypes.elementType.isRequired,
  children: PropTypes.node.isRequired,
};

const DataBrowserOptionsDropdown = ({
  disabled = false,
  numFiles,
  maxFiles,
  className,
  createCatalogLink,
  onOptionChange, // for integration with DataBrowserCommand
  activeOption = "search",
}) => {
  const isDisabled = disabled || numFiles > maxFiles;

  // current icon and button text based on active option
  let ButtonIcon;
  let buttonText;

  switch (activeOption) {
    case "intake":
      ButtonIcon = IntakeIcon;
      buttonText = "Intake Catalog";
      break;
    case "stac":
      ButtonIcon = STACIcon;
      buttonText = "STAC Catalog";
      break;
    case "search":
    default:
      ButtonIcon = FrevaIcon;
      buttonText = "Data Search";
  }

  const handleItemClick = (option, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    // update the active option
    onOptionChange(option);

    // close dropdown. it simulates a click outside
    // the dropdown to close it
    document.body.click();
  };

  return (
    <Dropdown className={className}>
      <OverlayTrigger
        overlay={
          isDisabled && activeOption !== "search" ? (
            <Tooltip>
              Please narrow down your search to a maximum of 100,000 results to
              enable catalog exports
            </Tooltip>
          ) : (
            <></>
          )
        }
      >
        <span>
          <Dropdown.Toggle
            as={CustomToggle}
            disabled={isDisabled && activeOption !== "search"}
          >
            <div className="d-flex align-items-center">
              <div
                className="d-flex align-items-center justify-content-center"
                style={{ width: "45px" }}
              >
                <ButtonIcon className="fs-5" />
              </div>
              <span className="ms-2">{buttonText}</span>
            </div>
          </Dropdown.Toggle>
        </span>
      </OverlayTrigger>

      <Dropdown.Menu style={{ minWidth: "200px" }}>
        <Dropdown.Item
          onClick={(e) => handleItemClick("search", e)}
          active={activeOption === "search"}
        >
          <DropdownItemContent icon={FrevaIcon}>
            Data Search
          </DropdownItemContent>
        </Dropdown.Item>

        {isDisabled ? (
          <OverlayTrigger
            overlay={
              <Tooltip>
                Please narrow down your search to a maximum of 100,000 results
                to enable catalog exports
              </Tooltip>
            }
          >
            <div>
              <Dropdown.Item
                onClick={(e) => e.preventDefault()}
                active={activeOption === "intake"}
                disabled
              >
                <DropdownItemContent icon={IntakeIcon}>
                  Intake Catalog
                </DropdownItemContent>
              </Dropdown.Item>
            </div>
          </OverlayTrigger>
        ) : (
          <Dropdown.Item
            onClick={(e) => handleItemClick("intake", e)}
            active={activeOption === "intake"}
            disabled={false}
            href={createCatalogLink("intake")}
            target="_blank"
            rel="noopener noreferrer"
          >
            <DropdownItemContent icon={IntakeIcon}>
              Intake Catalog
            </DropdownItemContent>
          </Dropdown.Item>
        )}

        {isDisabled ? (
          <OverlayTrigger
            overlay={
              <Tooltip>
                Please narrow down your search to a maximum of 100,000 results
                to enable catalog exports
              </Tooltip>
            }
          >
            <div>
              <Dropdown.Item
                onClick={(e) => e.preventDefault()}
                active={activeOption === "stac"}
                disabled
              >
                <DropdownItemContent icon={STACIcon}>
                  STAC Catalog
                </DropdownItemContent>
              </Dropdown.Item>
            </div>
          </OverlayTrigger>
        ) : (
          <Dropdown.Item
            onClick={(e) => handleItemClick("stac", e)}
            active={activeOption === "stac"}
            disabled={false}
            href={createCatalogLink("stac")}
            target="_blank"
            rel="noopener noreferrer"
          >
            <DropdownItemContent icon={STACIcon}>
              STAC Catalog
            </DropdownItemContent>
          </Dropdown.Item>
        )}
      </Dropdown.Menu>
    </Dropdown>
  );
};

DataBrowserOptionsDropdown.propTypes = {
  disabled: PropTypes.bool,
  createCatalogLink: PropTypes.func.isRequired,
  numFiles: PropTypes.number.isRequired,
  maxFiles: PropTypes.number.isRequired,
  className: PropTypes.string,
  onOptionChange: PropTypes.func,
  activeOption: PropTypes.string,
};

export default DataBrowserOptionsDropdown;
