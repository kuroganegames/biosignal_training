# EyeMovementDetectorEvaluation データ概要レポート

作成日：2026年11月14日  
調査対象：ローカルの `EyeMovementDetectorEvaluation/`  
対象コミット：`3e12416ab3fd6254c81811cf03f8e5d67c5d7129`

## 1. データセットの概要

**EyeMovementDetectorEvaluation は、視線の時系列から眼球運動イベントを検出・分類するアルゴリズムを評価するためのデータセットである。** 視線座標、瞳孔径、時刻情報に加え、2名の専門家によるサンプル単位のラベル、刺激画像・動画、MATLABの可視化・注釈ツールが収録されている。

中心となる研究は Andersson ら（2017）の眼球運動イベント検出アルゴリズム10種類の比較である。論文では、Lund大学の学生17名から得た34記録、103,872サンプルを使用し、2名の専門家の手作業による分類と比較している。静止画像だけでなく、動画や移動する点を見る状況も含むことが特徴である。[論文本文・Methods](https://link.springer.com/content/pdf/10.3758/s13428-016-0738-9.pdf)

本レポートでは、説明資料に記載された仕様と、ローカルファイルを実際に読み込んで確認した結果を区別する。原データの変更や補正は行っていない。

## 2. 収録条件とデータの位置づけ

| 項目 | 内容 |
| --- | --- |
| 計測装置 | SensoMotoric Instruments（SMI）の Hi-Speed 1250 |
| 計測対象 | 視線の水平・垂直座標、瞳孔径など |
| 使用する眼 | 論文では両眼計測のうち右眼を注釈・評価に使用 |
| 公称サンプリング周波数 | 500 Hz。ローカルの注釈データ165ファイルでも `sampFreq = 500` |
| 刺激 | 静止画像、動画、移動する点 |
| 注釈者 | `MN`、`RA` の2名 |
| 保存形式 | MATLABの `.mat` ファイル |
| 画面情報 | ローカルデータでは解像度1,024 × 768 px、物理寸法0.38 × 0.30 m、視距離0.67 m |

装置名の「1250」を、この公開データのサンプリング周波数と取り違えないこと。また、500 Hzというメタデータと時刻列が整合しないファイルがあり、時間を使う解析では第6節の確認が必要である。収録条件の出典は[同梱の説明資料](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/README.docx)と[原論文](https://link.springer.com/content/pdf/10.3758/s13428-016-0738-9.pdf)である。

## 3. ディレクトリ構成と収録規模

### 3.1 データの3つの区分

以下の件数は、対象コミットの `annotated_data/` 以下にある `.mat` ファイルを数えた結果である。

| ディレクトリ | ファイル数 | 内容・利用目的 |
| --- | ---: | --- |
| `originally uploaded data/` | 96 | 初期公開版。画像34、動画28、移動点34。論文に使用していない記録も含む |
| `data used in the article/` | 68 | 論文で使用した記録の注釈データ。論文再現時の基準 |
| `fix_by_Zemblys2018/` | 1 | 特定の注釈ミスを訂正した置き換え用ファイル |

これらは重複や修正版を含むため、合計165ファイルを165個の独立した記録として扱ってはいけない。初期公開版には誤って公開したファイルも残していると説明されており、用途に応じて論文用データと修正版を選ぶ。[初期公開版の説明](</media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/annotated_data/originally uploaded data/readme.md>)、[論文用データの説明](</media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/annotated_data/data used in the article/readme.md>)

### 3.2 論文用データの内訳

| 刺激 | サブディレクトリ | 記録数 | 注釈ファイル数 | 保存された行数の合計 | 全ゼロ行を除いた記録単位のサンプル数 |
| --- | --- | ---: | ---: | ---: | ---: |
| 静止画像 | `img/` | 14 | 28 | 127,700 | 63,849 |
| 移動点 | `dots/` | 11 | 22 | 21,995 | 10,994 |
| 動画 | `video/` | 9 | 18 | 58,071 | 29,029 |
| **合計** | — | **34** | **68** | **207,766** | **103,872** |

「記録」はファイル名から注釈者の接尾辞を除いて集計した。同じ記録に `MN` と `RA` の2ファイルが対応する。「保存された行数」は両者を合計した値であり、独立した観測数ではない。最右列は第6節で説明する全ゼロ行を読み込み後の配列から除き、各記録を1回だけ数えた実測値である。

### 3.3 関連ファイル

- `Stimuli/`：画像5点と動画4点。著作権上の理由で一部の刺激は含まれていないと説明資料に記載されている。
- `matlab_annotator/`：注釈・可視化GUIの `EventTag.m` と `EventTag.fig`、座標変換用の `pixels2degrees.m`。
- `matlab_analysis_code/`：検出処理、混同行列、Cohenのκ係数などの解析コードと、解析用の `20150807.mat`。この `.mat` は上記の注釈データ165ファイルには含めていない。

## 4. ファイル形式とラベルの意味

### 4.1 ファイル名と構造体

例：`UH29_img_Europe_labelled_MN.mat`

`img_Europe` は刺激の種別・名称、末尾の `MN` は注釈者を表す。移動点では `trial1` や `trial17`、動画では `video_BergoDalbana` などが使われる。被験者番号は先頭部分に含まれる数字で、論文用データでは17種類ある。`UH`、`UL`、`TH`、`TL` の接頭辞を含む文字列全体をそのまま別人のIDとすると、20種類となり人数を過大に数える。

注釈データの全165ファイルに `ETdata` 構造体があり、次の5フィールドを持つ。

| フィールド | 内容 |
| --- | --- |
| `sampFreq` | 公称サンプリング周波数（Hz） |
| `viewDist` | 眼から画面までの距離 |
| `screenDim` | 画面の物理寸法（m） |
| `screenRes` | 画面の解像度（px） |
| `pos` | サンプルごとの測定値・ラベルを格納した行列 |

今回の注釈ファイルでは、`pos` はすべて **N行 × 6列** だった。説明資料の基本形式は5列であり、注釈付きデータでは第6列が追加される。[データ形式の説明](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/README.docx)

| MATLABの列番号 | Pythonの列番号 | 内容 |
| ---: | ---: | --- |
| 1 | 0 | タイムスタンプ（マイクロ秒） |
| 2 | 1 | 水平方向の瞳孔径 |
| 3 | 2 | 垂直方向の瞳孔径 |
| 4 | 3 | 視線のx座標（画面上のpx） |
| 5 | 4 | 視線のy座標（画面上のpx） |
| 6 | 5 | 眼球運動イベントのラベル |

説明資料ではGUIに表示する垂直瞳孔径の単位をカメラ画素としている。瞳孔径をそのままmmとして解釈しないこと。視線座標も角度ではなく画素であり、視角への変換には画面寸法・解像度・視距離を使う。

### 4.2 ラベル一覧と分布

下表の件数は、**修正版を適用せず、全ゼロ行も除去していない論文用68ファイル**の第6列を集計した値である。注釈者2名分の延べ207,766行に対する割合であり、イベントの個数ではない。

| 値 | 名称 | 意味 | サンプル数 | 割合 |
| ---: | --- | --- | ---: | ---: |
| 1 | Fixation／固視 | 視線が比較的安定している区間 | 123,902 | 59.64% |
| 2 | Saccade／サッカード | 視線位置が急速に変わる区間 | 15,455 | 7.44% |
| 3 | Post-saccadic oscillation／PSO | サッカード直後に見られる信号の振動 | 8,849 | 4.26% |
| 4 | Smooth pursuit／滑動性追従眼球運動 | 動く対象を滑らかに追う運動 | 50,373 | 24.25% |
| 5 | Blink／瞬目 | まばたきに対応する区間 | 8,690 | 4.18% |
| 6 | Undefined／未定義 | 他の分類に当てはまらない区間 | 497 | 0.24% |

ラベル番号は[説明資料](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/README.docx)および[注釈コード](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_annotator/EventTag.m)と照合した。割合は四捨五入により合計が100%と一致しない場合がある。固視の割合が大きいため、分類性能を評価する際は全体の正解率に加えてクラス別の結果を見る必要がある。

## 5. 修正版の内容と選び方

`fix_by_Zemblys2018/UH29_img_Europe_labelled_FIX_MN.mat` は、論文用の `img/UH29_img_Europe_labelled_MN.mat` に対応する修正版である。[修正版の説明](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/annotated_data/fix_by_Zemblys2018/readme.md)

両ファイルを比較したところ、形状はともに4,988行 × 6列で、第1〜5列は完全に一致した。変更は第6列の75サンプルだけで、ラベルが **2（サッカード）から1（固視）** に訂正されていた。

- 論文の公開時点のラベルを基準とする比較では、未修正版を使用したことを明記する。
- 誤注釈を訂正したデータを使用する場合は、対応するMNファイルを修正版で置き換えて読み込む。修正版を新しい独立記録として追加しない。
- 原本は保持し、読み込み時の対応表や作業用コピーで切り替える。使用したコミット、ファイル一覧、修正版の適用有無を記録する。

## 6. 実データで確認した注意点

以下は論文用68ファイルをPython・SciPyで読み込んだ確認結果である。

### 6.1 時刻列とサンプリング周波数

移動点の22ファイルすべてでタイムスタンプ列に `NaN` があり、うち16ファイルでは列全体が `NaN` だった。また、画像・動画の計6ファイルでは、隣接時刻差の中央値が5,000 µs（5 ms）であり、`sampFreq = 500` から期待される2 msと一致しなかった。

5 msが観測されたのは、`UH47_img_Europe`、`UL47_img_konijntjes`、`UH47_video_BergoDalbana` の各MN・RAファイルである。時刻差だけから一律にメタデータを200 Hzへ変更する根拠までは確認できていない。速度やイベント持続時間を計算する前に、使用する時間軸と不整合の扱いを決め、仮定を記録する必要がある。

### 6.2 全ゼロ行と注釈者間の対応

34組のMN・RAファイルのうち5組で、保存されている行数が一致しなかった。さらに、68ファイル全体に、第1〜5列がすべて0の行が計22行あった。

確認用にこれらの全ゼロ行を配列上で除くと、**34組すべてで第1〜5列が一致**し、各記録を1回数えた合計は103,872サンプルとなった。刺激別の内訳も論文の値と一致した。これは行数差を理解するための検証結果であり、原ファイルへの補正は行っていない。

解析コードは注釈GUIの不具合を補正する目的で `POScleaner` を呼んでいるが、その関数本体は同梱されていない。注釈者間の一致率を計算する場合、行番号だけで無条件に対応づけず、入力列の一致を確認すること。[解析コード](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_analysis_code/mainDetection.m)

### 6.3 評価・学習での扱い

同じ記録のMN版とRA版は、同じ視線に対する別々の注釈である。学習用と評価用に分割する場合は、同じ記録や被験者が双方へ混入しないようにする。注釈者ごとに評価するか、注釈を統合するかも明示する。

また、xまたはy座標が0の行は計3,950行あり、上記の「第1〜5列がすべて0」の22行とは別の集計条件である。座標0を一律に欠損と決めず、瞳孔径や瞬目ラベルなどと併せて扱いを確認する。

## 7. 読み込みと利用の進め方

今回の利用では、まず論文用データを基準にファイル一覧を固定し、修正版の適用方針と時間軸・異常行の扱いを決める。その後、静止画像・動画・移動点を分けて可視化し、ラベルと信号の関係を確認するとよい。

### Pythonでの読み込み例

以下はSciPyが利用できる環境で実行する。修正版1ファイルの構造確認を行う例であり、全データの前処理は行わない。

```python
from pathlib import Path

import numpy as np
from scipy.io import loadmat

workspace = Path("/media/kurogane/backup/bisignal_training/work_sim_2")
path = (
    workspace / "EyeMovementDetectorEvaluation" / "annotated_data"
    / "fix_by_Zemblys2018" / "UH29_img_Europe_labelled_FIX_MN.mat"
)
et = loadmat(path, simplify_cells=True)["ETdata"]
pos = np.asarray(et["pos"])

timestamp_us = pos[:, 0]
gaze_xy_px = pos[:, 3:5]
labels = pos[:, 5].astype(int)

assert pos.shape == (4988, 6)
assert set(np.unique(labels)) <= {1, 2, 3, 4, 5, 6}
print("shape:", pos.shape, "nominal sampling frequency:", et["sampFreq"])
print("label counts:", np.unique(labels, return_counts=True))
print("all-zero sensor rows:", np.all(pos[:, :5] == 0, axis=1).sum())
```

### MATLABでの可視化

```matlab
cd('/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_annotator');
EventTag
```

GUIの「Load mat-file」で対象ファイルを選択すると、視線座標、速度、瞳孔径、ラベルなどを確認できる。編集結果は新しい名前で保存する。`mainDetection.m` は不足する補助関数や検出器を参照しており、そのまま一括実行して論文結果を再現できる完成済みパイプラインではない。[解析コードの注意書き](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/matlab_analysis_code/readme.txt)

## 8. 出典・確認方法

ローカルの説明資料、各データディレクトリのREADME、MATLABコードを確認し、`annotated_data/` の全165ファイルをSciPy 1.16.1・NumPy 2.3.2で読み込んだ。件数、形状、メタデータ、ラベル分布を集計し、論文用データについてMN・RA間と修正版との差分を比較した。MATLAB GUIや検出アルゴリズム自体の動作検証は実施していない。

[同梱の説明資料](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/README.docx)は、ソフトウェア・データ・刺激をGNU GPL v3で公開していると記載し、データ利用時に以下の3論文を引用するよう求めている。[LICENSE](/media/kurogane/backup/bisignal_training/work_sim_2/EyeMovementDetectorEvaluation/LICENSE)および各コードの著者表記も参照する。

1. Andersson, R., Larsson, L., Holmqvist, K., Stridh, M., & Nyström, M. (2017). *One algorithm to rule them all? An evaluation and discussion of ten eye movement event-detection algorithms.* Behavior Research Methods, 49(2), 616–637. [出版元の論文ページ](https://link.springer.com/article/10.3758/s13428-016-0738-9)
2. Larsson, L., Nyström, M., & Stridh, M. (2013). *Detection of saccades and postsaccadic oscillations in the presence of smooth pursuit.* IEEE Transactions on Biomedical Engineering, 60(9), 2484–2493. [DOI: 10.1109/TBME.2013.2258918](https://doi.org/10.1109/TBME.2013.2258918)
3. Larsson, L., Nyström, M., Andersson, R., & Stridh, M. (2015). *Detection of fixations and smooth pursuit movements in high-speed eye-tracking data.* Biomedical Signal Processing and Control, 18, 145–152. [Lund大学の論文情報](https://portal.research.lu.se/en/publications/detection-of-fixations-and-smooth-pursuit-movements-in-high-speed/)
