import flet as ft
import requests
import datetime

def get_country_info(name):
    global country_link
    country_link = f"https://restcountries.com/v3.1/name/{name}?fullText=true"
    try:
        response = requests.get(country_link)
        if response.status_code != 200: return None
        data = response.json()[0]
        lat, lon = data.get("latlng", [0, 0])
        weather_response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        )
        temp_display = "N/A"
        if weather_response.status_code == 200:
            celsius = weather_response.json().get("current_weather", {}).get("temperature")
            fahrenheit = (celsius * 9 / 5) + 32
            temp_display = f"{celsius}°C / {fahrenheit:.1f}°F"
        return {
            "official_name": data.get("name", {}).get("official", "N/A"),
            "capital": data.get("capital", ["N/A"])[0],
            "region": f"{data.get('region')} ({data.get('subregion')})",
            "population": f"{data.get('population', 0):,}",
            "currency": ", ".join([c["name"] for c in data.get("currencies").values()]),
            "languages": ", ".join(data.get("languages").values()),
            "flag": data.get("flags", {}).get("png", ""),
            "timezones": ", ".join(data.get("timezones")),
            "weather": temp_display,
            "code": data.get("cca2"),
        }
    except: return None

def fetch_country_suggestions(query):
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{query}")
        return [c["name"]["common"] for c in response.json()[:5]]
    except: return []

def main(page: ft.Page):
    page.title = "Global Travel Agency"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"
    page.padding = 20

    def SectionCard(content):
        return ft.Container(
            content=content,
            padding=20,
            bgcolor="#25292e", 
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color="#121212")
        )

    search_input = ft.TextField(label="Enter Country Name", width=400, border_radius=10, border_color="#448AFF")
    suggestions1 = ft.Column(spacing=0)
    results_area = ft.Column(visible=False, spacing=15)

    def choose_search_country(name):
        search_input.value = name
        suggestions1.controls = []
        page.update()

    def select_country(e):
        query = search_input.value.strip().lower()
        if len(query) < 2:
            suggestions1.controls = []
            page.update()
            return
        suggestions1.controls = [
            ft.ListTile(title=ft.Text(name), on_click=lambda e, n=name: choose_search_country(n)) 
            for name in fetch_country_suggestions(query)
        ]
        page.update()

    def handle_search(e):
        data = get_country_info(search_input.value.strip())
        if not data: return
        map_url = f"https://www.google.com/maps/search/{data['official_name'].replace(' ', '+')}"

        results_area.controls = [
            ft.Row([
                ft.Image(src=data["flag"], width=120, border_radius=5),
                ft.Column([
                    ft.Text(data["official_name"], size=22, weight="bold", width=250, color="#E3F2FD"),
                    ft.Text(f"🌡️ {data['weather']}", size=18, color="#64B5F6", weight="bold"),
                ])
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color="#424242"),
            ft.Text(f"📍 Capital: {data['capital']}", size=16, color="#90CAF9"),
            ft.Text(f"🗺️ Region: {data['region']}", color="#B0BEC5"),
            ft.Text(f"👥 Population: {data['population']}", color="#B0BEC5"),
            ft.Text(f"💱 Currency: {data['currency']}", color="#81C784"),
            ft.Text(f"🗣️ Languages: {data['languages']}", color="#B0BEC5"),
            ft.Text(f"🌐 Time Zones: {data['timezones']}", color="#B0BEC5"),
            ft.Text(f"🆔 Country Code: {data['code']}", color="#B0BEC5"),
            ft.ElevatedButton("View on Google Maps", icon=ft.icons.MAP, color="#448AFF", on_click=lambda _: page.launch_url(map_url))
        ]
        results_area.visible = True
        page.update()

    search_input.on_change = select_country

    tab1content = ft.Column([
        ft.Text("🌍 Global Discovery", size=32, weight="bold", color="#BBDEFB"),
        SectionCard(ft.Column([search_input, suggestions1])),
        ft.ElevatedButton("Search Details", icon=ft.icons.TRAVEL_EXPLORE, bgcolor="#1976D2", color="white", on_click=handle_search, height=50),
        results_area
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    selected_start_date = {"value": None}
    start_date_display = ft.Text("No date selected", italic=True, color="#78909C")

    def handle_date_picked(e):
        selected_start_date["value"] = e.control.value
        start_date_display.value = f"✈️ Departure: {e.control.value.strftime('%b %d, %Y')}"
        start_date_display.color = "#64B5F6"
        page.update()

    def delete_entry(container_to_remove):
        plan_list.controls.remove(container_to_remove)
        page.update()

    def edit_entry(container, name, country, days, note):
        client_name.value = name
        destination_country.value = country
        duration.value = days
        extras.value = note
        plan_list.controls.remove(container)
        page.update()

    def clear_all_plans(e):
        plan_list.controls.clear()
        page.update()

    def reset_errors(e):
        client_name.error_text = None
        client_name.border_color = "#4DB6AC"
        destination_country.error_text = None
        destination_country.border_color = "#4DB6AC"
        duration.error_text = None
        duration.border_color = "#4DB6AC"
        page.update()

    def add_to_plan(e):
        valid = True
        if not client_name.value.strip():
            client_name.error_text = "Missing Name"
            client_name.border_color = "red"
            valid = False
        if not duration.value.isdigit() or int(duration.value) <= 0:
            duration.error_text = "Invalid days"
            duration.border_color = "red"
            valid = False
        check_url = f"https://restcountries.com/v3.1/name/{destination_country.value.strip()}?fullText=true"
        response = requests.get(check_url)
        if response.status_code != 200:
            destination_country.error_text = "Invalid Country"
            destination_country.border_color = "red"
            valid = False
        if not selected_start_date["value"]:
            page.snack_bar = ft.SnackBar(ft.Text("Pick a date!"), bgcolor="red")
            page.snack_bar.open = True
            valid = False
        if not valid:
            page.update()
            return

        start_date = selected_start_date["value"]
        days_count = int(duration.value)
        end_date = start_date + datetime.timedelta(days=days_count)
        date_range = f"{start_date.strftime('%b %d')} → {end_date.strftime('%b %d, %Y')}"
        display_text = f"{client_name.value} - {duration.value} days - {extras.value} - {date_range}"

        new_entry = ft.Container(
            bgcolor="#1e2124",
            border_radius=10,
            padding=5,
            border=ft.border.all(1, "#37474F"),
            content=ft.ListTile(
                leading=ft.Icon(ft.icons.AIRPLANEMODE_ACTIVE, color="#64B5F6"),
                title=ft.Text(destination_country.value.title(), weight="bold", color="#E3F2FD"),
                subtitle=ft.Text(display_text, color="#90A4AE"),
                trailing=ft.Row([
                    ft.IconButton(
                        icon=ft.icons.EDIT_OUTLINED,
                        icon_color="#4DB6AC",
                        on_click=lambda e, n=client_name.value, c=destination_country.value, d=duration.value, nt=extras.value: 
                            edit_entry(new_entry, n, c, d, nt)
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color="#E57373",
                        on_click=lambda e: delete_entry(new_entry)
                    )
                ], tight=True)
            )
        )
        plan_list.controls.append(new_entry)
        destination_country.value = ""
        duration.value = ""
        extras.value = ""
        reset_errors(None)
        page.update()

    client_name = ft.TextField(label="Client Name", width=400, border_color="#4DB6AC", on_change=reset_errors)
    destination_country = ft.TextField(label="Destination", width=400, border_color="#4DB6AC", on_change=reset_errors)
    duration = ft.TextField(label="Days", width=100, border_color="#4DB6AC", on_change=reset_errors)
    extras = ft.TextField(label="Notes", width=400, multiline=True, border_color="#4DB6AC")
    plan_list = ft.Column(spacing=10)

    tab2content = ft.Column([
        ft.Text("Itinerary Builder", size=28, weight="bold", color="#B2DFDB"),
        SectionCard(ft.Column([
            client_name, destination_country,
            ft.Row([ft.ElevatedButton("Pick Date", icon=ft.icons.CALENDAR_MONTH, color="#4DB6AC", on_click=lambda _: page.open(ft.DatePicker(on_change=handle_date_picked))), start_date_display]),
            extras,
            ft.Row([duration, ft.FloatingActionButton(icon=ft.icons.ADD, bgcolor="#00897B", on_click=add_to_plan, mini=True)]),
        ])),
        ft.TextButton("Clear All Entries", icon=ft.icons.DELETE_SWEEP, icon_color="#EF5350", on_click=clear_all_plans),
        plan_list
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    tab3content = ft.Column([
        ft.Text("Pricing & Packages", size=28, weight="bold", color="#CE93D8"),
        SectionCard(ft.Text("Partner Placeholder", italic=True, color="#9E9E9E"))
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(ft.Tabs(
        tabs=[
            ft.Tab(text="Search", icon=ft.icons.SEARCH, content=tab1content),
            ft.Tab(text="Planner", icon=ft.icons.EDIT_CALENDAR, content=tab2content),
            ft.Tab(text="Pricing", icon=ft.icons.PAYMENTS, content=tab3content)
        ], expand=True))

ft.app(target=main)