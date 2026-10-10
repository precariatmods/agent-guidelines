# Output：文学紙芝居

このファイルを、文学紙芝居ワークフローの成果物、保存先、完成条件、Git公開可否に関する唯一の正本とします。相対パスはこのファイルがあるフォルダを基準とし、`<project_id>`は対象作品のIDに置き換えます。

## 成果物一覧

| ID | 成果物 | 保存先 | 必須性 | 完成条件 | Git公開 |
| --- | --- | --- | --- | --- | --- |
| script | 再生順の台本 | `project/<project_id>/dialogue.json` | 必須 | 各要素に`line_id`、`scene_id`、`image`、`character`、`text`があり、`line_id`が重複しない | サンプルのみ可 |
| voices | VOICEVOX話者対応表 | `project/<project_id>/voicevox_characters.csv` | 必須 | 指定の3列があり、台本の全話者にIDが対応する | サンプルのみ可 |
| image-orders | シーン別画像指示書 | `project/<project_id>/image_order/` | 必須 | 各シーンの番号付き指示書に`scene_id`、画像の保存先、視覚指示がある | サンプルのみ可 |
| images | シーン画像 | `project/<project_id>/images/` | 必須 | 台本が参照する全画像が存在し、16:9で利用できる | サンプルのみ可 |
| audio | VOICEVOX音声 | `project/<project_id>/audio/<line_id>.wav` | 必須 | 台本の全`line_id`に対応するWAVが生成され、再生できる | 原則不可 |
| render-data | Remotion用中間データ | `project/<project_id>/render_data.json` | 必須 | 素材検証が成功し、`prepare_remotion.py`が正常終了して生成される | 不可 |
| video | 完成MP4 | `project/<project_id>/output/video.mp4` | 利用者がレンダリングを依頼した場合は必須 | Remotionのレンダリングが正常終了し、映像・音声・字幕を再生確認できる | 原則不可 |

## 運用規則

- 処理前に対象の`<project_id>`を確定し、上記の保存先を絶対パスへ解決して利用者へ報告します。
- 保存先または成果物の種類を変更する場合は、先にこのファイルを更新します。
- 既存の作品と生成物は、利用者の指示なく上書きません。
- `render_data.json`は自動生成し、手作業で編集しません。
- サンプルとしてGit公開する入力は、著作権、個人情報、秘密情報を公開できることを確認します。
