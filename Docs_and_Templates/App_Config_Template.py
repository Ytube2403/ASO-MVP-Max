# -*- coding: utf-8 -*-
"""
ASO Keyword Planner - App Configuration Template
Version: 3.4
Purpose: Template configuration for deploying ASO Keyword Planner on a new application.
"""

APP_CONFIG = {
    # ==========================================
    # 1. IDENTITY & META (Thông tin định danh)
    # ==========================================
    "app_id": "com.example.yourapp",  # Bundle ID / Package ID của ứng dụng
    "app_name": "Your App Name",      # Tên ứng dụng đầy đủ
    "category": "Widget",             # Danh mục ứng dụng (Widget, Emulator, AR Filter, VPN...)
    "category_slug": "widget",        # Slug dùng cho đường dẫn (viết thường, không dấu, phân cách bởi gạch dưới)
    "market": "US_EN",                # Thị trường mục tiêu mặc định (US_EN, VN_VI, BR_PT, IN_EN...)
    "platform_mode": "google_play",   # Nền tảng: 'google_play' hoặc 'app_store'

    # ==========================================
    # 2. MARKET LANGUAGE POLICY (Chính sách ngôn ngữ)
    # ==========================================
    "market_language_policy": {
        "enabled": True,
        "required": True,
        "primary_languages": ["en"],              # Danh sách ngôn ngữ chính được phép xuất hiện trong Top 25 Core
        "secondary_languages": ["es", "es-MX"],   # Ngôn ngữ phụ (ví dụ tiếng Tây Ban Nha tại Mỹ), đưa vào danh sách Consider
        "optional_secondary_languages": [],       # Ngôn ngữ tùy chọn khác
        
        "primary_language_action": "keep",
        "secondary_language_action": "consider",
        "optional_secondary_action": "audit_or_consider",
        "foreign_language_action": "drop_to_audit",  # Loại bỏ các từ khóa ngoài chính sách ngôn ngữ và đưa vào Audit

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
    # 3. SEMANTIC GROUPS (Nhóm từ khóa ngữ nghĩa)
    # ==========================================
    "intent_core_terms": [
        # Các từ khóa cốt lõi thể hiện ý định tìm kiếm chính của ứng dụng
        # Ví dụ: "control panel", "control center" cho Control Widget
        "core term 1", "core term 2"
    ],
    
    "feature_terms": [
        # Các từ khóa mô tả tính năng / chức năng cụ thể của ứng dụng
        # Ví dụ: "brightness", "volume", "wifi toggle"
        "feature 1", "feature 2"
    ],
    
    "style_terms": [
        # Các từ khóa mô tả phong cách, giao diện, IP hoặc theme thẩm mỹ
        # Ví dụ: "aesthetic", "cute", "anime", "neon"
        # LƯU Ý: style_terms chỉ được phân bổ vào Full Description, không dùng ở Title/Subtitle để tránh vi phạm IP
        "style 1", "style 2"
    ],
    
    "visual_terms": [
        # Các từ khóa mô tả giao diện phụ trợ, hiệu ứng hình ảnh
        "visual 1", "visual 2"
    ],

    # ==========================================
    # 4. FILTERS & BLACKLIST (Các bộ lọc và danh sách đen)
    # ==========================================
    "competitor_brands": [
        # Tên các đối thủ cạnh tranh. Keyword chứa brand đối thủ sẽ bị cấm sử dụng trong Metadata chính
        "competitor brand 1", "competitor brand 2"
    ],
    
    "noise_terms": [
        # Các từ khóa chung chung, generic quá rộng không mang ý định tìm app cụ thể
        # Ví dụ: "app", "free", "download", "android"
        "app", "free", "download", "android", "new", "best"
    ],
    
    "typo_blacklist": [
        # Các từ khóa gõ sai chính tả phổ biến hoặc các từ khóa vô nghĩa thu được từ auto-suggest
        "typo 1", "typo 2"
    ],
    
    "irrelevant_intent_terms": [
        # Từ khóa thuộc danh mục khác, hoàn toàn không liên quan đến ứng dụng của bạn
        "calculator", "weather"
    ],
    
    "risky_ip_terms": [
        # Từ khóa chứa IP hoặc bản quyền nhạy cảm cần hạn chế
        "brandname"
    ],

    # ==========================================
    # 5. RISK HANDLING & PRECEDENCE (Chính sách rủi ro & Thứ tự ưu tiên)
    # ==========================================
    "risk_policy": {
        "competitor_brand_action": "drop",
        "risky_ip_action": "consider",
        "platform_style_action": "consider",
        "style_only_action": "reserve",
        "core_intent_override": True  # Nếu chứa core intent mạnh, không tự động loại khi dính lỗi nhẹ
    },

    "rule_precedence": [
        "force_drop_and_competitor_brand",
        "typo_truncated_broken_keyword",
        "foreign_language_mismatch",
        "irrelevant_intent",
        "core_intent_override",
        "risk_policy",
        "secondary_language_handling",
        "scoring_and_bucket_classification",
        "user_overrides_with_limits"
    ],

    # ==========================================
    # 6. KEYWORD QUOTA (Hạn ngạch phân bổ từ khóa)
    # ==========================================
    "keyword_quota": {
        "main_file": {
            "core_intent": 25,       # Số lượng keyword core chính (Top 25)
            "broad_expansion": 5,    # Số lượng keyword mở rộng rộng hơn (Top 5)
            "consider": 10,          # Số lượng keyword đưa vào danh sách Consider
            "consider_subquota": {
                "platform_style": 4,      # Quota cho keyword dính platform risk (iPhone, iOS...)
                "secondary_language": 3,  # Quota cho keyword ngôn ngữ phụ
                "missed_opportunity": 3   # Quota cho keyword điểm cao nhưng trượt Top 30
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

    # ==========================================
    # 7. LANGUAGE NATURALNESS (Độ tự nhiên ngôn ngữ)
    # ==========================================
    "language_naturalness": {
        "enabled": True,
        "penalty_unnatural": -0.35,      # Điểm phạt khi cụm từ kém tự nhiên
        "auto_drop_score_below": 0.15,   # Tự động loại nếu điểm Relevancy sau phạt dưới mức này
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
                "note": "Chỉ dùng để loại bỏ ngôn ngữ lạ, không flag nhầm secondary language",
                "forbidden_foreign_in_market": {},
                "flag": "LANGUAGE_BLEED"
            }
        }
    },

    # ==========================================
    # 8. SCORING WEIGHTS (Trọng số Relevancy & Balanced Score)
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
        "volume": "log_minmax",
        "difficulty": "inverse_0_100",
        "kei": "log_minmax",
        "rank": "tiered_rank_score",
        "unranked_rank_score": 0.0
    },

    # ==========================================
    # 9. METADATA SLOTS & OUTPUT (Phân bổ & Định dạng đầu ra)
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

    "max_word_overlap": 0.5,  # Tỷ lệ trùng lặp từ tối đa giữa các keyword trong Top N (tránh lặp ý)
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
    # 10. USER OVERRIDES (Ghi đè thủ công từ User)
    # ==========================================
    "user_overrides": {
        "do_not_auto_drop_terms": [],
        "force_consider_terms": [],
        "force_drop_terms": [],
        "force_top30_terms": [],
        "notes": []
    }
}
