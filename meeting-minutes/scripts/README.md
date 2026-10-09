# 会議議事録スクリプト

`process_meeting_audio.py`は全文文字起こし、話者分離、確認付きの人物紐付けを行います。

```powershell
.venv\Scripts\python.exe scripts\process_meeting_audio.py `
  input\meeting_voice.mp3 `
  work\master\person.csv `
  work
```

生成する中間ファイル：

- `work/transcript_raw.csv`
- `work/speaker_candidates.csv`
- `work/transcript.csv`

確認と要約後の4 CSVは`work/final/`へ保存します。

完成Excelは次のコマンドで作成します。

```powershell
.venv\Scripts\python.exe scripts\finalize_meeting.py work\final --force
```

`finalize_meeting.py`は4 CSVを検証し、`template/meeting.xlsx`へ値を直接書き込み、`output/meeting.xlsx`を作成します。CSVを`output/`へコピーせず、Excelの外部接続や更新操作も使用しません。
