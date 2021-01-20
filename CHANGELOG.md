# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Added
- Internationalization
- CLI_LOCALE environment variable
- Users can receive notifications
- Users can toggle notifications by using the /settings command
- Bot can forward messages without forward signature.
### Removed
- Channels administrators can no longer set a custom time range 
### Fixed
- Improved speed and reliability

## [0.1.0] - 2020-09-19
### Added
- Channel admins can now view detailed informations with /info (e.g. whether they can send messages or not);
- Admins can now change the settings with /settings
### Fixed
- The "Go to the message" button should redirect successfully now;
### Changed
- The NETWORK_SHORT_NAME environment variable is now optional

## [0.1.0-alpha] - 2020-09-05
Initial release
