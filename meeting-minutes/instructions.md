# Instructions：会議議事録

1. 最初に`POLICY.md`を読み、定義された確認方法と判断ルールに従う。
2. 元音声を変更せず、全文文字起こしを`work/transcript_raw.csv`へ出力する。
3. 会議名、開催日、開始時刻、終了時刻、場所を利用者に確認する。
4. 話者IDと主要発言を`work/speaker_candidates.csv`へ出力する。
5. 人物候補は`work/master/person.csv`から一人ずつ提示する。
6. 利用者が確認した対応だけを保存する。
7. 確認後の全文文字起こしを`work/transcript.csv`へ保存する。
8. 最終4 CSVを`work/final/`へ保存する。`output/`へは保存しない。
9. CSVの列名と列順は`template/`の同名CSVに完全一致させる。
10. `scripts/finalize_meeting.py`でテンプレートへ値を直接書き込む。
11. 最終成果物は`output/meeting.xlsx`だけとする。
12. Excelの外部接続、Power Query、マクロ、表示用数式は使用しない。

書き込み前に、入力CSVフォルダと完成Excelの絶対パスを利用者へ報告します。
