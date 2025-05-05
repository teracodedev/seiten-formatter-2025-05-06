"""
長久寺ホームページ上にある浄土真宗聖典からタグ・特殊文字を取り除いてプレーンなテキストにする。
"""

__author__ = "前田至法 <shiho.maeda.teracode@gmail.com>"
__status__ = "development"
__version__ = "0.1.1"
__date__ = "6 May 2025"

import re
import yaml
import requests
import os
from bs4 import BeautifulSoup

# スクリプトのディレクトリパスを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_settings(file_path):
    """
    設定ファイルをロードする関数
    :param file_path: 設定ファイルのパス
    :return: 設定値の辞書
    """
    try:
        with open(file_path, "r") as file:
            settings = yaml.safe_load(file)
        return settings
    except IOError as e:
        print(f"Error loading settings file: {e}")
        return None

def fetch_html(url):
    """
    指定されたURLまたはローカルファイルからHTMLを取得する関数
    :param url: 取得対象のURLまたはファイルパス
    :return: 取得したHTMLのテキスト
    """
    try:
        print(f"HTMLを読み込んでいます: {url}")
        if url.startswith('file://'):
            file_path = url[7:]  # 'file://' を除去
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"エラー: HTTPステータスコード {response.status_code}")
                return None
            response.encoding = response.apparent_encoding
            return response.text
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {url}")
        return None
    except IOError as e:
        print(f"エラー: ファイル読み込みエラー - {str(e)}")
        return None
    except requests.exceptions.Timeout:
        print("エラー: サーバーからの応答がタイムアウトしました")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"エラー: 接続エラーが発生しました - {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"エラー: リクエスト中にエラーが発生しました - {str(e)}")
        return None

def remove_tags(html_text):
    """
    HTMLテキストからrtタグとsupタグを削除する関数
    :param html_text: HTMLテキスト
    :return: タグ削除後のHTMLテキスト
    """
    soup = BeautifulSoup(html_text, "lxml")
    for element in soup.find_all(["rt", "sup"]):
        element.decompose()
    return soup

def extract_paragraphs(soup):
    """
    HTMLから段落を抽出し、改行を挿入して連結したテキストを返す関数
    :param soup: BeautifulSoupオブジェクト
    :return: 段落を連結したテキスト
    """
    output_text = ""
    paragraphs = soup.find_all("p")
    for paragraph in paragraphs:
        output_text += paragraph.text + "\n\n"
    return output_text

def remove_special_chars(text):
    """
    テキストから不要な特殊文字を削除し、一部の文字を置換する関数
    :param text: 処理対象のテキスト
    :return: 特殊文字削除後のテキスト
    """
    char_mapping = {
        "一": "", "　": "", "*": "", "^": "", "¬": "", "¼": "", "↓": "", "↑": "", "ª": "", "◎": "",
        "▲": "", "▼": "", "◆": "", "º": "", "↧": "", "↥": "", "↠": "", "↞": "", "↡": "", "↢": "",
        "↣": "", "↦": "", "▽": "", "△": "", "ˆ": "", "ˇ": "", "｡": "。", "､": "、", " ": ""
    }
    table = str.maketrans(char_mapping)
    text = text.translate(table)
    return text

def remove_numeric_patterns(text):
    """
    テキストから特定の数字パターンを削除する関数
    :param text: 処理対象のテキスト
    :return: 数字パターン削除後のテキスト
    """
    patterns = [
        r"\d{4}!\)", r"\)\d{4}", r"\d{4}\)", r"\d{4}"
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text)
    return text

def adjust_line_breaks(text):
    """
    テキストの改行位置を調整する関数
    :param text: 処理対象のテキスト
    :return: 改行調整後のテキスト
    """
    text = re.sub(r"。　", "。\n　", text)
    text = re.sub(r"【", "\n【", text)
    return text

def save_text_to_file(text, file_path):
    """
    テキストをファイルに保存する関数
    :param text: 保存するテキスト
    :param file_path: 保存先のファイルパス
    """
    try:
        with open(file_path, "w", encoding="UTF-8") as file:
            file.write(text)
        print(f"Text saved to {file_path}")
    except IOError as e:
        print(f"Error saving text to file: {e}")

def main():
    settings_file = os.path.join(SCRIPT_DIR, "settings.yaml")
    settings = load_settings(settings_file)

    if settings:
        url = settings["url"]
        output_file = settings["output_file"]

        html_text = fetch_html(url)
        if html_text:
            soup = remove_tags(html_text)
            text = extract_paragraphs(soup)
            text = remove_special_chars(text)
            text = remove_numeric_patterns(text)
            text = adjust_line_breaks(text)
            save_text_to_file(text, output_file)

if __name__ == "__main__":
    main()