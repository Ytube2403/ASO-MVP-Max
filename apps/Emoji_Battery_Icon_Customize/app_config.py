# -*- coding: utf-8 -*-
"""
ASO Keyword Planner - App Configuration File
Version: 4.1
Purpose: Configuration file for deploying ASO Keyword Planner on Emoji Battery Icon Customize.
"""
import sys

# Determine the market from sys.argv
_market = "US_EN"
for _i, _arg in enumerate(sys.argv):
    if _arg == "--market" and _i + 1 < len(sys.argv):
        _market = sys.argv[_i+1].upper()
        break
    elif "--csv" in _arg and _i + 1 < len(sys.argv):
        _csv_path = sys.argv[_i+1]
        if "ES-US" in _csv_path or "ES_US" in _csv_path:
            _market = "ES_US"

# If running for a Spanish market, make Spanish primary and English secondary
if "ES" in _market or "MX" in _market:
    _primary = ["es"]
    _secondary = ["en"]
    _core_intent = [
        "baterÃ­a emoji", "widget de baterÃ­a", "icono de baterÃ­a", "personalizar baterÃ­a",
        "estado de la baterÃ­a", "barra de estado emoji", "stickers emoji", "calcomanÃ­as emoji",
        "emoji battery", "emoji battery widget", "emoji battery status bar", "emoji battery icon",
        "custom battery icon", "battery icon customize", "emoji widget", "funny status bar",
        "custom status bar", "emoji status bar", "emoji sticker", "emoji stickers"
    ]
    _feature = [
        "emojis animados", "nivel de baterÃ­a", "barra de notificaciones",
        "personalizar Ã­cono", "muesca", "gestos de deslizamiento",
        "personalizar notch", "animated emojis", "gesture shortcuts", "notch customizer",
        "status bar stickers", "battery level"
    ]
    _style = [
        "lindos", "divertidos", "diseÃ±o lindo", "temas emojis", "kawaii faces", "pastel style"
    ]
    _visual = [
        "esquinas redondeadas", "diseÃ±o de corazÃ³n", "notch personalizado",
        "rounded corners", "heart shapes", "custom notch"
    ]
elif "VI" in _market or "VN" in _market:
    _primary = ["vi"]
    _secondary = ["en"]
    _core_intent = [
        "pin emoji", "widget pin", "tiện ích pin", "icon pin", "đổi icon pin", "thanh trạng thái",
        "nhãn dán emoji", "sticker emoji", "emoji battery", "emoji battery widget", "emoji battery status bar",
        "emoji battery icon", "custom battery icon", "battery icon customize", "emoji widget",
        "funny status bar", "custom status bar", "emoji status bar", "emoji sticker", "emoji stickers"
    ]
    _feature = [
        "hiệu ứng sạc", "animated emojis", "gesture shortcuts", "notch customizer",
        "status bar stickers", "battery level"
    ]
    _style = [
        "dễ thương", "kawaii", "cute bear", "pastel style"
    ]
    _visual = [
        "rounded corners", "heart shapes", "custom notch"
    ]
elif "ID" in _market:
    _primary = ["id"]
    _secondary = ["en"]
    _core_intent = [
        "baterai emoji", "widget baterai", "ikon baterai", "kustomisasi baterai",
        "stiker emoji", "emoji battery", "emoji battery widget", "emoji battery status bar",
        "emoji battery icon", "custom battery icon", "battery icon customize", "emoji widget",
        "funny status bar", "custom status bar", "emoji status bar", "emoji sticker", "emoji stickers"
    ]
    _feature = [
        "animated emojis", "gesture shortcuts", "notch customizer", "status bar stickers", "battery level"
    ]
    _style = [
        "lucu", "imut", "kawaii", "pastel style"
    ]
    _visual = [
        "rounded corners", "heart shapes", "custom notch"
    ]
elif "PT" in _market or "BR" in _market:
    _primary = ["pt"]
    _secondary = ["en"]
    _core_intent = [
        "bateria emoji", "widget de bateria", "Ã­cone de bateria", "personalizar bateria",
        "adesivo emoji", "adesivos emoji", "emoji battery", "emoji battery widget",
        "emoji battery status bar", "emoji battery icon", "custom battery icon", "battery icon customize",
        "emoji widget", "funny status bar", "custom status bar", "emoji status bar", "emoji sticker", "emoji stickers"
    ]
    _feature = [
        "emojis animados", "atalhos de gestos", "animated emojis", "gesture shortcuts", "notch customizer",
        "status bar stickers", "battery level"
    ]
    _style = [
        "fofo", "bonito", "lindos", "kawaii", "pastel style"
    ]
    _visual = [
        "rounded corners", "heart shapes", "custom notch"
    ]
elif "FIL" in _market or "TL" in _market or "PH" in _market:
    _primary = ["fil", "tl"]
    _secondary = ["en"]
    _core_intent = [
        "emoji baterya", "widget ng baterya", "sticker ng emoji", "emoji battery", "emoji battery widget",
        "emoji battery status bar", "emoji battery icon", "custom battery icon", "battery icon customize",
        "emoji widget", "funny status bar", "custom status bar", "emoji status bar", "emoji sticker", "emoji stickers"
    ]
    _feature = [
        "animated emojis", "gesture shortcuts", "notch customizer", "status bar stickers", "battery level"
    ]
    _style = [
        "kawaii faces", "pastel style", "cute bear", "sleepy cat"
    ]
    _visual = [
        "rounded corners", "heart shapes", "custom notch"
    ]
else:
    _primary = ["en"]
    _secondary = ["es", "es-MX"]
    _core_intent = [
        "emoji battery", "emoji battery widget", "emoji battery status bar", "emoji battery icon",
        "cute battery widget", "cute battery icon", "emoji battery widget bar", "custom battery icon",
        "battery icon customize", "emoji widget", "funny status bar", "custom status bar",
        "emoji status bar", "emoji battery stickers", "custom battery widget", "cute battery theme",
        "emoji sticker", "emoji stickers"
    ]
    _feature = [
        "animated emojis", "battery level", "battery status", "customization app", "customize detail",
        "gesture shortcuts", "notch customizer", "accessibility services", "status bar stickers",
        "battery widget styles", "notch overlay", "troll effects", "charging animation",
        "real-time display", "custom wifi icon", "pastel clock", "signal strength indicator",
        "rounded edges", "double tap shortcut"
    ]
    _style = [
        "kawaii faces", "pastel style", "cute bear", "sleepy cat", "sparkly star", "magic emoji",
        "funny themes", "vivid emojis", "aesthetic stickers", "pastel themes", "bold sparkly",
        "cute characters"
    ]
    _visual = [
        "rounded corners", "heart shapes", "custom notch", "status bar background", "battery colors",
        "battery templates", "battery icons", "icon customization", "pink theme", "aesthetic status bar"
    ]

APP_CONFIG = {
    # =========================================================================
    # 1. IDENTITY & META (ThÃ´ng tin Ä‘á»‹nh danh)
    # =========================================================================
    "app_id": "com.cute.emoji.battery.icon.widget.customize.emojisticker.statusbar",
    "app_name": "Emoji Battery Icon Customize",
    "category": "Personalization",
    "category_slug": "emoji_battery_customize",
    "market": "US_EN",
    "platform_mode": "google_play",
    "semantic_mode": "emoji_battery_customize",

    # =========================================================================
    # 2. MARKET LANGUAGE POLICY (ChÃ­nh sÃ¡ch ngÃ´n ngá»¯)
    # =========================================================================
    "market_language_policy": {
        "enabled": True,
        "required": True,
        "primary_languages": _primary,
        "secondary_languages": _secondary,
        "optional_secondary_languages": [],
        
        "primary_language_action": "keep",
        "secondary_language_action": "consider",
        "optional_secondary_action": "audit_or_consider",
        "foreign_language_action": "drop_to_audit",
        
        "allow_secondary_in_top25_core": False,
        "allow_secondary_in_broad_expansion": False,
        "secondary_max_quota_in_broad": 0,
        "secondary_max_quota_in_consider": 3,
        "allow_secondary_in_feature_file": False,
        "allow_secondary_in_style_file": False,

        "mixed_language_action": "manual_review",
        "unknown_language_action": "manual_review_if_high_score"
    },

    # =========================================================================
    # 3. PHÃ‚N NHÃ“M Tá»ª KHÃ“A NGá»® NGHÄ¨A (SEMANTIC GROUPS)
    # =========================================================================
    "ai_keyword_classifier": {
        "enabled": True,
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "batch_size": 50,
        "requests_per_second": 2.0,
        "prompt_version": "aso-keyword-classifier-v1",
        "fail_on_api_error": True,
        "min_confidence": 0.55,
        "cache_path": ".cache/ai_keyword_analysis.sqlite3",
        "pre_filter": {
            "enabled": True,
            "duplicate_strategy": "canonical_reuse",
            "preserve_if_matches_intent": True,
            "allow_possible_truncated_to_ai": True,
            "skip_rules": [
                "empty_keyword",
                "duplicate_keyword",
                "competitor_brand",
                "typo_blacklist",
                "truncated_keyword",
                "irrelevant_intent",
                "noise_only",
                "platform_affiliation",
                "platform_only"
            ]
        }
    },

    "intent_core_terms": _core_intent,
    "feature_terms": _feature,
    "style_terms": _style,
    "visual_terms": _visual,

    # =========================================================================
    # 4. Bá»˜ Lá»ŒC VÃ€ DANH SÃCH ÄEN (FILTERS & BLACKLIST)
    # =========================================================================
    "competitor_brands": [
        "hoangsi", "zappsolution", "rikatech", "bralyvn", "diy battery", "hoang devops", "feedback pirates"
    ],
    
    "noise_terms": [
        "app", "apps", "free", "download", "android", "for android", "new", "best", "top"
    ],
    
    "typo_blacklist": [
        "emojibattery", "emoji batery", "emojibatery"
    ],
    
    "irrelevant_intent_terms": [
        "zipper lock screen", "ziplock screen", "zipper lock", "ziplocker", "retro games",
        "voice changer", "voice effects", "ar filter", "face filter", "calculator lock", "app lock"
    ],
    
    "risky_ip_terms": [
        "disney", "kitty", "hello kitty", "barbie", "marvel"
    ],

    "risky_platform_terms": ["iphone", "ios", "ipad", "apple"],
    "ambiguous_brand_terms": [],
    "platform_affiliation_terms": [],
    "truncation_policy": {
        "enabled": True,
        "min_prefix_length": 2,
        "allowed_partial_terms": [],
        "protect_complete_tokens": True,
        "ignore_inflection_prefix": True,
        "low_confidence_action": "manual_review",
        "dangling_action": "manual_review"
    },

    # =========================================================================
    # 5. RISK HANDLING & PRECEDENCE (ChÃ­nh sÃ¡ch rá»§i ro & Thá»© tá»± Æ°u tiÃªn)
    # =========================================================================
    "risk_policy": {
        "competitor_brand_action": "drop",
        "ambiguous_brand_action": "consider",
        "risky_ip_action": "consider",
        "platform_context_action": "consider",
        "platform_only_action": "drop",
        "platform_affiliation_action": "drop",
        "style_only_action": "reserve",
        "core_intent_override": True
    },

    # =========================================================================
    # 6. KEYWORD QUOTA (Háº¡n ngáº¡ch phÃ¢n bá»• tá»« khÃ³a)
    # =========================================================================
    "keyword_quota": {
        "main_file": {
            "core_intent": 25,
            "broad_expansion": 5,
            "consider": 10,
            "consider_subquota": {
                "platform_style": 4,
                "secondary_language": 3,
                "missed_opportunity": 3
            }
        },
        "feature_file": {
            "max_keywords": 30,
            "core_feature": 20,
            "feature_expansion": 5,
            "feature_test": 5
        },
        "style_file": {
            "max_keywords": 30,
            "intent_linked_style": 15,
            "broad_style": 10,
            "platform_style_consider": 5
        },
        "fallback_policy": {
            "allow_under_quota": True,
            "fill_from_next_best_eligible_bucket": True,
            "do_not_force_weak_keywords": True,
            "min_relevancy_for_fill": 0.45,
            "add_fill_reason_column": True
        }
    },

    # =========================================================================
    # 7. LANGUAGE NATURALNESS (Äá»™ tá»± nhiÃªn ngÃ´n ngá»¯)
    # =========================================================================
    "language_naturalness": {
        "enabled": True,
        "penalty_unnatural": -0.35,
        "auto_drop_score_below": 0.15,
        "rules": {
            "grammar_violation": {
                "patterns": [
                    r"\b(app app|widget widget|theme theme)\b",
                    r"\b(what is|how to|why do|when is|where is)\b"
                ],
                "flag": "UNNATURAL"
            },
            "redundancy": {
                "max_word_repeat_ratio": 0.5,
                "flag": "STUFFING"
            },
            "length_anomaly": {
                "max_natural_words": 6,
                "exception_if_contains_core": True,
                "flag": "TOO_LONG"
            },
            "cross_language_bleed": {
                "note": "Chá»‰ dÃ¹ng Ä‘á»ƒ loáº¡i bá» ngÃ´n ngá»¯ láº¡, khÃ´ng flag nháº§m secondary language",
                "forbidden_foreign_in_market": {},
                "flag": "LANGUAGE_BLEED"
            }
        }
    },

    # =========================================================================
    # 8. SCORING WEIGHTS (Trá»ng sá»‘ Relevancy & Balanced Score)
    # =========================================================================
    "relevancy_weights": {
        "base": 0.30,
        "intent_core": 0.40,
        "feature_specific": 0.15,
        "style_theme": 0.10,
        "visual_extra": 0.05,
        "penalty_competitor": -0.25,
        "penalty_noise": -0.20,
        "penalty_language_mismatch": -0.35,
        "penalty_unnatural": -0.35
    },

    "balanced_weights": {
        "VolumeN": 0.50,
        "DifficultyN": 0.05,
        "KEIN": 0.05,
        "RelevancyScore": 0.25,
        "CurrentRankN": 0.05,
        "ExpansionValue": 0.10
    },

    "scoring_normalization": {
        "volume": "maximum_reach_or_exponential_search_popularity",
        "difficulty": "inverse_0_100",
        "kei": "log_minmax",
        "rank": "tiered_rank_score",
        "unranked_rank_score": 0.0
    },

    "volume_score_policy": {
        "search_popularity_floor": 5.0,
        "search_popularity_ceiling": 45.0,
        "exponential_curve_factor": 4.0,
        "current_volume_weight": 0.85,
        "historical_max_volume_weight": 0.15,
        "low_tier_threshold": 5.0,
        "low_tier_score_cap": 0.05,
        "exclude_low_tier_from_metadata_shortlist": False,
        "max_low_tier_consider_keywords": 999
    },

    # =========================================================================
    # 9. METADATA SLOTS & OUTPUT (PhÃ¢n bá»• & Äá»‹nh dáº¡ng Ä‘áº§u ra)
    # =========================================================================
    "metadata_slots": {
        "google_play": {
            "Title": 2,
            "Short Description": 7,
            "Full Description": 21
        },
        "app_store": {
            "Title": 2,
            "Subtitle": 5,
            "Keyword Field": 15,
            "Promotional Text": 5
        }
    },

    "max_word_overlap": 0.5,
    "dedup_policy": {
        "auto_merge_token_bag": False,
        "review_overlap_threshold": 0.80,
        "accent_fold_auto_merge_locales": [],
        "enable_review_log": True,
    },
    "output_prefix": "ASO_Keyword_Planner",
    "output_mode": "excel_workbook",
    "output_workbook": {
        "enabled": True,
        "filename_pattern": "ASO_Keyword_Planner_{app_name}_{market}.xlsx",
        "export_csv_package": False,
        "export_markdown_report": False,
        "include_all_candidates_sheet": True,
        "include_optional_audit_sheets": True,
        "freeze_header_rows": True,
        "enable_filters": True,
        "format_as_tables": True,
        "wrap_text_columns": ["Keyword", "Reason", "DecisionReason", "LanguageReason", "FillReason"],
        "required_sheets": [
            "00_README_CONFIG",
            "01_Main_Keyword_Shortlist",
            "02_Feature_Keywords",
            "03_Style_Keywords",
            "04_Dropped_Audit",
            "05_Report_Summary",
            "06_All_Candidates"
        ],
        "optional_sheets": [
            "07_Language_Mismatch",
            "08_Generic_Style_Reserve",
            "09_Manual_Review",
            "10_Top_By_Score",
            "11_Secondary_Language"
        ]
    },

    # =========================================================================
    # 10. USER OVERRIDES (Ghi Ä‘Ã¨ thá»§ cÃ´ng tá»« User)
    # =========================================================================
    "user_overrides": {
        "do_not_auto_drop_terms": [],
        "force_consider_terms": [],
        "force_drop_terms": [],
        "force_top30_terms": [],
        "notes": []
    }
}
