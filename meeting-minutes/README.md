# Meeting Minutes

会議音声から、利用者の確認を挟みながらExcel議事録を作成するサンプルです。

- `SKILL.md`：処理順序
- `POLICY.md`：AIの判断と利用者確認
- `SCHEMA.md`：CSVのデータ構造
- `Output.md`：保存先と完成条件

## 1. 準備

Windows、PowerShell、Python 3.11を使用します。

```powershell
.\setup.ps1
```

必要な環境がすでにあれば再利用します。不足している場合は、最大約2GBを使用する可能性を表示し、許可を得てから導入します。

会議音声を`input/`、人物候補を`work/master/person.csv`へ置きます。

## 2. 実行

```powershell
.\run.ps1 -Audio "input\meeting_voice.mp3"
```

画面の案内に従い、会議情報と各話者を確認します。確認後、議事録用データを整理してExcelを作成します。

```powershell
.venv\Scripts\python.exe scripts\finalize_meeting.py --force
```

## 3. 結果

完成品は`output/meeting.xlsx`です。CSVは内部作業用として`work/`に残り、`output/`には出力されません。

Excelには外部接続や表示用数式がないため、開くだけで完成内容を確認できます。
