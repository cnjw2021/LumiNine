#アプリケーションのセットアップを '編集可能なパッケージ' としてインストールします。
#この方法は、PYTHONPATHを手動で設定する必要なく、
#Pythonが core、apps などのすべてのモジュールの正確な位置を自動的に見つける最も堅牢で標準的な方法です。
from setuptools import setup, find_packages

setup(
    name="ninestarki-backend",
    version="0.1.0",
    packages=find_packages(),
)
