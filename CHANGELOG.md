# Changelog



All notable changes to this project will be documented in this file.

## [v2507.0.0]
## Added
- STAC Browser as a SPA
- Local ssh feature where the core lib is running on the same machin
- add development env for production chatbot

## Changed
- Turn token button into user dropdown button
- Change the Freva databrowser command display based on the neew freva-client
- After token expiration, user redirected to the home page instead of login page
- Help page stays always, the last item on the navbar

## Fixed
- Internal auth hotfix
- Getting the Freva RestAPI link through STAC-API self-link
- Protect the main layout from the changes that are coing through SPA
- 

## [v2506.0.1]
## Fixes
- Try to get information on the user via SSSD

## [v2506.0.0]
## Added
- Introduced a new component called FrevaGPT.
- Implemented authentication based on the auth-flow of the Freva-Nextgen REST API.
- Added a Token button next to the user account menu, allowing users to copy or download their access token and refresh token for use with the Freva CLI and Python client.
- Guest users are now automatically recognized via the SystemUser endpoint.
- Made the Plug-My-Plugin available to all users.

## [v2505.0.0]
## Changed
- Fix an issue on BBOX and removed the minor leftover of STAC-API

## [v2504.0.0]
## Changed
- Dropped STAC-API and supported only STATIC catalog

## [v2502.0.0]
## Changed
- Adjusted SelectField widget to support multiple inputs

## [v2411.0.0]
## Changed
- Create STAC API
- Add opensearch functionlity
- Limit opensearch entries to 1000 by default

## [v2408.0.0]

### Changed
- Use sendgrid to send emails.
- Use freva-rest API to manage authentication.


## [v2405.0.0]

### Fixed
- Fixed databrowser bug causing a NaN in the `found results`-number

### Changed
- Infrastructure like LDAP servers, cache server etc are passed via env
  variables.

## [v2403.0.0]

### Added
- Change lock file, to keep track of changes.


# Template:
## [Unreleased]

### Added
- New feature X.
- New feature Y.

### Changed
- Improved performance in component A.
- Updated dependency B to version 2.0.0.

### Fixed
- Fixed issue causing application crash on startup.
- Fixed bug preventing users from logging in.
