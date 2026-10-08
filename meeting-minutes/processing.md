# Processing：会議議事録

## 処理順序

1. 音声を全文文字起こしし、`work/transcript_raw.csv`へ保存する。
2. ヘッダー候補を一覧で提示し、利用者の確認後に`header.csv`を作成する。
3. 話者を分離し、各話者へ`speaker_001`形式の話者IDを付ける。
4. 話者IDごとの主要発言を`work/speaker_candidates.csv`へ保存する。
5. `work/master/person.csv`の人物候補を一人ずつ利用者へ提示する。
6. 利用者が確認した話者IDと人物IDだけを紐付ける。
7. 紐付け結果を`work/transcript.csv`と`participants.csv`へ反映する。
8. メンバー確定後、全文文字起こしを要約し、`minutes.csv`と`Agenda.csv`を作成する。
9. 4 CSVの列名、列順、文字コード、改行を検証する。
10. 4種類のCSVを`output/`へ保存する。
11. `template/meeting.xlsx`を内容変更せず`output/meeting.xlsx`へコピーする。
12. `output/`に4 CSVと`meeting.xlsx`があることを確認して終了する。

## データの役割

- `transcript_raw.csv`：全文文字起こし。内容は要約しない。
- `speaker_candidates.csv`：話者ID、主要発言、人物候補、確認状態。
- `transcript.csv`：人物紐付け後の全文文字起こし。要約の根拠。
- `minutes.csv`：時系列の要約発言。
- `Agenda.csv`：議題単位の内容と決定事項。
- `participants.csv`：話者IDと確定人物の対応。
- `header.csv`：確定した会議情報。
- `meeting.xlsx`：`template/meeting.xlsx`の無変更コピー。Excel側の更新操作でCSVを表示する。

最終4 CSVとコピーした`meeting.xlsx`以外は内部用です。未確認の人物、会議情報、決定事項は推測で埋めません。
