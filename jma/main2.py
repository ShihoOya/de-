import sqlite3
import requests
import json
from datetime import datetime

# API URL設定（気象庁のエリアコードを利用）
AREA_CODE = "130000"  # 例：東京都
API_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# SQLiteデータベース設定
DB_NAME = "weather.db"

# データベース初期化
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # エリア情報テーブル
    cursor.execute('''CREATE TABLE IF NOT EXISTS Area (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area_name TEXT UNIQUE NOT NULL,
                        area_code TEXT UNIQUE NOT NULL)''')

    # 天気情報テーブル
    cursor.execute('''CREATE TABLE IF NOT EXISTS WeatherData (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        area_id INTEGER,
                        date TEXT NOT NULL,
                        temperature REAL,
                        humidity INTEGER,
                        weather TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (area_id) REFERENCES Area(id))''')
    conn.commit()
    conn.close()

# APIからデータ取得
def fetch_weather_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("API取得失敗")
        return None

# データをDBに格納
def save_to_db(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # エリア情報の挿入
    cursor.execute("INSERT OR IGNORE INTO Area (area_name, area_code) VALUES (?, ?)", 
                   ("東京", AREA_CODE))
    cursor.execute("SELECT id FROM Area WHERE area_code = ?", (AREA_CODE,))
    area_id = cursor.fetchone()[0]

    # JSONデータから必要情報を取り出す
    for day in data[0]["timeSeries"][0]["timeDefines"]:
        weather = data[0]["timeSeries"][0]["areas"][0]["weathers"]
        date = day.split("T")[0]  # 日付フォーマット調整

        cursor.execute("INSERT INTO WeatherData (area_id, date, weather) VALUES (?, ?, ?)",
                       (area_id, date, weather))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    weather_data = fetch_weather_data()
    if weather_data:
        save_to_db(weather_data)
    print("データが正常にDBへ格納されました！")
