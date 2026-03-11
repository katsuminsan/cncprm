# cncprm_tool

Lightweight Python library for parsing and editing CNC parameter files in the **cncprm format**.

Design goals:

- No external dependencies
- Round-trip safe (preserve origianl formatting when unchanged)
- Immutable domain models
- Builder pattern for editting
- Extensible architecture for future ParamSpec / BitSpec integration

