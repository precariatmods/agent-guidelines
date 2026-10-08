# Instructions：会議議事録

1. 最初に`POLICY.md`を読み、定義された確認方法と判断ルールに従う。
2. 元音声を変更せず、全文文字起こしを`work/transcript_raw.csv`へ出力する。
3. 最初の対話では、会議名、開催日、開始時刻、終了時刻、場所だけを利用者に確認し、`header.csv`を作成する。
4. 話者分離後、話者IDと主要発言を`work/speaker_candidates.csv`へ出力する。
5. 人物候補は`work/master/person.csv`から氏名・部署とともに一人ずつ提示する。
6. 声や発言内容だけで人物を確定せず、利用者が確認した対応だけを保存する。
7. 確認済み話者は人物IDへ紐付け、未確認話者は仮話者IDのまま`work/transcript.csv`へ保存する。
8. 話者と人物の紐付け結果から`participants.csv`を作成する。
9. メンバー確定後、`work/transcript.csv`を要約し、会話の流れを`minutes.csv`、議題・内容・決定事項を`Agenda.csv`へ整理する。
10. 最終CSVの列名と列順は`template/`の同名CSVに完全一致させる。
11. 4種類のCSVが揃った後、`template/meeting.xlsx`を内容変更せず`output/meeting.xlsx`へコピーする。
12. Excel内部の編集や接続先の書き換えは行わない。
13. `output/`に4 CSVと`meeting.xlsx`があることを確認して完成とする。

出力先は`output/`です。書き込み前に解決した絶対パスを利用者へ報告します。
