# meetingheader.csv schema

会議全体のヘッダー情報を保存します。1つの音声ファイルを1会議として扱い、`meetingheader.csv`にはヘッダー行と1件のデータ行を保存します。

## 確定方針

- 会議情報は、議事録作成時のチャットで利用者に確認して確定する。
- 音声から会議名、日時、場所等を取得できた場合は、確定値ではなく確認候補としてチャットで案内する。
- 利用者が確認した内容だけを確定値として保存する。
- 音声と利用者の回答が異なる場合は、違いを案内したうえで利用者の回答を採用する。
- 確認できない項目は推測せず空欄にし、必要に応じて`notes`へ記録する。

## ファイル仕様

| 項目 | 定義 |
|---|---|
| 保存先 | `work/meetingheader.csv` |
| レコード数 | 1音声につき1会議、データ行は1行 |
| 文字コード | UTF-8（BOM付き） |
| 区切り文字 | カンマ |
| 改行 | CRLF |
| ヘッダー | 必須 |

## 列定義

| 列名 | 必須 | 型・形式 | 定義 |
|---|---:|---|---|
| `meeting_id` | 必須 | 文字列 | 内部管理で会議を一意に識別するID。出力ファイル名には使用しない |
| `meeting_name` | 必須 | 文字列 | 利用者が確認した会議名 |
| `meeting_date` | 任意 | `YYYY-MM-DD` | 開催日 |
| `start_time` | 任意 | `HH:MM` | 開始時刻 |
| `end_time` | 任意 | `HH:MM` | 終了時刻 |
| `timezone` | 任意 | IANAタイムゾーン | 時刻の基準。例：`Asia/Tokyo` |
| `location` | 任意 | 文字列 | 会議室名、拠点名、オンライン会議等の開催場所 |
| `meeting_format` | 任意 | 列挙値 | `対面`、`オンライン`、`ハイブリッド`のいずれか |
| `host_department` | 任意 | 文字列 | 主催部署 |
| `source_audio` | 必須 | 相対パス | `meeting-minutes/`を基準とした元音声のパス |
| `confirmation_status` | 必須 | 列挙値 | `未確認`または`確認済み` |
| `notes` | 任意 | 文字列 | 未確認事項や補足情報 |

ヘッダー行：

```csv
meeting_id,meeting_name,meeting_date,start_time,end_time,timezone,location,meeting_format,host_department,source_audio,confirmation_status,notes
```

## チャット確認例

```text
会議名：営業定例会議（音声からの候補）
開催日：2026-09-15（依頼内容からの候補）
時刻：10:00～11:00（音声からの候補）
場所：第2会議室（音声からの候補）
開催形式：対面（音声からの候補）
主催部署：営業部（音声からの候補）
```

利用者の回答を反映した後に`confirmation_status`を`確認済み`へ変更します。任意項目に空欄が残る場合でも、その状態を利用者が確認していれば`確認済み`にできます。

## 記入例

```csv
meeting_id,meeting_name,meeting_date,start_time,end_time,timezone,location,meeting_format,host_department,source_audio,confirmation_status,notes
20260915-sales-weekly,営業定例会議,2026-09-15,10:00,11:00,Asia/Tokyo,第2会議室,対面,営業部,input/meeting_voice.mp3,確認済み,
```

## 完成条件

- ヘッダー行と1件のデータ行で構成されている。
- 必須列が存在し、列順が定義どおりである。
- `source_audio`が実在する元音声を指している。
- 音声から得た候補が、利用者の確認なしに確定値として保存されていない。
- `confirmation_status`が実際の確認状況と一致している。
