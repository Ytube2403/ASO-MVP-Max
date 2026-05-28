# ASO Keyword Planner

**Phiên bản:** 3.4  
**Tên cũ:** ASO Keyword Master Pipeline — Universal Template  
**Tên mới:** ASO Keyword Planner  
**Mục đích:** Lọc, chấm điểm, phân nhóm và xuất shortlist keyword ASO theo từng app, từng market, từng ngôn ngữ và từng nền tảng metadata.  
**Dùng cho:** Google Play / App Store keyword research, metadata planning, ASO testing, UA keyword review.

---

## 0. Tư duy cốt lõi

ASO Keyword Planner không chỉ là một bộ lọc keyword. Mục tiêu của pipeline là tạo ra một **keyword decision sheet**: keyword nào nên dùng ngay, keyword nào nên giữ để cân nhắc, keyword nào chỉ nên dùng làm supporting keyword, keyword nào cần audit, và keyword nào phải loại.

Pipeline cần tránh 3 lỗi phổ biến:

1. **Quá máy móc theo điểm số**  
   Keyword có Volume/KEI cao nhưng quá rộng vẫn không nên chiếm slot chính.

2. **Quá gắt khi lọc rủi ro**  
   Một số keyword như iPhone / iOS / OS-style có thể có intent sát. Không nên auto drop nếu vẫn có giá trị nghiên cứu.

3. **Lẫn ngôn ngữ sai market**  
   Keyword khác ngôn ngữ metadata chính không nên tự động chen vào output chính, dù có điểm tốt. Tuy nhiên secondary language phù hợp quốc gia vẫn nên được giữ để Consider.

Nguyên tắc mới:

```text
Top keyword không chỉ là keyword có điểm cao nhất.
Top keyword phải là keyword có thể dùng được, đúng intent, đúng ngôn ngữ, đúng slot metadata, đúng platform và đúng mức rủi ro.
```

---

## 0.1 Yêu cầu chuẩn đầu vào (Input CSV Specifications)

Để đảm bảo pipeline xử lý dữ liệu chính xác và không gặp lỗi kiểu dữ liệu ở Bước 1 (Data Ingestion), file CSV đầu vào của từ khóa ASO cần tuân thủ nghiêm ngặt các tiêu chuẩn sau:

### 0.1.1 Định dạng và mã hóa file
- **Mã hóa (Encoding)**: Bắt buộc là **UTF-8** hoặc **UTF-8 with BOM** (`utf-8-sig`). Điều này cực kỳ quan trọng để bảo vệ các ký tự tiếng Việt (có dấu), tiếng Tây Ban Nha, tiếng Bồ Đào Nha hoặc tiếng Hindi không bị lỗi font (mojibake).
- **Dấu phân tách (Delimiter)**: Dấu phẩy chuẩn (`,`).

### 0.1.2 Tên file và thư mục lưu trữ
- **Quy chuẩn tên file**: `[AppName]_[Country]_[Language].csv` hoặc fallback `[Country]_[Language].csv`.
  - *Ví dụ*: `ARFilter_US_EN.csv`, `ControlWidget_BR_PT.csv`, `US_EN.csv`
- **Quy chuẩn đường dẫn thư mục**: `[Component]/Input/[MMYYYY]/[Tên_File].csv`
  - *Ví dụ*: `AR_Filter/Input/052026/ARFilter_US_EN.csv`

### 0.1.3 Các cột dữ liệu bắt buộc và tùy chọn

| Tên Cột | Kiểu Dữ Liệu | Trạng Thái | Mô Tả & Xử Lý Fallback |
|---|---|---|---|
| `Keyword` | String (Text) | **Bắt buộc** | Từ khóa cần đánh giá. Phải là văn bản không chứa ký tự lạ. Nếu dòng bị rỗng sẽ tự động bị bỏ qua. |
| `Volume` | Integer (Số nguyên) | Tùy chọn | Lượng tìm kiếm hiện tại của từ khóa. Nếu không có, mặc định gán = `0`. |
| `Max. Volume` hoặc `Max Volume` | Integer (Số nguyên) | Tùy chọn | Lượng tìm kiếm cao nhất trong 12 tháng qua. Nếu không có, mặc định lấy bằng giá trị cột `Volume`. |
| `Difficulty` | Integer (Số nguyên) | Tùy chọn | Điểm độ khó của từ khóa ($0 - 100$). Nếu không có, mặc định gán = `0`. |
| `KEI` | Float (Số thập phân) | Tùy chọn | Chỉ số hiệu quả từ khóa. Nếu không có, mặc định gán = `0.0`. |
| `Rank` hoặc `CurrentRank` | String hoặc Integer | Tùy chọn | Thứ hạng hiện tại của app cho từ khóa này. Nếu không có, mặc định gán = `"Unranked"`. |

### 0.1.4 Chuẩn hóa kiểu dữ liệu tự động
Khi đọc dữ liệu, pipeline sẽ tự động thực hiện ép kiểu và chuẩn hóa:
1. Ép các cột `Volume`, `Max. Volume`, `Difficulty` sang dạng số nguyên nguyên bản, điền `0` nếu gặp dữ liệu lỗi (`NaN` hoặc lỗi định dạng).
2. Ép cột `KEI` sang dạng số thực, điền `0.0` nếu lỗi.
3. Nếu cột `Max. Volume` bị thiếu, hệ thống tự động gán dữ liệu từ cột `Volume` để tính toán tỉ lệ `Traffic Stability`.

---

## 1. Output cuối cùng

Pipeline mặc định chỉ xuất **01 file Excel tổng** thay vì nhiều file rời.

```text
ASO_Keyword_Planner_[AppName]_[Market].xlsx
```

Workbook này là **single source of truth** cho toàn bộ kết quả keyword research: shortlist, feature/style grouping, audit, report và config đã dùng để chạy.

### 1.1 Workbook bắt buộc

| Sheet | Mục đích | Số lượng / Ghi chú |
|---|---|---:|
| `00_README_CONFIG` | Thông tin app, market, platform, config tóm tắt, thời gian chạy | 1 sheet |
| `01_Main_Keyword_Shortlist` | Top 30 + 10 Consider | 40 rows |
| `02_Feature_Keywords` | Keyword tính năng / type / intent chức năng | Tối đa 30 rows |
| `03_Style_Keywords` | Keyword style / theme / visual intent | Tối đa 30 rows |
| `04_Dropped_Audit` | Keyword bị loại + lý do | Không giới hạn |
| `05_Report_Summary` | Báo cáo tổng hợp pipeline | 1 sheet |
| `06_All_Candidates` | Toàn bộ keyword sau chuẩn hóa, scoring và classification | Không giới hạn |

### 1.2 Sheet phụ có điều kiện

Các sheet sau chỉ tạo nếu có dữ liệu tương ứng. Nếu không có dữ liệu, có thể bỏ qua hoặc tạo sheet rỗng với note `NO_DATA`.

| Sheet phụ | Mục đích |
|---|---|
| `07_Language_Mismatch` | Keyword sai ngôn ngữ market |
| `08_Generic_Style_Reserve` | Keyword style quá rộng, chưa nên dùng |
| `09_Manual_Review` | Keyword có rủi ro hoặc cần quyết định thủ công |
| `10_Top_By_Score` | Top keyword thuần theo BalancedScore để audit |
| `11_Secondary_Language` | Keyword ngôn ngữ phụ để nghiên cứu riêng |

### 1.3 Không xuất nhiều file rời mặc định

Không xuất các file CSV/MD/JSON riêng lẻ như mặc định cũ:

```text
01_Main_Keyword_Shortlist.csv
02_Feature_Keywords.csv
03_Style_Keywords.csv
04_Dropped_Keywords_Audit.csv
05_ASO_Report.md
sheet `00_README_CONFIG`
```

Thay vào đó, toàn bộ nội dung trên phải nằm trong **các sheet của cùng một workbook Excel**.

Chỉ export thêm CSV hoặc Markdown khi user yêu cầu rõ:

```text
export_csv_package = True
export_markdown_report = True
```

### 1.4 Quy chuẩn chung cho workbook

Mỗi sheet dạng bảng nên có:

- Header row cố định.
- Filter bật sẵn.
- Column width dễ đọc.
- Các cột text dài bật wrap text.
- Các cột score định dạng số thập phân.
- Các cột Volume / Difficulty / KEI / Rank định dạng số.
- Cột `Reason` hoặc `DecisionReason` để giải thích tại sao keyword được giữ, loại, đưa vào Consider hoặc reserve.
- Cột `Section` cho các sheet shortlist chính.
- Cột `QuotaStatus`, `FillSource`, `FillReason` nếu có dùng fallback.

Workbook phải đủ rõ để user có thể mở Excel và review ngay mà không cần ghép nhiều file lại với nhau.

## 2. Cấu trúc Top 30 mới

Sheet `01_Main_Keyword_Shortlist` không còn chọn thuần theo `BalancedScore`. Top 30 được chia theo quota:

```text
Top 30 Final Cut
= 25 Core / High Intent Keywords
+ 5 Broad Expansion Keywords

Extra
= 10 Consider Keywords
```

### 2.1 Top 25 Core / High Intent Keywords

Đây là nhóm keyword sát intent chính nhất của app.

Điều kiện:

- Có liên quan trực tiếp tới chức năng chính hoặc search intent chính.
- Không phải keyword style-only quá rộng.
- Không dính brand đối thủ.
- Không sai ngôn ngữ market.
- Ưu tiên primary language của market.
- Secondary language không được vào Top 25 mặc định, trừ khi user bật override rõ ràng.

Ví dụ với Control Widget:

```text
control panel
control widget
custom control panel
quick settings
notification panel
quick panel
volume control widget
shortcut widget
custom quick settings
control center themes
```

### 2.2 5 Broad Expansion Keywords

Đây là nhóm keyword rộng hơn nhưng vẫn có liên quan tới app. Mục tiêu là mở rộng semantic coverage và giúp nghiên cứu thêm hướng growth.

Điều kiện:

- Có liên quan tới category hoặc nhu cầu người dùng.
- Không quá generic.
- Không chiếm slot core intent.
- Ưu tiên keyword có gắn với widget / theme / custom / panel / setting / feature liên quan.
- Không quá 2 keyword style-only trong nhóm Broad Expansion.
- Secondary language chỉ được vào Broad Expansion nếu config cho phép và có quota riêng.

Ví dụ chấp nhận được:

```text
custom widget
color widgets
widget themes
custom themes
theme packs
cute widget
```

Ví dụ nên hạn chế:

```text
beauty theme
simple theme
stunning themes
themes wallpaper
diy theme pack
```

### 2.3 10 Consider Keywords

Đây là nhóm keyword có tiềm năng nhưng chưa nên đưa thẳng vào Top 30 chính.

Nhóm này có thể gồm:

- Keyword platform-style: iPhone / iOS / OS version.
- Keyword secondary language phù hợp với quốc gia.
- Keyword có intent sát nhưng hơi rủi ro về wording.
- Keyword có volume tốt nhưng cần review thêm.
- Keyword điểm cao nhưng bị loại khỏi Top 30 do overlap hoặc quota.

Sub-quota mặc định cho 10 Consider:

| Nhóm | Quota gợi ý | Ghi chú |
|---|---:|---|
| Platform-style / risky-but-relevant | 4 | Ví dụ iPhone / iOS / OS version |
| Secondary language | 3 | Chỉ áp dụng nếu market có secondary language phù hợp |
| High-score missed opportunities | 3 | Keyword điểm tốt nhưng không vào Top 30 |

Nếu một nhóm không đủ keyword, quota còn lại có thể chuyển cho nhóm khác. Không được nhét keyword yếu chỉ để đủ số lượng.

Ví dụ với Control Widget US_EN:

```text
iphone control center
ios control center
ios 17 control center
ios 16 widget
widget ios 18
theme iphone
themes iphone
os 18 control center
os 18 control center custom
os 17 widgets and themes
```

Yêu cầu output:

```text
File 01_Main_Keyword_Shortlist.csv phải có cột Section:
- Core Intent Final
- Broad Expansion
- Consider Keywords
```

---

## 3. Pipeline 10 bước

| Bước | Tên | Input | Output | Mục đích |
|---:|---|---|---|---|
| 1 | Data Ingestion | CSV thô | DataFrame chuẩn hóa | Đọc file, chuẩn hóa cột, ép kiểu dữ liệu |
| 2 | Hard Filter | DataFrame B1 | Candidate + Dropped | Loại typo, brand đối thủ, noise cứng, sai category |
| 3 | Market Language Policy | DataFrame B2 | DataFrame + language fields | Kiểm tra keyword có đúng ngôn ngữ market không |
| 4 | Language Naturalness Filter | DataFrame B3 | DataFrame + NaturalnessFlag | Phát hiện keyword không tự nhiên, stuffing, phrase lỗi |
| 5 | Relevancy Scoring | DataFrame B4 | DataFrame + RelevancyScore | Tính điểm liên quan với app |
| 6 | Balanced Score | DataFrame B5 | DataFrame + BalancedScore | Kết hợp Volume, Difficulty, KEI, Rank, Relevancy |
| 7 | Bucket Classification | DataFrame B6 | Keyword buckets | Chia Core / Broad / Consider / Reserve / Drop |
| 8 | Word Overlap & Diversity Filter | Buckets | Shortlist đa dạng | Tránh Top keyword bị lặp ý quá nhiều |
| 9 | Metadata Assignment | Shortlist | File output chính | Gợi ý keyword theo platform metadata |
| 10 | Export & Report | Output tables | CSV + Markdown | Xuất file, audit, báo cáo lý do giữ/loại |

---

## 4. APP_CONFIG Universal

```python
APP_CONFIG = {
    # ─── Identity ───
    "app_id": "com.yourcompany.yourapp",
    "app_name": "Your App Name",
    "category": "Widget",
    "category_slug": "widget",
    "market": "US_EN",
    "platform_mode": "google_play",  # google_play | app_store

    # ─── Market Language Policy ───
    "market_language_policy": {
        "enabled": True,
        "required": True,
        "primary_languages": ["en"],
        "secondary_languages": ["es", "es-MX"],
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

    # ─── Semantic Groups ───
    "feature_terms": [],
    "style_terms": [],
    "visual_terms": [],
    "intent_core_terms": [],

    # ─── Filters ───
    "competitor_brands": [],
    "noise_terms": [],
    "typo_blacklist": [],
    "irrelevant_intent_terms": [],
    "risky_ip_terms": [],

    # ─── Risk Handling ───
    "risk_policy": {
        "competitor_brand_action": "drop",
        "risky_ip_action": "consider",
        "platform_style_action": "consider",
        "style_only_action": "reserve",
        "core_intent_override": True
    },

    # ─── Rule Precedence ───
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

    # ─── Top Keyword Quotas ───
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

    # ─── Language Naturalness ───
    "language_naturalness": {
        "enabled": True,
        "penalty_unnatural": -0.35,
        "auto_drop_score_below": 0.15,
        "rules": {
            "grammar_violation": {
                "patterns": [],
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
                "note": "Only use for languages outside primary/secondary/optional policy. Do not flag valid secondary language as bleed.",
                "forbidden_foreign_in_market": {},
                "flag": "LANGUAGE_BLEED"
            }
        }
    },

    # ─── Relevancy Weights ───
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

    # ─── Balanced Score Weights ───
    "balanced_weights": {
        "VolumeN": 0.20,
        "DifficultyN": 0.15,
        "KEIN": 0.15,
        "RelevancyScore": 0.30,
        "CurrentRankN": 0.10,
        "ExpansionValue": 0.10
    },

    # ─── Scoring Normalization ───
    "scoring_normalization": {
        "volume": "log_minmax",
        "difficulty": "inverse_0_100",
        "kei": "log_minmax",
        "rank": "tiered_rank_score",
        "unranked_rank_score": 0.0
    },

    # ─── Metadata Slots by Platform ───
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

    # ─── Output Settings ───
    "max_word_overlap": 0.5,
    "output_prefix": "ASO_Keyword_Planner",
    "output_mode": "excel_workbook",  # excel_workbook | csv_package
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

    # ─── User Override Layer ───
    "user_overrides": {
        "do_not_auto_drop_terms": [],
        "force_consider_terms": [],
        "force_drop_terms": [],
        "force_top30_terms": [],
        "notes": []
    }
}
```

---

## 5. Market Language Policy

Pipeline phải kiểm tra keyword theo ngôn ngữ của market. Không phải keyword nào có điểm cao cũng được đưa vào output chính nếu sai ngôn ngữ.

### 5.1 Quy tắc bắt buộc

Mỗi lần chạy pipeline phải có `market_language_policy` rõ ràng.

```text
Nếu market_language_policy.enabled = True nhưng thiếu primary_languages,
pipeline phải dừng và yêu cầu bổ sung, không được tự đoán.
```

Mỗi market cần định nghĩa:

- Primary language
- Secondary language(s), nếu có
- Optional secondary language(s), nếu có
- Foreign language handling rule

Ví dụ với US_EN:

```text
Primary language: English
Secondary language: Spanish / es-MX
Optional secondary: none
Foreign languages: drop hoặc audit
```

Ví dụ với BR_PT:

```text
Primary language: Portuguese / pt-BR
Secondary language: English
Optional secondary: Spanish / es-MX / es-ES
Foreign languages: drop hoặc audit
```

Lưu ý: `MX` là quốc gia Mexico. Khi nói ngôn ngữ phụ nên ghi là `Spanish` hoặc `es-MX`.

### 5.2 Secondary language không phải Language Bleed

Đây là rule quan trọng của v3.1.

```text
Foreign language bleed ≠ Secondary language.
```

Nếu Spanish được khai báo là secondary language của US_EN, thì keyword như `centro de control` không được auto drop với lý do `LANGUAGE_BLEED`. Nó phải được xử lý là:

```text
LanguageGroup = SECONDARY
LanguageAction = CONSIDER hoặc AUDIT
```

Chỉ các ngôn ngữ nằm ngoài `primary_languages`, `secondary_languages`, và `optional_secondary_languages` mới được xem là foreign language mismatch.

### 5.3 Cách xử lý theo nhóm ngôn ngữ

| LanguageGroup | Cách xử lý |
|---|---|
| `PRIMARY` | Được xét vào Top 25 Core, 5 Broad, Feature Top 30, Style Top 30 |
| `SECONDARY` | Không auto drop, mặc định đưa vào Consider hoặc Secondary Language Keywords |
| `OPTIONAL_SECONDARY` | Chỉ giữ nếu data tốt, mặc định Audit hoặc Consider |
| `FOREIGN` | Drop hoặc đưa vào Language Mismatch Audit |
| `MIXED` | Chỉ giữ nếu tự nhiên với search behavior của market |
| `UNKNOWN` | Manual Review nếu điểm cao, drop nếu intent yếu |

### 5.4 Output language fields

Mỗi file chính nên có các cột:

| Cột | Ý nghĩa |
|---|---|
| `DetectedLanguage` | Ngôn ngữ nhận diện được |
| `LanguageGroup` | PRIMARY / SECONDARY / OPTIONAL_SECONDARY / FOREIGN / MIXED / UNKNOWN |
| `LanguageAction` | KEEP / CONSIDER / DROP / AUDIT / MANUAL_REVIEW |
| `LanguageReason` | Lý do xử lý |

Ví dụ:

| Keyword | LanguageGroup | Action | Reason |
|---|---|---|---|
| `control panel` | PRIMARY | KEEP | English keyword for US_EN |
| `centro de control` | SECONDARY | CONSIDER | Spanish keyword, possible US Hispanic search |
| `控制中心` | FOREIGN | DROP | Chinese is not allowed for US_EN |
| `centro de control widget` | MIXED | CONSIDER | Mixed Spanish + English, needs review |

### 5.5 Market language map mẫu

```python
MARKET_LANGUAGE_MAP = {
    "US_EN": {
        "primary": ["en"],
        "secondary": ["es", "es-MX"],
        "optional_secondary": [],
        "secondary_default_section": "Consider Keywords"
    },
    "MX_ES": {
        "primary": ["es", "es-MX"],
        "secondary": ["en"],
        "optional_secondary": [],
        "secondary_default_section": "Consider Keywords"
    },
    "BR_PT": {
        "primary": ["pt", "pt-BR"],
        "secondary": ["en"],
        "optional_secondary": ["es", "es-MX", "es-ES"],
        "secondary_default_section": "Consider Keywords"
    },
    "IN_EN": {
        "primary": ["en"],
        "secondary": ["hi"],
        "optional_secondary": [],
        "secondary_default_section": "Consider Keywords"
    },
    "VN_VI": {
        "primary": ["vi"],
        "secondary": ["en"],
        "optional_secondary": [],
        "secondary_default_section": "Consider Keywords"
    }
}
```

---

## 6. Rule Precedence

Pipeline có nhiều lớp rule. Vì vậy cần xác định rõ rule nào thắng rule nào.

Thứ tự ưu tiên bắt buộc:

```text
1. Force Drop / Competitor Brand / Policy hard drop
2. Typo / truncated / broken keyword
3. Foreign language mismatch
4. Clearly irrelevant intent
5. Core Intent Override
6. Risk Policy
7. Secondary / Optional Secondary language handling
8. Scoring + Bucket Classification
9. User Override Layer, trong phạm vi được phép
```

### 6.1 Rule nào không được override

User override có thể chuyển keyword giữa Top 30 / Consider / Reserve, nhưng không được override các nhóm sau:

- Competitor brand rõ ràng.
- Keyword broken / typo / truncated.
- Keyword sai intent rõ ràng.
- Foreign language nằm ngoài market policy.
- Policy hard drop.

Ví dụ:

| Keyword | User force_top30 có được không? | Lý do |
|---|---:|---|
| `control center themes` | Có | Intent sát |
| `iphone control center` | Không nên Top 30, nên Consider | Platform-style risk |
| `mi control center` | Không | Competitor brand |
| `center widg` | Không | Broken/truncated |
| `控制中心` trong US_EN | Không | Foreign language mismatch |

### 6.2 Core Intent Override không cứu competitor brand

Ví dụ:

```text
mi control center
```

Keyword này có `control center`, nhưng `mi control center` là competitor/app-style brand. Kết quả phải là:

```text
Dropped = Competitor brand
```

Không được giữ chỉ vì có core intent.

---

## 7. Hard Filter Rules

Hard filter chỉ dùng cho những trường hợp chắc chắn không nên dùng.

### 7.1 Auto Drop

Auto drop nếu keyword thuộc một trong các nhóm:

| Nhóm | Ví dụ |
|---|---|
| Competitor brand | `mi control center`, `power shade`, `one shade` |
| Typo/truncated | `control panl`, `center widg`, `widgit` |
| Irrelevant category | `calculator app`, `weather widget`, `call widget` nếu không liên quan |
| Foreign language mismatch | Keyword Trung / Việt / Bồ Đào Nha trong US_EN nếu không nằm trong language policy |
| Noise only | `app`, `phone`, `screen`, `theme` nếu đứng một mình hoặc quá rộng |

### 7.2 Không auto drop

Không auto drop mặc định nếu keyword thuộc các nhóm:

| Nhóm | Cách xử lý |
|---|---|
| iPhone / iOS / OS-style | Consider nếu có intent sát |
| Secondary language phù hợp country | Consider |
| Optional secondary language có data tốt | Audit hoặc Consider |
| Style/theme có liên quan tới core intent | Style file hoặc Full Description |
| Keyword dài nhưng natural | Giữ nếu có core intent |

---

## 8. Core Intent Override

Nếu keyword chứa core intent mạnh, pipeline không được loại tự động chỉ vì có term rủi ro nhẹ.

Ví dụ với Control Widget, core intent gồm:

```text
control center
control panel
control widget
quick settings
quick panel
notification panel
volume control
shortcut widget
```

Cách xử lý:

| Keyword | Không nên | Nên |
|---|---|---|
| `iphone control center` | Drop | Consider |
| `ios control center` | Drop | Consider |
| `control center themes` | Drop | Top 30 hoặc Style |
| `theme control center` | Drop | Style / Full Description |
| `mi control center` | Top 30 | Drop vì competitor/app brand |

---

## 9. Relevancy Scoring

`RelevancyScore` đánh giá keyword có sát app hay không.

Công thức gợi ý:

```text
RelevancyScore =
base
+ intent_core_match
+ feature_specific_match
+ style_theme_match
+ visual_extra_match
- competitor_penalty
- noise_penalty
- language_mismatch_penalty
- naturalness_penalty
```

### 9.1 Ví dụ điểm cao

```text
control panel
control widget
custom control panel
notification panel
quick settings
volume control widget
```

### 9.2 Ví dụ điểm trung bình

```text
widget themes
custom widget
color widgets
theme packs
cute widget
```

### 9.3 Ví dụ điểm thấp

```text
cute themes
beauty theme
simple theme
wallpaper themes
phone theme
```

---

## 10. Balanced Score & Scoring Normalization

`BalancedScore` dùng để xếp hạng trong từng bucket, không dùng để chọn toàn bộ Top 30 một cách mù quáng.

Công thức mặc định:

```text
BalancedScore =
0.20 * VolumeN
+ 0.15 * DifficultyN
+ 0.15 * KEIN
+ 0.30 * RelevancyScore
+ 0.10 * CurrentRankN
+ 0.10 * ExpansionValue
```

### 10.1 Công thức normalize bắt buộc

Để pipeline chạy ổn định giữa nhiều market, các biến phải được normalize rõ ràng.

#### VolumeN

Dùng log scale dựa trên lượng tìm kiếm đỉnh (`Max. Volume` trong 12 tháng qua) để tránh keyword volume lớn áp đảo quá mạnh và loại bỏ ảnh hưởng từ sự biến động ngắn hạn:

```text
VolumeN = log(Max. Volume + 1) / log(max_of_max_volumes + 1)
```

Nếu không có Max. Volume hoặc max_of_max_volumes = 0:

```text
VolumeN = 0
```

#### DifficultyN

Difficulty càng thấp càng tốt:

```text
DifficultyN = 1 - (Difficulty / 100)
```

Nếu Difficulty ngoài khoảng 0-100, clamp về 0-100 trước khi tính.

#### KEIN

KEI cũng dùng log scale:

```text
KEIN = log(KEI + 1) / log(MaxKEI + 1)
```

Nếu không có KEI hoặc MaxKEI = 0:

```text
KEIN = 0
```

#### CurrentRankN

Rank càng cao thì điểm càng tốt. Unranked không được cộng điểm rank.

| CurrentRank | CurrentRankN |
|---:|---:|
| 1-10 | 1.00 |
| 11-30 | 0.80 |
| 31-50 | 0.60 |
| 51-100 | 0.30 |
| >100 | 0.10 |
| Unranked / empty | 0.00 |

#### ExpansionValue

ExpansionValue đánh giá keyword có đáng mở rộng không.

Gợi ý tính:

```text
ExpansionValue =
0.45 * RelevancyScore
+ 0.25 * VolumeN
+ 0.20 * OpportunityRankGap
+ 0.10 * CompetitorCoverageN
```

Trong đó:

| Thành phần | Ý nghĩa |
|---|---|
| `OpportunityRankGap` | Cao nếu app rank yếu/unranked nhưng keyword vẫn sát intent |
| `CompetitorCoverageN` | Cao nếu nhiều competitor rank cho keyword đó |

Nếu không có dữ liệu competitor:

```text
CompetitorCoverageN = 0
```

Nếu không có rank:

```text
OpportunityRankGap = 1.0 nếu keyword liên quan cao và app unranked
OpportunityRankGap = 0.0 nếu keyword không liên quan
```

---

## 11. Bucket Classification

Sau scoring, keyword được phân loại vào các bucket sau:

| Bucket | Ý nghĩa |
|---|---|
| `Core Intent Final` | Keyword sát app nhất, ưu tiên Top 25 |
| `Broad Expansion` | Keyword rộng hơn nhưng vẫn hữu ích, chọn 5 |
| `Consider Keywords` | Keyword tiềm năng, cần review, chọn 10 |
| `Feature Keywords` | Keyword tính năng/type, xuất file 30 |
| `Style Keywords` | Keyword style/theme, xuất file 30 |
| `Generic Style Reserve` | Style quá rộng, không vào output chính |
| `Language Mismatch Audit` | Sai ngôn ngữ market |
| `Dropped` | Loại vì sai intent, typo, brand, noise |

---

## 12. Quota Fallback Policy

Không được nhét keyword yếu chỉ để đủ quota.

Nếu một section không đủ keyword qualified:

```text
1. Fill từ bucket đủ điều kiện gần nhất.
2. Chỉ fill nếu keyword đạt min_relevancy_for_fill.
3. Ghi rõ FillReason.
4. Nếu vẫn thiếu, output ít hơn quota và report rõ lý do.
```

Ví dụ:

```text
Core Intent chỉ có 18 keyword tốt.
→ Fill thêm 7 keyword từ Feature Expansion nếu đủ điểm.
→ Nếu vẫn thiếu, output 22 keyword thay vì nhét keyword rác để đủ 25.
```

Cột cần có khi fallback:

| Cột | Ý nghĩa |
|---|---|
| `FillSource` | Bucket gốc của keyword được dùng để fill |
| `FillReason` | Lý do được dùng để bù quota |
| `QuotaStatus` | EXACT / FILLED / UNDER_QUOTA |

---

## 13. Word Overlap Filter

Pipeline cần giảm trùng lặp giữa các keyword trong file chính.

Mặc định:

```python
max_word_overlap = 0.5
```

Áp dụng trong từng section trước:

- Core Intent Final
- Broad Expansion
- Consider Keywords
- Feature Keywords
- Style Keywords

Không nên so sánh quá gắt giữa Core và Consider, vì Consider có thể cố ý chứa variant để review.

Tuy nhiên có ngoại lệ cho core terms. Với app Control Widget, các từ như `control`, `panel`, `widget`, `quick`, `settings` có thể lặp vì đây là core của category.

Yêu cầu:

```text
Không loại keyword core chỉ vì lặp từ bắt buộc.
Chỉ loại nếu keyword gần như trùng ý và không thêm search intent mới.
```

Ví dụ:

| Keyword A | Keyword B | Cách xử lý |
|---|---|---|
| `control panel` | `custom control panel` | Có thể giữ cả hai |
| `quick settings` | `custom quick settings` | Có thể giữ cả hai |
| `cute themes` | `beauty theme` | Chỉ giữ nếu cần broad/style quota |
| `theme iphone` | `themes iphone` | Chỉ giữ một nếu không có lý do test cả hai |

---

## 14. Metadata Assignment by Platform

Không phải keyword điểm cao nào cũng nên vào slot quan trọng. Ngoài ra Google Play và App Store có slot khác nhau, nên pipeline phải có `platform_mode`.

### 14.1 Google Play mode

```python
"platform_mode": "google_play"
```

| Slot | Nên dùng | Không nên dùng |
|---|---|---|
| Title | Core intent an toàn | Brand đối thủ, platform-risk, style-only |
| Short Description | Core + feature + benefit | Keyword rủi ro cao, secondary language |
| Full Description | Long-tail, style, theme, broad, consider | Brand đối thủ |
| Consider | iOS/iPhone/platform-style, secondary language | Keyword sai intent rõ ràng |

### 14.2 App Store mode

```python
"platform_mode": "app_store"
```

| Slot | Nên dùng | Không nên dùng |
|---|---|---|
| Title | Core intent an toàn | Competitor brand, risky platform-style |
| Subtitle | Core + feature rõ | Keyword quá rộng |
| Keyword Field | High-value exact terms, variants | Duplicates, competitor brand |
| Promotional Text | Supporting phrases, broader benefit | Keyword stuffing |
| Consider | Secondary language, risky-but-relevant | Foreign language mismatch |

### 14.3 Ví dụ với Control Widget Google Play

| Slot | Keyword phù hợp |
|---|---|
| Title | `control panel`, `control widget` |
| Short Description | `custom control panel`, `quick settings`, `notification panel`, `volume control widget` |
| Full Description | `control center themes`, `widget themes`, `custom themes`, `theme control center` |
| Consider | `iphone control center`, `ios control center`, `theme iphone` |

---

## 15. Feature / Type file

Sheet `02_Feature_Keywords` chỉ xuất tối đa 30 keyword. Không được dump toàn bộ candidate.

Quota đề xuất:

```text
02_Feature_Keywords.csv
= 30 keyword curated

- 20 core feature keywords
- 5 feature expansion keywords
- 5 feature test keywords
```

Điều kiện:

- Phải mô tả chức năng/type/utility/search intent.
- Không chứa style-only keyword.
- Ưu tiên primary language.
- Secondary language chỉ xuất nếu config cho phép.
- Nếu không đủ 30 keyword chất lượng, output ít hơn và ghi `UNDER_QUOTA`.

Ví dụ với Control Widget:

```text
control panel
control widget
quick settings
notification panel
quick panel
volume control widget
shortcut widget
custom quick settings
android control panel
toggle settings
floating control panel
```

---

## 16. Style file

Sheet `03_Style_Keywords` chỉ xuất tối đa 30 keyword. Không được dump toàn bộ keyword style.

Quota đề xuất:

```text
03_Style_Keywords.csv
= 30 keyword curated

- 15 style keywords gắn với core intent
- 10 broad style keywords vẫn liên quan
- 5 platform-style consider keywords
```

Ưu tiên:

```text
control center themes
control center wallpaper
theme control center
control widget theme
widget themes
color widgets
custom themes
neon themes
cute widget
anime widget
```

Hạn chế:

```text
beauty theme
simple theme
stunning themes
diy theme pack
themes wallpaper
```

Nếu không đủ 30 keyword style chất lượng, output ít hơn và ghi rõ trong report.

---

## 17. User Override Layer

Sau mỗi lần user review, pipeline cần lưu lại các rule override cho app/category/market.

Override được phép:

- Chuyển keyword từ Reserve sang Consider.
- Chuyển keyword từ Consider sang Top 30 nếu không vi phạm hard filter.
- Giữ keyword iPhone/iOS/OS-style để review.
- Hạ generic style-only khỏi Core Top 25.

Override không được phép:

- Cứu competitor brand.
- Cứu keyword typo/truncated.
- Cứu keyword sai intent rõ ràng.
- Cứu keyword foreign language ngoài market policy vào output chính.

Ví dụ với Control Widget:

```python
"user_overrides": {
    "do_not_auto_drop_terms": [
        "control center",
        "iphone",
        "ios",
        "os 17",
        "os 18"
    ],
    "force_consider_terms": [
        "iphone control center",
        "ios control center",
        "theme iphone",
        "widget ios"
    ],
    "force_drop_terms": [
        "mi control center",
        "power shade",
        "one shade"
    ],
    "force_top30_terms": [
        "control panel",
        "control widget",
        "quick settings",
        "notification panel"
    ],
    "notes": [
        "Generic style-only keywords should not occupy core Top 25 slots.",
        "Sheet 01_Main_Keyword_Shortlist should include Top 30 plus 10 Consider rows at the bottom.",
        "Feature and Style sheets must be capped at 30 curated keywords each.",
        "Secondary language is not language bleed."
    ]
}
```

---

## 18. Control Widget APP_CONFIG mẫu

```python
APP_CONFIG = {
    "app_id": "com.control.widget.custom.panel.wallpaper.pack",
    "app_name": "Control Widget",
    "category": "Widget",
    "category_slug": "widget",
    "market": "US_EN",
    "platform_mode": "google_play",

    "market_language_policy": {
        "enabled": True,
        "required": True,
        "primary_languages": ["en"],
        "secondary_languages": ["es", "es-MX"],
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

    "feature_terms": [
        "control panel", "control center", "control widget",
        "quick settings", "notification panel", "quick panel",
        "volume panel", "brightness slider", "toggle", "shortcut",
        "settings panel", "wifi toggle", "bluetooth toggle",
        "flashlight toggle", "screen recorder", "screenshot",
        "dark mode", "airplane mode", "mobile data", "hotspot",
        "rotation lock", "do not disturb", "silent mode",
        "music control", "media control", "camera shortcut",
        "calculator shortcut", "floating", "edge panel", "side panel",
        "swipe gesture"
    ],

    "style_terms": [
        "ios 16", "ios 17", "ios 18", "ios style", "iphone style",
        "iphone control", "material you", "material design",
        "neon", "glassmorphism", "gradient", "blur", "transparent",
        "minimal", "clean", "elegant", "modern", "classic",
        "dark", "light", "amoled", "black", "colorful", "pastel",
        "aesthetic", "cute", "kawaii", "anime", "cyberpunk",
        "futuristic", "3d", "flat", "rounded"
    ],

    "intent_core_terms": [
        "control panel", "control center", "control widget",
        "quick settings", "notification panel", "quick panel",
        "volume control widget", "shortcut widget"
    ],

    "competitor_brands": [
        "mi control center", "power shade", "one shade",
        "volume styles", "super status bar", "bottom quick settings",
        "assistive touch", "dynamic island", "dynamic spot",
        "notiguy", "edge action", "sidebar"
    ],

    "noise_terms": [
        "widget", "widgets", "wallpaper", "wallpapers",
        "custom", "panel", "control", "settings", "android",
        "phone", "app", "application", "tool", "utility",
        "personalization", "theme", "themes", "launcher",
        "lock screen", "home screen", "display", "screen",
        "notification", "status", "bar", "quick", "shortcut",
        "icon", "icons", "font"
    ],

    "typo_blacklist": [
        "contol", "controll", "pannel", "widgit", "widjet",
        "custon", "custome", "setings", "sttings",
        "notifcation", "notificaion", "brigthness",
        "volum", "togel", "toggl", "shotcut", "shorcut",
        "shrtcut"
    ],

    "risk_policy": {
        "competitor_brand_action": "drop",
        "risky_ip_action": "consider",
        "platform_style_action": "consider",
        "style_only_action": "reserve",
        "core_intent_override": True
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

    "language_naturalness": {
        "enabled": True,
        "penalty_unnatural": -0.35,
        "auto_drop_score_below": 0.15,
        "rules": {
            "grammar_violation": {
                "patterns": [
                    r"\b(widget widget|panel panel|control control)\b",
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
                "note": "Spanish is secondary for US_EN, so Spanish words must not be auto-flagged as LANGUAGE_BLEED.",
                "forbidden_foreign_in_market": {
                    "US_EN": [
                        r"[\u4e00-\u9fff]",
                        r"[\u0400-\u04FF]",
                        r"[\u0600-\u06FF]"
                    ]
                },
                "flag": "LANGUAGE_BLEED"
            }
        }
    },

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
    "output_prefix": "ASO_Keyword_Planner_ControlWidget_US_EN",
    "output_mode": "excel_workbook",
    "output_workbook": {
        "enabled": True,
        "filename_pattern": "ASO_Keyword_Planner_ControlWidget_US_EN.xlsx",
        "export_csv_package": False,
        "export_markdown_report": False,
        "include_all_candidates_sheet": True,
        "include_optional_audit_sheets": True,
        "freeze_header_rows": True,
        "enable_filters": True,
        "format_as_tables": True,
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

    "user_overrides": {
        "do_not_auto_drop_terms": [
            "control center", "iphone", "ios", "os 17", "os 18"
        ],
        "force_consider_terms": [
            "iphone control center", "ios control center",
            "theme iphone", "themes iphone", "widget ios"
        ],
        "force_drop_terms": [
            "mi control center", "power shade", "one shade"
        ],
        "force_top30_terms": [
            "control panel", "control widget",
            "quick settings", "notification panel"
        ],
        "notes": [
            "Top 30 = 25 core intent + 5 broad expansion.",
            "Append 10 Consider Keywords at the bottom of sheet 01_Main_Keyword_Shortlist.",
            "Feature and Style files must be capped at 30 curated keywords.",
            "Secondary language keywords for US_EN should go to Consider, not Top 30.",
            "Spanish is secondary for US_EN, not language bleed."
        ]
    }
}
```

---

## 19. Prompt chạy pipeline

```markdown
Chạy ASO Keyword Planner cho app của tôi.

**App:** [Tên app]  
**App ID:** [Bundle ID]  
**Category:** [Category]  
**Market:** [Market code]  
**Platform:** [google_play hoặc app_store]  
**File CSV:** [đính kèm file CSV]

---

## APP_CONFIG

```python
[PASTE APP_CONFIG đã tùy chỉnh ở đây]
```

---

## YÊU CẦU

1. Đọc file CSV đính kèm.
2. Chạy đủ 10 bước của ASO Keyword Planner.
3. Xuất **01 file Excel tổng**:

   ```text
   ASO_Keyword_Planner_[AppName]_[Market].xlsx
   ```

4. Workbook Excel phải gồm các sheet bắt buộc:
   - `00_README_CONFIG`
   - `01_Main_Keyword_Shortlist`
   - `02_Feature_Keywords`
   - `03_Style_Keywords`
   - `04_Dropped_Audit`
   - `05_Report_Summary`
   - `06_All_Candidates`

5. Workbook có thể gồm các sheet phụ nếu có dữ liệu:
   - `07_Language_Mismatch`
   - `08_Generic_Style_Reserve`
   - `09_Manual_Review`
   - `10_Top_By_Score`
   - `11_Secondary_Language`

6. Sheet `01_Main_Keyword_Shortlist` phải gồm:
   - 25 Core / High Intent Keywords
   - 5 Broad Expansion Keywords
   - 10 Consider Keywords xếp cuối sheet

7. Sheet `02_Feature_Keywords` chỉ xuất tối đa 30 keyword curated.
8. Sheet `03_Style_Keywords` chỉ xuất tối đa 30 keyword curated.
9. Không đưa keyword sai ngôn ngữ market vào output chính.
10. Secondary language keyword không phải Language Bleed; chỉ đưa vào Consider nếu phù hợp với country.
11. Không auto drop iPhone / iOS / OS-style keyword nếu có core intent sát.
12. Generic style-only keyword không được chiếm slot Core Top 25.
13. Competitor brand phải bị loại khỏi metadata.
14. Áp dụng rule precedence trước user overrides.
15. Dùng scoring normalization theo định nghĩa trong pipeline.
16. Nếu không đủ quota, không nhét keyword yếu. Ghi rõ `UNDER_QUOTA` hoặc `FillReason`.
17. Sheet `05_Report_Summary` phải giải thích lý do giữ / loại / đưa vào Consider.
18. Không xuất nhiều file CSV/MD/JSON rời, trừ khi user yêu cầu thêm `export_csv_package = True`.

## PREVIEW TRONG CHAT

Hiển thị Top 10 keyword tốt nhất theo bảng:

| Section | Keyword | Volume | Difficulty | KEI | Rank | BalancedScore | Reason |
```

## 20. Báo cáo bắt buộc

Báo cáo không xuất thành file Markdown riêng mặc định. Nội dung báo cáo phải nằm trong sheet:

```text
05_Report_Summary
```

Sheet này nên chia thành các block rõ ràng để user mở Excel là review được ngay.

### 20.1 Summary

```text
Raw keywords:
Unique keywords:
Candidates after filter:
Dropped:
Core Intent Final:
Broad Expansion:
Consider:
Feature Keywords:
Style Keywords:
QuotaStatus:
Workbook output:
```

### 20.2 Language Summary

```text
PRIMARY:
SECONDARY:
OPTIONAL_SECONDARY:
FOREIGN:
MIXED:
UNKNOWN:
```

### 20.3 Naturalness Summary

```text
UNNATURAL:
STUFFING:
TOO_LONG:
LANGUAGE_BLEED:
```

### 20.4 Rule Precedence Summary

```text
Competitor drops:
Typo/truncated drops:
Foreign language mismatch:
Core intent override applied:
Risk policy consider:
User override applied:
User override rejected:
```

### 20.5 Top Decisions

Bảng trong sheet `05_Report_Summary`:

| Keyword | Section | Reason |
|---|---|---|
| `control panel` | Core Intent Final | Strong core intent |
| `iphone control center` | Consider | Strong intent but platform-style risk |
| `cute themes` | Generic Style Reserve | Style-only, weak app intent |
| `mi control center` | Dropped | Competitor brand |

### 20.6 Missed Opportunity Review

Danh sách keyword điểm cao nhưng không vào Top 30 chính:

| Keyword | Score | Vì sao không vào Top 30 |
|---|---:|---|
| `theme iphone` | 0.xx | Platform-style, moved to Consider |
| `cute themes` | 0.xx | Generic style-only |
| `centro de control` | 0.xx | Secondary language for US_EN |

### 20.7 Quota Fallback Review

Nếu section nào thiếu quota, report phải nói rõ:

| Section | Expected | Actual | QuotaStatus | Reason |
|---|---:|---:|---|---|
| Core Intent Final | 25 | 22 | UNDER_QUOTA | Not enough qualified core keywords |
| Broad Expansion | 5 | 5 | EXACT | — |
| Consider Keywords | 10 | 10 | FILLED | 2 items filled from missed opportunities |

### 20.8 Workbook Sheet Index

Sheet `05_Report_Summary` nên có thêm block `Workbook Sheet Index` để user biết từng sheet dùng làm gì.

| Sheet | Purpose | Row Count |
|---|---|---:|
| `01_Main_Keyword_Shortlist` | Top 30 + 10 Consider | 40 |
| `02_Feature_Keywords` | Feature/type keywords | <=30 |
| `03_Style_Keywords` | Style/theme keywords | <=30 |
| `04_Dropped_Audit` | Dropped keywords and reasons | n |
| `06_All_Candidates` | Full scored candidate pool | n |

## 21. Troubleshooting

### Vấn đề: Top 30 có quá nhiều keyword style chung

Cách sửa:

```text
- Tăng penalty cho style-only keyword.
- Bật style_only_action = reserve.
- Giữ quota 25 core + 5 broad.
- Chỉ cho style keyword vào Top 30 nếu có core intent.
```

### Vấn đề: Keyword iOS / iPhone bị loại hết

Cách sửa:

```text
- Không đưa iOS / iPhone vào hard drop.
- Thêm vào do_not_auto_drop_terms.
- Thêm force_consider_terms cho các keyword có intent sát.
```

### Vấn đề: Keyword secondary language bị flag nhầm là LANGUAGE_BLEED

Cách sửa:

```text
- Kiểm tra market_language_policy.secondary_languages.
- Không đưa từ thuộc secondary language vào forbidden_foreign_in_market.
- LANGUAGE_BLEED chỉ dùng cho foreign language ngoài policy.
```

### Vấn đề: Keyword ngôn ngữ khác lọt vào output chính

Cách sửa:

```text
- Bật market_language_policy.
- Định nghĩa primary_languages rõ ràng.
- Định nghĩa secondary_languages và optional_secondary_languages nếu cần.
- Đưa foreign language vào Language Mismatch Audit.
```

### Vấn đề: Sheet Feature / Style quá dài

Cách sửa:

```text
- Bật keyword_quota.feature_file.max_keywords = 30.
- Bật keyword_quota.style_file.max_keywords = 30.
- Chỉ đưa curated shortlist vào các sheet chính.
- Candidate pool đầy đủ chỉ xuất ở All_Candidates.csv hoặc Audit.
```

### Vấn đề: Keyword core bị loại vì word overlap

Cách sửa:

```text
- Thêm core terms vào overlap exception.
- Không loại keyword nếu nó thêm intent mới.
- Cho phép lặp các từ bắt buộc của category như control, panel, widget, quick, settings.
```

### Vấn đề: Không đủ quota 25/5/10

Cách sửa:

```text
- Không ép đủ quota bằng keyword yếu.
- Bật fallback_policy.allow_under_quota.
- Fill từ next best eligible bucket nếu đủ min_relevancy_for_fill.
- Ghi rõ FillReason và QuotaStatus trong report.
```

---

## 22. Quy tắc ngắn gọn để nhớ

```text
1. Top 30 = 25 sát intent + 5 mở rộng có kiểm soát.
2. Thêm 10 Consider ở cuối sheet chính.
3. Consider có sub-quota: platform-style, secondary language, missed opportunities.
4. Feature sheet chỉ lấy tối đa 30 keyword curated.
5. Style sheet chỉ lấy tối đa 30 keyword curated.
6. Mỗi market bắt buộc có primary / secondary / optional secondary language policy.
7. Secondary language không phải Language Bleed.
8. Keyword sai ngôn ngữ market không vào output chính.
9. iPhone / iOS / OS-style không auto drop nếu có intent sát.
10. Generic style-only không chiếm slot core.
11. Competitor brand phải drop, Core Intent Override không được cứu competitor brand.
12. BalancedScore phải normalize rõ ràng.
13. Nếu không đủ quota, output thiếu còn hơn nhét keyword yếu.
14. Metadata assignment phải theo platform_mode: google_play hoặc app_store.
15. Report phải nói rõ vì sao giữ, loại, đưa vào Consider hoặc fill quota.
```

---

## 23. Nội dung đã bổ sung ở v3.2

### P0 — Bổ sung bắt buộc

- Sửa mâu thuẫn Language Policy: secondary language không phải `LANGUAGE_BLEED`.
- Thêm `optional_secondary_languages`.
- Thêm Rule Precedence: rule nào thắng rule nào.
- Giới hạn quyền của User Override Layer.


### P2 — Thay đổi output mặc định

- Chuyển output mặc định từ nhiều file CSV/MD/JSON sang **01 Excel workbook tổng**.
- Mỗi output cũ trở thành một sheet trong workbook.
- Thêm `output_mode = "excel_workbook"` và block `output_workbook`.
- Thêm sheet `00_README_CONFIG` để lưu config, app info và run summary.
- Thêm sheet `05_Report_Summary` thay cho file `05_ASO_Report.md`.
- Giữ CSV/Markdown là export phụ, chỉ bật khi user yêu cầu.

### P1 — Bổ sung quan trọng

- Định nghĩa rõ công thức normalize cho Volume, Difficulty, KEI, Rank, ExpansionValue.
- Thêm Quota Fallback Policy khi không đủ 25/5/10 hoặc 30 Feature/Style.
- Thêm sub-quota cho 10 Consider Keywords.
- Thêm `platform_mode` và metadata slot riêng cho Google Play / App Store.

---

*ASO Keyword Planner v3.3*  
*Updated for single-workbook Excel output, strict language policy, rule precedence, scoring normalization, quota fallback, consider sub-quota, platform-specific metadata assignment, global text-level dedup, and Game Emulator semantic mode.*


---

## 24. Cập nhật v3.3 — Global Text-Level Dedup

### 24.1 Lý do bổ sung

Trong v3.2, bước `Word Overlap & Diversity Filter` đã có nhưng chưa đủ chặt ở cấp bảng cuối. Một số keyword gần giống về bề mặt chữ vẫn có thể lọt vào cùng output do quota fill, ví dụ:

```text
emulador de gba retrô
emulador de jogos de gba
emulador de gba
emulador gba
```

Từ v3.3, pipeline phải có một bước riêng:

```text
Final Text-Level Near-Duplicate Cleanup
```

Bước này chạy sau scoring/bucket classification nhưng trước khi xuất từng sheet curated.

### 24.2 Phạm vi áp dụng

Bắt buộc áp dụng cho tất cả bảng curated:

```text
01_Main_Keyword_Shortlist
02_Feature_Keywords hoặc 02_System_Keywords
03_Style_Keywords hoặc 03_Game_Keywords
```

Các sheet audit/raw sau vẫn giữ dữ liệu đầy đủ để truy vết:

```text
04_Dropped_Audit
06_All_Candidates
09_Manual_Review
10_Top_By_Score
11_Secondary_Language
```

Nếu có keyword bị loại khỏi sheet curated vì trùng gần, keyword đó không bị xóa khỏi `06_All_Candidates`.

### 24.3 Quy tắc text-level dedup

Dedup này không phải semantic clustering quá rộng. Chỉ loại keyword khi bề mặt chữ quá gần nhau.

Chuẩn hóa trước khi so sánh:

```text
- Lowercase
- Remove accents: retrô = retro
- Normalize spacing/punctuation
- Normalize singular/plural cơ bản:
  games -> game
  jogos -> jogo
  consoles -> console
  emuladores -> emulador
- Normalize spacing variants:
  game boy = gameboy
```

Loại nếu:

```text
1. Exact normalized duplicate
2. Same normalized token set
3. Cùng hệ máy + cùng intent chính + token overlap cao
```

Ví dụ phải loại bớt:

| Keyword A | Keyword B | Lý do |
|---|---|---|
| `gba jogos retrô` | `gba jogos retro` | Exact normalized duplicate |
| `jogos retro gba` | `gba jogos retrô` | Same normalized token set |
| `emulador de gba retrô` | `emulador de jogos de gba` | Same system + emulator wording |
| `emulador de game boy` | `emulador gameboy` | Same system + emulator wording |

Ví dụ không được loại:

| Keyword A | Keyword B | Lý do giữ |
|---|---|---|
| `gba emulador` | `gba jogos retrô` | Khác search intent: emulator query vs game query |
| `emulador arcade` | `jogos de arcade retrô` | Khác intent: emulator vs game catalog |
| `gameboy emulador` | `gameboy retro games` | Khác intent: emulator vs game discovery |

### 24.4 Dedup log bắt buộc

Workbook nên có sheet:

```text
12_Text_Dedup_Log
```

Cột bắt buộc:

| Column | Purpose |
|---|---|
| `Table` | Sheet bị lọc trùng |
| `RemovedKeyword` | Keyword bị bỏ khỏi curated table |
| `OriginalSection` | Section/bucket ban đầu |
| `KeptKeyword` | Keyword được giữ làm đại diện |
| `DedupReason` | Lý do loại |
| `BalancedScore` | Điểm keyword bị loại |
| `Note` | Ghi chú rằng keyword vẫn còn trong All Candidates |

### 24.5 Quota sau dedup

Quy tắc quota khác nhau theo sheet:

#### Sheet 01 — Main Keyword Shortlist

```text
01_Main_Keyword_Shortlist phải đủ quota:
25 Core / High Intent
+ 5 Broad Expansion
+ 10 Consider Keywords
= 40 rows
```

Nếu dedup làm thiếu keyword:

```text
1. Lấy keyword tiếp theo trong bucket đủ điều kiện.
2. Vẫn phải chạy text-level dedup với toàn sheet.
3. Không lấy keyword hard-drop, sai ngôn ngữ, competitor brand, typo/broken.
4. Ghi FillReason nếu keyword được dùng để bù quota.
```

Nói cách khác:

```text
01 cần đủ số lượng keyword theo yêu cầu.
Dedup xong thì fill tiếp bằng keyword đủ điều kiện, không dừng ở under-quota.
```

#### Sheet 02 và Sheet 03

```text
02 và 03 không bắt buộc đủ 30 keyword.
```

Nếu sau dedup chỉ còn ít hơn 30 keyword nhưng đúng intent:

```text
Dừng lại.
Không thêm keyword yếu chỉ để đủ số lượng.
```

---

## 25. Cập nhật v3.4 — Các thay đổi phổ quát hệ thống (Universal Pipeline Updates)

Phiên bản 3.4 chính thức bổ sung 4 cơ chế xử lý phổ quát cho toàn bộ các pipeline (bao gồm `AR_Filter`, `Control_Widget` và `Game_Emulator`) nhằm tối ưu hóa độ chính xác và tính thực tiễn của dữ liệu:

### 25.1 Loại bỏ điểm phạt và chuẩn hóa theo Peak Volume (Peak Volume Normalization)
Để khuyến khích các từ khóa có lượng tìm kiếm đỉnh trong quá khứ tốt (thể hiện tiềm năng thực tế cao mà không bị phạt bởi các biến động thuật toán hoặc thị trường ngắn hạn):
1. **Loại bỏ điểm phạt**: Hệ thống không còn áp dụng điểm phạt dựa trên tỷ lệ `Traffic Stability` vào điểm Volume chuẩn hóa. Cột `Traffic Stability` và phân loại `Stability Class` vẫn được giữ lại làm siêu dữ liệu xuất ra báo cáo để người dùng tham khảo, nhưng không ảnh hưởng tiêu cực đến điểm xếp hạng.
2. **Hiệu chỉnh công thức VolumeN**: Điểm Volume chuẩn hóa được tính trực tiếp dựa trên giá trị lượng tìm kiếm lớn nhất trong 12 tháng qua (`Max. Volume`):
   $$\text{VolumeN} = \frac{\ln(1 + \text{Max. Volume})}{\ln(1 + \text{max\_of\_max\_volumes})}$$
3. **Ý nghĩa**: Các từ khóa có tiềm năng cao trong quá khứ (kể cả khi lượng tìm kiếm hiện tại tạm thời sụt giảm do thuật toán Google thay đổi) vẫn được chấm điểm cao để người dùng giữ lại xem xét và tối ưu hóa lâu dài.

### 25.2 Nhận diện ngôn ngữ lai (Hybrid Language Detection Heuristic)
Nhằm ngăn ngừa hiện tượng loại bỏ sai các cụm từ ASO tiếng Anh ngắn do các thư viện tự động nhận diện ngôn ngữ gắn cờ nhầm là ngôn ngữ lạ (Language Bleed):
1. **Whitelist từ vựng**: Sử dụng whitelist 10,000 từ tiếng Anh phổ thông (`english_words_10k.txt`) kết hợp các nhóm từ khóa đặc thù ứng dụng trong `App_Profile.json` (ví dụ: `gba`, `nds`, `psp`, `emulator`).
2. **Kiểm tra trước**: Từ khóa sau khi loại bỏ các hậu tố thông thường (`s`, `es`, `ed`, `ing`...) nếu tất cả các từ đơn đều nằm trong whitelist sẽ được mặc định gắn nhãn `PRIMARY` (ngôn ngữ chính của market).
3. **Dự phòng (Fallback)**: Chỉ thực hiện gọi thư viện `langdetect` đối với các từ khóa chứa từ lạ ngoài danh sách whitelist. Điều này giúp loại bỏ triệt để hiện tượng lẫn tiếng Tây Ban Nha/Bồ Đào Nha vào thị trường US_EN mà vẫn giữ lại được các từ viết tắt hay thuật ngữ ASO đặc thù.

### 25.3 Siết chặt độ liên quan của từ khóa generic (Generic Relevancy Tightening)
Đối với các ứng dụng, các từ khóa quá chung chung chỉ chứa từ cốt lõi của danh mục mà không đi kèm với bất kỳ ngữ cảnh cụ thể nào (ví dụ: chỉ chứa `"emulator"` cho Game Emulator, chỉ chứa `"widget"` cho Control Widget, hay chỉ chứa `"filter"` / `"effect"` cho AR Filter) sẽ bị giới hạn điểm liên quan:
1. **Quy tắc tính điểm**: Từ cốt lõi của danh mục chỉ được cộng tối đa điểm thưởng liên quan (`+0.40`) nếu từ khóa đó có chứa ít nhất một thuật ngữ ngữ cảnh liên quan (ví dụ: tên hệ máy `gba`/`psp` đối với Emulator, tên tính năng/visual/style đối với Widget hay Filter).
2. **Hành vi**: Nếu không có ngữ cảnh đi kèm, điểm liên quan (Relevancy Score) của từ khóa sẽ chỉ đạt tối đa `0.40` (thấp hơn ngưỡng lọc tối thiểu `0.45`), từ đó tự động bị chuyển sang sheet loại bỏ `04_Dropped_Audit` dưới lý do `"Dropped: Weak app intent after scoring"`.

### 25.4 Thứ tự sắp xếp ưu tiên phụ (Tie-breaker Sorting Logic)
Khi nhiều từ khóa có cùng điểm `BalancedScore` (rất phổ biến đối với các từ khóa volume thấp), hệ thống không sắp xếp theo thứ tự ngẫu nhiên trong CSV gốc nữa mà áp dụng cơ chế phân hạng chi tiết:
1. **Chuyển đổi dữ liệu**: Cột `Rank` được chuyển đổi sang dạng số thông qua helper column `Rank_numeric` (các trường hợp không có rank hoặc unranked được điền mặc định là `999`).
2. **Thứ tự sắp xếp tối ưu**:
   - `BalancedScore` (giảm dần) - Ưu tiên điểm tổng hợp cao nhất.
   - `Rank_numeric` (tăng dần) - Ưu tiên từ khóa ứng dụng có thứ hạng tốt hơn (ví dụ: Rank 12 xếp trước Rank 24).
   - `KEI` (giảm dần) - Ưu tiên hiệu quả từ khóa cao hơn.
   - `Difficulty` (tăng dần) - Ưu tiên từ khóa dễ SEO hơn.
