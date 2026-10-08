# meeting_menber.csv schema

会議に関係する人物を保存します。人物は`work/master/person.csv`からチャットで選び、1人につき1行を`meeting_menber.csv`へ保存します。

## 確定方針

- 音声から人物名を取得できた場合は、人物マスターと照合して候補の`ID`、氏名、部署をチャットで案内する。
- 利用者が選択した人物IDだけを確定値として保存する。
- 音声だけを根拠に人物や役割を確定しない。
- 人物マスターに該当者がいない場合は、勝手に追加せず利用者へ案内する。
- 氏名、部署、メールアドレスはCSVへ重複保存せず、表示時に人物マスターから参照する。

## ファイル仕様

| 項目 | 定義 |
|---|---|
| 保存先 | `work/meeting_menber.csv` |
| レコード数 | 1会議につき0行以上。確定後は人物1人につき1行 |
| 文字コード | UTF-8（BOM付き） |
| 区切り文字 | カンマ |
| 改行 | CRLF |
| ヘッダー | 必須 |

## 列定義

| 列名 | 必須 | 型・形式 | 定義 |
|---|---:|---|---|
| `meeting_id` | 必須 | 文字列 | `meetingheader.csv`の`meeting_id` |
| `member_no` | 必須 | 文字列 `member_001` | 会議内で一意となる連番ID |
| `person_id` | 必須 | 人物ID | `person.csv`の`ID` |
| `roles` | 任意 | 列挙値の一覧 | `主催者`、`司会`、`議事録作成者`、`参加者`、`承認者`。複数は`;`で区切る |
| `attendance_status` | 必須 | 列挙値 | `出席`、`欠席`、`途中参加`、`途中退席`、`未確認`のいずれか |
| `attendance_method` | 任意 | 列挙値 | `対面`、`オンライン`、`電話`、`未確認`のいずれか |
| `confirmation_status` | 必須 | 列挙値 | `未確認`または`確認済み` |
| `notes` | 任意 | 文字列 | 参加・退出時刻、代理出席等の補足情報 |

ヘッダー行：

```csv
meeting_id,member_no,person_id,roles,attendance_status,attendance_method,confirmation_status,notes
```

## チャット確認例

```text
参加者候補：
- ID 1：佐藤（総務）／役割候補：議事録作成者
- ID 2：田中（営業）／役割候補：司会、参加者
- ID 4：高橋（役員）／役割候補：承認者
```

利用者へ、参加者、欠席者、役割、参加方法を確認します。回答を反映した行だけを`確認済み`とします。

## 記入例

```csv
meeting_id,member_no,person_id,roles,attendance_status,attendance_method,confirmation_status,notes
20260915-sales-weekly,member_001,1,議事録作成者;参加者,出席,対面,確認済み,
20260915-sales-weekly,member_002,2,司会;参加者,出席,対面,確認済み,
20260915-sales-weekly,member_003,4,承認者,出席,対面,確認済み,
```

## 完成条件

- 必須列が存在し、列順が定義どおりである。
- `meeting_id`が`meetingheader.csv`の会議IDと一致している。
- `member_no`が会議内で重複していない。
- 同じ会議で`person_id`が重複していない。
- すべての`person_id`が`person.csv`に存在する。
- 音声から得た人物候補が、利用者の確認なしに確定値として保存されていない。
- `confirmation_status`が実際の確認状況と一致している。
