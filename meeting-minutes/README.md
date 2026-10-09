# Meeting Minutes — AIによる会議議事録作成サンプル

会議音声を全文文字起こしし、声の特徴で仮話者IDへ分け、利用者との対話で会議情報と人物を確認して議事録を作成するサンプルです。

処理方針の正本は`POLICY.md`、成果物定義の正本は`Output.md`です。

## 初回実行時の注意

音声認識と話者分離には`faster-whisper`、`sherpa-onnx`、公開ONNXモデルを使用します。Excelへの値の書き込みには`openpyxl`を使用します。

必要な環境がない場合、`setup.ps1`は最大約2GBの保存容量を使う可能性があることを表示し、利用者が`y`または`yes`を入力した場合だけインストールします。既存環境で必要なバージョンが揃っていれば再利用します。

## 必要な環境

- Windows
- PowerShell
- Python 3.11推奨
- 初回構築時のインターネット接続
- Microsoft Excel（完成帳票の閲覧用）

直接指定するpipパッケージは`scripts/requirements.txt`を正本とします。

```text
faster-whisper==1.2.1
sherpa-onnx==1.13.8
openpyxl==3.1.5
```

## フォルダ構成

```text
meeting-minutes/
├─ input/                  元音声
├─ template/               Excel原本とCSV列定義
├─ work/                   全文文字起こしなどの内部データ
│  ├─ final/               Excel書き込み前の4 CSV
│  └─ master/person.csv    人物マスター
├─ output/                 完成したmeeting.xlsxのみ
└─ scripts/                処理スクリプト
```

## 環境構築と音声処理

```powershell
.\setup.ps1
.\run.ps1 -Audio "input\meeting_voice.mp3"
```

主な処理は次のとおりです。

1. Whisperで全文文字起こしする。
2. sherpa-onnxで声の特徴を抽出し、仮話者IDへ分類する。
3. 話者IDごとの主要発言と人物マスターの候補を提示する。
4. 利用者が確認した人物だけを話者IDへ紐付ける。
5. 確認済み文字起こしを`work/transcript.csv`へ保存する。

既存の文字起こしを明示的に再利用する場合は`-ReuseTranscript`、人物を確定せず候補だけ作る場合は`-NonInteractive`を指定します。

## 会議情報と人物の確認

ヘッダーは会議名、開催日、開始時刻、終了時刻、場所の5項目だけです。不明な項目を推測で確定せず、利用者へ確認します。

各話者について原則3件の主要発言と人物候補を提示します。声や発言だけで人物を確定せず、利用者の回答を反映します。

## 内部CSV

メンバー確定後、確認済みの文字起こしを要約し、次の4 CSVを`work/final/`へ作成します。

- `header.csv`
- `minutes.csv`
- `participants.csv`
- `Agenda.csv`

列名と列順は`template/`の同名CSVに合わせます。これらはExcel作成用の内部データであり、`output/`へはコピーしません。

## 完成Excelの作成

```powershell
.venv\Scripts\python.exe scripts\finalize_meeting.py --force
```

別の内部CSVフォルダを指定する場合：

```powershell
.venv\Scripts\python.exe scripts\finalize_meeting.py work\final --force
```

この処理は次を行います。

1. 4 CSVの列名、列順、データ行を検証する。
2. `template/meeting.xlsx`を書式原本としてコピーする。
3. Excelの表示シートと内部データシートへ値を直接書き込む。
4. `output/meeting.xlsx`だけを保存する。

完成Excelには外部CSV接続、Power Query、マクロ、表示用数式がありません。「すべて更新」は不要です。

## 注意事項

- 音声認識、話者分類、要約には誤りが含まれる可能性があります。
- 人名、会議日時、決定事項は必ず利用者が確認してください。
- 音声と議事録には機密情報や個人情報が含まれる可能性があります。
- 会話行や議題がテンプレートの初期行数を超える場合、必要な行を追加して書き込みます。
