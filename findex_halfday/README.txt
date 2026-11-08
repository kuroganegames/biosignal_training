ファインデックスの研究開発を半日で体験する
視野検査のばらつきを理解し、次回の測定値を予測する
作成日：2026-11-08（日本時間）

開始するには
1. findex_halfday.ipynb をGoogle ColabまたはJupyterで開いてください。
2. 上からセルを実行し、各章の「考える」をメモしてください。休憩を含み4時間です。
3. 教材用の実データはNotebook内に同梱されています。データ取得・R・GPUは不要です。
4. コードを実行せず読む場合、findex_halfday_guide.htmlに説明・実行例・図があります。

ファイル
  findex_halfday.ipynb : 日本語の解説と実行可能なコード、検証済み実行結果
  findex_halfday_guide.html : ブラウザで読める実行結果付き教材
  run_analysis.py : Notebookと同じ順のコードをまとめたスクリプト
  requirements.txt : 解析に必要なライブラリ
  data/ : 公開データ、位置地図、固定ソース、ライセンス、出典・変換記録
  outputs/ : 作成時の図・評価値・患者分割・研究メモ・実行環境

ローカルでの実行
  python -m venv .venv
  # 環境を有効化後
  python -m pip install -r requirements.txt
  jupyter notebook findex_halfday.ipynb
  # Notebookを使わず実行する場合
  python run_analysis.py

解析の設計
  30患者・30眼・360検査。54点のうち盲点付近2点を位置定義から除外。
  患者21人/9人を固定seedで分割。過去3回→次の1回を逐次予測。
  前回値、3回平均、標準化+Ridge(alpha=10)を比較。
  患者等重みMAEと患者単位の対応ありbootstrapで評価。
  疾病分類・長期進行予測・真の感度の推定を実証する教材ではありません。

データの出典
  visualFields::vfpwgRetest24d2, visualFields 1.0.7
  https://cran.r-universe.dev/visualFields/doc/manual.html#vfpwgRetest24d2
  Artes PH, O'Leary N, Nicolela MT, Chauhan BC, Crabb DP (2014).
  Visual field progression in glaucoma: What is the specificity of the Guided Progression Analysis?
  Ophthalmology 121(10):2023-2027. doi:10.1016/j.ophtha.2014.04.015
  パッケージのライセンス：Apache License 2.0（data/LICENSE.visualFields.txt）
  CSV化で日付をISO文字列に変換。その他の測定値は変更していません。
  位置座標は右眼基準。左眼の臨床的表示には水平反転が必要です。

公開求人と研究をもとに独立に作成した教材で、ファインデックスの監修教材ではありません。
