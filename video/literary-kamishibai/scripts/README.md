# 音声を作る

`CreateVoice.py` は既存の `CreateScenarioVoice.py` を公開用に整理したものです。`Voice.py` と同じフォルダに置いて使います。Python 3.10以上の標準ライブラリだけで動き、pipでの追加導入は不要です。

まず、リポジトリ直下で入力だけ確認します。VOICEVOXの起動は不要です。

```powershell
python video/literary-kamishibai/scripts/CreateVoice.py scenario/projects/first_test --line line_001 --check
```

`CHECK OK` なら音声生成へ進めます。不備があれば `ERROR` と理由を表示し、終了コード1で停止します。成功時は終了コード0です。`--check` は通信・音声生成・出力ファイルの作成や変更をしません。台本、音声マスター、対象行、間の秒数を確認します。VOICEVOX接続や実際の話者の存在、画像、Remotionの確認は含みません。台本全体の不備も確認するため、未使用の仮データも修正してください。

VOICEVOXを起動し、`--check` を外して実行します。

```powershell
python video/literary-kamishibai/scripts/Voice.py speakers
python video/literary-kamishibai/scripts/CreateVoice.py scenario/projects/first_test --line line_001
```

セグメント単位の場合：

```powershell
python video/literary-kamishibai/scripts/CreateVoice.py scenario/projects/first_test --segment segment_001
```

`--line` または `--segment` で範囲を指定します。どちらも指定しないと全セリフを生成します。再実行すると対象のWAVと対応する出力CSVを上書きするため、残したい出力は先に別の場所へ保存してください。`--line` は `--segment` より優先されるので通常は片方だけ使います。

## 入力

作品フォルダに次を用意します。

- `input/dialogue.json`
- `masters/character_master.csv`
- `masters/voice_style_master.csv`
- `masters/emotion_master.csv`
- `input/remotion_segment_assets.json`（`--segment` 使用時）

dialogue.jsonの1行の例：

```json
[
  {
    "line_id": "line_001",
    "scene_id": "scene_001",
    "type": "narration",
    "speaker": "ナレーター",
    "emotion": "通常",
    "text": "こんにちは。音声の確認です。",
    "reading": "こんにちは。おんせいのかくにんです。",
    "pause_before_sec": 0,
    "pause_after_sec": 0.5
  }
]
```

セグメント指定用の例：

```json
[
  {"segment_id": "segment_001", "dialogue_line_ids": ["line_001"]}
]
```

マスターの列は `assets/basetemplate/masters/` のCSVを参照します。ひな形の `__SPEAKER_ID__` 等は実値に変更し、使わない仮の登場人物行は削除してください。VOICEVOXの利用可能な話者ID・スタイルを `Voice.py speakers` で確認し、作品のマスターと合わせます。

## 出力

- `output/voice/<line_id>.wav`
- `output/voice_manifest.csv`、`output/timeline.csv`、`output/credits.txt`
- `--segment` 指定時のCSVとクレジットは `output/remotion/<segment_id>/` に保存
- `--line` 指定時はCSV名が `voice_manifest_selected.csv`・`timeline_selected.csv` になり、credits.txtは更新しない

タイムラインの画像・効果音欄は音声生成時点では空です。映像配置工程で補います。

接続先は通常 `http://localhost:50021`。生成するセリフをこのVOICEVOXへ送信します。

動作確認：VOICEVOX Engine 0.25.2でテスト文1行からWAV・segment別タイムライン・manifest・クレジットの生成を確認しています。別PCでは利用可能な話者と接続先を確認してください。
