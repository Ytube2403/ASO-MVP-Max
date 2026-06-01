import os
import sqlite3
from datetime import datetime

DB_NAME = "keyword_tracker.db"

def get_db_path():
    # Store database in the same directory as this file
    dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, DB_NAME)

def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table to store keyword data per app, locale, month, and keyword
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keyword_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            locale TEXT NOT NULL,
            month TEXT NOT NULL,
            keyword TEXT NOT NULL,
            brand INTEGER DEFAULT 0, -- 0 = False, 1 = True
            volume INTEGER DEFAULT 0,
            max_volume INTEGER DEFAULT 0,
            difficulty INTEGER DEFAULT 0,
            kei INTEGER DEFAULT 0,
            rank INTEGER DEFAULT 0, -- 0 = Unranked
            rank_status TEXT DEFAULT 'unranked',
            growth INTEGER DEFAULT 0,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(app_name, locale, month, keyword)
        )
    """)
    
    # Indexes for fast querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_locale_month ON keyword_data(app_name, locale, month)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_data(keyword)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_locale_keyword ON keyword_data(app_name, locale, keyword)")
    
    # Table for tracking imported files and hashes (to prevent duplicate work)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL UNIQUE,
            file_hash TEXT NOT NULL,
            app_name TEXT NOT NULL,
            locale TEXT NOT NULL,
            month TEXT NOT NULL,
            row_count INTEGER DEFAULT 0,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_import_log(file_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_hash, row_count FROM import_log WHERE file_path = ?", (file_path,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_import_log(file_path, file_hash, app_name, locale, month, row_count):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO import_log (file_path, file_hash, app_name, locale, month, row_count, imported_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (file_path, file_hash, app_name, locale, month, row_count))
    conn.commit()
    conn.close()

def clear_import_data(app_name, locale, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?
    """, (app_name, locale, month))
    conn.commit()
    conn.close()

def insert_keyword_rows(rows):
    """
    rows: List of dicts matching database columns
    """
    if not rows:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executemany("""
        INSERT OR REPLACE INTO keyword_data (
            app_name, locale, month, keyword, brand, volume, max_volume, difficulty, kei, rank, rank_status, growth, imported_at
        ) VALUES (
            :app_name, :locale, :month, :keyword, :brand, :volume, :max_volume, :difficulty, :kei, :rank, :rank_status, :growth, CURRENT_TIMESTAMP
        )
    """, rows)
    
    conn.commit()
    conn.close()

def get_available_apps():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT app_name FROM keyword_data ORDER BY app_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_available_locales(app_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT locale FROM keyword_data WHERE app_name = ? ORDER BY locale ASC", (app_name,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_available_months(app_name, locale):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT month FROM keyword_data 
        WHERE app_name = ? AND locale = ? 
        ORDER BY SUBSTR(month, 3, 4) ASC, SUBSTR(month, 1, 2) ASC
    """, (app_name, locale))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def calculate_aso_power_score_db(app_name, locale, month):
    """
    Tier-based ASO Power Score calculation:
    - Top 1: Vol * 10
    - Top 2-3: Vol * 7
    - Top 4-10: Vol * 4
    - Top 11-30: Vol * 2
    - Top 31-100: Vol * 1
    - Others/Unranked: 0
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT volume, rank FROM keyword_data
        WHERE app_name = ? AND locale = ? AND month = ? AND rank > 0 AND rank <= 100
    """, (app_name, locale, month))
    
    rows = cursor.fetchall()
    conn.close()
    
    score = 0
    for volume, rank in rows:
        vol = volume or 0
        if rank == 1:
            score += vol * 10
        elif rank in (2, 3):
            score += vol * 7
        elif rank >= 4 and rank <= 10:
            score += vol * 4
        elif rank >= 11 and rank <= 30:
            score += vol * 2
        elif rank >= 31 and rank <= 100:
            score += vol * 1
            
    return score

def get_overview_data(app_name, locale):
    """
    Get trend of ASO Power Score and Rank Distribution over all months.
    """
    months = get_available_months(app_name, locale)
    if not months:
        return []
        
    conn = get_connection()
    cursor = conn.cursor()
    
    results = []
    for month in months:
        # Calculate Power Score
        score = calculate_aso_power_score_db(app_name, locale, month)
        
        # Count rank distributions
        # Tiers: Top 1, Top 2-3, Top 4-10, Top 11-30, Top 31-100, Unranked (rank=0 or rank > 100)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN rank = 1 THEN 1 END) as top_1,
                COUNT(CASE WHEN rank IN (2, 3) THEN 1 END) as top_2_3,
                COUNT(CASE WHEN rank >= 4 AND rank <= 10 THEN 1 END) as top_4_10,
                COUNT(CASE WHEN rank >= 11 AND rank <= 30 THEN 1 END) as top_11_30,
                COUNT(CASE WHEN rank >= 31 AND rank <= 100 THEN 1 END) as top_31_100,
                COUNT(CASE WHEN rank = 0 OR rank > 100 THEN 1 END) as unranked,
                COUNT(*) as total_keywords
            FROM keyword_data
            WHERE app_name = ? AND locale = ? AND month = ?
        """, (app_name, locale, month))
        
        counts = cursor.fetchone()
        counts_dict = dict(counts) if counts else {
            "top_1": 0, "top_2_3": 0, "top_4_10": 0, "top_11_30": 0, "top_31_100": 0, "unranked": 0, "total_keywords": 0
        }
        
        results.append({
            "month": month,
            "aso_power_score": score,
            "tiers": counts_dict
        })
        
    conn.close()
    return results

def get_comparison_data(app_name, locale, month_a, month_b):
    """
    Compare month_a (base) and month_b (target).
    If month_a == month_b or month_a is empty, just returns target month data with 0 deltas.
    Returns list of dicts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if not month_a or month_a == month_b:
        # Single month view (just month_b)
        cursor.execute("""
            SELECT 
                keyword, brand, 
                0 as volume_a, volume as volume_b, volume as diff_volume,
                0 as difficulty_a, difficulty as difficulty_b, difficulty as diff_difficulty,
                0 as rank_a, rank as rank_b, 0 as diff_rank,
                'unranked' as rank_status_a, rank_status as rank_status_b,
                0 as growth_a, growth as growth_b,
                '→' as status
            FROM keyword_data
            WHERE app_name = ? AND locale = ? AND month = ?
            ORDER BY volume_b DESC, keyword ASC
        """, (app_name, locale, month_b))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
        
    # Standard 2-month comparison
    # Use FULL OUTER JOIN emulation using LEFT JOIN and UNION
    cursor.execute("""
        SELECT 
            COALESCE(b.keyword, a.keyword) as keyword,
            COALESCE(b.brand, a.brand) as brand,
            COALESCE(a.volume, 0) as volume_a,
            COALESCE(b.volume, 0) as volume_b,
            (COALESCE(b.volume, 0) - COALESCE(a.volume, 0)) as diff_volume,
            COALESCE(a.difficulty, 0) as difficulty_a,
            COALESCE(b.difficulty, 0) as difficulty_b,
            (COALESCE(b.difficulty, 0) - COALESCE(a.difficulty, 0)) as diff_difficulty,
            COALESCE(a.rank, 0) as rank_a,
            COALESCE(b.rank, 0) as rank_b,
            COALESCE(a.rank_status, 'unranked') as rank_status_a,
            COALESCE(b.rank_status, 'unranked') as rank_status_b,
            COALESCE(a.growth, 0) as growth_a,
            COALESCE(b.growth, 0) as growth_b
        FROM 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) a
        LEFT JOIN 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) b
        ON a.keyword = b.keyword
        
        UNION
        
        SELECT 
            COALESCE(b.keyword, a.keyword) as keyword,
            COALESCE(b.brand, a.brand) as brand,
            COALESCE(a.volume, 0) as volume_a,
            COALESCE(b.volume, 0) as volume_b,
            (COALESCE(b.volume, 0) - COALESCE(a.volume, 0)) as diff_volume,
            COALESCE(a.difficulty, 0) as difficulty_a,
            COALESCE(b.difficulty, 0) as difficulty_b,
            (COALESCE(b.difficulty, 0) - COALESCE(a.difficulty, 0)) as diff_difficulty,
            COALESCE(a.rank, 0) as rank_a,
            COALESCE(b.rank, 0) as rank_b,
            COALESCE(a.rank_status, 'unranked') as rank_status_a,
            COALESCE(b.rank_status, 'unranked') as rank_status_b,
            COALESCE(a.growth, 0) as growth_a,
            COALESCE(b.growth, 0) as growth_b
        FROM 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) b
        LEFT JOIN 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) a
        ON a.keyword = b.keyword
    """, (app_name, locale, month_a, app_name, locale, month_b, app_name, locale, month_b, app_name, locale, month_a))
    
    raw_rows = cursor.fetchall()
    conn.close()
    
    # Post-process rank delta and status
    processed = []
    for r in raw_rows:
        d = dict(r)
        rank_a = d['rank_a']
        rank_b = d['rank_b']
        
        # Calculate rank diff: rank_b - rank_a
        # But we must be careful: 0 means unranked (treated as infinity in comparisons)
        # So we can calculate effective ranks for delta calculations:
        eff_a = rank_a if rank_a > 0 else 999
        eff_b = rank_b if rank_b > 0 else 999
        
        if rank_a == 0 and rank_b == 0:
            d['diff_rank'] = 0
            d['status'] = '→'
        elif rank_a == 0:  # New rank / entered chart
            d['diff_rank'] = -eff_b  # improvement (negative delta)
            d['status'] = 'New' if volume_a_not_exists(app_name, locale, month_a, d['keyword']) else '↑'
        elif rank_b == 0:  # Left chart / lost rank
            d['diff_rank'] = eff_a  # decline (positive delta)
            d['status'] = 'Lost' if volume_b_not_exists(app_name, locale, month_b, d['keyword']) else '↓'
        else:
            d['diff_rank'] = rank_b - rank_a
            if rank_b < rank_a:
                d['status'] = '↑'
            elif rank_b > rank_a:
                d['status'] = '↓'
            else:
                d['status'] = '→'
                
        # Refine status for keywords that are completely new or completely lost between months
        # Let's define:
        # - "New" if the keyword is present in B but not in A
        # - "Lost" if the keyword is present in A but not in B
        # In SQL outer join, we can check if it is missing in A or B
        # Note: raw SQL leaves missing month values as 0/default. Let's look at the database.
        # If we want to check if the keyword actually did not exist in A:
        # A keyword is "New" if it did not exist in A at all.
        # Let's check volume_a. In the UNION query above, if a keyword was NOT in A, a.volume would be NULL, which COALESCE maps to 0.
        # But maybe the keyword was in A and volume was 0? Highly unlikely since all imported keywords have some presence.
        # Let's do a more robust check in python:
        # If the keyword didn't exist in A (which we can know if it was not in month_a's data).
        # We can find this by querying the lists of keywords for month_a and month_b.
        # But we can also infer: if rank_a == 0 and volume_a == 0 and difficulty_a == 0: likely not in A.
        # Let's adjust this: if we want to be exact, we can retrieve keywords in month_a and month_b and check membership.
        # To avoid extra DB hits, we can check if the UNION results indicate absence.
        # Wait, if we rewrite the query to return whether it existed in month_a and month_b:
        # we can select `a.keyword IS NOT NULL as in_a`, `b.keyword IS NOT NULL as in_b`. Let's do that!
        processed.append(d)
        
    # Sort: put larger target volume first
    processed.sort(key=lambda x: (x['volume_b'], -x['rank_b'] if x['rank_b'] > 0 else -999), reverse=True)
    return processed

def volume_a_not_exists(app_name, locale, month, keyword):
    # Quick check if keyword existed in month A
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM keyword_data WHERE app_name=? AND locale=? AND month=? AND keyword=?", (app_name, locale, month, keyword))
    res = cursor.fetchone()
    conn.close()
    return res is None

def volume_b_not_exists(app_name, locale, month, keyword):
    # Quick check if keyword existed in month B
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM keyword_data WHERE app_name=? AND locale=? AND month=? AND keyword=?", (app_name, locale, month, keyword))
    res = cursor.fetchone()
    conn.close()
    return res is None

def get_comparison_data_v2(app_name, locale, month_a, month_b):
    """
    Better comparison query that includes existence flags.
    """
    if not month_a or month_a == month_b:
        return get_comparison_data(app_name, locale, None, month_b)
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # We will query with existence flags `in_a` and `in_b`
    cursor.execute("""
        SELECT 
            COALESCE(b.keyword, a.keyword) as keyword,
            COALESCE(b.brand, a.brand) as brand,
            COALESCE(a.volume, 0) as volume_a,
            COALESCE(b.volume, 0) as volume_b,
            (COALESCE(b.volume, 0) - COALESCE(a.volume, 0)) as diff_volume,
            COALESCE(a.difficulty, 0) as difficulty_a,
            COALESCE(b.difficulty, 0) as difficulty_b,
            (COALESCE(b.difficulty, 0) - COALESCE(a.difficulty, 0)) as diff_difficulty,
            COALESCE(a.rank, 0) as rank_a,
            COALESCE(b.rank, 0) as rank_b,
            COALESCE(a.rank_status, 'unranked') as rank_status_a,
            COALESCE(b.rank_status, 'unranked') as rank_status_b,
            COALESCE(a.growth, 0) as growth_a,
            COALESCE(b.growth, 0) as growth_b,
            (a.keyword IS NOT NULL) as in_a,
            (b.keyword IS NOT NULL) as in_b
        FROM 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) a
        LEFT JOIN 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) b
        ON a.keyword = b.keyword
        
        UNION
        
        SELECT 
            COALESCE(b.keyword, a.keyword) as keyword,
            COALESCE(b.brand, a.brand) as brand,
            COALESCE(a.volume, 0) as volume_a,
            COALESCE(b.volume, 0) as volume_b,
            (COALESCE(b.volume, 0) - COALESCE(a.volume, 0)) as diff_volume,
            COALESCE(a.difficulty, 0) as difficulty_a,
            COALESCE(b.difficulty, 0) as difficulty_b,
            (COALESCE(b.difficulty, 0) - COALESCE(a.difficulty, 0)) as diff_difficulty,
            COALESCE(a.rank, 0) as rank_a,
            COALESCE(b.rank, 0) as rank_b,
            COALESCE(a.rank_status, 'unranked') as rank_status_a,
            COALESCE(b.rank_status, 'unranked') as rank_status_b,
            COALESCE(a.growth, 0) as growth_a,
            COALESCE(b.growth, 0) as growth_b,
            (a.keyword IS NOT NULL) as in_a,
            (b.keyword IS NOT NULL) as in_b
        FROM 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) b
        LEFT JOIN 
            (SELECT * FROM keyword_data WHERE app_name = ? AND locale = ? AND month = ?) a
        ON a.keyword = b.keyword
    """, (app_name, locale, month_a, app_name, locale, month_b, app_name, locale, month_b, app_name, locale, month_a))
    
    raw_rows = cursor.fetchall()
    conn.close()
    
    processed = []
    for r in raw_rows:
        d = dict(r)
        rank_a = d['rank_a']
        rank_b = d['rank_b']
        in_a = d['in_a']
        in_b = d['in_b']
        
        eff_a = rank_a if rank_a > 0 else 999
        eff_b = rank_b if rank_b > 0 else 999
        
        if not in_a:  # Present in B but not in A (completely new keyword)
            d['diff_rank'] = -eff_b if rank_b > 0 else 0
            d['status'] = 'New'
        elif not in_b:  # Present in A but not in B (completely lost keyword)
            d['diff_rank'] = eff_a if rank_a > 0 else 0
            d['status'] = 'Lost'
        else:  # Present in both
            if rank_a == 0 and rank_b == 0:
                d['diff_rank'] = 0
                d['status'] = '→'
            elif rank_a == 0:  # Gained rank
                d['diff_rank'] = -eff_b
                d['status'] = '↑'
            elif rank_b == 0:  # Lost rank
                d['diff_rank'] = eff_a
                d['status'] = '↓'
            else:
                d['diff_rank'] = rank_b - rank_a
                if rank_b < rank_a:
                    d['status'] = '↑'
                elif rank_b > rank_a:
                    d['status'] = '↓'
                else:
                    d['status'] = '→'
                    
        # Remove helper boolean flags for JSON payload sizing
        del d['in_a']
        del d['in_b']
        processed.append(d)
        
    # Sort: Volume B desc
    processed.sort(key=lambda x: (x['volume_b'], x['volume_a']), reverse=True)
    return processed

def get_keyword_trend(app_name, locale, keyword):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Sort order by month chronologically
    cursor.execute("""
        SELECT month, volume, max_volume, difficulty, kei, rank, rank_status, growth
        FROM keyword_data
        WHERE app_name = ? AND locale = ? AND keyword = ?
        ORDER BY SUBSTR(month, 3, 4) ASC, SUBSTR(month, 1, 2) ASC
    """, (app_name, locale, keyword))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_movers(app_name, locale, month_a, month_b, limit=20):
    """
    Get top rank gainers, losers, new keywords, and lost keywords.
    """
    comparison = get_comparison_data_v2(app_name, locale, month_a, month_b)
    
    # Filter groups
    # 1. Gainers: both present, rank improved (diff_rank < 0), ranked in both
    gainers = [c for c in comparison if c['status'] == '↑' and c['rank_a'] > 0 and c['rank_b'] > 0]
    # Sort gainers by most negative diff_rank (best improvement first)
    gainers.sort(key=lambda x: x['diff_rank'])
    
    # 2. Losers: both present, rank declined (diff_rank > 0), ranked in both
    losers = [c for c in comparison if c['status'] == '↓' and c['rank_a'] > 0 and c['rank_b'] > 0]
    # Sort losers by most positive diff_rank (worst decline first)
    losers.sort(key=lambda x: x['diff_rank'], reverse=True)
    
    # 3. New: status == 'New'
    new_kw = [c for c in comparison if c['status'] == 'New']
    
    # 4. Lost: status == 'Lost'
    lost_kw = [c for c in comparison if c['status'] == 'Lost']
    
    # Also handle keywords that became ranked or unranked
    # Keywords that were unranked in A but became ranked in B:
    gained_rank = [c for c in comparison if c['rank_a'] == 0 and c['rank_b'] > 0 and c['status'] != 'New']
    gained_rank.sort(key=lambda x: x['rank_b'])
    
    # Keywords that were ranked in A but became unranked in B:
    lost_rank = [c for c in comparison if c['rank_a'] > 0 and c['rank_b'] == 0 and c['status'] != 'Lost']
    lost_rank.sort(key=lambda x: x['rank_a'], reverse=True)
    
    # Merge gained_rank into gainers, lost_rank into losers for convenience?
    # Actually, let's keep them clean:
    # Let's count unranked -> rank as rank improvement of (999 - rank_b)
    # Let's define a sorting key for gainers:
    # If rank_a was 0 (unranked), improvement is huge (e.g. from 999 -> rank_b)
    # Let's calculate effective improvement:
    # eff_a = rank_a if rank_a > 0 else 999
    # eff_b = rank_b if rank_b > 0 else 999
    # improvement = eff_a - eff_b
    # Let's build a unified gainers list including unranked -> ranked:
    all_gainers = [c for c in comparison if (c['status'] == '↑' or (c['rank_a'] == 0 and c['rank_b'] > 0)) and c['status'] != 'New']
    all_gainers.sort(key=lambda x: (x['rank_a'] if x['rank_a'] > 0 else 999) - x['rank_b'], reverse=True)
    
    all_losers = [c for c in comparison if (c['status'] == '↓' or (c['rank_a'] > 0 and c['rank_b'] == 0)) and c['status'] != 'Lost']
    all_losers.sort(key=lambda x: x['rank_b'] - (x['rank_a'] if x['rank_a'] > 0 else 999) if x['rank_b'] > 0 else 999 - x['rank_a'], reverse=True)
    
    return {
        "gainers": all_gainers[:limit],
        "losers": all_losers[:limit],
        "new": new_kw[:limit],
        "lost": lost_kw[:limit]
    }
