import sys
import requests
import pydub
import pydub.playback
from bs4 import BeautifulSoup
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_form import Ui_MainWindow


def fetch_html(word: str) -> str:
    """获取单词的整个 HTML 页面。"""
    url = "https://www.youdao.com/result?word=" + word + "&lang=en"
    response = requests.get(url)
    html = response.text
    return html


def extract_phonogram(html: str) -> str:
    """从 HTML 页面中提取音标。"""
    soup = BeautifulSoup(html, "html.parser")

    def extract_original(phone_div):
        # 提取原式的音标字符串。
        phone = phone_div.find("span", class_="phonetic").text.strip(" /")

        # 将音标的斜线替换为中括号。
        return f"[{phone.replace('/', '[').replace(' ', ']').replace('[', ' [')}]"

    phone_divs = soup.find_all("div", class_="per-phone")
    eng_phone = extract_original(phone_divs[0])
    ame_phone = extract_original(
        phone_divs[1] if len(phone_divs) > 1 else phone_divs[0]
    )
    return f"英 {eng_phone} 美 {ame_phone}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建UI对象
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.source_radio_buttons = [
            self.ui.radio_1,
            self.ui.radio_2,
            self.ui.radio_3,
            self.ui.radio_4,
        ]
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.audio_cache = None

        # 连接信号和槽
        self.ui.button_paste.clicked.connect(self.on_button_paste_clicked)
        self.ui.button_confirm.clicked.connect(self.on_button_confirm_clicked)
        self.ui.radio_1.clicked.connect(self.on_radio_clicked)
        self.ui.radio_2.clicked.connect(self.on_radio_clicked)
        self.ui.radio_3.clicked.connect(self.on_radio_clicked)
        self.ui.radio_4.clicked.connect(self.on_radio_clicked)
        self.ui.list_words.currentRowChanged.connect(
            self.on_list_words_current_row_changed
        )

    def on_button_paste_clicked(self):
        self.ui.button_paste.setEnabled(False)

        text = QApplication.clipboard().text()
        words = text.strip("\n").split("\n")
        self.ui.list_words.addItems(words)
        self.ui.list_words.setCurrentRow(0)

        # 默认使用有道美音。
        if not self.get_current_source():
            self.ui.radio_2.click()

    def on_button_confirm_clicked(self):
        current_source = self.get_current_source()
        item = self.ui.list_words.currentItem()
        if item is None:
            return
        word = item.text()
        self.thread_pool.submit(self.save, word, current_source)
        self.ui.list_words.takeItem(self.ui.list_words.currentRow())

    def on_radio_clicked(self):
        item = self.ui.list_words.currentItem()
        if item is None:
            return
        word = item.text()
        source = self.get_current_source()
        self.thread_pool.submit(self.play, word, source)

    def on_list_words_current_row_changed(self, current_row):
        word = self.ui.list_words.item(current_row).text()
        self.ui.label.setText(extract_phonogram(fetch_html(word)))

        current_source = self.get_current_source()
        if not current_source:
            return
        self.source_radio_buttons[current_source - 1].click()

    def get_current_source(self):
        for i, radio in enumerate(self.source_radio_buttons):
            if radio.isChecked():
                return i + 1
        return 0

    def download(self, word, source):
        url = None
        match source:
            case 1:
                url = f"https://dict.youdao.com/dictvoice?audio={word}&type=1"
            case 2:
                url = f"https://dict.youdao.com/dictvoice?audio={word}&type=2"
            case 3:
                url = f"https://ssl.gstatic.com/dictionary/static/sounds/oxford/{word}--_gb_1.mp3"
            case 4:
                url = f"https://ssl.gstatic.com/dictionary/static/sounds/oxford/{word}--_us_1.mp3"
        return requests.get(url).content

    def play(self, word, source):
        try:
            audio = self.download(word, source)
            file = BytesIO(audio)
            segment = pydub.AudioSegment.from_mp3(file)
            pydub.playback.play(segment)
        except Exception as e:
            print(e)

    def save(self, word, source):
        try:
            audio = self.download(word, source)
            with open(f"{word}.mp3", "wb") as f:
                f.write(audio)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
