# 文学紙芝居・最小動画サンプル

貼り付けたストーリーから、静止画像、VOICEVOX音声、字幕による約5分の紙芝居動画を作る最小サンプルです。

## PolicyとSkill

このサンプルでは、AIエージェントへの指示を「Policy」と「Skill」に明示的に分けています。

- [POLICY.md](POLICY.md)：制作方針、判断基準、制約の正本
- [SKILL.md](SKILL.md)：Policyに従い、使用するファイル、プログラム、処理順を定める実行手順の正本

```text
POLICY.md
  ↓ 方針・判断
SKILL.md
  ↓ 実行手順
scripts / Remotion
  ↓ 処理
project/
  ↓
MP4
```

READMEは全体像と利用者向けの入口です。制作判断は`POLICY.md`、エージェントの具体的な処理順は`SKILL.md`を参照してください。

## 必要なプログラム

- Python 3.10以上
- Node.jsとnpm
- Remotion（`remotion/`でnpmから導入）
- VOICEVOX Engine（利用者が起動）

制作前に確認します。

```powershell
python scripts/check_environment.py
```

Remotionがない場合だけ、初回導入用の絶対パスとコマンドが表示されます。導入後は再インストールを促しません。不足する環境がある場合、制作は開始しません。また、このサンプルは外部ソフトを自動インストールしません。

## フォルダ

```text
literary-kamishibai/
├─ POLICY.md
├─ SKILL.md
├─ README.md
├─ scripts/                 共通Pythonプログラム
├─ remotion/                全シナリオ共通のRemotion環境
├─ project/
│  └─ 002/                  シナリオ単位のフォルダ
│     ├─ dialogue.json
│     ├─ voicevox_characters.csv
│     ├─ image_order/       AI向けの画像指示書
│     ├─ images/            生成画像
│     ├─ audio/             VOICEVOX音声
│     ├─ render_data.json   自動生成される中間データ
│     └─ output/            完成MP4
└─ 前のファイル/            比較用の旧版（変更しない）
```

`dialogue.json`、`voicevox_characters.csv`、`image_order/`、`images/`が入力です。`audio/*.wav`、`render_data.json`、`output/video.mp4`は処理による生成物です。`render_data.json`は手作業で編集しません。

## 入力例

`dialogue.json`は記載順が再生順です。

```json
[
  {
    "line_id": "001",
    "scene_id": "scene_001",
    "image": "images/scene_001.png",
    "character": "語り手",
    "text": "物語が始まりました。"
  }
]
```

`line_id`は重複させず、先頭のゼロを保つため文字列にします。音声は`audio/001.wav`のように保存されます。同じ場面で同じ画像を使う場合は、同じ`scene_id`と`image`を指定します。

`voicevox_characters.csv`は3列だけです。

```csv
シナリオ登場キャラ名,VoiceVOXキャラ名,VoiceVOXキャラID
語り手,四国めたん,2
```

## 利用者向け実行例

VOICEVOX Engineを起動し、音声を作ります。

```powershell
python scripts/create_voice.py project/002
```

素材を検査し、すべて揃っている場合だけ共通Remotionへ配置します。

```powershell
python scripts/prepare_remotion.py project/002
```

Remotionが未導入の場合だけ、`check_environment.py`が表示した共通`remotion/`フォルダで`npm install`を実行します。その後、同フォルダで確認またはレンダリングします。

```powershell
npm run studio
npm run render -- ../project/002/output/video.mp4
```

表示は静止画像、話者名、字幕のみです。各セリフの後に固定1秒を空け、最後のセリフ後には追加しません。詳しい処理順は`SKILL.md`を参照してください。
