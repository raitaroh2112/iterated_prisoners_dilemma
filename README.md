# iterated_prisoners_dilemma

こちらは、oTreeを用いた2人でのオンライン繰り返し囚人のジレンマを実施するためのプログラムです。

## 目次

- [概要](#概要)
- [始め方](#始め方)
- [インストール](#インストール)
- [使用方法](#使用方法)

## 概要

- [oTree](https://github.com/oTree-org/oTree)はDjangoをベースにした経済実験や心理学実験をPCを用いて実施するためのゲーム作成用オープンソースプラットフォームです。
本プログラムはこちらのサンプルプログラムをベースに、各ページに制限時間をつけて、実験用にカスタマイズしたものになります。

## 始め方

このセクションでは、プロジェクトの要件と開発環境の設定方法について説明します。

### 前提条件

- Python 3.9.6 以上

## インストール

1. リポジトリをクローンまたはダウンロードします。

2. 必要なライブラリやモジュールをインストールします。
```bash
pip install -r requirements.txt
```

## 使用方法（ローカル）

1. `iterated_prisoners_dilemma`のディレクトリに入り以下コマンドを打ちます。
```bash
otree prodserver 8000
```
2.　Google Chromeで以下のにアクセスします。

- [http://localhost:8000/](http://localhost:8000/)

同一ネットワーク内であれば、他のPCからもアクセス可能です。（localhostをホストのIPアドレスに変更してください）

3.　`config.py`でパラメータを設定してください。

4.　ゲームではOption I （C）かOption J (D)のどちらかをクリックしてください。一度押したら、そのラウンドでは選び直しができない設定になっています。

5.　csvファイルの内容は以下です。
| カラム名 | 内容 |
| ---- | ---- |
| `session` | プレイヤーが所属していたセッション |
| `player` | セッション内での個人を識別する（1か2） |
| `round` | 何回目のゲームか |
| `cooperate` | 0:未入力　1:Option I 2:Option J |
| `payoff` | 得点 |
| `start_choice_time` | Decisionページの開始時間 |
| `end_choice_time` | Decisionページの終了時間 |


## 主要な機能
- 2人繰り返し囚人のジレンマゲームの実施
- 結果をcsv形式で出力

## ディレクトリ構造
- `_rooms/`: テンプレートディレクトリ
- `_static/`: テンプレートディレクトリ
- `_templates/`: テンプレートディレクトリ

  
- `iterated_prisoner/`: ゲームのファイルを含むディレクトリ
  - `__init__.py`: ゲームを動かすためのプログラム
  - `file_write.py`: ゲームの結果をcsv形式で出力するためのプログラム
  - `config.py`:　ゲーム設定を書き込むファイル
  - `setting.py`:　oTree用の設定のファイル
  - 　`instruction.html`: ゲームの指示を書くためのhtmlファイル
  - 　`Introduction.html`: 最初のページのためのhtmlファイル
  - 　`Decision.html`: ゲームの選択を考えるページのhtmlファイル
  - 　`Result.html`: ゲームの結果を表示するページのhtmlファイル

- `output/`: 出力ファイルを格納するディレクトリ


## 参照先

Chen, Daniel L., Martin Schonger, and Chris Wickens.
2016. "oTree - An open-source platform for laboratory, online, and field experiments."
Journal of Behavioral and Experimental Finance, vol 9: 88-97.

[https://otree.readthedocs.io/en/latest/](https://otree.readthedocs.io/en/latest/)

[https://yshimod.github.io/otree5-seminar/](https://yshimod.github.io/otree5-seminar/)

