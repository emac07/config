import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
)
from PyQt5.QtCore import QTimer, Qt, QSize, QRect
from PyQt5.QtGui import QFont, QKeyEvent
import requests
import datetime

class DeathCountdownApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Death Countdown")
        self.setFixedSize(400, 300)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        form_layout = QVBoxLayout()
        layout.addLayout(form_layout)

        self.countries = ["United States", "Canada", "United Kingdom", "France", "Germany", "China", "Chad"]

        self.sex_label = QLabel("Sex:")
        form_layout.addWidget(self.sex_label)
        self.sex_dropdown = QComboBox()
        self.sex_dropdown.addItems(["male", "female"])
        form_layout.addWidget(self.sex_dropdown)

        self.country_label = QLabel("Country:")
        form_layout.addWidget(self.country_label)
        self.country_dropdown = QComboBox()
        self.country_dropdown.addItems(self.countries)
        form_layout.addWidget(self.country_dropdown)

        self.dob_label = QLabel("Date of Birth (YYYY-MM-DD):")
        form_layout.addWidget(self.dob_label)
        self.dob_entry = QLineEdit()
        form_layout.addWidget(self.dob_entry)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_button)

        self.countdown_label = QLabel("")
        font = QFont("Helvetica", 10)  # Decreased font size
        self.countdown_label.setFont(font)
        layout.addWidget(self.countdown_label)

        self.full_screen = False
        self.setWindowState(Qt.WindowMaximized)  # Start in maximized window

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if not self.full_screen:
            self.showFullScreen()
            self.full_screen = True
        else:
            self.showNormal()
            self.full_screen = False

    def calculate(self):
        sex = self.sex_dropdown.currentText()
        country = self.country_dropdown.currentText()
        dob = self.dob_entry.text()

        try:
            dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError as e:
            self.countdown_label.setText("Invalid date format. Please use YYYY-MM-DD.")
            return

        try:
            api_url = f"https://d6wn6bmjj722w.population.io:443/1.0/life-expectancy/total/{sex}/{country}/{dob}/?format=json"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for 4XX or 5XX status codes

            data = response.json()
            life_expectancy = data['total_life_expectancy']

            today = datetime.date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            years_left = life_expectancy - age

            countdown_text = self.get_formatted_countdown(years_left)
            self.countdown_label.setText(f"Countdown:\n{countdown_text}")

            self.update_countdown(years_left)
        except requests.RequestException as e:
            self.countdown_label.setText("Error fetching data. Please check your connection.")
        except KeyError:
            self.countdown_label.setText("Data format error. Please try again later.")


    def update_countdown(self, years_left):
        if years_left > 0:
            years_left -= 1 / (365.25 * 24 * 60 * 60)
            countdown_text = self.get_formatted_countdown(years_left)
            self.countdown_label.setText(f"Countdown:\n{countdown_text}")
            self.update_label_color(years_left)

            QTimer.singleShot(1000, lambda: self.update_countdown(years_left))
        else:
            self.countdown_label.setText("Time's up!")
            self.countdown_label.setStyleSheet("color: red;")

    def get_formatted_countdown(self, years):
        seconds_in_year = 365.25 * 24 * 60 * 60
        years_remaining = int(years)
        months_remaining = int((years - years_remaining) * 12)
        days_remaining = int((years * 365.25) % 365.25)
        hours_remaining = int((years * seconds_in_year) % (24 * 60 * 60)) // 3600
        minutes_remaining = int((years * seconds_in_year) % (60 * 60)) // 60
        seconds_remaining = int((years * seconds_in_year) % 60)

        countdown = f"{years_remaining} years\n{months_remaining} months\n{days_remaining} days\n{hours_remaining} hours\n{minutes_remaining} minutes\n{seconds_remaining} seconds"

        return countdown

    def update_label_color(self, years_left):
        if years_left > 10:
            self.countdown_label.setStyleSheet("color: green;")
        elif years_left > 5:
            self.countdown_label.setStyleSheet("color: yellow;")
        elif years_left > 1:
            self.countdown_label.setStyleSheet("color: orange;")
        else:
            self.countdown_label.setStyleSheet("color: red;")


def main():
    app = QApplication(sys.argv)
    window = DeathCountdownApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()