# Output：三角関数

このファイルを成果物・保存先・完成条件の唯一の正本とします。相対パスはこの教材フォルダを基準に解決します。

現在は教材設計案（版0.1）です。利用者の指導方針と提示画像に基づく教材定義を作成します。追加した導入・ヒント・判定基準は教材作成者による確認前であり、授業の実施や学習レポートの生成は行いません。

| ID | 成果物 | 出力先 | 必須 | 完成条件 | Git公開 |
|---|---|---|---|---|---|
| design | 教材定義 | `README.md`、`input.md`、`processing.md`、`instructions.md`、`work/guideline.md`、`input/student-sheet.md` | 必須 | 固定教材、対象、目標、最初の問題、6段階の課題、ヒント、判定基準を定義し、教材作成者が確認済み。現時点は確認前の設計案 | 可 |
| dialogue | 学習対話 | 利用中の対話画面 | 学習実施時 | `instructions.md`に従い、最初の問いと`intro-figure`の表示用画像を同じメッセージで提示し、一度に一問だけ出して学習者の回答を待つ | 個人の回答を含むため公開しない |
| circle-sin-simple | 主要角のsin・cos導入 | `output/circle-sin-simple.htm` | 知る・覚える段階 | 0°〜180°の角度を一つ入力すると、単位円上の点、横のcos、縦のsinと値を表示する。範囲・係数・中の角・波形を持たない導入専用版 | 可 |
| circle-sin | 円とsin・cosの軌跡（試作） | `output/circle-sin.html` | 試作時 | 円とsin・cosを連動。表示を切り替え、正の係数0.5〜3で半径・振幅を変更できる。θの−720°〜720°の開始・終了と開閉端点、さらに中の角 `φ＝aθ＋b`（a＝1/3、1、2、3、bは度）を設定すると、θとφの範囲を併記して、円弧、グラフ、再生に反映する。座標の縮尺を固定し、sinは縦、cosは横の座標を表す。Q7用に単位円のcosと `2−cos²θ−cosθ` の値を凡例付きで連動表示できる。軌跡の消去に対応する | 可 |
| report | 学習レポート | `output/learning-report.md` | 学習実施時 | 教材ID・版、実施した問題・段階、回答と支援、到達した知識単位、判定根拠、戻り先と再確認、説明の品質と教材整合性、残る問いと復習案を記録する | 公開しない |
| browser-demo | ブラウザ操作用HTML | `output/trigonometric-demo.html` | 操作体験時 | circle-sinを単独で開けるHTMLへ変換し、表示と操作を確認する | 可 |
| questions-tex | 確認問題のLaTeX原稿 | `output/latex/trigonometric-questions.tex` | 問題用紙制作時 | 生徒用教材Q1〜Q7の式と範囲を保持し、解答を含まないLuaLaTeX原稿 | 可 |
| questions-pdf | 確認問題PDF | `output/pdf/trigonometric-questions.pdf` | 問題用紙制作時 | A4・1ページ。sin・cosの7問を掲載し、日本語・分数・根号・角度範囲が読める。解答なし。描画して目視確認済み | 配布用教材として可 |
| intro-figure | 最初の問いに添付する導入図 | `output/images/unit-circle-intro.png`（表示用）、`output/images/unit-circle-intro.svg`（編集用） | 知る段階の開始時 | 静止画1枚に、右向きの横軸から半径OPへ測るθの弧、半径1、横cos θ、縦sin θを表示。表示用PNGを最初の問いと同じメッセージで、問題文より先に表示できる | 可 |
| right-triangle-figures | 主要角の直角三角形 | `output/images/right-triangle-30.svg`、`output/images/right-triangle-45.svg`、`output/images/right-triangle-60.svg`、`output/images/right-triangle-120.svg`、`output/images/right-triangle-135.svg`、`output/images/right-triangle-150.svg` | 覚える段階 | 30°・45°・60°と、第2象限の120°・135°・150°について、斜辺・となり側・向かい側とsin・cosの比を示す。第2象限ではcosが負、sinが正になることを、基準角と結び付けて確認する | 可 |
| upper-semicircle-figure | 0°〜180°の単位円 | `output/images/unit-circle-0-to-180.svg` | 覚える段階 | 0°、30°、45°、60°、90°、120°、135°、150°、180°を上半円に配置し、90°・180°の座標と第1・第2象限の符号を確認する | 可 |

実験を実施した場合のみ、条件・予想・観察・理由の説明もレポートへ記録します。過去教材を参照した場合は、その教材と知識単位を記録します。未実施の学習履歴や合格判定を生成しません。

PDFや実験画面を制作する場合は、先にこのファイルへ保存先と完成条件を追加します。既存の学習レポートがある場合は、保存先をここで更新してから別の学習記録を作成し、上書きを避けます。
