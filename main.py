import requests
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.widget import Widget
from kivy.animation import Animation

class BrentPriceGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.ellipses = []  # Хранение экземпляров Ellipse

    def update_graph(self):
        self.canvas.clear()
        Color(1, 1, 1, 1)

        # Очистка списка ellipses при каждом обновлении
        self.ellipses = []

        for i, point in enumerate(self.points):
            height = self.height / 2 + (point - self.points[0]) * 60 / 0.05
            ellipse = Ellipse(pos=(i * 20, height), size=(10, 10))
            self.ellipses.append(ellipse)  # Добавление в список ellipses
            self.canvas.add(ellipse)

        # Обновление анимации для каждого Ellipse
        for i, ellipse in enumerate(self.ellipses):
            Animation(pos=(i * 20, self.height / 2 + (self.points[i] - self.points[0]) * 60 / 0.05),
                      duration=1).start(ellipse)

class BrentPriceApp(App):
    def build(self):
        # Create BoxLayout for label and points
        layout = BoxLayout(orientation='vertical')

        # Create label for displaying Brent crude oil price
        self.brent_label = Label(text='Loading', font_size='60sp')
        layout.add_widget(self.brent_label)

        # Create widget for displaying points
        self.brent_points = BrentPriceGraph()
        layout.add_widget(self.brent_points)

        # Run update_brent_price method every second
        Clock.schedule_interval(self.update_brent_price, 1)

        # Flag to check if the update_brent_price is in progress
        self.update_in_progress = False

        return layout

    def update_brent_price(self, *args):
        if not self.update_in_progress:
            self.update_in_progress = True
            try:
                # Send a GET request to the website and parse HTML content
                url = "https://markets.ft.com/data/commodities/tearsheet/summary?c=Brent+Crude+Oil"
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful
                soup = BeautifulSoup(response.content, "html.parser")

                # Find the element containing the Brent crude oil price and extract text
                brent_price = soup.find("span", {"class": "mod-ui-data-list__value"}).text.strip()

                # Update label with the new Brent crude oil price
                self.brent_label.text = f"Brent: {brent_price}"

                # Update points with the new Brent crude oil price
                price = float(brent_price.replace(',', ''))
                self.brent_points.points.append(price)

                # If points reach the end of the window, clear the graph and start again
                if len(self.brent_points.points) * 20 > self.brent_points.width:
                    self.brent_points.points = []

                # Update the graph with animation
                self.brent_points.update_graph()

            except requests.RequestException as e:
                print(f"Request failed: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                self.update_in_progress = False

if __name__ == '__main__':
    BrentPriceApp().run()
