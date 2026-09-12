# 制作フロー

## 目的

パブリックドメイン文学を、独自の現代日本語、会話、ナレーション、イラスト、効果音、間、VOICEVOX、Remotionへ変換する。要約動画ではなく、原作の文章へ視聴者を戻す入口を作る。

## 権利と原典

- 原作者、発表年、作者の没年、制作・公開地域での権利状態、参照元を確認する。
- 原著がパブリックドメインでも現代翻訳は別著作物として扱う。
- 原則は「原文 → 制作用の新しい日本語 → 紙芝居用再構成」。
- 不明な権利情報を推測で確定しない。
- `source/rights_check.md` と最終 `credits.txt` に根拠を残す。

## 新規プロジェクト

```powershell
python <skill>/scripts/create_project.py `
  --workspace-root C:\path\to\workspace `
  --project-id 0004_example `
  --title "作品名" `
  --source-file C:\path\to\original.txt `
  --brief-file C:\path\to\brief.md `
  --author "原作者" `
  --author-death-year 1900 `
  --source-url "https://example.com/source"
```

元テキストと企画メモは最初に `sozai/` へ置く。承認後、整理した内容だけを正式フォルダへ反映する。

## 段階別の成果物

| 段階 | 主な成果物 |
|---|---|
| 原典確認 | `source/original_source.txt`, `source/source_notes.md`, `source/rights_check.md` |
| 脚色方針 | `story/local_rules.md`, `story/adaptation_notes.md` |
| 人物設計 | `story/voice_cast.json`, character/relationship notes, character image prompts |
| シナリオ | `input/dialogue.json`, `input/scenes.json` |
| 画像設計 | `input/image_prompts.json`, 16:9画像 |
| 音響設計 | `input/sfx_cues.json`, pause values, `output/voice/`, `output/sfx/` |
| 分割制作 | `input/video_segments.md`, `input/remotion_segment_assets.json` |
| 確定時間 | segment別 `timeline.csv`, manifests |
| 動画 | `output/video_horizontal/`, `output/video_shorts/`, `output/final/` |

## シナリオ判断

- 会話は目的、関係、感情、決断を進める。
- ナレーションは美しい文章、比喩、皮肉、絵だけでは不足する情報に絞る。
- 絵で分かる説明は文章から削る候補にする。
- 効果音は空間、生活感、季節、物の存在を担う。
- 無言の時間も「イラスト＋効果音＋間」として設計する。
- シーン数、登場人物数、完成尺を人工的に固定しない。原作と作品別ルールを優先する。

## 画像判断

原文を画像生成へ直送しない。

```text
原文
→ 比喩と感情の意味
→ 現実の視覚情報
→ 人物・背景・光・構図
→ 16:9、文字なしの生成指示
```

感情の読みやすさ、構図、衣装や髪型による識別を優先する。画像生成前に、シナリオ・人物・画像案についてユーザーの最終確認を得る。

## 音声と時間

`dialogue.json` の新規行には `text` と `reading` を持たせる。音声ファイルへ長い無音を埋めず、`pause_before_sec` と `pause_after_sec` を別データにする。VOICEVOX生成後にwav実尺を取得し、segment別timelineを確定する。

## Remotion

- 長編は1〜2分程度のセグメントへ分ける。
- 配置依頼と動画化依頼を区別する。
- segment別に timeline、sfx manifest、placement manifest、Remotion snapshotを残す。
- 動画完成後、作品固有の作業状態は復元手順とともに `output/remotion_restore/` へ退避する。

## 完成確認

- 原作の価値、会話の進行、説明過多、比喩の視覚化、感情の読みやすさを確認する。
- VOICEVOX実尺、pause、効果音、字幕、画像、出力順を照合する。
- `credits.txt` と `manifest.csv` を作る。
- 共通化できる学びはワークスペースの共通方針へ、作品固有の学びは `story/local_rules.md` へ記録する。
