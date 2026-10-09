# 音声文字起こしスクリプト

`process_meeting_audio.py`は、全文文字起こし、話者分離、人物マスターとの確認付き紐付けを一括実行します。元音声と人物マスターは変更しません。

## ローカル環境

既存のPython環境に必要なバージョンが揃っていれば再利用し、不足時だけ`meeting-minutes/`直下へローカル環境を構築します。

```powershell
cd meeting-minutes
.\setup.ps1
.\run.ps1 -Audio "input\meeting_voice.mp3"
```

新規構築時は`.venv/`へ依存関係を導入し、Whisperと話者特徴ONNXモデルは`.cache/`へ保存します。アカウントやアクセストークンは不要です。

`setup.ps1`は既存のPythonコンポーネントを確認します。利用可能ならそのまま使用し、不足時だけ最大約2GBの容量警告とインストール確認を表示します。`run.ps1`は依存関係または公開ONNXモデルが不足する場合だけ`setup.ps1`を呼びます。

## 入力

1. 元音声
2. `work/master/person.csv`
3. 中間ファイルを保存する`work/`

## Pythonを直接実行する場合

```powershell
.venv\Scripts\python.exe scripts\process_meeting_audio.py `
  input\meeting_voice.mp3 `
  work\master\person.csv `
  work
```

対話可能なターミナルでは、検出した話者IDごとに主要発言と人物マスターの候補を表示します。人物IDを入力した場合だけ人物へ紐付け、空欄なら仮話者IDを維持します。

既存の全文文字起こしは自動再利用しません。同じ音声のものと確認済みの場合だけ`--reuse-transcript`を指定し、確認できない場合は`--force`で作り直します。

人物を確定せず、話者IDと主要発言だけを作成する場合：

```powershell
.venv\Scripts\python.exe scripts\process_meeting_audio.py `
  input\meeting_voice.mp3 `
  work\master\person.csv `
  work `
  --non-interactive
```

## 生成ファイル

- `work/transcript_raw.csv`：全文文字起こし
- `work/speaker_candidates.csv`：話者ID、主要発言、人物候補
- `work/transcript.csv`：人物紐付け結果を反映した全文文字起こし

最終の`header.csv`、`minutes.csv`、`participants.csv`、`Agenda.csv`は、話者確認と要約後に別工程で作成します。

## 最終出力

4 CSVが揃った後、次のコマンドでCSVの列を検証し、テンプレートを内容変更せず`output/meeting.xlsx`へコピーします。

```powershell
.venv\Scripts\python.exe scripts\finalize_meeting.py `
  output `
  --force
```

この工程はPython標準ライブラリだけを使用します。Excelファイルの生成・内部編集・接続先変更は行いません。

## 注意事項

- 初回は`setup.ps1`が`requirements.txt`の依存関係を`.venv/`へ導入します。
- 話者分類は公開3D-Speaker ONNXモデルを使用し、人物名は自動特定しません。
- 声だけから人物を確定しません。
- 人物マスターはUTF-8またはCP932で読み込めます。
- 既存ファイルを上書きする場合だけ`--force`を指定します。
