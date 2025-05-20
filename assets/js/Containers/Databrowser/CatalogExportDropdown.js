import React from "react";
import PropTypes from "prop-types";
import { OverlayTrigger, Tooltip, Dropdown } from "react-bootstrap";
import { FaFileExport } from "react-icons/fa";

import IntakeIcon from "../../Icons/IntakeIcon";
import STACIcon from "../../Icons/STACIcon";

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

          <Dropdown.Item
            href={createCatalogLink("stac")}
            target="_blank"
            rel="noopener noreferrer"
          >
            <DropdownItemContent icon={STACIcon}>
              STAC Catalog
            </DropdownItemContent>
          </Dropdown.Item>
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
