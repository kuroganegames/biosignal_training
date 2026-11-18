網膜感度データ解析チュートリアル
視野検査のばらつきを理解し、次回の測定値を予測する
作成日：2026-11-08（日本時間）

このリポジトリについて
ChatGPTに網膜データを用いた解析のチュートリアルを作成してもらい、
できるだけコードを見ずに、説明・図・実行結果を中心に解析を進めた記録です。
使用するのは、視野検査で測定された網膜感度の数値データです。

開始するには
1. retina_tutorial.ipynb をGoogle ColabまたはJupyterで開いてください。
2. 上からセルを実行し、説明・図・結果を確認しながら、各章の「考える」をメモしてください。
3. 教材用の実データはNotebook内に同梱されています。データ取得・R・GPUは不要です。
4. コードを実行せず読む場合、retina_tutorial_guide.htmlに説明・実行例・図があります。

ファイル
  retina_tutorial.ipynb : 日本語の解説と実行可能なコード、実行結果
  retina_tutorial_guide.html : ブラウザで読める実行結果付き教材
  retina_beginner_glossary.html : 初学者向け用語集
  retina_exploration.ipynb : 探索的な解析の記録
  run_analysis.py : Notebookと同じ順のコードをまとめたスクリプト
  requirements.txt : 解析に必要なライブラリ
  data/ : 公開データ、位置地図、固定ソース、ライセンス、出典・変換記録
  outputs/ : 作成時の図・評価値・患者分割・研究メモ・実行環境

ローカルでの実行
  python -m venv .venv
  # 環境を有効化後
  python -m pip install -r requirements.txt
  jupyter notebook retina_tutorial.ipynb
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

解析結果はoutputs/に保存され、retina_results.zipにまとめられます。
