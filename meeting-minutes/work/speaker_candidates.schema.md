# speaker_candidates.csv schema

pyannote.audioが検出した話者と、利用者が確認した人物マスターの対応を保存します。声だけを根拠に人物を自動確定しません。

## ファイル仕様

| 項目 | 定義 |
|---|---|
| 保存先 | `work/speaker_candidates.csv` |
| 文字コード | UTF-8（BOM付き） |
| 区切り文字 | カンマ |
| 改行 | CRLF |
| ヘッダー | 必須 |
| レコード数 | 検出話者1人につき1行 |

## 列定義

| 列名 | 必須 | 定義 |
|---|---:|---|
| `diarization_speaker_id` | 必須 | pyannote.audioが付けた話者ラベル。例：`SPEAKER_00` |
| `speaker_id` | 必須 | 未確認時は`speaker_001`形式、確認後は`person:<ID>` |
| `person_id` | 任意 | 利用者が`work/master/person.csv`から確認した人物ID |
| `name` | 任意 | 確認済み人物の氏名 |
| `department` | 任意 | 確認済み人物の部署 |
| `confirmation_status` | 必須 | `未確認`または`確認済み` |
| `total_seconds` | 必須 | 話者として検出された合計秒数 |
| `sample_text` | 任意 | 人物確認に使用する発言例。複数は` / `で区切る |

ヘッダー行：

```csv
diarization_speaker_id,speaker_id,person_id,name,department,confirmation_status,total_seconds,sample_text
```

## 確定ルール

- `person_id`は利用者が発言例と音声を確認して選択する。
- `person_id`は`work/master/person.csv`に存在する人物IDだけを使用する。
- 未確認時は`person_id`、`name`、`department`を空欄にする。
- 同一人物の声が複数の話者ラベルへ分かれた場合は、複数行を同じ`person_id`へ対応させることができる。
- 参加者ではないナレーター等は人物へ紐付けず、仮話者IDのまま保持する。

## 完成条件

- 検出されたすべての話者ラベルが1行ずつ存在する。
- `speaker_id`が文字起こしCSVで使用する値と一致する。
- `確認済み`の行だけに有効な`person_id`が設定されている。
- 人物を推測だけで確定していない。
