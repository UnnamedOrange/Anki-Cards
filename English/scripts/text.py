import requests
from bs4 import BeautifulSoup


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

    eng_phone = extract_original(soup.find_all("div", class_="per-phone")[0])
    ame_phone = extract_original(soup.find_all("div", class_="per-phone")[1])
    return f"英 {eng_phone} 美 {ame_phone}"


def extract_chinese(html: str) -> str:
    """从 HTML 页面中提取中文释义。"""
    soup = BeautifulSoup(html, "html.parser")

    # 按词性分类的中文释义。
    chinese_meanings = soup.find_all("li", class_="word-exp")

    # 遍历每个词性。
    ret_list = []
    for meaning in chinese_meanings:
        pos = meaning.find("span", class_="pos")
        # 跳过人名。
        if pos is None:
            continue
        pos = pos.text.strip()
        trans = meaning.find("span", class_="trans").text.strip()

        my_class_map = {
            "n.": "pos_n",
            "v.": "pos_v",
            "vi.": "pos_v",
            "vt.": "pos_v",
            "adj.": "pos_a",
        }
        my_class = my_class_map.get(pos, "pos_r")
        ret_list.append(f'<a class="{my_class}">{pos}</a>{trans}')

    return "<br>".join(ret_list)


def make_line(word: str) -> str:
    """将单词转换为最终的行。"""
    html = fetch_html(word)
    phonogram = extract_phonogram(html)
    chinese = extract_chinese(html)
    return f"{word}\t{phonogram}\t{chinese}"


def make_all_lines(words: list) -> str:
    """将单词列表转换为可导入 Anki 的纯文本。"""
    ret = ""
    ret += "# 由 UnnamedOrange 的制卡工具生成。\n"
    ret += "# (1)英语单词\t(2)英美音标\t(3)中文释义\n"

    success = 0
    for word in words:
        try:
            ret += make_line(word) + "\n"
            success += 1
        except Exception as e:
            print(f"制卡 {word} 时出错：{e}")

    print(f"成功制卡 {success} 张，失败 {len(words) - success} 张。")

    return ret


def main():
    print("请输入单词，一行一个，以空行结束：")
    words = []
    while True:
        word = input()
        if word == "":
            break
        words.append(word)

    with open("Anki.txt", "w", encoding="utf-8") as f:
        f.write(make_all_lines(words))


if __name__ == "__main__":
    main()
