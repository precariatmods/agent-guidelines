# Output：反比例

このファイルを成果物・保存先・完成条件の唯一の正本とします。相対パスはこの教材フォルダを基準に解決します。

現在は教材設計案（版0.1）です。追加した問題、ヒント、解答、判定基準は教材作成者による確認前であり、授業の実施や学習レポートの生成は行いません。

| ID | 成果物 | 出力先 | 必須 | 完成条件 | Git公開 |
|---|---|---|---|---|---|
| design | 教材定義 | `README.md`、`input.md`、`processing.md`、`instructions.md`、`work/guideline.md`、`input/student-sheet.md` | 必須 | 固定教材、対象、目標、最初の問い、6段階の課題、ヒント、解答、判定基準を定義し、教材作成者が確認済み。現時点は確認前の設計案 | 可 |
| dialogue | 学習対話 | 利用中の対話画面 | 学習実施時 | 教師用方針に従い、学習者の回答を待って一問ずつ進行する | 個人の回答を含むため公開しない |
| report | 学習レポート | `output/learning-report.md` | 学習実施時 | 教材ID・版、実施した問題・段階、回答と支援、到達した知識単位、判定根拠、戻り先と再確認、説明の品質、残る問いと復習案を記録する | 公開しない |
| graph | 反比例の検証グラフ | `output/inverse-proportional-travel-graph.svg` | 図を制作する場合 | 速さx（km/h）と時間y（時間）、式、固定問題の代表点、x＝0を含まない現実の定義域を正しく表示する | 可 |
| student-tex | 生徒用教材のLaTeX原稿 | `output/latex/inverse-proportional-student.tex` | PDF制作時 | `input/student-sheet.md`の前提、理解・応用課題、Q1〜Q7、説明課題を保持し、解答を含まないupLaTeX原稿 | 可 |
| student-pdf | 生徒用教材PDF | `output/pdf/inverse-proportional-student.pdf` | PDF制作時 | A4。数式、日本語、表、記入欄が読みやすく、解答を含まず、全ページを描画して目視確認済み | 配布用教材として可 |

比例教材と組み合わせた比較を実施した場合は、比例と反比例の判別根拠もreportへ記録します。未実施の学習履歴や合格判定は生成しません。
