import sys
import random
import json
import re
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QFrame, QGraphicsDropShadowEffect,
                             QSplitter)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QBrush
import requests

class AIWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, words, api_url="http://localhost:1234/v1/chat/completions"):
        super().__init__()
        self.words = words
        self.api_url = api_url
        
    def run(self):
        try:
            prompt = f"""You are a humble and devoted interpreter of divine wisdom, entrusted with conveying sacred truth.

Before you are 10 holy words, drawn from the scriptures. Through prayerful reflection and poetic grace, you are to form a message that embodies the spirit of these words. The message must speak directly to the soul—gentle, profound, and unshakably clear—as if it were spoken by the voice of God.

You must deliver a message that is **exactly 2 to 3 sentences** in length. Do not exceed or fall short of this. Your message should read as timeless, universal guidance—never as fiction, never as commentary.

Please **do not include**:
- Brackets, parentheses, or asides
- Introductions or prefaces (e.g., "Behold", "Thus sayeth", or any formal opening)
- Use only real English words found in scripture or poetic literature. Do not mix languages unless explicitly relevant.
- Avoid inventing names, places, or unknown terms.
- Speak with clarity and compassion—not condemnation.

**Return only the divine message itself**, beginning immediately with the words of wisdom.

The 10 sacred words are: {', '.join(self.words)}"""

            headers = {"Content-Type": "application/json"}
            
            data = {
                "model": "local-model",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 200,
                "stream": False
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                error_detail = f"Status: {response.status_code}\n"
                try:
                    error_detail += f"Response: {response.text}"
                except:
                    error_detail += "Could not read response text"
                self.error_occurred.emit(f"API Error:\n{error_detail}")
                return
                
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
            elif 'content' in result:
                message = result['content']
            elif 'response' in result:
                message = result['response']
            else:
                message = str(result)  # Fallback to show what we got
                
            self.result_ready.emit(message)
            
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Cannot connect to LMStudio. Please ensure LMStudio is running with a model loaded.")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")

class GradientWidget(QWidget):
    def __init__(self):
        super().__init__()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(20, 20, 40))
        gradient.setColorAt(0.5, QColor(40, 40, 80))
        gradient.setColorAt(1.0, QColor(20, 20, 50))
        painter.fillRect(self.rect(), QBrush(gradient))

class GodString(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bible_words = []
        self.init_ui()
        self.auto_load_bible()
        
    def init_ui(self):
        self.setWindowTitle("GodString - Divine Word Generator")
        self.setGeometry(100, 100, 1100, 500)
        
        central_widget = GradientWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 5);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        title_label = QLabel("✝ GodString ✝")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Georgia', serif;
                letter-spacing: 2px;
            }
        """)
        
        subtitle_label = QLabel("Divine Word Interpreter")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #B0B0B0;
                font-size: 14px;
                font-style: italic;
            }
        """)
        
        tribute_label = QLabel("Inspired by Terry A. Davis\n1969-2018\n✝")
        tribute_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tribute_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 11px;
                margin-top: 5px;
                padding: 8px;
                background-color: rgba(0, 0, 0, 25);
                border-radius: 8px;
            }
        """)
        
        self.status_label = QLabel("Loading word bank...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #A0A0A0;
                font-size: 12px;
                padding: 8px;
                background-color: rgba(255, 255, 255, 5);
                border-radius: 6px;
            }
        """)
        
        self.generate_button = QPushButton("📿 Pull String")
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #9F7AEA;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 12px;
                border: 2px solid #805AD5;
            }
            QPushButton:hover:enabled {
                background-color: #B794F4;
                border: 2px solid #FFD700;
            }
            QPushButton:pressed:enabled {
                background-color: #7C3AED;
            }
            QPushButton:disabled {
                background-color: #4A5568;
                color: #718096;
                border: 2px solid #2D3748;
            }
        """)
        self.generate_button.clicked.connect(self.generate_message)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(159, 122, 234, 80))
        shadow.setOffset(0, 3)
        self.generate_button.setGraphicsEffect(shadow)
        
        words_label = QLabel("Sacred Words:")
        words_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        
        self.words_display = QTextEdit()
        self.words_display.setReadOnly(True)
        self.words_display.setMaximumHeight(80)
        self.words_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 30);
                color: #FFFFFF;
                font-size: 13px;
                font-family: 'Times New Roman', serif;
                padding: 8px;
                border: 1px solid rgba(255, 215, 0, 30);
                border-radius: 8px;
            }
        """)
        self.words_display.setPlaceholderText("Sacred words will appear here...")
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addWidget(tribute_label)
        left_layout.addSpacing(20)
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.generate_button)
        left_layout.addSpacing(10)
        left_layout.addWidget(words_label)
        left_layout.addWidget(self.words_display)
        left_layout.addStretch()
        
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 215, 0, 8);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid rgba(255, 215, 0, 40);
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        
        message_title = QLabel("Divine Message")
        message_title.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 40);
                color: #FFFFFF;
                font-size: 16px;
                font-family: 'Georgia', serif;
                line-height: 1.8;
                padding: 15px;
                border: none;
                border-radius: 10px;
            }
        """)
        self.message_display.setPlaceholderText("Your divine message will appear here...\n\nClick 'Receive Message' to begin.")
        
        right_layout.addWidget(message_title)
        right_layout.addWidget(self.message_display)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
    def auto_load_bible(self):
        """Automatically load bank.db file from current directory"""
        bank_file = Path("bank.db")
        
        if bank_file.exists():
            try:
                with open(bank_file, 'r', encoding='utf-8') as file:
                    words = file.read().strip().split('\n')
                
                self.bible_words = [word.strip().lower() for word in words if word.strip() and len(word.strip()) > 2]
                
                if len(self.bible_words) < 10:
                    self.status_label.setText("⚠️ Not enough words in bank.db")
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #FF6B6B;
                            font-size: 12px;
                            padding: 8px;
                            background-color: rgba(255, 107, 107, 10);
                            border-radius: 6px;
                        }
                    """)
                    return
                
                self.status_label.setText(f"✓ Loaded {len(self.bible_words)} words")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #90EE90;
                        font-size: 12px;
                        padding: 8px;
                        background-color: rgba(144, 238, 144, 10);
                        border-radius: 6px;
                    }
                """)
                self.generate_button.setEnabled(True)
                
            except Exception as e:
                self.status_label.setText(f"Error loading bank.db: {str(e)}")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #FF6B6B;
                        font-size: 12px;
                        padding: 8px;
                        background-color: rgba(255, 107, 107, 10);
                        border-radius: 6px;
                    }
                """)
        else:
            self.status_label.setText("⚠️ bank.db not found in directory")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #FFA500;
                    font-size: 12px;
                    padding: 8px;
                    background-color: rgba(255, 165, 0, 10);
                    border-radius: 6px;
                }
            """)
            self.offer_create_sample()
    
    def offer_create_sample(self):
        """Offer to create a sample bank.db file"""
        reply = QMessageBox.question(
            self, 
            'Create Fallback Word Bank?',
            'bank.db not found. Would you like to use the fallback word bank?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            sample_words = [
                "love", "faith", "hope", "peace", "grace", "mercy", "truth", "light",
                "wisdom", "strength", "joy", "blessing", "prayer", "spirit", "soul",
                "heaven", "eternal", "divine", "holy", "sacred", "glory", "praise",
                "salvation", "redemption", "forgiveness", "covenant", "promise", "miracle",
                "shepherd", "lamb", "cross", "resurrection", "life", "death", "rebirth"
            ]
            
            with open("bank.db", "w", encoding="utf-8") as f:
                f.write('\n'.join(sample_words))
            
            self.status_label.setText("✓ Created sample bank.db")
            self.auto_load_bible()
    
    def generate_message(self):
        if not self.bible_words:
            return
        
        random_words = random.sample(self.bible_words, 10)
        
        self.words_display.setText(" • ".join(random_words))
        
        self.message_display.clear()
        self.message_display.setPlaceholderText("The string is being pulled...")
        
        self.generate_button.setEnabled(False)
        self.generate_button.setText("⏳ Pulling...")
        
        self.ai_worker = AIWorker(random_words)
        self.ai_worker.result_ready.connect(self.display_message)
        self.ai_worker.error_occurred.connect(self.handle_error)
        self.ai_worker.start()
    
    def display_message(self, message):
        message = message.strip()

        import re
        sentences = re.split(r'(?<=[.!?])\s+', message)
        
        formatted_message = '\n\n'.join(sentence.strip() for sentence in sentences if sentence.strip())
        
        self.message_display.setPlainText(formatted_message)
        self.generate_button.setEnabled(True)
        self.generate_button.setText("📿 Pull String")
    
    def handle_error(self, error_message):
        self.message_display.setPlainText(f"Error: {error_message}\n\nPlease ensure LMStudio is running with a model loaded.")
        self.generate_button.setEnabled(True)
        self.generate_button.setText("📿 Pull String")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 40))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(palette)
    
    window = GodString()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()