# ローカル制作ツール

このリファレンスは、対象ワークスペースに対応ツールがある場合だけ使う。存在しない絶対パスを前提にしない。個人作成の実行ファイルは配布・推奨せず、公開READMEに記載した一般公開ツールだけを使う。

## VOICEVOX

- `story/voice_cast.json` と `masters/*.csv` で話者とstyle IDを確定する。
- 対象segmentの `dialogue_line_ids` だけを生成対象にする。
- 出力は原則 `output/voice/<line_id>.wav`。
- wav実尺を測定してからtimelineを確定する。

## Remotion

`package.json` とRemotion入口がある場合、既存の構成と作品別ルールを先に調べる。新規segmentは既存作品のcomposition IDや固定パスを流用しない。

- `Remotion配置`: ソース、生成データ、素材コピー、manifest、snapshotまで。
- `動画化してください`: 明示されたsegmentだけレンダリング。
- 完成後: active sourceを消す前に復元可能なsnapshotと`RESTORE.md`を残す。
