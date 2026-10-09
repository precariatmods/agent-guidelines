# Processing：会議議事録

## 処理順序

1. 音声を全文文字起こしし、`work/transcript_raw.csv`へ保存する。
2. ヘッダー候補を提示し、利用者の確認を得る。
3. 話者を分離し、`speaker_001`形式の話者IDを付ける。
4. 話者IDごとの主要発言を`work/speaker_candidates.csv`へ保存する。
5. `work/master/person.csv`の人物候補を一人ずつ利用者へ提示する。
6. 利用者が確認した話者IDと人物IDだけを紐付ける。
7. 紐付け結果を`work/transcript.csv`へ反映する。
8. メンバー確定後、全文文字起こしを要約する。
9. `work/final/`へ`header.csv`、`minutes.csv`、`participants.csv`、`Agenda.csv`を保存する。
10. 4 CSVを検証し、`template/meeting.xlsx`へ値を直接書き込む。
11. `output/meeting.xlsx`だけを最終成果物として保存する。

全文文字起こしと4 CSVは内部データです。Excelは外部接続や数式へ依存しないため、開いた時点で完成内容を表示します。
