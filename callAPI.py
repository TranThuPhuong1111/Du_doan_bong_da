import requests
import pandas as pd
import os
import time
from datetime import datetime

CSV_FILE_PATH = 'ket_qua_tran_dau.csv'
BASE_URL = "https://api.football-data.org/v4"

# Cac giai chau Au mien phi (TIER_ONE)
LEAGUES = {
    "PL": "Premier League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "PD": "La Liga",
    "FL1": "Ligue 1",
    "DED": "Eredivisie",
    "PPL": "Primeira Liga",
    "CL": "Champions League",
}

def get_match_data():
    # Neu da co file CSV thi load luon
    if os.path.exists(CSV_FILE_PATH):
        print(f"Da tim thay file '{CSV_FILE_PATH}'. Dang load du lieu...")
        return pd.read_csv(CSV_FILE_PATH)
    
    print("Chua co file CSV. Dang goi API ")
    
    headers = {
        "X-Auth-Token": "[ENCRYPTION_KEY]"
    }

    all_matches = []
    
    for code, name in LEAGUES.items():
        print(f"\n--- Dang lay du lieu: {name} ({code}) ---")
        
        url = f"{BASE_URL}/competitions/{code}/matches"
        params = {
            "season": "2025",       # Mua giai 2025-2026
            "status": "FINISHED",   # Chi lay tran da ket thuc
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            # Neu bi rate limit (429), doi 60 giay roi thu lai
            if response.status_code == 429:
                print("  Bi rate limit! Doi 60 giay...")
                time.sleep(60)
                response = requests.get(url, headers=headers, params=params)
            
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  Loi khi goi API cho {name}: {e}")
            continue
        
        matches = data.get('matches', [])
        print(f"  Tim thay {len(matches)} tran da ket thuc.")
        
        for match in matches:
            # Ngay dien ra
            utc_date = match.get('utcDate', '')
            try:
                formatted_date = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = utc_date
            
            # Doi bong
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            
            # Ti so
            score = match.get('score', {})
            ft = score.get('fullTime', {})
            home_goals = ft.get('home', 0) if ft.get('home') is not None else 0
            away_goals = ft.get('away', 0) if ft.get('away') is not None else 0
            
            # Ket qua dang chuoi
            match_result = f"{home_team} {home_goals} - {away_goals} {away_team}"
            
            all_matches.append({
                'Ngay': formatted_date,
                'Giai dau': name,
                'Doi nha': home_team,
                'Doi khach': away_team,
                'Ban thang doi nha': home_goals,
                'Ban thang doi khach': away_goals,
                'Ket qua': match_result,
            })
        
        time.sleep(6)

    if not all_matches:
        print("\nKhong lay duoc du lieu nao!")
        return None

    # Tao DataFrame va luu CSV
    df = pd.DataFrame(all_matches)
    df = df.sort_values('Ngay').reset_index(drop=True)
    df.to_csv(CSV_FILE_PATH, index=False, encoding='utf-8-sig')
    
    print(f"\n=== Da luu thanh cong {len(df)} tran dau vao '{CSV_FILE_PATH}'! ===")
    print(f"Cac giai: {df['Giai dau'].unique().tolist()}")
    return df

# === Chay chinh ===
if __name__ == "__main__":
    df = get_match_data()
    if df is not None:
        print(f"\nTong so tran: {len(df)}")
        print(f"\n 10 dong dau:")
        print(df.head(10).to_string(index=False))
