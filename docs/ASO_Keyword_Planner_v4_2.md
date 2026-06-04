# ASO Keyword Planner

**PhiÃªn báº£n:** 4.2
**TÃªn cÅ©:** ASO Keyword Master Pipeline â€” Universal Template  
**TÃªn má»›i:** ASO Keyword Planner  
**Má»¥c Ä‘Ã­ch:** Lá»c, cháº¥m Ä‘iá»ƒm, phÃ¢n nhÃ³m vÃ  xuáº¥t shortlist keyword ASO theo tá»«ng app, tá»«ng market, tá»«ng ngÃ´n ngá»¯ vÃ  tá»«ng ná»n táº£ng metadata.  
**DÃ¹ng cho:** Google Play / App Store keyword research, metadata planning, ASO testing, UA keyword review.

---

## 0. TÆ° duy cá»‘t lÃµi

ASO Keyword Planner khÃ´ng chá»‰ lÃ  má»™t bá»™ lá»c keyword. Má»¥c tiÃªu cá»§a pipeline lÃ  táº¡o ra má»™t **keyword decision sheet**: keyword nÃ o nÃªn dÃ¹ng ngay, keyword nÃ o nÃªn giá»¯ Ä‘á»ƒ cÃ¢n nháº¯c, keyword nÃ o chá»‰ nÃªn dÃ¹ng lÃ m supporting keyword, keyword nÃ o cáº§n audit, vÃ  keyword nÃ o pháº£i loáº¡i.

Pipeline cáº§n trÃ¡nh 3 lá»—i phá»• biáº¿n:

1. **QuÃ¡ mÃ¡y mÃ³c theo Ä‘iá»ƒm sá»‘**  
   Keyword cÃ³ Volume/KEI cao nhÆ°ng quÃ¡ rá»™ng váº«n khÃ´ng nÃªn chiáº¿m slot chÃ­nh.

2. **QuÃ¡ gáº¯t khi lá»c rá»§i ro**  
   Má»™t sá»‘ keyword nhÆ° iPhone / iOS / OS-style cÃ³ thá»ƒ cÃ³ intent sÃ¡t. KhÃ´ng nÃªn auto drop náº¿u váº«n cÃ³ giÃ¡ trá»‹ nghiÃªn cá»©u.

3. **Láº«n ngÃ´n ngá»¯ sai market**  
   Keyword khÃ¡c ngÃ´n ngá»¯ metadata chÃ­nh khÃ´ng nÃªn tá»± Ä‘á»™ng chen vÃ o output chÃ­nh, dÃ¹ cÃ³ Ä‘iá»ƒm tá»‘t. Tuy nhiÃªn secondary language phÃ¹ há»£p quá»‘c gia váº«n nÃªn Ä‘Æ°á»£c giá»¯ Ä‘á»ƒ Consider.

NguyÃªn táº¯c má»›i:

```text
Top keyword khÃ´ng chá»‰ lÃ  keyword cÃ³ Ä‘iá»ƒm cao nháº¥t.
Top keyword pháº£i lÃ  keyword cÃ³ thá»ƒ dÃ¹ng Ä‘Æ°á»£c, Ä‘Ãºng intent, Ä‘Ãºng ngÃ´n ngá»¯, Ä‘Ãºng slot metadata, Ä‘Ãºng platform vÃ  Ä‘Ãºng má»©c rá»§i ro.
```

---

## 0.1 YÃªu cáº§u chuáº©n Ä‘áº§u vÃ o (Input CSV Specifications)

Äá»ƒ Ä‘áº£m báº£o pipeline xá»­ lÃ½ dá»¯ liá»‡u chÃ­nh xÃ¡c vÃ  khÃ´ng gáº·p lá»—i kiá»ƒu dá»¯ liá»‡u á»Ÿ BÆ°á»›c 1 (Data Ingestion), file CSV Ä‘áº§u vÃ o cá»§a tá»« khÃ³a ASO cáº§n tuÃ¢n thá»§ nghiÃªm ngáº·t cÃ¡c tiÃªu chuáº©n sau:

### 0.1.1 Äá»‹nh dáº¡ng vÃ  mÃ£ hÃ³a file
- **MÃ£ hÃ³a (Encoding)**: Báº¯t buá»™c lÃ  **UTF-8** hoáº·c **UTF-8 with BOM** (`utf-8-sig`). Äiá»u nÃ y cá»±c ká»³ quan trá»ng Ä‘á»ƒ báº£o vá»‡ cÃ¡c kÃ½ tá»± tiáº¿ng Viá»‡t (cÃ³ dáº¥u), tiáº¿ng TÃ¢y Ban Nha, tiáº¿ng Bá»“ ÄÃ o Nha hoáº·c tiáº¿ng Hindi khÃ´ng bá»‹ lá»—i font (mojibake).
- **Dáº¥u phÃ¢n tÃ¡ch (Delimiter)**: Dáº¥u pháº©y chuáº©n (`,`).

### 0.1.2 TÃªn file vÃ  thÆ° má»¥c lÆ°u trá»¯
- **Quy chuáº©n tÃªn file**: `[AppName]_[Country]_[Language].csv` hoáº·c fallback `[Country]_[Language].csv`.
  - *VÃ­ dá»¥*: `ARFilter_US_EN.csv`, `ControlWidget_BR_PT.csv`, `US_EN.csv`
- **Quy chuáº©n Ä‘Æ°á»ng dáº«n thÆ° má»¥c**: `[Component]/Input/[MMYYYY]/[TÃªn_File].csv`
  - *VÃ­ dá»¥*: `apps/AR_Filter/Input/052026/ARFilter_US_EN.csv`

### 0.1.3 CÃ¡c cá»™t dá»¯ liá»‡u báº¯t buá»™c vÃ  tÃ¹y chá»n

| TÃªn Cá»™t | Kiá»ƒu Dá»¯ Liá»‡u | Tráº¡ng ThÃ¡i | MÃ´ Táº£ & Xá»­ LÃ½ Fallback |
|---|---|---|---|
| `Keyword` | String (Text) | **Báº¯t buá»™c** | Tá»« khÃ³a cáº§n Ä‘Ã¡nh giÃ¡. Pháº£i lÃ  vÄƒn báº£n khÃ´ng chá»©a kÃ½ tá»± láº¡. Náº¿u dÃ²ng bá»‹ rá»—ng sáº½ tá»± Ä‘á»™ng bá»‹ bá» qua. |
| `Volume` | Integer (Sá»‘ nguyÃªn) | TÃ¹y chá»n | LÆ°á»£ng tÃ¬m kiáº¿m hiá»‡n táº¡i cá»§a tá»« khÃ³a. Náº¿u khÃ´ng cÃ³, máº·c Ä‘á»‹nh gÃ¡n = `0`. |
| `Max. Volume` hoáº·c `Max Volume` | Integer (Sá»‘ nguyÃªn) | TÃ¹y chá»n | LÆ°á»£ng tÃ¬m kiáº¿m cao nháº¥t trong 12 thÃ¡ng qua. Náº¿u khÃ´ng cÃ³, máº·c Ä‘á»‹nh láº¥y báº±ng giÃ¡ trá»‹ cá»™t `Volume`. |
| `MaximumReach` hoáº·c `Maximum Reach` | Integer (Sá»‘ nguyÃªn) | TÃ¹y chá»n | LÆ°á»£ng impression tá»‘i Ä‘a Æ°á»›c tÃ­nh. Náº¿u cÃ³, pipeline Æ°u tiÃªn dÃ¹ng cá»™t nÃ y Ä‘á»ƒ normalize volume theo traffic thá»±c táº¿. |
| `Difficulty` | Integer (Sá»‘ nguyÃªn) | TÃ¹y chá»n | Äiá»ƒm Ä‘á»™ khÃ³ cá»§a tá»« khÃ³a ($0 - 100$). Náº¿u khÃ´ng cÃ³, máº·c Ä‘á»‹nh gÃ¡n = `0`. |
| `KEI` | Float (Sá»‘ tháº­p phÃ¢n) | TÃ¹y chá»n | Chá»‰ sá»‘ hiá»‡u quáº£ tá»« khÃ³a. Náº¿u khÃ´ng cÃ³, máº·c Ä‘á»‹nh gÃ¡n = `0.0`. |
| `Rank` hoáº·c `CurrentRank` | String hoáº·c Integer | TÃ¹y chá»n | Thá»© háº¡ng hiá»‡n táº¡i cá»§a app cho tá»« khÃ³a nÃ y. Náº¿u khÃ´ng cÃ³, máº·c Ä‘á»‹nh gÃ¡n = `"Unranked"`. |

### 0.1.4 Chuáº©n hÃ³a kiá»ƒu dá»¯ liá»‡u tá»± Ä‘á»™ng
Khi Ä‘á»c dá»¯ liá»‡u, pipeline sáº½ tá»± Ä‘á»™ng thá»±c hiá»‡n Ã©p kiá»ƒu vÃ  chuáº©n hÃ³a:
1. Ã‰p cÃ¡c cá»™t `Volume`, `Max. Volume`, `MaximumReach`, `Difficulty` sang dáº¡ng sá»‘, Ä‘iá»n `0` náº¿u gáº·p dá»¯ liá»‡u lá»—i (`NaN` hoáº·c lá»—i Ä‘á»‹nh dáº¡ng).
2. Ã‰p cá»™t `KEI` sang dáº¡ng sá»‘ thá»±c, Ä‘iá»n `0.0` náº¿u lá»—i.
3. Náº¿u cá»™t `Max. Volume` bá»‹ thiáº¿u, há»‡ thá»‘ng tá»± Ä‘á»™ng gÃ¡n dá»¯ liá»‡u tá»« cá»™t `Volume` Ä‘á»ƒ tÃ­nh toÃ¡n tá»‰ lá»‡ `Traffic Stability`.

---

## 1. Output cuá»‘i cÃ¹ng

Pipeline máº·c Ä‘á»‹nh chá»‰ xuáº¥t **01 file Excel tá»•ng** thay vÃ¬ nhiá»u file rá»i.

```text
ASO_Keyword_Planner_[AppName]_[Market].xlsx
```

Workbook nÃ y lÃ  **single source of truth** cho toÃ n bá»™ káº¿t quáº£ keyword research: shortlist, feature/style grouping, audit, report vÃ  config Ä‘Ã£ dÃ¹ng Ä‘á»ƒ cháº¡y.

### 1.1 Workbook báº¯t buá»™c

| Sheet | Má»¥c Ä‘Ã­ch | Sá»‘ lÆ°á»£ng / Ghi chÃº |
|---|---|---:|
| `00_README_CONFIG` | ThÃ´ng tin app, market, platform, config tÃ³m táº¯t, thá»i gian cháº¡y | 1 sheet |
| `01_Main_Keyword_Shortlist` | Top 30 + 10 Consider | 40 rows |
| `02_Feature_Keywords` | Keyword tÃ­nh nÄƒng / type / intent chá»©c nÄƒng | Tá»‘i Ä‘a 30 rows |
| `03_Style_Keywords` | Keyword style / theme / visual intent | Tá»‘i Ä‘a 30 rows |
| `04_Dropped_Audit` | Keyword bá»‹ loáº¡i + lÃ½ do | KhÃ´ng giá»›i háº¡n |
| `05_Report_Summary` | BÃ¡o cÃ¡o tá»•ng há»£p pipeline | 1 sheet |
| `06_All_Candidates` | ToÃ n bá»™ keyword sau chuáº©n hÃ³a, scoring vÃ  classification | KhÃ´ng giá»›i háº¡n |

### 1.2 Sheet phá»¥ cÃ³ Ä‘iá»u kiá»‡n

CÃ¡c sheet sau chá»‰ táº¡o náº¿u cÃ³ dá»¯ liá»‡u tÆ°Æ¡ng á»©ng. Náº¿u khÃ´ng cÃ³ dá»¯ liá»‡u, cÃ³ thá»ƒ bá» qua hoáº·c táº¡o sheet rá»—ng vá»›i note `NO_DATA`.

| Sheet phá»¥ | Má»¥c Ä‘Ã­ch |
|---|---|
| `07_Language_Mismatch` | Keyword sai ngÃ´n ngá»¯ market |
| `08_Generic_Style_Reserve` | Keyword style quÃ¡ rá»™ng, chÆ°a nÃªn dÃ¹ng |
| `09_Manual_Review` | Keyword cÃ³ rá»§i ro hoáº·c cáº§n quyáº¿t Ä‘á»‹nh thá»§ cÃ´ng |
| `10_Top_By_Score` | Top keyword thuáº§n theo BalancedScore Ä‘á»ƒ audit |
| `11_Secondary_Language` | Keyword ngÃ´n ngá»¯ phá»¥ Ä‘á»ƒ nghiÃªn cá»©u riÃªng |

### 1.3 KhÃ´ng xuáº¥t nhiá»u file rá»i máº·c Ä‘á»‹nh

KhÃ´ng xuáº¥t cÃ¡c file CSV/MD/JSON riÃªng láº» nhÆ° máº·c Ä‘á»‹nh cÅ©:

```text
01_Main_Keyword_Shortlist.csv
02_Feature_Keywords.csv
03_Style_Keywords.csv
04_Dropped_Keywords_Audit.csv
05_ASO_Report.md
sheet `00_README_CONFIG`
```

Thay vÃ o Ä‘Ã³, toÃ n bá»™ ná»™i dung trÃªn pháº£i náº±m trong **cÃ¡c sheet cá»§a cÃ¹ng má»™t workbook Excel**.

Chá»‰ export thÃªm CSV hoáº·c Markdown khi user yÃªu cáº§u rÃµ:

```text
export_csv_package = True
export_markdown_report = True
```

### 1.4 Quy chuáº©n chung cho workbook

Má»—i sheet dáº¡ng báº£ng nÃªn cÃ³:

- Header row cá»‘ Ä‘á»‹nh.
- Filter báº­t sáºµn.
- Column width dá»… Ä‘á»c.
- CÃ¡c cá»™t text dÃ i báº­t wrap text.
- CÃ¡c cá»™t score Ä‘á»‹nh dáº¡ng sá»‘ tháº­p phÃ¢n.
- CÃ¡c cá»™t Volume / Difficulty / KEI / Rank Ä‘á»‹nh dáº¡ng sá»‘.
- Cá»™t `Reason` hoáº·c `DecisionReason` Ä‘á»ƒ giáº£i thÃ­ch táº¡i sao keyword Ä‘Æ°á»£c giá»¯, loáº¡i, Ä‘Æ°a vÃ o Consider hoáº·c reserve.
- Cá»™t `Section` cho cÃ¡c sheet shortlist chÃ­nh.
- Cá»™t `QuotaStatus`, `FillSource`, `FillReason` náº¿u cÃ³ dÃ¹ng fallback.

Workbook pháº£i Ä‘á»§ rÃµ Ä‘á»ƒ user cÃ³ thá»ƒ má»Ÿ Excel vÃ  review ngay mÃ  khÃ´ng cáº§n ghÃ©p nhiá»u file láº¡i vá»›i nhau.

## 2. Cáº¥u trÃºc Top 30 má»›i

Sheet `01_Main_Keyword_Shortlist` khÃ´ng cÃ²n chá»n thuáº§n theo `BalancedScore`. Top 30 Ä‘Æ°á»£c chia theo quota:

```text
Top 30 Final Cut
= 25 Core / High Intent Keywords
+ 5 Broad Expansion Keywords

Extra
= 10 Consider Keywords
```

### 2.1 Top 25 Core / High Intent Keywords

ÄÃ¢y lÃ  nhÃ³m keyword sÃ¡t intent chÃ­nh nháº¥t cá»§a app.

Äiá»u kiá»‡n:

- CÃ³ liÃªn quan trá»±c tiáº¿p tá»›i chá»©c nÄƒng chÃ­nh hoáº·c search intent chÃ­nh.
- KhÃ´ng pháº£i keyword style-only quÃ¡ rá»™ng.
- KhÃ´ng dÃ­nh brand Ä‘á»‘i thá»§.
- KhÃ´ng sai ngÃ´n ngá»¯ market.
- Æ¯u tiÃªn primary language cá»§a market.
- Secondary language khÃ´ng Ä‘Æ°á»£c vÃ o Top 25 máº·c Ä‘á»‹nh, trá»« khi user báº­t override rÃµ rÃ ng.

VÃ­ dá»¥ vá»›i Control Widget:

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

ÄÃ¢y lÃ  nhÃ³m keyword rá»™ng hÆ¡n nhÆ°ng váº«n cÃ³ liÃªn quan tá»›i app. Má»¥c tiÃªu lÃ  má»Ÿ rá»™ng semantic coverage vÃ  giÃºp nghiÃªn cá»©u thÃªm hÆ°á»›ng growth.

Äiá»u kiá»‡n:

- CÃ³ liÃªn quan tá»›i category hoáº·c nhu cáº§u ngÆ°á»i dÃ¹ng.
- KhÃ´ng quÃ¡ generic.
- KhÃ´ng chiáº¿m slot core intent.
- Æ¯u tiÃªn keyword cÃ³ gáº¯n vá»›i widget / theme / custom / panel / setting / feature liÃªn quan.
- KhÃ´ng quÃ¡ 2 keyword style-only trong nhÃ³m Broad Expansion.
- Secondary language chá»‰ Ä‘Æ°á»£c vÃ o Broad Expansion náº¿u config cho phÃ©p vÃ  cÃ³ quota riÃªng.

VÃ­ dá»¥ cháº¥p nháº­n Ä‘Æ°á»£c:

```text
custom widget
color widgets
widget themes
custom themes
theme packs
cute widget
```

VÃ­ dá»¥ nÃªn háº¡n cháº¿:

```text
beauty theme
simple theme
stunning themes
themes wallpaper
diy theme pack
```

### 2.3 10 Consider Keywords

ÄÃ¢y lÃ  nhÃ³m keyword cÃ³ tiá»m nÄƒng nhÆ°ng chÆ°a nÃªn Ä‘Æ°a tháº³ng vÃ o Top 30 chÃ­nh.

NhÃ³m nÃ y cÃ³ thá»ƒ gá»“m:

- Keyword platform-style: iPhone / iOS / OS version.
- Keyword secondary language phÃ¹ há»£p vá»›i quá»‘c gia.
- Keyword cÃ³ intent sÃ¡t nhÆ°ng hÆ¡i rá»§i ro vá» wording.
- Keyword cÃ³ volume tá»‘t nhÆ°ng cáº§n review thÃªm.
- Keyword Ä‘iá»ƒm cao nhÆ°ng bá»‹ loáº¡i khá»i Top 30 do overlap hoáº·c quota.

Sub-quota máº·c Ä‘á»‹nh cho 10 Consider:

| NhÃ³m | Quota gá»£i Ã½ | Ghi chÃº |
|---|---:|---|
| Platform-style / risky-but-relevant | 4 | VÃ­ dá»¥ iPhone / iOS / OS version |
| Secondary language | 3 | Chá»‰ Ã¡p dá»¥ng náº¿u market cÃ³ secondary language phÃ¹ há»£p |
| High-score missed opportunities | 3 | Keyword Ä‘iá»ƒm tá»‘t nhÆ°ng khÃ´ng vÃ o Top 30 |

Náº¿u má»™t nhÃ³m khÃ´ng Ä‘á»§ keyword, quota cÃ²n láº¡i cÃ³ thá»ƒ chuyá»ƒn cho nhÃ³m khÃ¡c. KhÃ´ng Ä‘Æ°á»£c nhÃ©t keyword yáº¿u chá»‰ Ä‘á»ƒ Ä‘á»§ sá»‘ lÆ°á»£ng.

VÃ­ dá»¥ vá»›i Control Widget US_EN:

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

YÃªu cáº§u output:

```text
File 01_Main_Keyword_Shortlist.csv pháº£i cÃ³ cá»™t Section:
- Core Intent Final
- Broad Expansion
- Consider Keywords
```

---

## 3. Pipeline 10 bÆ°á»›c

| BÆ°á»›c | TÃªn | Input | Output | Má»¥c Ä‘Ã­ch |
|---:|---|---|---|---|
| 1 | Data Ingestion | CSV thÃ´ | DataFrame chuáº©n hÃ³a | Äá»c file, chuáº©n hÃ³a cá»™t, Ã©p kiá»ƒu dá»¯ liá»‡u |
| 2 | Hard Filter | DataFrame B1 | Candidate + Dropped | Loáº¡i typo, brand Ä‘á»‘i thá»§, noise cá»©ng, sai category |
| 3 | Market Language Policy | DataFrame B2 | DataFrame + language fields | Kiá»ƒm tra keyword cÃ³ Ä‘Ãºng ngÃ´n ngá»¯ market khÃ´ng |
| 4 | Language Naturalness Filter | DataFrame B3 | DataFrame + NaturalnessFlag | PhÃ¡t hiá»‡n keyword khÃ´ng tá»± nhiÃªn, stuffing, phrase lá»—i |
| 5 | Relevancy Scoring | DataFrame B4 | DataFrame + RelevancyScore | TÃ­nh Ä‘iá»ƒm liÃªn quan vá»›i app |
| 6 | Balanced Score | DataFrame B5 | DataFrame + BalancedScore | Káº¿t há»£p Volume, Difficulty, KEI, Rank, Relevancy |
| 7 | Bucket Classification | DataFrame B6 | Keyword buckets | Chia Core / Broad / Consider / Reserve / Drop |
| 8 | Word Overlap & Diversity Filter | Buckets | Shortlist Ä‘a dáº¡ng | TrÃ¡nh Top keyword bá»‹ láº·p Ã½ quÃ¡ nhiá»u |
| 9 | Metadata Assignment | Shortlist | File output chÃ­nh | Gá»£i Ã½ keyword theo platform metadata |
| 10 | Export & Report | Output tables | CSV + Markdown | Xuáº¥t file, audit, bÃ¡o cÃ¡o lÃ½ do giá»¯/loáº¡i |

---

## 4. APP_CONFIG Universal

```python
APP_CONFIG = {
    # â”€â”€â”€ Identity â”€â”€â”€
    "app_id": "com.yourcompany.yourapp",
    "app_name": "Your App Name",
    "category": "Widget",
    "category_slug": "widget",
    "market": "US_EN",
    "platform_mode": "google_play",  # google_play | app_store

    # â”€â”€â”€ Market Language Policy â”€â”€â”€
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

    # â”€â”€â”€ Semantic Groups â”€â”€â”€
    "feature_terms": [],
    "style_terms": [],
    "visual_terms": [],
    "intent_core_terms": [],

    # â”€â”€â”€ Filters â”€â”€â”€
    "competitor_brands": [],
    "noise_terms": [],
    "typo_blacklist": [],
    "irrelevant_intent_terms": [],
    "risky_ip_terms": [],
    "truncation_policy": {
        "enabled": True,
        "min_prefix_length": 2,
        "allowed_partial_terms": [],
        "protect_complete_tokens": True,
        "ignore_inflection_prefix": True,
        "low_confidence_action": "manual_review",
        "dangling_action": "manual_review"
    },

    # â”€â”€â”€ Risk Handling â”€â”€â”€
    "risk_policy": {
        "competitor_brand_action": "drop",
        "risky_ip_action": "consider",
        "platform_style_action": "consider",
        "style_only_action": "reserve",
        "core_intent_override": True
    },

    # â”€â”€â”€ Rule Precedence â”€â”€â”€
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

    # â”€â”€â”€ Top Keyword Quotas â”€â”€â”€
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

    # â”€â”€â”€ Language Naturalness â”€â”€â”€
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

    # â”€â”€â”€ Relevancy Weights â”€â”€â”€
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

    # â”€â”€â”€ Balanced Score Weights â”€â”€â”€
    "balanced_weights": {
        "VolumeN": 0.20,
        "DifficultyN": 0.15,
        "KEIN": 0.15,
        "RelevancyScore": 0.30,
        "CurrentRankN": 0.10,
        "ExpansionValue": 0.10
    },

    # â”€â”€â”€ Scoring Normalization â”€â”€â”€
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

    # â”€â”€â”€ Metadata Slots by Platform â”€â”€â”€
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

    # â”€â”€â”€ Output Settings â”€â”€â”€
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

    # â”€â”€â”€ User Override Layer â”€â”€â”€
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

Pipeline pháº£i kiá»ƒm tra keyword theo ngÃ´n ngá»¯ cá»§a market. KhÃ´ng pháº£i keyword nÃ o cÃ³ Ä‘iá»ƒm cao cÅ©ng Ä‘Æ°á»£c Ä‘Æ°a vÃ o output chÃ­nh náº¿u sai ngÃ´n ngá»¯.

### 5.1 Quy táº¯c báº¯t buá»™c

Má»—i láº§n cháº¡y pipeline pháº£i cÃ³ `market_language_policy` rÃµ rÃ ng.

```text
Náº¿u market_language_policy.enabled = True nhÆ°ng thiáº¿u primary_languages,
pipeline pháº£i dá»«ng vÃ  yÃªu cáº§u bá»• sung, khÃ´ng Ä‘Æ°á»£c tá»± Ä‘oÃ¡n.
```

Má»—i market cáº§n Ä‘á»‹nh nghÄ©a:

- Primary language
- Secondary language(s), náº¿u cÃ³
- Optional secondary language(s), náº¿u cÃ³
- Foreign language handling rule

VÃ­ dá»¥ vá»›i US_EN:

```text
Primary language: English
Secondary language: Spanish / es-MX
Optional secondary: none
Foreign languages: drop hoáº·c audit
```

VÃ­ dá»¥ vá»›i BR_PT:

```text
Primary language: Portuguese / pt-BR
Secondary language: English
Optional secondary: Spanish / es-MX / es-ES
Foreign languages: drop hoáº·c audit
```

LÆ°u Ã½: `MX` lÃ  quá»‘c gia Mexico. Khi nÃ³i ngÃ´n ngá»¯ phá»¥ nÃªn ghi lÃ  `Spanish` hoáº·c `es-MX`.

### 5.2 Secondary language khÃ´ng pháº£i Language Bleed

ÄÃ¢y lÃ  rule quan trá»ng cá»§a v3.1.

```text
Foreign language bleed â‰  Secondary language.
```

Náº¿u Spanish Ä‘Æ°á»£c khai bÃ¡o lÃ  secondary language cá»§a US_EN, thÃ¬ keyword nhÆ° `centro de control` khÃ´ng Ä‘Æ°á»£c auto drop vá»›i lÃ½ do `LANGUAGE_BLEED`. NÃ³ pháº£i Ä‘Æ°á»£c xá»­ lÃ½ lÃ :

```text
LanguageGroup = SECONDARY
LanguageAction = CONSIDER hoáº·c AUDIT
```

Chá»‰ cÃ¡c ngÃ´n ngá»¯ náº±m ngoÃ i `primary_languages`, `secondary_languages`, vÃ  `optional_secondary_languages` má»›i Ä‘Æ°á»£c xem lÃ  foreign language mismatch.

### 5.3 CÃ¡ch xá»­ lÃ½ theo nhÃ³m ngÃ´n ngá»¯

| LanguageGroup | CÃ¡ch xá»­ lÃ½ |
|---|---|
| `PRIMARY` | ÄÆ°á»£c xÃ©t vÃ o Top 25 Core, 5 Broad, Feature Top 30, Style Top 30 |
| `SECONDARY` | KhÃ´ng auto drop, máº·c Ä‘á»‹nh Ä‘Æ°a vÃ o Consider hoáº·c Secondary Language Keywords. Náº¿u raw keyword khá»›p chÃ­nh xÃ¡c `intent_core_terms`, giá»¯ vai trÃ² Core. |
| `OPTIONAL_SECONDARY` | Chá»‰ giá»¯ náº¿u data tá»‘t, máº·c Ä‘á»‹nh Audit hoáº·c Consider |
| `FOREIGN` | Drop hoáº·c Ä‘Æ°a vÃ o Language Mismatch Audit |
| `MIXED` | Chá»‰ giá»¯ náº¿u tá»± nhiÃªn vá»›i search behavior cá»§a market |
| `UNKNOWN` | Manual Review náº¿u Ä‘iá»ƒm cao, drop náº¿u intent yáº¿u |

### 5.4 Output language fields

Má»—i file chÃ­nh nÃªn cÃ³ cÃ¡c cá»™t:

| Cá»™t | Ã nghÄ©a |
|---|---|
| `DetectedLanguage` | NgÃ´n ngá»¯ nháº­n diá»‡n Ä‘Æ°á»£c |
| `LanguageGroup` | PRIMARY / SECONDARY / OPTIONAL_SECONDARY / FOREIGN / MIXED / UNKNOWN |
| `LanguageAction` | KEEP / CONSIDER / DROP / AUDIT / MANUAL_REVIEW |
| `LanguageReason` | LÃ½ do xá»­ lÃ½ |

VÃ­ dá»¥:

| Keyword | LanguageGroup | Action | Reason |
|---|---|---|---|
| `control panel` | PRIMARY | KEEP | English keyword for US_EN |
| `centro de control` | SECONDARY | CONSIDER | Spanish keyword, possible US Hispanic search |
| `æŽ§åˆ¶ä¸­å¿ƒ` | FOREIGN | DROP | Chinese is not allowed for US_EN |
| `centro de control widget` | MIXED | CONSIDER | Mixed Spanish + English, needs review |

### 5.5 Market language map máº«u

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

Pipeline cÃ³ nhiá»u lá»›p rule. VÃ¬ váº­y cáº§n xÃ¡c Ä‘á»‹nh rÃµ rule nÃ o tháº¯ng rule nÃ o.

Thá»© tá»± Æ°u tiÃªn báº¯t buá»™c:

```text
1. Force Drop / Competitor Brand / Policy hard drop
2. Typo / high-confidence truncated / broken keyword
3. Foreign language mismatch
4. Clearly irrelevant intent
5. Core Intent Override
6. Risk Policy
7. Secondary / Optional Secondary language handling
8. Scoring + Bucket Classification
9. User Override Layer, trong pháº¡m vi Ä‘Æ°á»£c phÃ©p
```

### 6.1 Rule nÃ o khÃ´ng Ä‘Æ°á»£c override

User override cÃ³ thá»ƒ chuyá»ƒn keyword giá»¯a Top 30 / Consider / Reserve, nhÆ°ng khÃ´ng Ä‘Æ°á»£c override cÃ¡c nhÃ³m sau:

- Competitor brand rÃµ rÃ ng.
- Keyword broken / typo / truncated.
- Keyword sai intent rÃµ rÃ ng.
- Foreign language náº±m ngoÃ i market policy.
- Policy hard drop.

VÃ­ dá»¥:

| Keyword | User force_top30 cÃ³ Ä‘Æ°á»£c khÃ´ng? | LÃ½ do |
|---|---:|---|
| `control center themes` | CÃ³ | Intent sÃ¡t |
| `iphone control center` | KhÃ´ng nÃªn Top 30, nÃªn Consider | Platform-style risk |
| `mi control center` | KhÃ´ng | Competitor brand |
| `center widg` | KhÃ´ng | Broken/truncated high-confidence |
| `battery emoji` | CÃ³ | Complete token, khÃ´ng bá»‹ hiá»ƒu nháº§m lÃ  `emoji -> emojis` |
| `æŽ§åˆ¶ä¸­å¿ƒ` trong US_EN | KhÃ´ng | Foreign language mismatch |

### 6.2 Core Intent Override khÃ´ng cá»©u competitor brand

VÃ­ dá»¥:

```text
mi control center
```

Keyword nÃ y cÃ³ `control center`, nhÆ°ng `mi control center` lÃ  competitor/app-style brand. Káº¿t quáº£ pháº£i lÃ :

```text
Dropped = Competitor brand
```

KhÃ´ng Ä‘Æ°á»£c giá»¯ chá»‰ vÃ¬ cÃ³ core intent.

---

## 7. Hard Filter Rules

Hard filter chá»‰ dÃ¹ng cho nhá»¯ng trÆ°á»ng há»£p cháº¯c cháº¯n khÃ´ng nÃªn dÃ¹ng.

### 7.1 Auto Drop

Auto drop náº¿u keyword thuá»™c má»™t trong cÃ¡c nhÃ³m:

| NhÃ³m | VÃ­ dá»¥ |
|---|---|
| Competitor brand | `mi control center`, `power shade`, `one shade` |
| Typo/truncated | `control panl`, `center widg`, `widgit`; prefix thiáº¿u anchor vÃ o `possible_truncated_keyword`/Manual Review |
| Irrelevant category | `calculator app`, `weather widget`, `call widget` náº¿u khÃ´ng liÃªn quan |
| Foreign language mismatch | Keyword Trung / Viá»‡t / Bá»“ ÄÃ o Nha trong US_EN náº¿u khÃ´ng náº±m trong language policy |
| Noise only | `app`, `phone`, `screen`, `theme` náº¿u Ä‘á»©ng má»™t mÃ¬nh hoáº·c quÃ¡ rá»™ng |

### 7.2 KhÃ´ng auto drop

KhÃ´ng auto drop máº·c Ä‘á»‹nh náº¿u keyword thuá»™c cÃ¡c nhÃ³m:

| NhÃ³m | CÃ¡ch xá»­ lÃ½ |
|---|---|
| iPhone / iOS / OS-style | Consider náº¿u cÃ³ intent sÃ¡t |
| Secondary language phÃ¹ há»£p country | Consider |
| Optional secondary language cÃ³ data tá»‘t | Audit hoáº·c Consider |
| Style/theme cÃ³ liÃªn quan tá»›i core intent | Style file hoáº·c Full Description |
| Keyword dÃ i nhÆ°ng natural | Giá»¯ náº¿u cÃ³ core intent |

---

## 8. Core Intent Override

Náº¿u keyword chá»©a core intent máº¡nh, pipeline khÃ´ng Ä‘Æ°á»£c loáº¡i tá»± Ä‘á»™ng chá»‰ vÃ¬ cÃ³ term rá»§i ro nháº¹.

VÃ­ dá»¥ vá»›i Control Widget, core intent gá»“m:

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

CÃ¡ch xá»­ lÃ½:

| Keyword | KhÃ´ng nÃªn | NÃªn |
|---|---|---|
| `iphone control center` | Drop | Consider |
| `ios control center` | Drop | Consider |
| `control center themes` | Drop | Top 30 hoáº·c Style |
| `theme control center` | Drop | Style / Full Description |
| `mi control center` | Top 30 | Drop vÃ¬ competitor/app brand |

---

## 9. Relevancy Scoring

`RelevancyScore` Ä‘Ã¡nh giÃ¡ keyword cÃ³ sÃ¡t app hay khÃ´ng.

CÃ´ng thá»©c gá»£i Ã½:

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

### 9.1 VÃ­ dá»¥ Ä‘iá»ƒm cao

```text
control panel
control widget
custom control panel
notification panel
quick settings
volume control widget
```

### 9.2 VÃ­ dá»¥ Ä‘iá»ƒm trung bÃ¬nh

```text
widget themes
custom widget
color widgets
theme packs
cute widget
```

### 9.3 VÃ­ dá»¥ Ä‘iá»ƒm tháº¥p

```text
cute themes
beauty theme
simple theme
wallpaper themes
phone theme
```

---

## 10. Balanced Score & Scoring Normalization

`BalancedScore` dÃ¹ng Ä‘á»ƒ xáº¿p háº¡ng trong tá»«ng bucket, khÃ´ng dÃ¹ng Ä‘á»ƒ chá»n toÃ n bá»™ Top 30 má»™t cÃ¡ch mÃ¹ quÃ¡ng.

CÃ´ng thá»©c máº·c Ä‘á»‹nh:

```text
BalancedScore =
0.20 * VolumeN
+ 0.15 * DifficultyN
+ 0.15 * KEIN
+ 0.30 * RelevancyScore
+ 0.10 * CurrentRankN
+ 0.10 * ExpansionValue
```

### 10.1 CÃ´ng thá»©c normalize báº¯t buá»™c

Äá»ƒ pipeline cháº¡y á»•n Ä‘á»‹nh giá»¯a nhiá»u market, cÃ¡c biáº¿n pháº£i Ä‘Æ°á»£c normalize rÃµ rÃ ng.

#### VolumeN

`Volume` tá»« AppTweak lÃ  Search Popularity theo thang phi tuyáº¿n `5â€“100`, khÃ´ng pháº£i sá»‘ lÆ°á»£t tÃ¬m kiáº¿m tuyá»‡t Ä‘á»‘i. Pipeline Æ°u tiÃªn `MaximumReach` náº¿u CSV cÃ³ cá»™t nÃ y. Náº¿u CSV khÃ´ng cÃ³ `MaximumReach`, pipeline dÃ¹ng proxy exponential trÃªn thang Search Popularity tuyá»‡t Ä‘á»‘i:

```text
CurrentVolumeN = exp_curve(Volume, floor=5, ceiling=100)
HistoricalVolumeN = exp_curve(Max. Volume, floor=5, ceiling=100)
VolumeN = 0.85 * CurrentVolumeN + 0.15 * HistoricalVolumeN
```

Náº¿u `Volume <= 5`, `VolumeN` bá»‹ giá»›i háº¡n tá»‘i Ä‘a á»Ÿ `0.05`. Keyword tier tháº¥p váº«n cÃ²n trong pool nghiÃªn cá»©u, nhÆ°ng máº·c Ä‘á»‹nh khÃ´ng tá»± Ä‘á»™ng Ä‘i vÃ o Core/Broad metadata shortlist. Danh sÃ¡ch Consider chá»‰ giá»¯ tá»‘i Ä‘a `3` keyword tier tháº¥p Ä‘á»ƒ review.

#### DifficultyN

Difficulty cÃ ng tháº¥p cÃ ng tá»‘t:

```text
DifficultyN = 1 - (Difficulty / 100)
```

Náº¿u Difficulty ngoÃ i khoáº£ng 0-100, clamp vá» 0-100 trÆ°á»›c khi tÃ­nh.

#### KEIN

KEI cÅ©ng dÃ¹ng log scale:

```text
KEIN = log(KEI + 1) / log(MaxKEI + 1)
```

Náº¿u khÃ´ng cÃ³ KEI hoáº·c MaxKEI = 0:

```text
KEIN = 0
```

#### CurrentRankN

Rank cÃ ng cao thÃ¬ Ä‘iá»ƒm cÃ ng tá»‘t. Unranked khÃ´ng Ä‘Æ°á»£c cá»™ng Ä‘iá»ƒm rank.

| CurrentRank | CurrentRankN |
|---:|---:|
| 1-10 | 1.00 |
| 11-30 | 0.80 |
| 31-50 | 0.60 |
| 51-100 | 0.30 |
| >100 | 0.10 |
| Unranked / empty | 0.00 |

#### ExpansionValue

ExpansionValue Ä‘Ã¡nh giÃ¡ keyword cÃ³ Ä‘Ã¡ng má»Ÿ rá»™ng khÃ´ng.

Gá»£i Ã½ tÃ­nh:

```text
ExpansionValue =
0.45 * RelevancyScore
+ 0.25 * VolumeN
+ 0.20 * OpportunityRankGap
+ 0.10 * CompetitorCoverageN
```

Trong Ä‘Ã³:

| ThÃ nh pháº§n | Ã nghÄ©a |
|---|---|
| `OpportunityRankGap` | Cao náº¿u app rank yáº¿u/unranked nhÆ°ng keyword váº«n sÃ¡t intent |
| `CompetitorCoverageN` | Cao náº¿u nhiá»u competitor rank cho keyword Ä‘Ã³ |

Náº¿u khÃ´ng cÃ³ dá»¯ liá»‡u competitor:

```text
CompetitorCoverageN = 0
```

Náº¿u khÃ´ng cÃ³ rank:

```text
OpportunityRankGap = 1.0 náº¿u keyword liÃªn quan cao vÃ  app unranked
OpportunityRankGap = 0.0 náº¿u keyword khÃ´ng liÃªn quan
```

---

## 11. Bucket Classification

Sau scoring, keyword Ä‘Æ°á»£c phÃ¢n loáº¡i vÃ o cÃ¡c bucket sau:

| Bucket | Ã nghÄ©a |
|---|---|
| `Core Intent Final` | Keyword sÃ¡t app nháº¥t, Æ°u tiÃªn Top 25 |
| `Broad Expansion` | Keyword rá»™ng hÆ¡n nhÆ°ng váº«n há»¯u Ã­ch, chá»n 5 |
| `Consider Keywords` | Keyword tiá»m nÄƒng, cáº§n review, chá»n 10 |
| `Feature Keywords` | Keyword tÃ­nh nÄƒng/type, xuáº¥t file 30 |
| `Style Keywords` | Keyword style/theme, xuáº¥t file 30 |
| `Generic Style Reserve` | Style quÃ¡ rá»™ng, khÃ´ng vÃ o output chÃ­nh |
| `Language Mismatch Audit` | Sai ngÃ´n ngá»¯ market |
| `Dropped` | Loáº¡i vÃ¬ sai intent, typo, brand, noise |

---

## 12. Quota Fallback Policy

KhÃ´ng Ä‘Æ°á»£c nhÃ©t keyword yáº¿u chá»‰ Ä‘á»ƒ Ä‘á»§ quota.

Náº¿u má»™t section khÃ´ng Ä‘á»§ keyword qualified:

```text
1. Fill tá»« bucket Ä‘á»§ Ä‘iá»u kiá»‡n gáº§n nháº¥t.
2. Chá»‰ fill náº¿u keyword Ä‘áº¡t min_relevancy_for_fill.
3. Ghi rÃµ FillReason.
4. Náº¿u váº«n thiáº¿u, output Ã­t hÆ¡n quota vÃ  report rÃµ lÃ½ do.
```

VÃ­ dá»¥:

```text
Core Intent chá»‰ cÃ³ 18 keyword tá»‘t.
â†’ Fill thÃªm 7 keyword tá»« Feature Expansion náº¿u Ä‘á»§ Ä‘iá»ƒm.
â†’ Náº¿u váº«n thiáº¿u, output 22 keyword thay vÃ¬ nhÃ©t keyword rÃ¡c Ä‘á»ƒ Ä‘á»§ 25.
```

Cá»™t cáº§n cÃ³ khi fallback:

| Cá»™t | Ã nghÄ©a |
|---|---|
| `FillSource` | Bucket gá»‘c cá»§a keyword Ä‘Æ°á»£c dÃ¹ng Ä‘á»ƒ fill |
| `FillReason` | LÃ½ do Ä‘Æ°á»£c dÃ¹ng Ä‘á»ƒ bÃ¹ quota |
| `QuotaStatus` | EXACT / FILLED / UNDER_QUOTA |

---

## 13. Word Overlap Filter

Pipeline cáº§n giáº£m trÃ¹ng láº·p giá»¯a cÃ¡c keyword trong file chÃ­nh.

Máº·c Ä‘á»‹nh:

```python
max_word_overlap = 0.5
```

Ãp dá»¥ng trong tá»«ng section trÆ°á»›c:

- Core Intent Final
- Broad Expansion
- Consider Keywords
- Feature Keywords
- Style Keywords

KhÃ´ng nÃªn so sÃ¡nh quÃ¡ gáº¯t giá»¯a Core vÃ  Consider, vÃ¬ Consider cÃ³ thá»ƒ cá»‘ Ã½ chá»©a variant Ä‘á»ƒ review.

Tuy nhiÃªn cÃ³ ngoáº¡i lá»‡ cho core terms. Vá»›i app Control Widget, cÃ¡c tá»« nhÆ° `control`, `panel`, `widget`, `quick`, `settings` cÃ³ thá»ƒ láº·p vÃ¬ Ä‘Ã¢y lÃ  core cá»§a category.

YÃªu cáº§u:

```text
KhÃ´ng loáº¡i keyword core chá»‰ vÃ¬ láº·p tá»« báº¯t buá»™c.
Chá»‰ loáº¡i náº¿u keyword gáº§n nhÆ° trÃ¹ng Ã½ vÃ  khÃ´ng thÃªm search intent má»›i.
```

VÃ­ dá»¥:

| Keyword A | Keyword B | CÃ¡ch xá»­ lÃ½ |
|---|---|---|
| `control panel` | `custom control panel` | CÃ³ thá»ƒ giá»¯ cáº£ hai |
| `quick settings` | `custom quick settings` | CÃ³ thá»ƒ giá»¯ cáº£ hai |
| `cute themes` | `beauty theme` | Chá»‰ giá»¯ náº¿u cáº§n broad/style quota |
| `theme iphone` | `themes iphone` | Chá»‰ giá»¯ má»™t náº¿u khÃ´ng cÃ³ lÃ½ do test cáº£ hai |

---

## 14. Metadata Assignment by Platform

KhÃ´ng pháº£i keyword Ä‘iá»ƒm cao nÃ o cÅ©ng nÃªn vÃ o slot quan trá»ng. NgoÃ i ra Google Play vÃ  App Store cÃ³ slot khÃ¡c nhau, nÃªn pipeline pháº£i cÃ³ `platform_mode`.

### 14.1 Google Play mode

```python
"platform_mode": "google_play"
```

| Slot | NÃªn dÃ¹ng | KhÃ´ng nÃªn dÃ¹ng |
|---|---|---|
| Title | Core intent an toÃ n | Brand Ä‘á»‘i thá»§, platform-risk, style-only |
| Short Description | Core + feature + benefit | Keyword rá»§i ro cao, secondary language |
| Full Description | Long-tail, style, theme, broad, consider | Brand Ä‘á»‘i thá»§ |
| Consider | iOS/iPhone/platform-style, secondary language | Keyword sai intent rÃµ rÃ ng |

### 14.2 App Store mode

```python
"platform_mode": "app_store"
```

| Slot | NÃªn dÃ¹ng | KhÃ´ng nÃªn dÃ¹ng |
|---|---|---|
| Title | Core intent an toÃ n | Competitor brand, risky platform-style |
| Subtitle | Core + feature rÃµ | Keyword quÃ¡ rá»™ng |
| Keyword Field | High-value exact terms, variants | Duplicates, competitor brand |
| Promotional Text | Supporting phrases, broader benefit | Keyword stuffing |
| Consider | Secondary language, risky-but-relevant | Foreign language mismatch |

### 14.3 VÃ­ dá»¥ vá»›i Control Widget Google Play

| Slot | Keyword phÃ¹ há»£p |
|---|---|
| Title | `control panel`, `control widget` |
| Short Description | `custom control panel`, `quick settings`, `notification panel`, `volume control widget` |
| Full Description | `control center themes`, `widget themes`, `custom themes`, `theme control center` |
| Consider | `iphone control center`, `ios control center`, `theme iphone` |

---

## 15. Feature / Type file

Sheet `02_Feature_Keywords` chá»‰ xuáº¥t tá»‘i Ä‘a 30 keyword. KhÃ´ng Ä‘Æ°á»£c dump toÃ n bá»™ candidate.

Quota Ä‘á» xuáº¥t:

```text
02_Feature_Keywords.csv
= 30 keyword curated

- 20 core feature keywords
- 5 feature expansion keywords
- 5 feature test keywords
```

Äiá»u kiá»‡n:

- Pháº£i mÃ´ táº£ chá»©c nÄƒng/type/utility/search intent.
- KhÃ´ng chá»©a style-only keyword.
- Æ¯u tiÃªn primary language.
- Secondary language chá»‰ xuáº¥t náº¿u config cho phÃ©p.
- Náº¿u khÃ´ng Ä‘á»§ 30 keyword cháº¥t lÆ°á»£ng, output Ã­t hÆ¡n vÃ  ghi `UNDER_QUOTA`.

VÃ­ dá»¥ vá»›i Control Widget:

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

Sheet `03_Style_Keywords` chá»‰ xuáº¥t tá»‘i Ä‘a 30 keyword. KhÃ´ng Ä‘Æ°á»£c dump toÃ n bá»™ keyword style.

Quota Ä‘á» xuáº¥t:

```text
03_Style_Keywords.csv
= 30 keyword curated

- 15 style keywords gáº¯n vá»›i core intent
- 10 broad style keywords váº«n liÃªn quan
- 5 platform-style consider keywords
```

Æ¯u tiÃªn:

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

Háº¡n cháº¿:

```text
beauty theme
simple theme
stunning themes
diy theme pack
themes wallpaper
```

Náº¿u khÃ´ng Ä‘á»§ 30 keyword style cháº¥t lÆ°á»£ng, output Ã­t hÆ¡n vÃ  ghi rÃµ trong report.

---

## 17. User Override Layer

Sau má»—i láº§n user review, pipeline cáº§n lÆ°u láº¡i cÃ¡c rule override cho app/category/market.

Override Ä‘Æ°á»£c phÃ©p:

- Chuyá»ƒn keyword tá»« Reserve sang Consider.
- Chuyá»ƒn keyword tá»« Consider sang Top 30 náº¿u khÃ´ng vi pháº¡m hard filter.
- Giá»¯ keyword iPhone/iOS/OS-style Ä‘á»ƒ review.
- Háº¡ generic style-only khá»i Core Top 25.

Override khÃ´ng Ä‘Æ°á»£c phÃ©p:

- Cá»©u competitor brand.
- Cá»©u keyword typo/truncated.
- Cá»©u keyword sai intent rÃµ rÃ ng.
- Cá»©u keyword foreign language ngoÃ i market policy vÃ o output chÃ­nh.

VÃ­ dá»¥ vá»›i Control Widget:

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

## 18. Control Widget APP_CONFIG máº«u

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

    "truncation_policy": {
        "enabled": True,
        "min_prefix_length": 2,
        "allowed_partial_terms": [],
        "protect_complete_tokens": True,
        "ignore_inflection_prefix": True,
        "low_confidence_action": "manual_review",
        "dangling_action": "manual_review"
    },

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

## 19. Prompt cháº¡y pipeline

```markdown
Cháº¡y ASO Keyword Planner cho app cá»§a tÃ´i.

**App:** [TÃªn app]  
**App ID:** [Bundle ID]  
**Category:** [Category]  
**Market:** [Market code]  
**Platform:** [google_play hoáº·c app_store]  
**File CSV:** [Ä‘Ã­nh kÃ¨m file CSV]

---

## APP_CONFIG

```python
[PASTE APP_CONFIG Ä‘Ã£ tÃ¹y chá»‰nh á»Ÿ Ä‘Ã¢y]
```

---

## YÃŠU Cáº¦U

1. Äá»c file CSV Ä‘Ã­nh kÃ¨m.
2. Cháº¡y Ä‘á»§ 10 bÆ°á»›c cá»§a ASO Keyword Planner.
3. Xuáº¥t **01 file Excel tá»•ng**:

   ```text
   ASO_Keyword_Planner_[AppName]_[Market].xlsx
   ```

4. Workbook Excel pháº£i gá»“m cÃ¡c sheet báº¯t buá»™c:
   - `00_README_CONFIG`
   - `01_Main_Keyword_Shortlist`
   - `02_Feature_Keywords`
   - `03_Style_Keywords`
   - `04_Dropped_Audit`
   - `05_Report_Summary`
   - `06_All_Candidates`

5. Workbook cÃ³ thá»ƒ gá»“m cÃ¡c sheet phá»¥ náº¿u cÃ³ dá»¯ liá»‡u:
   - `07_Language_Mismatch`
   - `08_Generic_Style_Reserve`
   - `09_Manual_Review`
   - `10_Top_By_Score`
   - `11_Secondary_Language`

6. Sheet `01_Main_Keyword_Shortlist` pháº£i gá»“m:
   - 25 Core / High Intent Keywords
   - 5 Broad Expansion Keywords
   - 10 Consider Keywords xáº¿p cuá»‘i sheet

7. Sheet `02_Feature_Keywords` chá»‰ xuáº¥t tá»‘i Ä‘a 30 keyword curated.
8. Sheet `03_Style_Keywords` chá»‰ xuáº¥t tá»‘i Ä‘a 30 keyword curated.
9. KhÃ´ng Ä‘Æ°a keyword sai ngÃ´n ngá»¯ market vÃ o output chÃ­nh.
10. Secondary language keyword khÃ´ng pháº£i Language Bleed; chá»‰ Ä‘Æ°a vÃ o Consider náº¿u phÃ¹ há»£p vá»›i country.
11. KhÃ´ng auto drop iPhone / iOS / OS-style keyword náº¿u cÃ³ core intent sÃ¡t.
12. Generic style-only keyword khÃ´ng Ä‘Æ°á»£c chiáº¿m slot Core Top 25.
13. Competitor brand pháº£i bá»‹ loáº¡i khá»i metadata.
14. Ãp dá»¥ng rule precedence trÆ°á»›c user overrides.
15. DÃ¹ng scoring normalization theo Ä‘á»‹nh nghÄ©a trong pipeline.
16. Náº¿u khÃ´ng Ä‘á»§ quota, khÃ´ng nhÃ©t keyword yáº¿u. Ghi rÃµ `UNDER_QUOTA` hoáº·c `FillReason`.
17. Sheet `05_Report_Summary` pháº£i giáº£i thÃ­ch lÃ½ do giá»¯ / loáº¡i / Ä‘Æ°a vÃ o Consider.
18. KhÃ´ng xuáº¥t nhiá»u file CSV/MD/JSON rá»i, trá»« khi user yÃªu cáº§u thÃªm `export_csv_package = True`.

## PREVIEW TRONG CHAT

Hiá»ƒn thá»‹ Top 10 keyword tá»‘t nháº¥t theo báº£ng:

| Section | Keyword | Volume | Difficulty | KEI | Rank | BalancedScore | Reason |
```

## 20. BÃ¡o cÃ¡o báº¯t buá»™c

BÃ¡o cÃ¡o khÃ´ng xuáº¥t thÃ nh file Markdown riÃªng máº·c Ä‘á»‹nh. Ná»™i dung bÃ¡o cÃ¡o pháº£i náº±m trong sheet:

```text
05_Report_Summary
```

Sheet nÃ y nÃªn chia thÃ nh cÃ¡c block rÃµ rÃ ng Ä‘á»ƒ user má»Ÿ Excel lÃ  review Ä‘Æ°á»£c ngay.

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
Typo/high-confidence truncated drops:
Possible truncated manual review:
Foreign language mismatch:
Core intent override applied:
Risk policy consider:
User override applied:
User override rejected:
```

### 20.5 Top Decisions

Báº£ng trong sheet `05_Report_Summary`:

| Keyword | Section | Reason |
|---|---|---|
| `control panel` | Core Intent Final | Strong core intent |
| `iphone control center` | Consider | Strong intent but platform-style risk |
| `cute themes` | Generic Style Reserve | Style-only, weak app intent |
| `mi control center` | Dropped | Competitor brand |

### 20.6 Missed Opportunity Review

Danh sÃ¡ch keyword Ä‘iá»ƒm cao nhÆ°ng khÃ´ng vÃ o Top 30 chÃ­nh:

| Keyword | Score | VÃ¬ sao khÃ´ng vÃ o Top 30 |
|---|---:|---|
| `theme iphone` | 0.xx | Platform-style, moved to Consider |
| `cute themes` | 0.xx | Generic style-only |
| `centro de control` | 0.xx | Secondary language for US_EN |

### 20.7 Quota Fallback Review

Náº¿u section nÃ o thiáº¿u quota, report pháº£i nÃ³i rÃµ:

| Section | Expected | Actual | QuotaStatus | Reason |
|---|---:|---:|---|---|
| Core Intent Final | 25 | 22 | UNDER_QUOTA | Not enough qualified core keywords |
| Broad Expansion | 5 | 5 | EXACT | â€” |
| Consider Keywords | 10 | 10 | FILLED | 2 items filled from missed opportunities |

### 20.8 Workbook Sheet Index

Sheet `05_Report_Summary` nÃªn cÃ³ thÃªm block `Workbook Sheet Index` Ä‘á»ƒ user biáº¿t tá»«ng sheet dÃ¹ng lÃ m gÃ¬.

| Sheet | Purpose | Row Count |
|---|---|---:|
| `01_Main_Keyword_Shortlist` | Top 30 + 10 Consider | 40 |
| `02_Feature_Keywords` | Feature/type keywords | <=30 |
| `03_Style_Keywords` | Style/theme keywords | <=30 |
| `04_Dropped_Audit` | Dropped keywords and reasons | n |
| `06_All_Candidates` | Full scored candidate pool | n |

## 21. Troubleshooting

### Váº¥n Ä‘á»: Top 30 cÃ³ quÃ¡ nhiá»u keyword style chung

CÃ¡ch sá»­a:

```text
- TÄƒng penalty cho style-only keyword.
- Báº­t style_only_action = reserve.
- Giá»¯ quota 25 core + 5 broad.
- Chá»‰ cho style keyword vÃ o Top 30 náº¿u cÃ³ core intent.
```

### Váº¥n Ä‘á»: Keyword iOS / iPhone bá»‹ loáº¡i háº¿t

CÃ¡ch sá»­a:

```text
- KhÃ´ng Ä‘Æ°a iOS / iPhone vÃ o hard drop.
- ThÃªm vÃ o do_not_auto_drop_terms.
- ThÃªm force_consider_terms cho cÃ¡c keyword cÃ³ intent sÃ¡t.
```

### Váº¥n Ä‘á»: Keyword secondary language bá»‹ flag nháº§m lÃ  LANGUAGE_BLEED

CÃ¡ch sá»­a:

```text
- Kiá»ƒm tra market_language_policy.secondary_languages.
- KhÃ´ng Ä‘Æ°a tá»« thuá»™c secondary language vÃ o forbidden_foreign_in_market.
- LANGUAGE_BLEED chá»‰ dÃ¹ng cho foreign language ngoÃ i policy.
```

### Váº¥n Ä‘á»: Keyword ngÃ´n ngá»¯ khÃ¡c lá»t vÃ o output chÃ­nh

CÃ¡ch sá»­a:

```text
- Báº­t market_language_policy.
- Äá»‹nh nghÄ©a primary_languages rÃµ rÃ ng.
- Äá»‹nh nghÄ©a secondary_languages vÃ  optional_secondary_languages náº¿u cáº§n.
- ÄÆ°a foreign language vÃ o Language Mismatch Audit.
```

### Váº¥n Ä‘á»: Sheet Feature / Style quÃ¡ dÃ i

CÃ¡ch sá»­a:

```text
- Báº­t keyword_quota.feature_file.max_keywords = 30.
- Báº­t keyword_quota.style_file.max_keywords = 30.
- Chá»‰ Ä‘Æ°a curated shortlist vÃ o cÃ¡c sheet chÃ­nh.
- Candidate pool Ä‘áº§y Ä‘á»§ chá»‰ xuáº¥t á»Ÿ All_Candidates.csv hoáº·c Audit.
```

### Váº¥n Ä‘á»: Keyword core bá»‹ loáº¡i vÃ¬ word overlap

CÃ¡ch sá»­a:

```text
- ThÃªm core terms vÃ o overlap exception.
- KhÃ´ng loáº¡i keyword náº¿u nÃ³ thÃªm intent má»›i.
- Cho phÃ©p láº·p cÃ¡c tá»« báº¯t buá»™c cá»§a category nhÆ° control, panel, widget, quick, settings.
```

### Váº¥n Ä‘á»: KhÃ´ng Ä‘á»§ quota 25/5/10

CÃ¡ch sá»­a:

```text
- KhÃ´ng Ã©p Ä‘á»§ quota báº±ng keyword yáº¿u.
- Báº­t fallback_policy.allow_under_quota.
- Fill tá»« next best eligible bucket náº¿u Ä‘á»§ min_relevancy_for_fill.
- Ghi rÃµ FillReason vÃ  QuotaStatus trong report.
```

---

## 22. Quy táº¯c ngáº¯n gá»n Ä‘á»ƒ nhá»›

```text
1. Top 30 = 25 sÃ¡t intent + 5 má»Ÿ rá»™ng cÃ³ kiá»ƒm soÃ¡t.
2. ThÃªm 10 Consider á»Ÿ cuá»‘i sheet chÃ­nh.
3. Consider cÃ³ sub-quota: platform-style, secondary language, missed opportunities.
4. Feature sheet chá»‰ láº¥y tá»‘i Ä‘a 30 keyword curated.
5. Style sheet chá»‰ láº¥y tá»‘i Ä‘a 30 keyword curated.
6. Má»—i market báº¯t buá»™c cÃ³ primary / secondary / optional secondary language policy.
7. Secondary language khÃ´ng pháº£i Language Bleed.
8. Keyword sai ngÃ´n ngá»¯ market khÃ´ng vÃ o output chÃ­nh.
9. iPhone / iOS / OS-style khÃ´ng auto drop náº¿u cÃ³ intent sÃ¡t.
10. Generic style-only khÃ´ng chiáº¿m slot core.
11. Competitor brand pháº£i drop, Core Intent Override khÃ´ng Ä‘Æ°á»£c cá»©u competitor brand.
12. BalancedScore pháº£i normalize rÃµ rÃ ng.
13. Náº¿u khÃ´ng Ä‘á»§ quota, output thiáº¿u cÃ²n hÆ¡n nhÃ©t keyword yáº¿u.
14. Metadata assignment pháº£i theo platform_mode: google_play hoáº·c app_store.
15. Report pháº£i nÃ³i rÃµ vÃ¬ sao giá»¯, loáº¡i, Ä‘Æ°a vÃ o Consider hoáº·c fill quota.
```

---

## 23. Ná»™i dung Ä‘Ã£ bá»• sung á»Ÿ v3.2

### P0 â€” Bá»• sung báº¯t buá»™c

- Sá»­a mÃ¢u thuáº«n Language Policy: secondary language khÃ´ng pháº£i `LANGUAGE_BLEED`.
- ThÃªm `optional_secondary_languages`.
- ThÃªm Rule Precedence: rule nÃ o tháº¯ng rule nÃ o.
- Giá»›i háº¡n quyá»n cá»§a User Override Layer.


### P2 â€” Thay Ä‘á»•i output máº·c Ä‘á»‹nh

- Chuyá»ƒn output máº·c Ä‘á»‹nh tá»« nhiá»u file CSV/MD/JSON sang **01 Excel workbook tá»•ng**.
- Má»—i output cÅ© trá»Ÿ thÃ nh má»™t sheet trong workbook.
- ThÃªm `output_mode = "excel_workbook"` vÃ  block `output_workbook`.
- ThÃªm sheet `00_README_CONFIG` Ä‘á»ƒ lÆ°u config, app info vÃ  run summary.
- ThÃªm sheet `05_Report_Summary` thay cho file `05_ASO_Report.md`.
- Giá»¯ CSV/Markdown lÃ  export phá»¥, chá»‰ báº­t khi user yÃªu cáº§u.

### P1 â€” Bá»• sung quan trá»ng

- Äá»‹nh nghÄ©a rÃµ cÃ´ng thá»©c normalize cho Volume, Difficulty, KEI, Rank, ExpansionValue.
- ThÃªm Quota Fallback Policy khi khÃ´ng Ä‘á»§ 25/5/10 hoáº·c 30 Feature/Style.
- ThÃªm sub-quota cho 10 Consider Keywords.
- ThÃªm `platform_mode` vÃ  metadata slot riÃªng cho Google Play / App Store.

---

*ASO Keyword Planner v4.2*
*Updated for the shared hard-filter platform, compiled matcher runtime, indexed multilingual dedup, reliable translation/profile services, exact app registry, scoped cache and concurrent batch execution.*


---

## 24. Cáº­p nháº­t v3.3 â€” Global Text-Level Dedup

### 24.1 LÃ½ do bá»• sung

Trong v3.2, bÆ°á»›c `Word Overlap & Diversity Filter` Ä‘Ã£ cÃ³ nhÆ°ng chÆ°a Ä‘á»§ cháº·t á»Ÿ cáº¥p báº£ng cuá»‘i. Má»™t sá»‘ keyword gáº§n giá»‘ng vá» bá» máº·t chá»¯ váº«n cÃ³ thá»ƒ lá»t vÃ o cÃ¹ng output do quota fill, vÃ­ dá»¥:

```text
emulador de gba retrÃ´
emulador de jogos de gba
emulador de gba
emulador gba
```

Tá»« v3.3, pipeline pháº£i cÃ³ má»™t bÆ°á»›c riÃªng:

```text
Final Text-Level Near-Duplicate Cleanup
```

BÆ°á»›c nÃ y cháº¡y sau scoring/bucket classification nhÆ°ng trÆ°á»›c khi xuáº¥t tá»«ng sheet curated.

### 24.2 Pháº¡m vi Ã¡p dá»¥ng

Tá»« v4.0, dedup chá»‰ Ã¡p dá»¥ng cho:

```text
01_Main_Keyword_Shortlist
```

CÃ¡c sheet tÃ­nh nÄƒng, style, system, game vÃ  chá»§ Ä‘á» Ã¢m thanh khÃ´ng lá»c trÃ¹ng. CÃ¡c sheet nÃ y xáº¿p háº¡ng keyword theo score/rank/KEI/difficulty nhÆ° bÃ¬nh thÆ°á»ng Ä‘á»ƒ giá»¯ Ä‘áº§y Ä‘á»§ dá»¯ liá»‡u Ä‘Ã¡nh giÃ¡.

CÃ¡c sheet audit/raw sau váº«n giá»¯ dá»¯ liá»‡u Ä‘áº§y Ä‘á»§ Ä‘á»ƒ truy váº¿t:

```text
04_Dropped_Audit
06_All_Candidates
09_Manual_Review
10_Top_By_Score
11_Secondary_Language
```

Náº¿u cÃ³ keyword bá»‹ merge khá»i main shortlist vÃ¬ tÆ°Æ¡ng Ä‘Æ°Æ¡ng cháº¯c cháº¯n, keyword Ä‘Ã³ khÃ´ng bá»‹ xÃ³a khá»i `06_All_Candidates`.

### 24.3 Quy táº¯c text-level dedup

Dedup nÃ y khÃ´ng pháº£i semantic clustering quÃ¡ rá»™ng. Chá»‰ loáº¡i keyword khi bá» máº·t chá»¯ quÃ¡ gáº§n nhau.

Pháº¡m vi dedup lÃ  **ná»™i bá»™ `01_Main_Keyword_Shortlist`**. Má»™t keyword máº¡nh Ä‘Æ°á»£c phÃ©p xuáº¥t hiá»‡n Ä‘á»“ng thá»i trong main shortlist vÃ  má»™t sheet chá»§ Ä‘á» nhÆ° `05_Prank_Sound_General`. CÃ¡c sheet chá»§ Ä‘á» lÃ  cÃ¡c gÃ³c nhÃ¬n Ä‘á»™c láº­p Ä‘á»ƒ ngÆ°á»i dÃ¹ng lá»c tá»« trÃªn xuá»‘ng dÆ°á»›i theo tá»«ng nhÃ³m intent.

Chuáº©n hÃ³a trÆ°á»›c khi so sÃ¡nh:

```text
- Unicode NFKC
- Unicode casefold()
- Preserve combining marks cho Hindi, Arabic, Thai vÃ  cÃ¡c há»‡ chá»¯ tÆ°Æ¡ng tá»±
- Normalize spacing/punctuation
- Snowball stemming theo locale khi tokenizer Unicode Ä‘Ã¡ng tin cáº­y
- KhÃ´ng Ã¡p dá»¥ng suffix rule toÃ n cá»¥c
```

Tá»± Ä‘á»™ng loáº¡i náº¿u:

```text
1. Exact NFKC + casefold duplicate
2. Same stemmed sequence theo locale
3. Same stemmed token set theo locale
```

Accent-fold, token overlap cao hoáº·c cÃ¡c biáº¿n thá»ƒ chá»‰ gáº§n giá»‘ng khÃ´ng táº¡o `ReviewVariants` vÃ  khÃ´ng bá»‹ loáº¡i máº·c Ä‘á»‹nh. VÃ­ dá»¥ `retrÃ´` vÃ  `retro` Ä‘Æ°á»£c giá»¯ nhÆ° hai keyword Ä‘á»™c láº­p, trá»« khi locale chá»§ Ä‘á»™ng opt-in accent-fold auto-merge.

VÃ­ dá»¥ pháº£i loáº¡i bá»›t:

| Keyword A | Keyword B | LÃ½ do |
|---|---|---|
| `AR FILTER` | `ar-filter` | Exact NFKC + casefold duplicate |
| `filters app` | `filter app` | Same stemmed sequence tiáº¿ng Anh |
| `retro gba games` | `games gba retro` | Same stemmed token set |

VÃ­ dá»¥ khÃ´ng Ä‘Æ°á»£c loáº¡i:

| Keyword A | Keyword B | LÃ½ do giá»¯ |
|---|---|---|
| `gba emulador` | `gba jogos retrÃ´` | KhÃ¡c search intent: emulator query vs game query |
| `emulador arcade` | `jogos de arcade retrÃ´` | KhÃ¡c intent: emulator vs game catalog |
| `gameboy emulador` | `gameboy retro games` | KhÃ¡c intent: emulator vs game discovery |

### 24.4 Dedup log báº¯t buá»™c

Workbook nÃªn cÃ³ sheet:

```text
12_Text_Dedup_Log
```

Cá»™t báº¯t buá»™c:

| Column | Purpose |
|---|---|
| `Table` | Sheet bá»‹ lá»c trÃ¹ng |
| `Action` | `PRUNED` |
| `ClusterId` | ID cluster |
| `DedupRule` | Rule táº¡o cluster |
| `Confidence` | Äá»™ tin cáº­y rule |
| `RemovedKeyword` | Keyword bá»‹ bá» khá»i curated table |
| `RemovedVolume` | Volume hiá»‡n táº¡i cá»§a keyword bá»‹ merge khá»i main shortlist |
| `OriginalSection` | Section/bucket ban Ä‘áº§u |
| `KeptKeyword` | Keyword Ä‘Æ°á»£c giá»¯ lÃ m Ä‘áº¡i diá»‡n |
| `KeptVolume` | Volume hiá»‡n táº¡i cá»§a keyword Ä‘Æ°á»£c giá»¯ |
| `NormalizedKey` | Key Unicode hoáº·c token key dÃ¹ng Ä‘á»ƒ so sÃ¡nh |
| `BalancedScore` | Äiá»ƒm keyword bá»‹ loáº¡i |
| `Note` | Ghi chÃº ráº±ng keyword váº«n cÃ²n trong All Candidates |

### 24.5 Quota sau dedup

Quy táº¯c quota khÃ¡c nhau theo sheet:

#### Sheet 01 â€” Main Keyword Shortlist

```text
01_Main_Keyword_Shortlist pháº£i Ä‘á»§ quota:
25 Core / High Intent
+ 5 Broad Expansion
+ 10 Consider Keywords
= 40 rows
```

Náº¿u dedup lÃ m thiáº¿u keyword:

```text
1. Láº¥y keyword tiáº¿p theo trong bucket Ä‘á»§ Ä‘iá»u kiá»‡n.
2. Váº«n pháº£i cháº¡y text-level dedup vá»›i toÃ n sheet.
3. KhÃ´ng láº¥y keyword hard-drop, sai ngÃ´n ngá»¯, competitor brand, typo/broken.
4. Ghi FillReason náº¿u keyword Ä‘Æ°á»£c dÃ¹ng Ä‘á»ƒ bÃ¹ quota.
```

NÃ³i cÃ¡ch khÃ¡c:

```text
01 cáº§n Ä‘á»§ sá»‘ lÆ°á»£ng keyword theo yÃªu cáº§u.
Dedup xong thÃ¬ fill tiáº¿p báº±ng keyword Ä‘á»§ Ä‘iá»u kiá»‡n, khÃ´ng dá»«ng á»Ÿ under-quota.
```

#### Sheet 02, Sheet 03 vÃ  cÃ¡c sheet chá»§ Ä‘á»

```text
CÃ¡c sheet phá»¥ khÃ´ng cháº¡y dedup vÃ  khÃ´ng báº¯t buá»™c Ä‘á»§ 30 keyword.
```

Náº¿u bucket chá»‰ cÃ³ Ã­t hÆ¡n 30 keyword Ä‘Ãºng intent:

```text
Dá»«ng láº¡i.
KhÃ´ng thÃªm keyword yáº¿u chá»‰ Ä‘á»ƒ Ä‘á»§ sá»‘ lÆ°á»£ng.
```

---

## 25. Cáº­p nháº­t v3.5 â€” CÃ¡c thay Ä‘á»•i phá»• quÃ¡t há»‡ thá»‘ng (Universal Pipeline Updates)

PhiÃªn báº£n 3.5 chuáº©n hÃ³a láº¡i toÃ n bá»™ pipeline hiá»‡n táº¡i (bao gá»“m `AR_Filter`, `Control_Widget`, `Game_Emulator`, `Prank_Sounds` vÃ  `App_Template`) nháº±m tá»‘i Æ°u hÃ³a Ä‘á»™ chÃ­nh xÃ¡c vÃ  tÃ­nh thá»±c tiá»…n cá»§a dá»¯ liá»‡u:

### 25.1 Chuáº©n hÃ³a Search Popularity phi tuyáº¿n
Äá»ƒ trÃ¡nh keyword tier tháº¥p Ä‘Æ°á»£c cháº¥m quÃ¡ cao do peak volume lá»‹ch sá»­:
1. **Loáº¡i bá» Ä‘iá»ƒm pháº¡t**: Há»‡ thá»‘ng khÃ´ng cÃ²n Ã¡p dá»¥ng Ä‘iá»ƒm pháº¡t dá»±a trÃªn tá»· lá»‡ `Traffic Stability` vÃ o Ä‘iá»ƒm Volume chuáº©n hÃ³a. Cá»™t `Traffic Stability` vÃ  phÃ¢n loáº¡i `Stability Class` váº«n Ä‘Æ°á»£c giá»¯ láº¡i lÃ m siÃªu dá»¯ liá»‡u xuáº¥t ra bÃ¡o cÃ¡o Ä‘á»ƒ ngÆ°á»i dÃ¹ng tham kháº£o, nhÆ°ng khÃ´ng áº£nh hÆ°á»Ÿng tiÃªu cá»±c Ä‘áº¿n Ä‘iá»ƒm xáº¿p háº¡ng.
2. **Æ¯u tiÃªn dá»¯ liá»‡u reach**: Náº¿u CSV cÃ³ `MaximumReach`, há»‡ thá»‘ng dÃ¹ng tá»· lá»‡ reach thá»±c táº¿ Ä‘á»ƒ pháº£n Ã¡nh báº£n cháº¥t exponential cá»§a Search Popularity.
3. **Fallback exponential**: Náº¿u thiáº¿u `MaximumReach`, há»‡ thá»‘ng dÃ¹ng proxy exponential trÃªn thang Search Popularity tuyá»‡t Ä‘á»‘i `5â€“100`, thay vÃ¬ log-minmax theo keyword máº¡nh nháº¥t trong file.
4. **Giá»¯ peak volume á»Ÿ vai trÃ² phá»¥**: `Volume` hiá»‡n táº¡i chiáº¿m `85%`, cÃ²n `Max. Volume` lá»‹ch sá»­ chiáº¿m `15%`.
5. **Cap tier tháº¥p**: Keyword cÃ³ `Volume <= 5` chá»‰ nháº­n tá»‘i Ä‘a `0.05` Ä‘iá»ƒm `VolumeN`.
6. **KhÃ´ng Ã©p Ä‘á»§ quota báº±ng keyword yáº¿u**: Tier `5` máº·c Ä‘á»‹nh khÃ´ng Ä‘Æ°á»£c tá»± Ä‘á»™ng Ä‘Æ°a vÃ o Core/Broad metadata shortlist; Consider chá»‰ giá»¯ tá»‘i Ä‘a `3` keyword Ä‘á»ƒ review.

### 25.2 Nháº­n diá»‡n ngÃ´n ngá»¯ lai (Hybrid Language Detection Heuristic)
Nháº±m ngÄƒn ngá»«a hiá»‡n tÆ°á»£ng loáº¡i bá» sai cÃ¡c cá»¥m tá»« ASO tiáº¿ng Anh ngáº¯n do cÃ¡c thÆ° viá»‡n tá»± Ä‘á»™ng nháº­n diá»‡n ngÃ´n ngá»¯ gáº¯n cá» nháº§m lÃ  ngÃ´n ngá»¯ láº¡ (Language Bleed):
1. **Whitelist tá»« vá»±ng**: Sá»­ dá»¥ng whitelist 10,000 tá»« tiáº¿ng Anh phá»• thÃ´ng (`english_words_10k.txt`) káº¿t há»£p cÃ¡c nhÃ³m tá»« khÃ³a Ä‘áº·c thÃ¹ á»©ng dá»¥ng trong `App_Profile.json` (vÃ­ dá»¥: `gba`, `nds`, `psp`, `emulator`).
2. **Kiá»ƒm tra trÆ°á»›c**: Tá»« khÃ³a sau khi loáº¡i bá» cÃ¡c háº­u tá»‘ thÃ´ng thÆ°á»ng (`s`, `es`, `ed`, `ing`...) náº¿u táº¥t cáº£ cÃ¡c tá»« Ä‘Æ¡n Ä‘á»u náº±m trong whitelist sáº½ Ä‘Æ°á»£c máº·c Ä‘á»‹nh gáº¯n nhÃ£n `PRIMARY` (ngÃ´n ngá»¯ chÃ­nh cá»§a market).
3. **Dá»± phÃ²ng (Fallback)**: Chá»‰ thá»±c hiá»‡n gá»i thÆ° viá»‡n `langdetect` Ä‘á»‘i vá»›i cÃ¡c tá»« khÃ³a chá»©a tá»« láº¡ ngoÃ i danh sÃ¡ch whitelist. Äiá»u nÃ y giÃºp loáº¡i bá» triá»‡t Ä‘á»ƒ hiá»‡n tÆ°á»£ng láº«n tiáº¿ng TÃ¢y Ban Nha/Bá»“ ÄÃ o Nha vÃ o thá»‹ trÆ°á»ng US_EN mÃ  váº«n giá»¯ láº¡i Ä‘Æ°á»£c cÃ¡c tá»« viáº¿t táº¯t hay thuáº­t ngá»¯ ASO Ä‘áº·c thÃ¹.

### 25.3 Siáº¿t cháº·t Ä‘á»™ liÃªn quan cá»§a tá»« khÃ³a generic (Generic Relevancy Tightening)
Äá»‘i vá»›i cÃ¡c á»©ng dá»¥ng, cÃ¡c tá»« khÃ³a quÃ¡ chung chung chá»‰ chá»©a tá»« cá»‘t lÃµi cá»§a danh má»¥c mÃ  khÃ´ng Ä‘i kÃ¨m vá»›i báº¥t ká»³ ngá»¯ cáº£nh cá»¥ thá»ƒ nÃ o (vÃ­ dá»¥: chá»‰ chá»©a `"emulator"` cho Game Emulator, chá»‰ chá»©a `"widget"` cho Control Widget, hay chá»‰ chá»©a `"filter"` / `"effect"` cho AR Filter) sáº½ bá»‹ giá»›i háº¡n Ä‘iá»ƒm liÃªn quan:
1. **Quy táº¯c tÃ­nh Ä‘iá»ƒm**: Tá»« cá»‘t lÃµi cá»§a danh má»¥c chá»‰ Ä‘Æ°á»£c cá»™ng tá»‘i Ä‘a Ä‘iá»ƒm thÆ°á»Ÿng liÃªn quan (`+0.40`) náº¿u tá»« khÃ³a Ä‘Ã³ cÃ³ chá»©a Ã­t nháº¥t má»™t thuáº­t ngá»¯ ngá»¯ cáº£nh liÃªn quan (vÃ­ dá»¥: tÃªn há»‡ mÃ¡y `gba`/`psp` Ä‘á»‘i vá»›i Emulator, tÃªn tÃ­nh nÄƒng/visual/style Ä‘á»‘i vá»›i Widget hay Filter).
2. **HÃ nh vi**: Náº¿u khÃ´ng cÃ³ ngá»¯ cáº£nh Ä‘i kÃ¨m, Ä‘iá»ƒm liÃªn quan (Relevancy Score) cá»§a tá»« khÃ³a sáº½ chá»‰ Ä‘áº¡t tá»‘i Ä‘a `0.40` (tháº¥p hÆ¡n ngÆ°á»¡ng lá»c tá»‘i thiá»ƒu `0.45`), tá»« Ä‘Ã³ tá»± Ä‘á»™ng bá»‹ chuyá»ƒn sang sheet loáº¡i bá» `04_Dropped_Audit` dÆ°á»›i lÃ½ do `"Dropped: Weak app intent after scoring"`.

### 25.4 Thá»© tá»± sáº¯p xáº¿p Æ°u tiÃªn phá»¥ (Tie-breaker Sorting Logic)
Khi nhiá»u tá»« khÃ³a cÃ³ cÃ¹ng Ä‘iá»ƒm `BalancedScore` (ráº¥t phá»• biáº¿n Ä‘á»‘i vá»›i cÃ¡c tá»« khÃ³a volume tháº¥p), há»‡ thá»‘ng khÃ´ng sáº¯p xáº¿p theo thá»© tá»± ngáº«u nhiÃªn trong CSV gá»‘c ná»¯a mÃ  Ã¡p dá»¥ng cÆ¡ cháº¿ phÃ¢n háº¡ng chi tiáº¿t:
1. **Chuyá»ƒn Ä‘á»•i dá»¯ liá»‡u**: Cá»™t `Rank` Ä‘Æ°á»£c chuyá»ƒn Ä‘á»•i sang dáº¡ng sá»‘ thÃ´ng qua helper column `Rank_numeric` (cÃ¡c trÆ°á»ng há»£p khÃ´ng cÃ³ rank hoáº·c unranked Ä‘Æ°á»£c Ä‘iá»n máº·c Ä‘á»‹nh lÃ  `999`).
2. **Thá»© tá»± sáº¯p xáº¿p tá»‘i Æ°u**:
   - `BalancedScore` (giáº£m dáº§n) - Æ¯u tiÃªn Ä‘iá»ƒm tá»•ng há»£p cao nháº¥t.
   - `Rank_numeric` (tÄƒng dáº§n) - Æ¯u tiÃªn tá»« khÃ³a á»©ng dá»¥ng cÃ³ thá»© háº¡ng tá»‘t hÆ¡n (vÃ­ dá»¥: Rank 12 xáº¿p trÆ°á»›c Rank 24).
   - `KEI` (giáº£m dáº§n) - Æ¯u tiÃªn hiá»‡u quáº£ tá»« khÃ³a cao hÆ¡n.
   - `Difficulty` (tÄƒng dáº§n) - Æ¯u tiÃªn tá»« khÃ³a dá»… SEO hÆ¡n.

---

## 26. Cap nhat v3.5 - Shared Language & Keyword Filter Logic

Phien ban v3.5 tach logic nhan dien ngon ngu va loc keyword dung chung cho 5 pipeline vao thu muc `shared/`, de tranh tinh trang moi pipeline co rule rieng va ket qua lech nhau.

### 26.1 Module dung chung
1. `shared/language_detector.py` la nguon chinh cho `detect_keyword_language(keyword, market_lang, config=None, english_vocab=None)`.
2. Tai v3.5, `shared/keyword_filter.py` la nguon chinh cho cac rule loc keyword: `is_noise_only`, `is_irrelevant_keyword`, `check_naturalness`, `calculate_expansion`, `classify_keyword`.
3. Ghi chu lich su: v3.5 tung cho phep fallback legacy. Tu v4.0, file nay da duoc tach thanh package `shared/keyword_filter/` va fallback local da bi loai bo.

### 26.2 Language bucket policy
`LanguageGroup` duoc xu ly theo policy thi truong:
- `PRIMARY`: co the vao core bucket neu dat cac dieu kien diem va intent.
- `SECONDARY`: mac dinh giu lai o `Consider Keywords`. Neu raw keyword khop chinh xac `intent_core_terms`, giu vai tro core; nhan ngon ngu va semantic intent la hai truc rieng.
- `MIXED`: vao `Consider Keywords` neu market policy `mixed_allowed=True`; neu khong thi vao `Manual Review`.
- `FOREIGN`: vao `Language Mismatch Audit`.
- `UNKNOWN`: vao `Manual Review`.

Vi du voi Philippines:
- `PH_FIL`: Filipino/Tagalog la primary, English la secondary, va mixed Filipino-English duoc phep review trong `Consider Keywords`.
- `tunog prank` trong `PH_FIL` la `MIXED` hop le, nen vao `Consider Keywords`.
- `sonidos de broma` trong `PH_FIL` la Spanish/foreign, nen vao `Language Mismatch Audit`.

### 26.3 Naturalness v3.5
Naturalness khong con dung rule `LANGUAGE_BLEED` de drop keyword non-Latin hoac keyword khac script. Viec script/ngon ngu thuoc trach nhiem cua `language_detector`.

`NaturalnessFlag` chi tap trung vao chat luong keyword: empty keyword, keyword stuffing, query phrase kieu `how to`, keyword qua dai nhung khong co core/feature intent, hoac lap token canh nhau qua bat thuong.

### 26.4 Noise, irrelevant va scoring
- Noise/irrelevant duoc normalize truoc khi match.
- Phrase nhu `for android` duoc match theo phrase, khong split thanh tung word gay sai logic.
- Rule match dung token/word boundary thay vi substring tho.
- Neu keyword co core intent manh va `risk_policy.core_intent_override=True`, irrelevant term rong khong hard-drop keyword; keyword se duoc chuyen sang `Consider Keywords` neu van con rui ro.
- Expansion score khong con hard-code `widget/control`; boost duoc tinh tu `intent_core_terms`, `feature_terms`, style intent va do dai keyword.
- Language bonus chi cong cho `PRIMARY` va nhe hon cho `SECONDARY`; khong cong bonus cho `MIXED`/`UNKNOWN`.

### 26.5 Selection cache
Khi ton tai `selected_keywords.json`, pipeline kiem tra metadata co ban gom market va input file name/hash neu co. Neu cache khong khop run hien tai, pipeline bo qua cache va dung shortlist moi. Cache cu khong bi xoa tu dong.

### 26.6 Kiem thu lien quan
Khi sua logic shared, can chay:

```powershell
python -m unittest discover -s ASO-MVP-Max\tests -p "test_*.py"
python -m py_compile ASO-MVP-Max\shared\language_detector.py ASO-MVP-Max\shared\text_dedup.py ASO-MVP-Max\apps\Prank_Sounds\run_pipeline.py ASO-MVP-Max\apps\App_Template\run_pipeline.py ASO-MVP-Max\apps\AR_Filter\run_ar_filter_v4_0.py ASO-MVP-Max\apps\Control_Widget\run_control_widget_v4_0.py ASO-MVP-Max\apps\Game_Emulator\run_game_emulator_v4_0.py
```

---

## 27. Lich su v3.6 - Multilingual Text Dedup

Phien ban 3.6 tung nang cap text-level dedup cho Unicode va ngon ngu khong Latin. Day la baseline lich su; hanh vi hien tai da duoc thay the boi muc `28.5 Indexed near-duplicate clustering`.

1. `shared/text_dedup.py` dung `NFKC` + `casefold()` de nhan dien cac bien the Unicode tuong duong.
2. Combining marks co y nghia duoc bao toan; Hindi, Arabic, Thai va cac he chu tuong tu khong con bi mat dau cau tao.
3. Snowball stemming chi chay theo locale; suffix rule toan cuc da duoc bo khoi dedup.
4. Cluster duoc tao noi bo tung curated sheet truoc quota. Winner duoc chon theo thu tu:
   `Volume DESC`, `Max. Volume DESC`, `BalancedScore DESC`, `Rank_numeric ASC`, `KEI DESC`, `original_row_order ASC`.
5. Topic sheets doc lap voi main shortlist.
6. `MergedVariants` ghi alias da prune; `ReviewVariants` ghi bien the chi can xem lai.
7. Accent-fold tao `Action=REVIEW` mac dinh. Config `dedup_policy.accent_fold_auto_merge_locales` cho phep opt-in theo locale.
8. `12_Text_Dedup_Log` ghi ca `PRUNED` va `REVIEW`.
9. `TokenizerAdapter` da san sang de tich hop ICU tokenizer o release tiep theo; v3.6 chua bat buoc `PyICU`.

Dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Checklist day du cho may Windows moi: `docs/SETUP_WINDOWS.md`.

---

## 28. Cap nhat v4.0 - Hard Filter Platform & Scale Hardening

Phien ban 4.0 chuyen pipeline tu cac script loc keyword rieng le sang mot nen tang dung chung de co the van hanh toi 100 app, moi locale toi 10.000 keyword. Logic scoring va workbook curated dac thu cua tung app van duoc giu nguyen.

### 28.1 Shared hard-filter package

`shared/keyword_filter.py` da duoc tach thanh package `shared/keyword_filter/`:

```text
matcher.py
hard_filters.py
classifier.py
validator.py
audit.py
cache.py
runtime.py
version.py
```

Tat ca runner bat buoc dung shared engine. Khong con fallback local khi import shared logic loi.

`build_filter_runtime(config)` compile matcher mot lan theo `config_hash` va tai su dung cho toan bo row. API cu nhan `config` van duoc giu de tuong thich voi test va script ngoai repo.

### 28.2 Hard-filter policy

Hard filter chay doi xung tren keyword raw va cot `EN`:

```text
competitor
irrelevant
noise
risky IP
ambiguous brand
platform affiliation
truncation
```

Audit workbook ghi:

| Column | Purpose |
|---|---|
| `HardFilterRule` | Rule quyet dinh |
| `HardFilterTerm` | Term da match |
| `HardFilterSource` | `raw`, `EN`, hoac `raw+EN` |
| `PolicyFlags` | Cac co policy lien quan |

`force_top30` khong duoc phep nang keyword risk hoac hard-drop len Core. Truncation detection theo huong conservative de bat cac query dang do nhu `prank so`, `prank sou`.

Truncation logic tu v4.1 duoc harden o shared engine de tranh drop nham keyword tot tren app/ngon ngu khac:

- Token cuoi neu la tu hoan chinh trong semantic terms, feature/style/visual terms, noise terms hoac language lexicon se khong bi coi la cat cut. Vi du `battery emoji`, `battery icon`, `prank sound`, `ar filter`, `control widget` duoc giu lai.
- Bien the singular/plural don gian nhu `emoji/emojis`, `icon/icons`, `sound/sounds`, `filter/filters` khong duoc coi la truncation.
- Prefix co anchor ro rang va co completion trong candidate terms van la high-confidence `truncated_keyword`, vi du `control widg -> widget`, `prank sou -> sound`.
- Prefix co completion nhung thieu anchor se gan `possible_truncated_keyword`; mac dinh dua vao `Manual Review`, khong hard-drop.
- Connector/dangling term dung cuoi cum nhu `de`, `para`, `with`, `of` duoc gan `possible_truncated_keyword` va mac dinh vao `Manual Review`, tranh hard-drop nham cum ngon ngu khac.

Config mac dinh:

```python
"truncation_policy": {
    "enabled": True,
    "min_prefix_length": 2,
    "allowed_partial_terms": [],
    "protect_complete_tokens": True,
    "ignore_inflection_prefix": True,
    "low_confidence_action": "manual_review",
    "dangling_action": "manual_review"
}
```

### 28.3 Config rieng theo app va registry

Moi app co `app_config.py` rieng. Shared package khong chua term dac thu niche.

Config bat buoc khai bao ro:

```text
semantic_mode
ambiguous_brand_terms
platform_affiliation_terms
truncation_policy
```

Validator fail-fast khi competitor overlap voi feature/platform hoac config co duplicate.

`shared/app_registry.py` map chinh xac:

```text
alias -> app folder -> runner -> config
```

`run_aso_filter.py` khong con routing theo substring va khong fallback mac dinh sang Control Widget. App chua dang ky se fail ro rang.

### 28.4 Cache scoped va locale parser

Selection cache duoc scope theo:

```text
app_id
market
input_hash
config_hash
engine_version
```

Cache ghi atomic de tranh hai locale chay song song ghi de len nhau.

`shared/locale_parser.py` la parser locale dung chung cho orchestrator, exporter, Keyword Tracker va batch runner. Parser ho tro cac format nhu:

```text
US_EN
PH_FIL
BR_PT-BR
```

### 28.5 Indexed near-duplicate clustering

`shared/text_dedup.py` khong con so sanh moi cap keyword O(n^2) trong auto-merge.

Auto-merge dung index theo:

```text
surface_key
accent-fold key
stem sequence
token-bag key
```

Dedup chi chay cho `01_Main_Keyword_Shortlist`. Cac sheet tinh nang, style, system, game va chu de am thanh chi sort theo uu tien thong thuong.

Winner priority va `MergedVariants` van duoc giu. Bien the chi gan giong khong tao `ReviewVariants`; chung duoc giu lai de danh gia nhu keyword doc lap.

### 28.6 Shared translation service

`shared/translation_service.py` gom toan bo logic dich keyword sang EN:

```text
Provider: LibreTranslate self-host
Endpoint mac dinh: http://127.0.0.1:5102
Endpoint override: LIBRETRANSLATE_URL
API key tuy chon: LIBRETRANSLATE_API_KEY
Cache: .cache/translations.sqlite3
SQLite mode: WAL
TLS verification: bat buoc neu endpoint dung HTTPS
Retry: toi da 3 lan
Backoff: 0.5s, 1s, 2s
Timeout mac dinh: 5s
Global rate limit mac dinh: 2 request/giay
DataFrame translation workers mac dinh: 2
Health check: GET /health, lazy va dung chung cho moi TranslationService
```

Cache key gom provider, source language, target language va normalized keyword. Provider key LibreTranslate tach biet voi cache Google GTX cu. `fil` duoc map sang `tl`; mixed chi gom English va mot ngon ngu khac duoc map truc tiep; `unknown` hoac mixed nhieu ngon ngu duoc gui bang `auto`. Market `BR_PT-BR` uu tien model `pb`.

Service van ghi trang thai noi bo de test va audit ky thuat:

| Column | Values |
|---|---|
| `TranslationStatus` | `NOT_REQUIRED`, `PROVIDED_EN`, `CACHE_HIT`, `TRANSLATED`, `FAILED_RAW_FALLBACK` |
| `TranslationError` | Loi cuoi sau retry neu co |

Neu health check hoac dich loi, pipeline tiep tuc dung raw keyword thay vi fail locale va in canh bao tong hop. `TranslationStatus` va `TranslationError` khong hien thi trong workbook review thong thuong.

### 28.7 Shared profile service

`shared/profile_service.py` gom logic profile va Google Play scraping:

```text
Custom profile: <app_folder>/App_Profile.json
Generated cache: <app_folder>/.cache/profiles/generated_profile.json
TTL mac dinh: 14 ngay
TLS verification: bat buoc
Generated cache write: atomic
```

Custom profile co uu tien tuyet doi va chi doc. Generated cache khong bao gio ghi de custom profile.

Workbook ghi `ProfileStatus`:

| Status | Meaning |
|---|---|
| `CUSTOM` | Dang dung profile custom |
| `GENERATED_FRESH` | Generated cache con moi hoac vua fetch |
| `GENERATED_STALE_FALLBACK` | Fetch loi, dang dung cache cu |
| `EMPTY_FETCH_FAILED` | Fetch loi va khong co cache |

### 28.8 Batch runner

`run_aso_batch.py` chay nhieu app/locale tu JSON manifest:

```json
{
  "jobs": [
    {"app": "Pranky", "csv": "path/to/Pranky_US_EN.csv"},
    {"app": "ARFilter", "csv": "path/to/ARFilter_BR_PT.csv"}
  ]
}
```

Quy tac:

```text
- app bat buoc la alias trong registry
- locale lay tu filename bang shared locale parser
- locale-only filename van hop le vi manifest da ghi app
- validate toan bo manifest truoc khi chay
- cold Libre cache mac dinh --cold-cache-workers 1
- warm Libre cache mac dinh --max-workers 2
- khong ho tro interactive mode trong batch
- mot locale loi khong chan job khac
- exit code khac 0 neu co it nhat mot job loi
```

Report JSON gom:

```text
app
locale
input
output
elapsed time
status
exit code
error excerpt
```

### 28.9 Downstream va workbook audit

Downstream khong phu thuoc so thu tu sheet. Exporter tim sheet theo suffix:

```text
Dropped_Audit
All_Candidates
```

Master Keywords loai toan bo hard-drop va van giu `Consider Keywords`.

Workbook giu nguyen curated sheets dac thu niche. Cac cot review chinh bat dau lien nhau theo thu tu:

```text
Keyword
EN
Volume
Max. Volume
Difficulty
KEI
Rank
BalancedScore
```

Workbook khong hien thi cac cot ky thuat:

```text
TranslationStatus
TranslationError
VolumeN
ReviewVariants
```

Audit hard-filter van giu:

```text
HardFilterRule
HardFilterTerm
HardFilterSource
PolicyFlags
```

### 28.10 Kiem thu v4.0

Lenh regression chuan:

```powershell
python -m unittest discover -s tests -v
python -m py_compile (rg --files -g "*.py")
```

Smoke bat buoc truoc release:

```text
AR Filter: BR_PT
Pranky: US_EN
Control Widget: US_EN
Batch: it nhat 3 locale chay dong thoi
```

Runner hien tai da dong bo ten file `*_v4_0.py` (hoac `*_v4_1.py`). `Prank_Sounds` va `App_Template` tiep tuc dung ten trung tinh `run_pipeline.py`.

---

## 29. Cap nhat v4.1 - Low-Volume Keywords & Preserved Permutations & Swapped Locale Logic

Phien ban 4.1 dieu chinh mot so quy tac quan trong de tranh mat mat tu khoa co volume thap nhung dung intent, giu lai cac bien the hoan vi cua tu khoa trong shortlist, va sua loi nhan dien locale nguoc format trong language detector.

### 29.1 Chap nhan Keyword Volume thap (Volume <= 5)
- **Truoc day (v4.0)**: Cau hinh `exclude_low_tier_from_metadata_shortlist` duoc set la `True` lam cho cac tu khoa co volume cuc nho (khoang tu 5 tro xuong) tu dong bi loai khoi Shortlist hoac bi gioi han quota ngat ngheo.
- **Thay doi (v4.1)**: Cho phep tat bo loc nay (`exclude_low_tier_from_metadata_shortlist = False` va `max_low_tier_consider_keywords = 999`). Nhung tu khoa volume bang 5 khong con bi loai bo ma nhan diem normalize volume `VolumeN = 0.0` (priority thap nhat), giup chung giu lai co hoi vao shortlist va Consider list neu nhu co diem RelevancyScore hoac KEI tot.

### 29.2 Giu lai bien the hoan vi tu (Preserve Word Order Permutations)
- **Truoc day (v4.0)**: Thiet lap de-duplication mac dinh gop cac tu khoa co cung tap tu (token-bag deduplication) vi du `emoji battery widget` va `battery emoji widget` se bi coi la trung va chi giu lai tu co diem cao hon (hoac tu dau tien).
- **Thay doi (v4.1)**: Tich hop cau hinh `auto_merge_token_bag` trong `dedup_policy`. Khi set la `False`, thuat toan se khong con tu dong gop cac bien the hoan vi tu, chap nhan chung la nhung keyword doc lap vi tren cua hang hanh vi go thu tu tu khac nhau co the mang lai ket qua khac nhau.

### 29.3 Sua loi hoan vi locale trong Parser (Swapped Locale Logic)
- **Van de**: Khi chay cac locale viet theo chuan `Language_Country` (nhu `EN_US.csv`), bo parse locale cu parse ra `Country = EN` va `Language = US`. Dieu nay lam lech map `MARKET_LANGUAGE_MAP` vi he thong hieu nham `US` la ngon ngu phu (Secondary) khong dung voi thiet lap.
- **Sua doi**: Them co che hoan doi (swap) trong `parse_market` cua `shared/language_detector.py` va `shared/locale_parser.py` neu phat hien thay match nguoc, hoan doi tu `EN_US` thanh `US_EN` thong qua kiem tra override truoc khi dinh dang.

### 29.4 Cap nhat cau hinh app (app_config.py)
- Thay doi trong `VolumeN` weight de phan anh dung gia tri volume thuc: Tang trong so volume len cao (vi du `0.50`) de uu tien tu khoa co volume lon va giam ti trong cua cac yeu to phu khac, dong thoi giam `search_popularity_ceiling` tu 100 ve `45.0` phu hop voi dai phan bo volume thuc te cua du lieu de tranh cac tu khoa bi don lai o muc diem qua nho.

### 29.5 Hardening Truncation Logic toan he thong
- **Van de**: Logic cu chi can token cuoi la prefix cua candidate trong semantic terms la co the bi gan `truncated_keyword`, lam drop nham keyword tot nhu `battery emoji`, `widget emoji`, `battery icon`, `prank sound`, `hair clipper prank`.
- **Thay doi (v4.1)**: Shared engine tao tap complete token tu semantic terms, feature/style/visual terms, noise terms va language lexicons. Token hoan chinh va bien the singular/plural don gian (`emoji/emojis`, `icon/icons`, `sound/sounds`, `filter/filters`) khong bi hard-drop.
- **Ket qua**: Prefix co anchor ro rang van bi drop high-confidence (`prank sou -> sound`, `control widg -> widget`); prefix thieu anchor vao `possible_truncated_keyword` va mac dinh `Manual Review`.
- **Config moi**: `protect_complete_tokens=True`, `ignore_inflection_prefix=True`, `low_confidence_action="manual_review"`, `dangling_action="manual_review"`.

---

## 30. Cap nhat v4.2 - DeepSeek AI Classifier & Conservative Pre-AI Filter

Phien ban 4.2 thay doi huong nhan dien ngon ngu/semantic cho keyword bang cach dua DeepSeek AI classifier vao truoc cac buoc bucket chinh, dong thoi them `pre_ai_filter` de tiet kiem API ma khong lam mat keyword rong co lien quan.

### 30.1 Vi tri moi trong pipeline

```text
Input CSV
-> normalize keyword
-> pre_ai_filter
-> cache lookup / DeepSeek only for NeedsAI=True
-> merge AI result back to full dataframe
-> hard filters
-> naturalness
-> keyword bucket classifier
-> shortlist/export
```

`pre_ai_filter` khong thay the semantic classifier. No chi chan cac truong hop deterministic/high-confidence waste truoc khi goi cache/API.

### 30.2 Nguyen tac bao ve keyword rong lien quan

Keyword rong, gan nghia hoac lien quan gian tiep van duoc gui AI neu co kha nang phuc vu ASO intent, vi du `theme pin`, `trang tri dien thoai`, `icon pack`, `battery widget`, `status bar`, `pin de thuong`, `cute charging`, `phone personalization`.

Mac dinh khong pre-skip `possible_truncated_keyword`, `risky_ip`, `ambiguous_brand` hoac `platform_context`; cac rule nay van duoc hard filter/classifier phia sau xu ly khi da co ngu canh semantic.

### 30.3 Cac truong hop duoc skip truoc AI

- Keyword rong/invalid/khong co token hop le.
- Duplicate sau normalize/canonicalize: chi goi AI cho canonical dau tien, cac ban lap dung lai ket qua.
- Competitor brand ro rang.
- Typo blacklist ro rang.
- `truncated_keyword` hard-drop ro rang.
- `noise_only` khong co core/feature/style/visual intent.
- `platform_affiliation` hoac `platform_only` khong co app intent.
- `irrelevant_intent` ro rang va khong co tin hieu lien quan den core/feature/style/visual terms.

### 30.4 Config moi

```python
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
}
```

API key khong duoc luu vao repo/config. Dat qua bien moi truong `DEEPSEEK_API_KEY` tren may chay pipeline.

### 30.5 Audit columns moi

Sheet `06_All_Candidates` va dataframe noi bo co cac cot moi de truy vet chi phi API va ly do pre-filter:

```text
NeedsAI
PreAIAction
PreAIRule
PreAIReason
CanonicalKeyword
AISemanticBucket
AIDecisionRule
AIReason
AIConfidence
AIStatus
```

`AIStatus` co cac trang thai chinh: `AI_CLASSIFIED`, `AI_CACHE_HIT`, `AI_REUSED_CANONICAL`, `AI_SKIPPED_PREFILTER`, `AI_DISABLED_HEURISTIC`.

### 30.6 Kiem thu v4.2

Regression bat buoc:

```powershell
python -m unittest discover -s ASO-MVP-Max\tests
python -m unittest discover -s ASO-MVP-Lite\tests
```

Test moi can dam bao keyword rong lien quan khong bi pre-skip, duplicate chi goi AI mot lan, va keyword waste deterministic bi `AI_SKIPPED_PREFILTER`.
