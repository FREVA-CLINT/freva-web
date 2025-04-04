import React from "react";
import PropTypes from "prop-types";
import { OverlayTrigger, Tooltip, Dropdown } from "react-bootstrap";
import { FaFileExport } from "react-icons/fa";

import IntakeIcon from "../../Icons/IntakeIcon";
import STACSTATICIcon from "../../Icons/STACSTATICIcon";
import STACDYNAMICIcon from "../../Icons/STACDYNAMICIcon";

import { ENABLE_STAC_API, STAC_API_MAXIMUM } from "./constants";

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
      <FaFileExport className="fs-5 me-2" />
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
    <Icon className="me-2" />
    <span>{children}</span>
  </div>
);

DropdownItemContent.propTypes = {
  icon: PropTypes.elementType.isRequired,
  children: PropTypes.node.isRequired,
};

const CatalogExportDropdown = ({
  disabled = false,
  createCatalogLink,
  numFiles,
  maxFiles,
  className,
}) => {
  const isDisabled = disabled || numFiles > maxFiles;
  const isDynamicDisabled = numFiles > STAC_API_MAXIMUM;

  return (
    <Dropdown className={className}>
      <OverlayTrigger
        overlay={
          isDisabled ? (
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
          <Dropdown.Toggle as={CustomToggle} disabled={isDisabled}>
            Export Catalog
          </Dropdown.Toggle>
        </span>
      </OverlayTrigger>

      {!isDisabled && (
        <Dropdown.Menu style={{ minWidth: "200px" }}>
          <Dropdown.Item
            href={createCatalogLink("intake")}
            target="_blank"
            rel="noopener noreferrer"
          >
            <DropdownItemContent icon={IntakeIcon}>
              Intake Catalog
            </DropdownItemContent>
          </Dropdown.Item>

          <Dropdown.Divider />
          <Dropdown.Header className="fw-bold">STAC Catalog</Dropdown.Header>

          <Dropdown.Item
            href={createCatalogLink("stac")}
            target="_blank"
            rel="noopener noreferrer"
          >
            <DropdownItemContent icon={STACSTATICIcon}>
              Static STAC
            </DropdownItemContent>
          </Dropdown.Item>

          {ENABLE_STAC_API && (
            <OverlayTrigger
              overlay={
                isDynamicDisabled ? (
                  <Tooltip>
                    Please narrow down your search to a maximum of{" "}
                    {STAC_API_MAXIMUM} results to enable Dynamic STAC
                  </Tooltip>
                ) : (
                  <></>
                )
              }
            >
              <span className="d-block">
                <Dropdown.Item
                  href={
                    !isDynamicDisabled ? createCatalogLink("stac", true) : "#"
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                  disabled={isDynamicDisabled}
                  style={
                    isDynamicDisabled
                      ? { pointerEvents: "none", opacity: 0.65 }
                      : {}
                  }
                >
                  <DropdownItemContent icon={STACDYNAMICIcon}>
                    Dynamic STAC
                  </DropdownItemContent>
                </Dropdown.Item>
              </span>
            </OverlayTrigger>
          )}
        </Dropdown.Menu>
      )}
    </Dropdown>
  );
};

CatalogExportDropdown.propTypes = {
  disabled: PropTypes.bool,
  createCatalogLink: PropTypes.func.isRequired,
  numFiles: PropTypes.number.isRequired,
  maxFiles: PropTypes.number.isRequired,
  className: PropTypes.string,
};

export default CatalogExportDropdown;
