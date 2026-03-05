import flet as ft
import requests

def get_country_info(name):
    country_link = f"https://restcountries.com/v3.1/name/{name}?fullText=true"
    
    try:
        response = requests.get(country_link)
        if response.status_code != 200: 
            return None

        data = response.json()[0]
        lat, lon = data.get("latlng", [0, 0])

        weather_link = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_link)

        temp_display = "N/A"
        if weather_response.status_code == 200:
            celsius = weather_response.json().get('current_weather', {}).get('temperature')
            fahrenheit = (celsius * 9/5) + 32
            temp_display = f"{celsius}°C / {fahrenheit:.1f}°F"

        return {
            "official_name": data.get("name", {}).get("official", "N/A"),
            "capital": data.get("capital", ["N/A"])[0],
            "region": f"{data.get('region')} ({data.get('subregion')})",
            "population": f"{data.get('population', 0)}",
            "currency": ", ".join([c['name'] for c in data.get("currencies").values()]),
            "languages": ", ".join(data.get("languages").values()),
            "flag": data.get("flags", {}).get("png", ""),
            "timezones": ", ".join(data.get("timezones")),
            "weather": temp_display,
            "code": data.get("cca2")
        }
    except:
        return None

def main(page: ft.Page):
    page.title = "Global Travel Agency"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    search_input = ft.TextField(label="Enter Country Name", width=400)
    results_area = ft.Column(visible=False, spacing=15)

    def handle_search(e):
        results_area.visible = False
        page.update()

        country_data = get_country_info(search_input.value)

        if country_data:
            results_area.controls = [
                ft.Image(src=country_data["flag"], width=250, border_radius=10),
                ft.Text(country_data["official_name"], size=28, weight="bold"),
                ft.Text(f"📍 Capital: {country_data['capital']} | 🌡️ Weather: {country_data['weather']}", 
                        size=20, color="blue", weight="w600"),
                ft.Divider(),
                ft.Text(f"Region: {country_data['region']}"),
                ft.Text(f"Population: {country_data['population']}"),
                ft.Text(f"Currency: {country_data['currency']}"),
                ft.Text(f"Languages: {country_data['languages']}"),
                ft.Text(f"Time Zones: {country_data['timezones']}"),
                ft.Text(f"Country Code: {country_data['code']}")
            ]
        else:

            results_area.controls = [
                ft.Text(f"Error: Could not find '{search_input.value}'. Please check the spelling.", 
                        color=ft.Colors.RED_700, size=18, weight="bold")
            ]

        results_area.visible = True
        page.update()

    page.add(
        ft.Text("🌍 Travel Agency Search Portal", size=32, weight="bold"),
        ft.Row([
            search_input, 
            ft.ElevatedButton("Search", icon=ft.Icons.SEARCH, on_click=handle_search)
        ]),
        ft.Divider(height=30),
        results_area
    )

ft.app(target=main)