# 文学紙芝居プロジェクト テンプレート

## 使い方

1. スキル付属の `scripts/create_project.py` で、この `basetemplate` を `projects/<project_id>/` としてコピーする。
2. スクリプトが `job.json` の `__PROJECT_ID__` と `__TITLE__` を置き換える。手作業でコピーした場合だけ自分で置き換える。
3. `sozai/` に原文、権利メモ、人物、台本、画像、効果音、動画分割などの新作案を置く。
4. `sozai/` のドラフトを `source/`, `story/`, `input/`, `images/` へ整理して展開する。
5. 作品固有の `masters/character_master.csv` と `masters/voice_style_master.csv` を確定する。

## ほぼ固定で使えるマスタ

- `masters/emotion_master.csv`
- `masters/voicevox_speaker_master.csv`
- `masters/visual_preset_master.json`

## 作品ごとに確認するマスタ

- `masters/character_master.csv`
- `masters/voice_style_master.csv`

話者、VOICEVOXキャラ、感情の組み合わせは作品ごとに変わるため、空テンプレから確定する。
