import os
import re


APP_REGISTRY = {
    "ar_filter": {
        "folder": "apps/AR_Filter",
        "runner": "apps/AR_Filter/run_ar_filter_v4_0.py",
        "config": "apps/AR_Filter/app_config.py",
        "aliases": ["ARFilter", "AR_Filter"],
    },
    "game_emulator": {
        "folder": "apps/Game_Emulator",
        "runner": "apps/Game_Emulator/run_game_emulator_v4_0.py",
        "config": "apps/Game_Emulator/app_config.py",
        "aliases": ["GameEmulator", "GameRetro", "Game_Emulator"],
    },
    "prank_sounds": {
        "folder": "apps/Prank_Sounds",
        "runner": "apps/Prank_Sounds/run_pipeline.py",
        "config": "apps/Prank_Sounds/app_config.py",
        "aliases": ["Pranky", "PrankSounds", "Prank_Sounds"],
    },
    "control_widget": {
        "folder": "apps/Control_Widget",
        "runner": "apps/Control_Widget/run_control_widget_v4_0.py",
        "config": "apps/Control_Widget/app_config.py",
        "aliases": ["ControlWidget", "Control_Widget"],
    },
    "app_template": {
        "folder": "apps/App_Template",
        "runner": "apps/App_Template/run_pipeline.py",
        "config": "apps/App_Template/app_config.py",
        "aliases": ["AppTemplate", "App_Template"],
    },
}


def normalize_alias(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def resolve_app(alias, project_root=None):
    normalized = normalize_alias(alias)
    for app_key, entry in APP_REGISTRY.items():
        aliases = [app_key, entry["folder"], *entry.get("aliases", [])]
        if normalized in {normalize_alias(candidate) for candidate in aliases}:
            resolved = dict(entry)
            resolved["key"] = app_key
            if project_root:
                resolved["runner_path"] = os.path.join(project_root, *entry["runner"].split("/"))
                resolved["config_path"] = os.path.join(project_root, *entry["config"].split("/"))
            return resolved
    raise KeyError(f"Unknown app alias '{alias}'. Registered aliases: {registered_aliases()}")


def registered_aliases():
    return sorted(alias for entry in APP_REGISTRY.values() for alias in entry.get("aliases", []))
