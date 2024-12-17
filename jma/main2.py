import sqlite3
import requests

# データベース接続
def create_db():
    conn = sqlite3.connect('weather_forecast.db')
    cursor = conn.cursor()

    # テーブル作成（Areas、Weather）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Areas (
        area_code TEXT PRIMARY KEY,
        area_name TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_code TEXT,
        date TEXT,
        weather TEXT,
        wind TEXT,
        temperature REAL,
        FOREIGN KEY (area_code) REFERENCES Areas (area_code)
    );
    ''')

    # コミットしてDBに反映
    conn.commit()
    return conn, cursor


# エリア情報をAPIから取得し、DBに格納
def insert_area_data(cursor):
    area_url = "http://www.jma.go.jp/bosai/common/const/area.json"
    response = requests.get(area_url)

    if response.status_code == 200:
        area_data = response.json()
        for area in area_data:
            area_code = area['code']
            area_name = area['name']
            cursor.execute("INSERT OR REPLACE INTO Areas (area_code, area_name) VALUES (?, ?)", (area_code, area_name))
    else:
        print("エリア情報の取得に失敗しました")


# 天気予報データをAPIから取得してDBに格納
def insert_weather_data(cursor, area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    response = requests.get(url)

    if response.status_code == 200:
        forecast_data = response.json()

        # エリア情報を格納
        area_name = forecast_data[0]["timeSeries"][0]["areas"][0]["area"]["name"]
        cursor.execute("INSERT OR REPLACE INTO Areas (area_code, area_name) VALUES (?, ?)", (area_code, area_name))

        # 天気予報情報を格納
        for time_series in forecast_data[0]["timeSeries"]:
            for area in time_series["areas"]:
                weather = area["weathers"]
                wind = area["winds"]
                temperature = area.get("temps", [None])[0]  # 気温データがない場合もあるので安全に取得

                # 日付を取得（今回は単純に最初の日時を使用）
                date = time_series["timeDefines"][0]

                # Weatherテーブルにデータを格納
                cursor.execute("INSERT INTO Weather (area_code, date, weather, wind, temperature) VALUES (?, ?, ?, ?, ?)", 
                               (area_code, date, ",".join(weather), ",".join(wind), temperature))
    else:
        print(f"天気予報データの取得に失敗しました: {area_code}")


# 過去の天気予報を取得
def get_weather_for_date(cursor, area_code, date):
    cursor.execute("""
        SELECT * FROM Weather 
        WHERE area_code = ? AND date = ?
    """, (area_code, date))

    weather_data = cursor.fetchall()
    if weather_data:
        for record in weather_data:
            print(f"エリアコード: {record[1]}, 日付: {record[2]}, 天気: {record[3]}, 風: {record[4]}, 気温: {record[5]}")
    else:
        print("指定された日付の天気情報はありません")


def main():
    # データベース作成
    conn, cursor = create_db()

    # エリア情報の挿入
    insert_area_data(cursor)

    # 例: 東京都のエリアコード（130000）の天気予報を取得
    area_code = "130000"
    insert_weather_data(cursor, area_code)

    # データベース接続をコミットして閉じる
    conn.commit()

    # 過去の天気予報を表示（例: 2024-12-04T12:00:00+09:00）
    get_weather_for_date(cursor, area_code, "2024-12-04T12:00:00+09:00")

    # 最後にデータベース接続を閉じる
    conn.close()


if __name__ == "__main__":
    main()
