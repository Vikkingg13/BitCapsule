import sys
import os
import zipfile
import requests
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QFileDialog, QMessageBox, QCalendarWidget,
                            QHBoxLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
import make_timelock_capsule as capsule

class TimeLockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BitCapsule")
        self.setMinimumSize(600, 800)
        
        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel("BitCapsule")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFFFFF; margin-bottom: 15px; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # Описание
        description = QLabel("Create a time-locked Bitcoin address that can only be spent after a specific date.")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #B0B0B0; font-size: 15px; line-height: 1.5; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # Выбор даты
        date_label = QLabel("Unlock Date:")
        date_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        date_label.setStyleSheet("color: #FFFFFF; margin-top: 25px; margin-bottom: 8px;")
        layout.addWidget(date_label)
        
        # Создаем фрейм для календаря
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Создаем календарь
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QCalendarWidget QToolButton {
                color: #FFFFFF;
                background-color: transparent;
                border: none;
                padding: 5px;
                font-size: 14px;
            }
            QCalendarWidget QMenu {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QCalendarWidget QSpinBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 3px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #2D2D2D;
                color: #FFFFFF;
                selection-background-color: #2196F3;
                selection-color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #555555;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2D2D2D;
            }
        """)
        
        # Устанавливаем начальную дату (1 год от текущей)
        self.calendar.setSelectedDate(QDate.currentDate().addYears(1))
        self.calendar.clicked.connect(self.update_time_label)
        
        # Устанавливаем минимальный размер для календаря
        self.calendar.setMinimumSize(500, 350)
        calendar_layout.addWidget(self.calendar)
        
        layout.addWidget(calendar_frame)
        
        # Метка с временем до разблокировки
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #B0B0B0; font-size: 14px; margin-top: 10px;")
        self.update_time_label()  # Инициализируем метку
        layout.addWidget(self.time_label)
        
        # Кнопка генерации
        self.generate_btn = QPushButton("Generate Time Capsule")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 14px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_capsule)
        layout.addWidget(self.generate_btn)
        
        # Добавляем растягивающийся спейсер
        layout.addStretch()
        
        # Устанавливаем стиль для всего окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)

    def update_time_label(self):
        """Обновляет метку с примерным временем до разблокировки."""
        unlock_date = self.calendar.selectedDate().toPyDate()
        current_date = date.today()
        
        # Вычисляем разницу в годах, месяцах и днях
        delta = relativedelta(unlock_date, current_date)
        
        # Формируем строку с временем
        time_parts = []
        if delta.years > 0:
            time_parts.append(f"{delta.years} {'year' if delta.years == 1 else 'years'}")
        if delta.months > 0:
            time_parts.append(f"{delta.months} {'month' if delta.months == 1 else 'months'}")
        if delta.days > 0:
            time_parts.append(f"{delta.days} {'day' if delta.days == 1 else 'days'}")
        
        if time_parts:
            time_str = " ".join(time_parts)
            self.time_label.setText(f"Approximate unlock time: {time_str}")
        else:
            self.time_label.setText("Please select a future date")

    def get_current_block_height(self):
        """Получает текущий номер блока Bitcoin через API."""
        try:
            response = requests.get('https://blockchain.info/q/getblockcount')
            if response.status_code == 200:
                return int(response.text)
            else:
                raise Exception(f"API request failed with status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to get current block height: {str(e)}")

    def calculate_target_block(self, target_date):
        """Вычисляет целевой номер блока на основе даты."""
        try:
            current_block = self.get_current_block_height()
            current_date = datetime.now().date()
            days_difference = (target_date - current_date).days
            
            # Среднее количество блоков в день (144 блока = 24 часа * 6 блоков в час)
            blocks_per_day = 144
            target_block = current_block + (days_difference * blocks_per_day)
            
            return target_block
        except Exception as e:
            raise Exception(f"Failed to calculate target block: {str(e)}")

    def generate_capsule(self):
        try:
            # Получаем выбранную дату
            unlock_date = self.calendar.selectedDate().toPyDate()
            
            # Вычисляем целевой номер блока
            target_block = self.calculate_target_block(unlock_date)
            
            # Создаем временную директорию для файлов
            temp_dir = "temp_capsule"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Генерируем капсулу
            capsule.unlock_block = target_block
            capsule.output_dir = temp_dir
            capsule.main()
            
            # Создаем ZIP архив
            zip_path = QFileDialog.getSaveFileName(
                self,
                "Save Time Capsule",
                "bitcoin_time_capsule.zip",
                "Zip files (*.zip)"
            )[0]
            
            if zip_path:
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.basename(file_path)
                            zipf.write(file_path, arcname)
                
                # Очищаем временную директорию
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
                
                # Создаем и стилизуем окно сообщения
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Success")
                msg_box.setText("Time capsule has been generated successfully!")
                msg_box.setInformativeText(
                    "The ZIP file contains:\n"
                    "- QR code of the P2SH address (send Bitcoin here)\n"
                    "- QR code of the private key (keep this safe!)\n"
                    "- Text file with all information\n\n"
                    "Keep your private key secure and never share it with anyone!"
                )
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2D2D2D;
                    }
                    QMessageBox QLabel {
                        color: #FFFFFF;
                        font-size: 15px;
                        line-height: 1.5;
                    }
                    QMessageBox QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-size: 14px;
                        min-width: 100px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #1976D2;
                    }
                    QMessageBox QPushButton:pressed {
                        background-color: #0D47A1;
                    }
                """)
                msg_box.exec()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while generating the time capsule:\n{str(e)}"
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeLockApp()
    window.show()
    sys.exit(app.exec()) 