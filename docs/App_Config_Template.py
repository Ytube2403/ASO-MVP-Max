# -*- coding: utf-8 -*-
"""
ASO Keyword Planner - App Configuration Template
Version: 4.3
Purpose: Template configuration for deploying ASO Keyword Planner on a new application.
"""

APP_CONFIG = {
    # ==========================================
    # 1. IDENTITY & META (ThÃ´ng tin Ä‘á»‹nh danh)
    # ==========================================
    "app_id": "com.example.yourapp",  # Bundle ID / Package ID cá»§a á»©ng dá»¥ng
    "app_name": "Your App Name",      # TÃªn á»©ng dá»¥ng Ä‘áº§y Ä‘á»§
    "category": "Widget",             # Danh má»¥c á»©ng dá»¥ng (Widget, Emulator, AR Filter, VPN...)
    "category_slug": "widget",        # Slug dÃ¹ng cho Ä‘Æ°á»ng dáº«n (viáº¿t thÆ°á»ng, khÃ´ng dáº¥u, phÃ¢n cÃ¡ch bá»Ÿi gáº¡ch dÆ°á»›i)
    "market": "US_EN",                # Thá»‹ trÆ°á»ng má»¥c tiÃªu máº·c Ä‘á»‹nh (US_EN, VN_VI, BR_PT, IN_EN...)
    "platform_mode": "google_play",   # Ná»n táº£ng: 'google_play' hoáº·c 'app_store'

    "semantic_mode": "personalization_widget",

    # ==========================================
    # 2. MARKET LANGUAGE POLICY (ChÃ­nh sÃ¡ch ngÃ´n ngá»¯)
    # ==========================================
    "market_language_policy": {
        "enabled": True,
        "required": True,
        "primary_languages": ["en"],              # Danh sÃ¡ch ngÃ´n ngá»¯ chÃ­nh Ä‘Æ°á»£c phÃ©p xuáº¥t hiá»‡n trong Top 25 Core
        "secondary_languages": ["es", "es-MX"],   # NgÃ´n ngá»¯ phá»¥ (vÃ­ dá»¥ tiáº¿ng TÃ¢y Ban Nha táº¡i Má»¹), Ä‘Æ°a vÃ o danh sÃ¡ch Consider
        "optional_secondary_languages": [],       # NgÃ´n ngá»¯ tÃ¹y chá»n khÃ¡c

        "primary_language_action": "keep",
        "secondary_language_action": "consider",
        "optional_secondary_action": "audit_or_consider",
        "foreign_language_action": "drop_to_audit",  # Loáº¡i bá» cÃ¡c tá»« khÃ³a ngoÃ i chÃ­nh sÃ¡ch ngÃ´n ngá»¯ vÃ  Ä‘Æ°a vÃ o Audit

        "allow_secondary_in_top25_core": False,
        "allow_secondary_in_broad_expansion": False,
        "secondary_max_quota_in_broad": 0,
        "secondary_max_quota_in_consider": 3,
        "allow_secondary_in_feature_file": False,
        "allow_secondary_in_style_file": False,

        "mixed_language_action": "manual_review",
        "unknown_language_action": "manual_review_if_high_score"
    },

    # ==========================================
    # 2.5 AI KEYWORD CLASSIFIER (DeepSeek + cache + pre-filter + key pool)
    # ==========================================
    "ai_keyword_classifier": {
        "enabled": True,
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "batch_size": 50,
        "requests_per_second": 2.0,
        "requests_per_second_per_key": 1.0,
        "max_workers": 2,
        "key_strategy": "round_robin",
        "failover_on_key_error": True,
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

    # ==========================================
    # 3. SEMANTIC GROUPS (NhÃ³m tá»« khÃ³a ngá»¯ nghÄ©a)
    # ==========================================
    "intent_core_terms": [
        # CÃ¡c tá»« khÃ³a cá»‘t lÃµi thá»ƒ hiá»‡n Ã½ Ä‘á»‹nh tÃ¬m kiáº¿m chÃ­nh cá»§a á»©ng dá»¥ng
        # VÃ­ dá»¥: "control panel", "control center" cho Control Widget
        "core term 1", "core term 2"
    ],

    "feature_terms": [
        # CÃ¡c tá»« khÃ³a mÃ´ táº£ tÃ­nh nÄƒng / chá»©c nÄƒng cá»¥ thá»ƒ cá»§a á»©ng dá»¥ng
        # VÃ­ dá»¥: "brightness", "volume", "wifi toggle"
        "feature 1", "feature 2"
    ],

    "style_terms": [
        # CÃ¡c tá»« khÃ³a mÃ´ táº£ phong cÃ¡ch, giao diá»‡n, IP hoáº·c theme tháº©m má»¹
        # VÃ­ dá»¥: "aesthetic", "cute", "anime", "neon"
        # LÆ¯U Ã: style_terms chá»‰ Ä‘Æ°á»£c phÃ¢n bá»• vÃ o Full Description, khÃ´ng dÃ¹ng á»Ÿ Title/Subtitle Ä‘á»ƒ trÃ¡nh vi pháº¡m IP
        "style 1", "style 2"
    ],

    "visual_terms": [
        # CÃ¡c tá»« khÃ³a mÃ´ táº£ giao diá»‡n phá»¥ trá»£, hiá»‡u á»©ng hÃ¬nh áº£nh
        "visual 1", "visual 2"
    ],

    # ==========================================
    # 4. FILTERS & BLACKLIST (CÃ¡c bá»™ lá»c vÃ  danh sÃ¡ch Ä‘en)
    # ==========================================
    "competitor_brands": [
        # TÃªn cÃ¡c Ä‘á»‘i thá»§ cáº¡nh tranh. Keyword chá»©a brand Ä‘á»‘i thá»§ sáº½ bá»‹ cáº¥m sá»­ dá»¥ng trong Metadata chÃ­nh
        "competitor brand 1", "competitor brand 2"
    ],

    "noise_terms": [
        # CÃ¡c tá»« khÃ³a chung chung, generic quÃ¡ rá»™ng khÃ´ng mang Ã½ Ä‘á»‹nh tÃ¬m app cá»¥ thá»ƒ
        # VÃ­ dá»¥: "app", "free", "download", "android"
        "app", "free", "download", "android", "new", "best"
    ],

    "typo_blacklist": [
        # CÃ¡c tá»« khÃ³a gÃµ sai chÃ­nh táº£ phá»• biáº¿n hoáº·c cÃ¡c tá»« khÃ³a vÃ´ nghÄ©a thu Ä‘Æ°á»£c tá»« auto-suggest
        "typo 1", "typo 2"
    ],

    "irrelevant_intent_terms": [
        # Tá»« khÃ³a thuá»™c danh má»¥c khÃ¡c, hoÃ n toÃ n khÃ´ng liÃªn quan Ä‘áº¿n á»©ng dá»¥ng cá»§a báº¡n
        "calculator", "weather"
    ],

    "risky_ip_terms": [
        # Tá»« khÃ³a chá»©a IP hoáº·c báº£n quyá»n nháº¡y cáº£m cáº§n háº¡n cháº¿
        "brandname"
    ],

    "risky_platform_terms": ["iphone", "ios", "ipad", "apple", "android", "tiktok", "snapchat", "instagram"],
    "ambiguous_brand_terms": [],
    "platform_affiliation_terms": ["official tiktok", "official snapchat", "official instagram"],
    "truncation_policy": {
        "enabled": True,
        "min_prefix_length": 2,
        "allowed_partial_terms": [],
        "protect_complete_tokens": True,
        "ignore_inflection_prefix": True,
        "low_confidence_action": "manual_review",
        "dangling_action": "manual_review"
    },

    # ==========================================
    # 5. RISK HANDLING & PRECEDENCE (ChÃ­nh sÃ¡ch rá»§i ro & Thá»© tá»± Æ°u tiÃªn)
    # ==========================================
    "risk_policy": {
        "competitor_brand_action": "drop",
        "ambiguous_brand_action": "consider",
        "risky_ip_action": "consider",
        "platform_context_action": "consider",
        "platform_only_action": "drop",
        "platform_affiliation_action": "drop",
        "style_only_action": "reserve",
        "core_intent_override": True  # Náº¿u chá»©a core intent máº¡nh, khÃ´ng tá»± Ä‘á»™ng loáº¡i khi dÃ­nh lá»—i nháº¹
    },

    # ==========================================
    # 6. KEYWORD QUOTA (Háº¡n ngáº¡ch phÃ¢n bá»• tá»« khÃ³a)
    # ==========================================
    "keyword_quota": {
        "main_file": {
            "core_intent": 25,       # Sá»‘ lÆ°á»£ng keyword core chÃ­nh (Top 25)
            "broad_expansion": 5,    # Sá»‘ lÆ°á»£ng keyword má»Ÿ rá»™ng rá»™ng hÆ¡n (Top 5)
            "consider": 10,          # Sá»‘ lÆ°á»£ng keyword Ä‘Æ°a vÃ o danh sÃ¡ch Consider
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

    # ==========================================
    # 7. LANGUAGE NATURALNESS (Äá»™ tá»± nhiÃªn ngÃ´n ngá»¯)
    # ==========================================
    "language_naturalness": {
        "enabled": True,
        "penalty_unnatural": -0.35,      # Äiá»ƒm pháº¡t khi cá»¥m tá»« kÃ©m tá»± nhiÃªn
        "auto_drop_score_below": 0.15,   # Tá»± Ä‘á»™ng loáº¡i náº¿u Ä‘iá»ƒm Relevancy sau pháº¡t dÆ°á»›i má»©c nÃ y
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
                "note": "Legacy note only. From v3.5, script/language mismatch is handled by shared/language_detector.py; naturalness must not hard-drop non-Latin text as LANGUAGE_BLEED.",
                "forbidden_foreign_in_market": {},
                "flag": "LANGUAGE_BLEED"
            }
        }
    },

    # ==========================================
    # 8. SCORING WEIGHTS (Trá»ng sá»‘ Relevancy & Balanced Score)
    # ==========================================
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
        "VolumeN": 0.20,
        "DifficultyN": 0.15,
        "KEIN": 0.15,
        "RelevancyScore": 0.30,
        "CurrentRankN": 0.10,
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
        "search_popularity_ceiling": 100.0,
        "exponential_curve_factor": 4.0,
        "current_volume_weight": 0.85,
        "historical_max_volume_weight": 0.15,
        "low_tier_threshold": 5.0,
        "low_tier_score_cap": 0.05,
        "exclude_low_tier_from_metadata_shortlist": False,
        "max_low_tier_consider_keywords": 999
    },

    # ==========================================
    # 9. METADATA SLOTS & OUTPUT (PhÃ¢n bá»• & Äá»‹nh dáº¡ng Ä‘áº§u ra)
    # ==========================================
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

    "max_word_overlap": 0.5,  # Tá»· lá»‡ trÃ¹ng láº·p tá»« tá»‘i Ä‘a giá»¯a cÃ¡c keyword trong Top N (trÃ¡nh láº·p Ã½)
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

    # ==========================================
    # 10. USER OVERRIDES (Ghi Ä‘Ã¨ thá»§ cÃ´ng tá»« User)
    # ==========================================
    "user_overrides": {
        "do_not_auto_drop_terms": [],
        "force_consider_terms": [],
        "force_drop_terms": [],
        "force_top30_terms": [],
        "notes": []
    }
}
