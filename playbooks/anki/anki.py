import random

import requests
import streamlit
import yaml

# プリセットのYAMLファイルURL
PRESET_URLS = {
    "My中文": "https://www.dropbox.com/scl/fi/njz18tevsn89duq3i5vg1/zhonwen.yaml?rlkey=4tdft8dfgqfjw30ziilowf1bf&streamlit=240f39pg&dl=1",
    "カスタムURL": "",
}


@streamlit.cache_data(ttl=3600)
def load_deck(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return yaml.safe_load(response.text)
    except requests.exceptions.RequestException as e:
        streamlit.error(f"YAMLファイルの読み込みに失敗しました: {e}")
        return None


@streamlit.cache_data
def get_keys(data, randomize: bool):
    keys = list(data.keys())
    if randomize:
        random.shuffle(keys)
    return keys


streamlit.title(":star: anki")

# プリセットURLの選択
yaml_key = streamlit.sidebar.selectbox("デッキを選択", list(PRESET_URLS.keys()))
if yaml_key in PRESET_URLS and PRESET_URLS[yaml_key]:
    yaml_url = PRESET_URLS[yaml_key]
else:
    yaml_url = streamlit.sidebar.text_input("またはカスタムURLを入力", "")

if not yaml_url:
    streamlit.warning("プリセットから選択または URL を入力してください")
    streamlit.stop()

if streamlit.sidebar.button("Super Reload"):
    streamlit.cache_data.clear()

# YAMLファイルの読み込み
data = load_deck(yaml_url)

if data:
    streamlit.success(f"{len(data)} 単語の読み込みに成功しました！")

    # YAMLデータの単語帳を作成
    randomize = streamlit.toggle("Randomize", value=True)
    rev = streamlit.toggle("Reverse order", value=False)

    keys = get_keys(data, randomize)
    index = streamlit.number_input(
        "page", value=0, min_value=0, max_value=len(keys) - 1
    )
    key = keys[index]
    if not rev:
        with streamlit.expander(key):
            streamlit.markdown(data[key])
    else:
        with streamlit.expander(data[key]):
            streamlit.markdown(key)
