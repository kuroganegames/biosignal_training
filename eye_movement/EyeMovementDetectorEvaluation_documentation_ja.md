# EyeMovementDetectorEvaluation 日本語ドキュメント

作成日：2026年11月14日  
翻訳対象コミット：`3e12416ab3fd6254c81811cf03f8e5d67c5d7129`

本書は、`EyeMovementDetectorEvaluation` に同梱された `README.docx`、トップレベルの `readme.md`、各データフォルダと解析コードの説明文を統合した日本語訳である。変数名、ファイル名、GUIのボタン名は、実際のデータや操作画面と照合できるよう原表記を使用する。原文への補足は「訳注」または第8節に示す。

## 1. Eye Movement Detector Evaluationについて

本リポジトリには、注釈ツール、使用した刺激、および2名の注釈者がラベルを付けたデータが含まれている。コードとデータはMATLAB形式で提供されている。

解析の一部は対話的に行われたため、解析コードは完全なものではない。ただし、どのような処理が行われたかを理解する手がかりになる。

このデータは、第3節に示す Andersson ら（2017）の研究で使用された。

## 2. ライセンス

ソフトウェア、データ、および刺激は、GNU General Public License バージョン3（GNU GPL v3）の下で公開されている。詳細は[GNU GPL v3の原文](https://www.gnu.org/licenses/gpl-3.0.html)を参照すること。

一部の刺激は、著作権上の理由により収録されていない。

> 訳注：ここでは `README.docx` のライセンス説明を翻訳している。ライセンス本文は、同梱の [LICENSE](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/LICENSE) を参照。

## 3. はじめに・関連論文

本データは、SensoMotoric Instruments（SMI）のHi-speedシステムを用い、500 Hzで収集されたものである。参加者が画像、動画、移動する点を見ている間に計測した。

データの詳しい説明は、以下の論文に記載されている。

1. Larsson, L., Nyström, M., & Stridh, M. (2013). *Detection of saccades and postsaccadic oscillations in the presence of smooth pursuit.* IEEE Transactions on Biomedical Engineering, 60(9), 2484–2493.  
   題名の訳：滑動性追従眼球運動が存在する状況でのサッカードとサッカード後振動の検出。

同じデータベースは、以下の研究でも使用されている。

2. Larsson, L., Nyström, M., Andersson, R., & Stridh, M. (2015). *Detection of fixations and smooth pursuit movements in high-speed eye-tracking data.* Biomedical Signal Processing and Control, 18, 145–152.  
   題名の訳：高速アイトラッキングデータにおける固視と滑動性追従眼球運動の検出。
3. Andersson, R., Larsson, L., Holmqvist, K., Stridh, M., & Nyström, M. (2017). *One algorithm to rule them all? An evaluation and discussion of ten eye movement event-detection algorithms.* Behavior Research Methods, 49(2), 616–637. [DOI: 10.3758/s13428-016-0738-9](https://doi.org/10.3758/s13428-016-0738-9)  
   題名の訳：すべてに対応できるアルゴリズムはあるか？ 10種類の眼球運動イベント検出アルゴリズムの評価と考察。

**ここで提供するデータを利用する際は、これらの論文を引用すること。**

## 4. データの形式と内容

### 4.1 保存形式

データはMATLABのネイティブ形式である `.mat` ファイルに保存されている。各ファイルは、1名の参加者が1種類の刺激を見たときの記録に対応する。

各 `.mat` ファイルには、次のフィールドを持つ構造体 `ETdata` が含まれている。

| フィールド | 説明 |
| --- | --- |
| `sampFreq` | データ記録時のサンプリング周波数 |
| `viewDist` | 眼から画面までの距離 |
| `screenDim` | 画面の物理的な大きさ。単位はメートル |
| `screenRes` | 画面の解像度。単位はピクセル |
| `pos` | 各行が1サンプルを表す `n × 5` の行列 |

### 4.2 `pos` の各列

| 列番号（MATLAB） | 内容 |
| ---: | --- |
| 1 | タイムスタンプ。単位はマイクロ秒 |
| 2 | 水平方向の瞳孔径 |
| 3 | 垂直方向の瞳孔径 |
| 4 | 視線のx座標 |
| 5 | 視線のy座標 |

名前の末尾に `labelled` が付く注釈済みの `.mat` ファイルでは、第6列が追加される。この列は各サンプルのラベル、すなわち手作業によるラベル付けの結果を表す。

> 訳注：公開されているファイルには `UH29_img_Europe_labelled_MN.mat` のように、`labelled` の後ろに注釈者の識別子が付くものもある。注釈済みファイルの `pos` は `n × 6` となる。

### 4.3 イベントラベル

| ラベル値 | 原語 | 日本語 |
| ---: | --- | --- |
| 1 | Fixation | 固視 |
| 2 | Saccade | サッカード |
| 3 | Post-saccadic oscillation | サッカード後振動（PSO） |
| 4 | Smooth pursuit | 滑動性追従眼球運動 |
| 5 | Blink | 瞬目（まばたき） |
| 6 | Undefined | 未定義。他のいずれのカテゴリにも当てはまらないサンプル |

## 5. データの可視化と注釈

### 5.1 GUIでデータを開く

データを簡単に可視化するには、MATLABのGUIである `EventTag.m` を実行する。GUIが開いたら、**「Load mat-file」** ボタンを押し、確認したいファイルを選択する。

イベントは、第5.3節の表に示す色で表示される。

### 5.2 画面の構成

GUIには5つの表示領域があり、すべて同じ時間範囲から選択されたデータを表示する。

| 表示位置 | 内容 |
| --- | --- |
| 左上 | 視線のx座標とy座標。単位はピクセル |
| 左中央 | 隣接サンプル間から求めた速度 |
| 左下 | 垂直方向の瞳孔径。単位はカメラのピクセル |
| 右上 | 視線座標の `(x, y)` プロット |
| 右下 | 直近に検出されたイベントの拡大表示 |

左側のグラフの横軸は時間で、単位はミリ秒（ms）である。

![EventTagのGUI。左側に視線座標・速度・瞳孔径、右側に視線軌跡と拡大図を表示する。](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation_documentation_ja_assets/eventtag_gui.png)

図1：データの可視化とラベル付けを行うMATLAB GUI。`README.docx` に収録された原図を掲載している。

### 5.3 ラベル付けの操作

このGUIでは、ショートカットキーを使って手作業で注釈を付けることもできる。

1. 付けたいイベントの種類に対応するキーを押す。
2. 対象となる区間の開始点と終了点をクリックする。
3. 注釈が反映されると、対象サンプルの表示色が変わる。
4. ラベル付けが終わったら、**「Save mat-file」** ボタンを押す。
5. 新しいファイル名を付けて保存する。

| 表示色 | イベント | ショートカットキー |
| --- | --- | --- |
| 赤 | 固視（Fixation） | `F` |
| 緑 | サッカード（Saccade） | `S` |
| 黄 | サッカード後振動（PSO） | `G` |
| ピンク | 滑動性追従眼球運動（Smooth pursuit） | `P` |
| 黒 | 瞬目（Blink） | `B` |
| ターコイズ（水色） | 未定義（Undefined） | `U` |

表1：`EventTag.m` で手作業のラベル付けを行う際の色分けとショートカット。

保存時には、元のファイル名を `name` とすると、既定の候補として `name_labelled.mat` が提示される。

> 訳注：原文には `name_labelled.m` と記載されているが、`EventTag.m` の保存処理は `_labelled.mat` を指定している。本訳では実装に合わせて拡張子を修正した。

## 6. 注釈データの各フォルダについて

### 6.1 初期公開データ

対象：`annotated_data/originally uploaded data/`

このフォルダには、Anderssonらのアルゴリズム比較研究で使用したものより少し多くのデータと、異なるデータが含まれている。

誤って一部のファイルを公開してしまったが、透明性を確保するためにそのまま残している。利用者の目的には、通常はもう一方のフォルダにあるデータの方が適している。

> 訳注：「もう一方のフォルダ」は、次節の `data used in the article/` を指す。

### 6.2 論文で使用した注釈データ

対象：`annotated_data/data used in the article/`

このフォルダには、Anderssonらのアルゴリズム比較研究で使用したデータの部分集合のみが含まれている。研究結果を再現したい場合は、このフォルダを使用すること。

自分のアルゴリズムに入力する注釈データとして、より良いものを利用したい場合は、`fix_by_Zemblys2018/` フォルダの修正版も忘れずに取得すること。

### 6.3 Zemblys（2018）の指摘に基づく修正版

対象：`annotated_data/fix_by_Zemblys2018/`

元の注釈データには、注釈者による明らかな誤りがあった。このフォルダのファイルを取得し、対応する元のファイルと置き換えること。

## 7. MATLAB解析コードについて

対象：`matlab_analysis_code/`

このフォルダには、Anderssonら（2017）の論文で使用したMATLABコードの一部が含まれている。

**このコードは整理・整備が完了していない。完全に整ったコードを後で共有することよりも、現時点で共有することを優先して公開されている。**

スクリプト内の一部の値は、解析中に対話的に変更された可能性がある。そのため、一度実行するだけですべての結果が得られるコードとして扱わないこと。

`kappa.m` は別の著者がMATLAB File Exchangeで公開したものである。このコードを利用する際は、その著者を適切にクレジットすること。詳細は `.m` ファイル内の説明を参照すること。

> 訳注：同梱の [kappa.m](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_analysis_code/kappa.m) には、著者としてGiuseppe Cardillo、引用情報としてCardillo G.（2007）が記載されている。

## 8. ローカル環境で利用する際の補足

本節は翻訳者による補足である。

MATLABでGUIを起動する場合は、次のように作業ディレクトリを移動してから実行する。

```matlab
cd('/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_annotator');
EventTag
```

原本のデータは保持し、編集や補正の結果は別名・別ディレクトリに保存する。修正版を使う際は、次の対応を記録する。

| 項目 | ファイル |
| --- | --- |
| 置き換え対象 | `annotated_data/data used in the article/img/UH29_img_Europe_labelled_MN.mat` |
| 修正版 | `annotated_data/fix_by_Zemblys2018/UH29_img_Europe_labelled_FIX_MN.mat` |

原資料の「500 Hz」という記述やサンプルの対応関係については、ローカルの実データで注意を要する点が確認されている。データ件数、時間情報の不整合、全ゼロ行、注釈者間の対応、修正版の差分、Pythonでの読み込み例は、[データ概要レポート](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation_report_ja.md)を参照すること。

## 9. 翻訳元資料

| 原資料 | 本書への反映箇所 |
| --- | --- |
| [readme.md](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/readme.md) | 第1節、関連論文 |
| [README.docx](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/README.docx) | 第2〜5節、図1、表1 |
| [初期公開データのreadme.md](</media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/annotated_data/originally uploaded data/readme.md>) | 第6.1節 |
| [論文使用データのreadme.md](</media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/annotated_data/data used in the article/readme.md>) | 第6.2節 |
| [修正版のreadme.md](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/annotated_data/fix_by_Zemblys2018/readme.md) | 第6.3節 |
| [解析コードのreadme.txt](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_analysis_code/readme.txt) | 第7節 |

図1の画像ファイルは、同じ作業ディレクトリ内の `EyeMovementDetectorEvaluation_documentation_ja_assets/eventtag_gui.png` に保存している。
