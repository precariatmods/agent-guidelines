# Output：会議議事録

このファイルを出力先と成果物一覧の正本とします。相対パスは`meeting-minutes/`基準です。

## 保存先

| 用途 | 保存先 |
|---|---|
| 元音声 | `input/` |
| 作業データ | `work/` |
| 人物マスター | `work/master/person.csv` |
| CSV列定義 | `template/` |
| 最終成果物 | `output/` |

## 内部用データ

| ファイル | 内容 |
|---|---|
| `work/transcript_raw.csv` | 全文文字起こし。話者紐付け前 |
| `work/speaker_candidates.csv` | 話者ID、主要発言、人物候補、確認結果 |
| `work/transcript.csv` | 話者紐付け後の全文文字起こし |

全文文字起こしは必ず保存しますが、最終成果物の表面では使用しません。

## 最終成果物

| ファイル | 列名・列順 |
|---|---|
| `header.csv` | `template/header.csv`と完全一致 |
| `minutes.csv` | `template/minutes.csv`と完全一致 |
| `participants.csv` | `template/participants.csv`と完全一致 |
| `Agenda.csv` | `template/Agenda.csv`と完全一致 |
| `meeting.xlsx` | `template/meeting.xlsx`を内容変更せずコピーする |

4種類のCSVはUTF-8（BOM付き）、CRLFで保存します。CSV作成後、テンプレートExcelを同じフォルダへコピーして終了します。Excelの生成・編集・接続先変更は行いません。
