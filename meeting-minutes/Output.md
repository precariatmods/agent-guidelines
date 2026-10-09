# Output：会議議事録

このファイルを出力先と成果物一覧の正本とします。相対パスは`meeting-minutes/`基準です。

## 保存先

| 用途 | 保存先 |
|---|---|
| 元音声 | `input/` |
| 作業データ | `work/` |
| 人物マスター | `work/master/person.csv` |
| 最終4 CSV（内部用） | `work/final/` |
| Excel原本・CSV列定義 | `template/` |
| 最終成果物 | `output/meeting.xlsx` |

## 内部用データ

- `work/transcript_raw.csv`：全文文字起こし。話者紐付け前。
- `work/speaker_candidates.csv`：話者ID、主要発言、人物候補、確認結果。
- `work/transcript.csv`：話者紐付け後の全文文字起こし。
- `work/final/header.csv`：確定した会議情報。
- `work/final/minutes.csv`：時系列の要約発言。
- `work/final/participants.csv`：確定した参加者。
- `work/final/Agenda.csv`：議題、内容、決定事項。

CSVはExcel作成用の内部データです。`output/`へコピーしません。

## 最終成果物

最終成果物は`output/meeting.xlsx`の1ファイルだけです。

`template/meeting.xlsx`の書式を原本としてコピーし、`openpyxl`で確認済みデータを値として直接書き込みます。外部データ接続、Power Query、マクロ、表示用の数式は使用しません。Excelで「すべて更新」を行う必要もありません。
