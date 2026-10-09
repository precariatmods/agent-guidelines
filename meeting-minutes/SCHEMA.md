# Meeting Minutes CSV Schema

CSVはUTF-8（BOM付き）、カンマ区切り、CRLF、ヘッダー付きで保存します。

## 全文文字起こし

```csv
line_id,speaker_id,start_time,end_time,text
```

1行を1発話とし、音声順に保存します。未確認話者は`speaker_001`形式、確認済み人物は`person:<ID>`形式です。全文文字起こしは要約しません。

## 話者候補

```csv
diarization_speaker_id,speaker_id,person_id,name,department,confirmation_status,total_seconds,sample_text
```

検出話者1人につき1行とし、利用者が確認した人物だけに`person_id`を設定します。

## Excel書き込み用CSV

列名と列順は`template/`の同名CSVを正本とします。

```csv
会議名,開催日,開始時刻,終了時刻,場所
LineID,開始時刻,終了時刻,話者ID,発言者,議事内容
話者ID,社員ID,社員名,EMAIL
議題,内容,決定事項
```

- `header.csv`：確認済みの会議情報
- `minutes.csv`：時系列の要約発言
- `participants.csv`：確認済みの参加者
- `Agenda.csv`：議題、内容、明示された決定事項

人物マスターは`work/master/person.csv`を正本とし、ID、氏名、部署、メールアドレスを保持します。
