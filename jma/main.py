import requests
import flet as ft

# 気象庁APIエンドポイント
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
WEATHER_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# 地域データを取得
def fetch_area_data():
    try:
        response = requests.get(AREA_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching area data: {e}")
        return {}

# 天気データを取得
def fetch_weather_data(area_code):
    weather_url = WEATHER_URL_TEMPLATE.format(area_code=area_code)
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data for {area_code}: {e}")
        return []

# メインアプリ
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.theme_mode = "light"

    appbar = ft.AppBar(
        title=ft.Text("天気予報アプリ", weight="bold"),
        bgcolor=ft.colors.BLUE_900,
        center_title=True,
    )

    region_list = ft.ListView(expand=True, spacing=10, padding=10)
    detail_view = ft.Column(
        controls=[
            ft.Text("地域を選択してください", size=20, weight="bold"),
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # 地方リストを読み込む
    def load_regions():
        area_data = fetch_area_data()
        for center_code, center_info in area_data["centers"].items():
            region_name = center_info["name"]
            children = center_info["children"]
            region_list.controls.append(
                ft.ListTile(
                    title=ft.Text(region_name),
                    on_click=lambda e, codes=children: load_prefectures(codes),
                )
            )
        page.update()

    # 都道府県リストを読み込む
    def load_prefectures(prefecture_codes):
        detail_view.controls = [ft.Text("都道府県を選択してください", size=20, weight="bold")]
        area_data = fetch_area_data()
        for code in prefecture_codes:
            prefecture_info = area_data["offices"].get(code, {})
            prefecture_name = prefecture_info.get("name", "不明")
            children = prefecture_info.get("children", [])
            detail_view.controls.append(
                ft.ListTile(
                    title=ft.Text(prefecture_name),
                    on_click=lambda e, codes=children: load_areas(codes),
                )
            )
        page.update()

    # 地域リストを読み込む
    def load_areas(area_codes):
        detail_view.controls = [ft.Text("地域を選択してください", size=20, weight="bold")]
        area_data = fetch_area_data()
        for code in area_codes:
            area_info = area_data["class10s"].get(code, {})
            area_name = area_info.get("name", "不明")
            detail_view.controls.append(
                ft.ListTile(
                    title=ft.Text(area_name),
                    on_click=lambda e, code=code: show_weather(code),
                )
            )
        page.update()

    # 天気データを表示
    def show_weather(area_code):
        weather_data = fetch_weather_data(area_code)
        detail_view.controls = [ft.Text(f"{area_code}の天気予報", size=20, weight="bold")]

        if weather_data:
            forecasts = weather_data[0].get("timeSeries", [])
            if forecasts:
                areas = forecasts[0].get("areas", [])
                area_weather = next((a for a in areas if a["area"]["code"] == area_code), None)
                if area_weather:
                    weather = area_weather.get("weathers", ["不明"])[0]
                    temps = area_weather.get("temps", ["不明", "不明"])
                    detail_view.controls.append(ft.Text(f"天気: {weather}", size=16))
                    detail_view.controls.append(ft.Text(f"最高気温: {temps[0]}°C", size=14))
                    detail_view.controls.append(ft.Text(f"最低気温: {temps[1]}°C", size=14))
        else:
            detail_view.controls.append(ft.Text("天気情報が取得できませんでした。"))

        page.update()

    # ページレイアウト
    page.appbar = appbar
    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    ft.Column(
                        controls=[
                            ft.Text("地方を選択", size=18, weight="bold"),
                            region_list,
                        ],
                        spacing=10,
                    ),
                    width=300,
                    bgcolor=ft.colors.GREY_200,
                    padding=10,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(detail_view, expand=True, padding=20),
            ],
            expand=True,
        )
    )

    load_regions()

ft.app(target=main)
