# App Workspaces

Each application keeps its own configuration, profile, archived inputs and generated outputs in this folder.

- `AR_Filter/`
- `Control_Widget/`
- `Game_Emulator/`
- `Prank_Sounds/`
- `App_Template/`

Use the root `run_aso_filter.py` orchestrator for normal execution. Add new app aliases and runner paths in `shared/app_registry.py`.

All app runners must use the shared `keyword_filter` engine. Truncation handling is centralized there so complete tokens such as `emoji`, `icon`, `sound`, `filter`, and `widget` are not dropped as broken prefixes across apps or locales.
