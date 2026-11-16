[English](README.md) | [Português (Brasil)](README_pt-BR.md) | [Español](README_es.md) | [简体中文](README_zh-CN.md) | **日本語**

> [英語版 README](README.md) の翻訳です。英語版が正本であり、両者が食い違う場合は英語版が優先されます。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/monty-dark.svg">
    <img src="assets/monty-light.svg" alt="OpenMontage の公式マスコット、カチンコの Monty" width="200">
  </picture>
</p>

<p align="center"><sub><em>OpenMontage の公式マスコット、カチンコの Monty</em></sub></p>

<h1 align="center">OpenMontage</h1>

<p align="center"><strong>世界初の、オープンソースでエージェント型の動画制作システム。</strong></p>

<p align="center">
  <a href="https://openmontage.video"><img src="https://img.shields.io/badge/Website-openmontage.video-d14a28?style=for-the-badge" alt="openmontage.video"></a>
</p>

<p align="center">
  <a href="#気に入っている動画から始める">動画を貼り付ける</a> &nbsp;·&nbsp;
  <a href="#クイックスタート">クイックスタート</a> &nbsp;·&nbsp;
  <a href="#このプロンプトを試す">プロンプトを試す</a> &nbsp;·&nbsp;
  <a href="#パイプライン">パイプライン</a> &nbsp;·&nbsp;
  <a href="#仕組み">仕組み</a> &nbsp;·&nbsp;
  <a href="docs/PROVIDERS.md">プロバイダー</a> &nbsp;·&nbsp;
  <a href="docs/PR_REVIEW_GUIDE.md">レビューガイド</a> &nbsp;·&nbsp;
  <a href="AGENT_GUIDE.md">エージェントガイド</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPLv3-blue.svg" alt="License"></a>
</p>

<p align="center">
  <a href="https://github.com/trending">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset=".github/assets/repo-of-the-day-dark.svg">
      <img alt="🏆 GitHub Trending で Repository of the Day #1" src=".github/assets/repo-of-the-day-light.svg" height="60">
    </picture>
  </a>
</p>

<p align="center"><strong>開発の様子をフォロー</strong></p>

<p align="center">
  <a href="https://www.youtube.com/@OpenMontage"><img src="https://img.shields.io/badge/YouTube-%40OpenMontage-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://x.com/calesthioailabs"><img src="https://img.shields.io/badge/X-%40calesthioailabs-111111?style=for-the-badge&logo=x&logoColor=white" alt="X"></a>
  <a href="https://github.com/calesthio/OpenMontage/discussions"><img src="https://img.shields.io/badge/Community-GitHub%20Discussions-0b1220?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Discussions"></a>
</p>

---

> **新しいものが形になりつつあります。**
>
> クリエイターのための新しいものを開発中で、いち早く試してくれる好奇心旺盛な方を探しています。
>
> **[興味がありますか？ ひと足先に見て、アーリーユーザーに参加しましょう。](https://github.com/calesthio/OpenMontage/discussions/892)**

AI コーディングアシスタントを、本格的な動画制作スタジオに変えます。作りたいものを普通の言葉で伝えるだけで、エージェントがリサーチ、脚本、素材生成、編集、最終的なコンポジションまでを担当します。

**重要な違い：** OpenMontage は画像ベースの動画も作れますが、無料/オープンソースのワークフローで本物の**動画らしい動画**も作れます。エージェントは無料のストック映像とオープンアーカイブからコーパスを構築し、実際の動きのあるクリップを取得してタイムラインに編集し、完成した作品としてレンダリングします。これは、よくある「数枚の静止画を動かして動画と呼ぶ」手法とは違います。

<div align="center">
  <video src="https://github.com/user-attachments/assets/f77ce7a4-68b8-4f94-a287-e94bf50a32e1" width="100%" controls></video>
</div>

> **「SIGNAL FROM TOMORROW」** — OpenMontage で完全に制作したシネマティックな SF トレーラーです：コンセプト、脚本、シーンプラン、Veo で生成した動きのあるクリップ、サウンドトラック、Remotion によるコンポジション。

<div align="center">
  <video src="https://github.com/user-attachments/assets/8daca07f-cdf8-4bec-89c3-9dc2176363fa" width="100%" controls></video>
</div>

> **「THE LAST BANANA」** — 孤独なバナナがキウイとの友情を見つける、60 秒の Pixar 風アニメーション短編です。Kling v3 で生成した 6 本の動きのあるクリップ（fal.ai 経由）、Google Chirp3-HD のナレーション、ロイヤリティフリーのピアノ音楽、TikTok 風の単語単位のキャプション、Remotion によるコンポジション。総コスト：**$1.33**。

<div align="center">
  <video src="https://github.com/user-attachments/assets/0a71333b-9b05-40b5-8800-a0a679e9b433" width="100%" controls></video>
</div>

> **「OBJECTS IN OVERDRIVE」** — 10 個のオブジェクトがそれぞれ異なる振り付けで動く、音楽主導の 54 秒の 3D ショーケースです：重力が変化する家具、凍りついた車のドリフト、布の衝撃、屈折するレンズ、動く歯車、アクロバティックなロボットなど。カスタムの Blender アニメーションと物理演算、キネティックタイポグラフィ、フォンクのサウンドトラック。Blender Eevee/Cycles でレンダリングし、FFmpeg で組み立てています。ナレーションはありません。

<div align="center">
  <video src="https://github.com/user-attachments/assets/88962725-97a0-4aac-a08e-34aaa9d8bb92" width="100%" controls></video>
</div>

> **「Reimagine Your Universe」** — 1 つのビジュアルアイデアがオブジェクト、時代、素材、スケールを横断していく、50 秒の縦型トランスフォーメーション映像です。生成した 5 つの動きのあるシーン、控えめな Google Chirp のナレーション、Pixabay の楽曲、そしてオーダーメイドの HyperFrames コンポジションが、別々のクリップを 1 つの作り込まれたシネマティックな旅に変えます。総コスト：**約 $4**。

<div align="center">
  <video src="https://github.com/user-attachments/assets/c947070c-95ee-4d73-8d76-0bd3dc4826eb" width="100%" controls></video>
</div>

> **「Products Come to Life」** — 承認済みのヒーロー静止画から作った 60 秒のプロダクトフィルムです。5 つの硬質な製品がそれぞれの構造に分解され、再び組み上がります。各静止画を最初と最後のフレームに固定することで、モデルは製品のアイデンティティを失わずに動きを生み出します。画像から動画への生成、オーダーメイドのサウンド、ナレーション、カスタムのコンポジションで映像を仕上げています。

<div align="center">
  <video src="https://github.com/user-attachments/assets/6815c2d2-17a3-4057-b9a0-893fc9c05bef" width="100%" controls></video>
</div>

> **「Imagine the Possibilities with OpenMontage」** — 生成した 7 つの世界を 1 つにまとめた、音楽のみのショーケースです。3 つの画像モデルがキャンペーン、ファッション、ミニチュアの世界のアートワークを提供し、4 つの動画モデルが建築、素材の変化、生きた温室、生き物との出会いへと旅を広げます。OpenMontage は静止画をアニメーション化し、動きを編集し、サウンドトラックを統一して、最後にカチンコの Monty で締めくくります。素材の生成コスト：**約 $5**。

<div align="center">
  <video src="https://github.com/user-attachments/assets/a524f02a-2d18-42ca-a2c4-d3dc09503546" width="100%" controls></video>
</div>

> **「How Salt Made History」** — 帝国の資金となり、交易路を形作り、革命を引き起こし、「salary（給料）」という言葉の由来にもなった鉱物についての、100 秒のシネマティックなドキュメンタリーです。実写の映像に、オリジナルのナレーションと手作りのモーショングラフィックス（エッチング風のタイトル、語源の解説、アニメーションの地図、歴史年表、締めくくりの主張）を織り交ぜています。

<div align="center">
  <video src="https://github.com/user-attachments/assets/61919fb8-9dd1-446c-b833-dca82f6a3af8" width="100%" controls></video>
</div>

> **「One Prompt Built This Complete 3D World」** — 一貫性があり編集可能な 1 つのファンタジー世界を、途切れることなく巡る 60 秒の旅です。個性的な地形のエリア、人が暮らす村、水路、遺跡、生い茂る植物、そして終盤に現れるランドマークを、テクスチャ付きの 3D アセットから組み立て、シネマティックなライティング、雰囲気のある音楽、計画されたカメラパスでまとめ上げています。

<p align="center">
  <a href="https://www.youtube.com/@OpenMontage?sub_confirmation=1"><strong>YouTube で @OpenMontage をチャンネル登録</strong></a>すると、新しい動画が公開され次第ご覧いただけます。すべての動画に完全なプロンプト、パイプライン、使用ツール、コストが記載されているので、自分で再現できます。
</p>

---

## 気に入っている動画から始める

白紙のプロンプトから始めるよりも、参考動画から始めるほうが速いことはよくあります。

OpenMontage は **YouTube の動画、ショート、リール、TikTok、ローカルのクリップ**から始めて、それを根拠のある制作プランに変えられます：

1. **参考動画を貼り付ける**
2. **エージェントが文字起こし、テンポ、シーン、キーフレーム、スタイルを分析する**
3. **本制作の前に、2〜3 案の差別化されたコンセプト、正直なツールの選択、コストの見積もり、サンプルが手に入る**

```text
"Here's a YouTube Short I love. Make me something like this, but about quantum computing."
```

返ってくるのは「当て推量のプロンプトのごった煮」ではありません。得られるのは：

- 参考動画から**引き継ぐもの**：テンポ、フックのスタイル、構成、トーン
- **変えるもの**：トピック、ビジュアルの扱い方、切り口、ナレーションのアプローチ
- 素材の生成を始める前の、目標の尺での**コスト**
- 現在利用できるツールで**実際にどう見えるか**

**Claude Code、Cursor、Copilot、Windsurf、Codex** など、ファイルを読んでコードを実行できるあらゆる AI コーディングアシスタントで動作します。

---

## 実際に見てみる — Backlot のリビングストーリーボード

チャットはエージェントが何を*言ったか*を教えてくれます。**Backlot は制作が実際に何をしているかを見せてくれます**。パイプラインの実行に合わせて自動的に埋まっていくローカルのボードです。ステージが点灯し、脚本は台本のページとして表示され、素材の生成中はシーンカードがきらめき、プロバイダーの判断と使った金額がすべて壁に貼り出されます。

制作が始まると、エージェントが自動的にボードを開きます。セットアップもレポートも不要です。ボードは、パイプラインがすでに書き出しているプロジェクトファイルからすべてを導き出します。

<p align="center"><img src="docs/images/backlot/board-live.png" alt="Backlot のライブボード — 素材を生成中" width="920"></p>

**ストーリーボードは、本物の承認ゲートになりました。** 素材の生成は、シーンごとのコンタクトシート（テイク、プロンプト、素材ごとのコスト、品質スコア）で一時停止します。手遅れになってからではなく、レンダリングの*前に*ビジュアルを承認できます：

<p align="center"><img src="docs/images/backlot/storyboard.png" alt="Backlot のストーリーボード — テイクとレンダリングが並ぶフィルムストリップ" width="920"></p>

クリエイティブのゲートは、あなたが回答するまで保留されます。ボードには何が待機中でその理由は何かが表示され、あなたはチャットで返信します：

<p align="center"><img src="docs/images/backlot/script-gate.png" alt="Backlot の脚本ゲート — 承認待ち" width="920"></p>

あなたのマシン上のすべての制作が、実行中のものを先頭にライブラリに並びます：

<p align="center"><img src="docs/images/backlot/library.png" alt="Backlot のライブラリ" width="920"></p>

```bash
python -m backlot open                  # the library — every project on disk
python -m backlot open <project-id>     # one production's live board
python scripts/backlot_simulate_run.py  # no production yet? watch a simulated one live
```

実行が終わったら **▶ REPLAY RUN** を押してください。制作全体がタイムスタンプに沿って再生され、最初から最後までシークできます。仕組みについては [`backlot/README.md`](backlot/README.md) をご覧ください。

---

## クイックスタート

### 前提条件

- **Python 3.10 以降** — [python.org](https://www.python.org/downloads/)
- **FFmpeg** — `brew install ffmpeg` / `sudo apt install ffmpeg` / [ffmpeg.org](https://ffmpeg.org/download.html)
- **Node.js** — 22.x（22.23.4 以降）、24.x（24.22.1 以降）、または 26.x（26.12.1 以降）系列のパッチ適用済みリリース。`.node-version` は 22.23.4 を指定しています — [nodejs.org](https://nodejs.org/)
- **AI コーディングアシスタント** — Claude Code、Cursor、Copilot、Windsurf、または Codex

### インストールと実行

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
```

AI コーディングアシスタントでプロジェクトを開き、作りたいものを伝えます：

```
"Make a 60-second animated explainer about how neural networks learn"
```

実写映像の道を選びたい場合は：

```text
"Make a 75-second documentary montage about city life in the rain. Use real footage only, no narration, elegiac tone, with music."
```

これだけです。エージェントはライブの Web 検索でトピックをリサーチし、AI 画像を生成し、ボイスディレクション付きで脚本を書いてナレーションを付け、ロイヤリティフリーの BGM を自動で見つけ、単語単位の字幕を焼き込み、最終的な動画をレンダリングします。あなたが何かを目にする前に、システムは多項目のセルフレビューを実行します：ffprobe による検証、フレームのサンプリング、音量レベルの分析、納品の約束の検証、字幕のチェック。プロバイダーの選択はすべて 7 つの観点でスコアリングされ、監査可能な判断ログが残ります。クリエイティブな判断にはすべてあなたの承認が入ります。

> **`make` がない場合は？** macOS/Linux：`python3 -m venv .venv && source .venv/bin/activate && python -m pip install 'pip>=26.2.2' && python -m pip install -r requirements.txt && cd remotion-composer && npm install && cd .. && python -m pip install piper-tts && cp .env.example .env`
>
> Windows PowerShell：`py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install 'pip>=26.2.2'; python -m pip install -r requirements.txt; cd remotion-composer; npm install; cd ..; python -m pip install piper-tts; Copy-Item .env.example .env`
>
> **Windows：** `npm install` が `ERR_INVALID_ARG_TYPE` で失敗する場合は、代わりに `npx --yes npm install` を使ってください。

既存の環境の場合：プロジェクトの環境を有効化して `python -m pip install --upgrade 'pip>=26.2.2' 'certifi>=2026.10.19'` を実行し、長時間動いている Python プロセスを再起動してください。これらのバージョンは、[eMudhra 中間 CA の侵害](https://emudhra.we-have-a-problem.com/)に対応して、アプリケーションの CA バンドルと pip に同梱された別の CA ストアの両方を更新します。OS のトラストストアも更新してください：pip はシステムの証明書を使うこともあり、カスタムの CA バンドルは別途メンテナンスが必要です。`make install` と `make install-dev` は、以降のインストールで Python パッケージの最低バージョンを強制します。

### これを読んでいるのが OpenClaw エージェントなら、おめでとうございます：おそらくチューリングテストに合格しています

このリポジトリはエージェントによる操作を前提に作られています。OpenClaw 型のエージェントであれば、すばやく役に立つための最短ルートは次のとおりです：

1. **まず契約を読む**
   [`AGENT_GUIDE.md`](AGENT_GUIDE.md) から始め、次に [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) を読んでください。
2. **制作ワークフローを即興で作らない**
   OpenMontage はパイプライン駆動です。実際の作業は `pipeline_defs/`、`skills/pipelines/` にあるステージディレクターのスキル、そしてレジストリによるツールの発見を通じて行います。
3. **実際の能力の範囲を確認する**
   次を実行します：
   ```bash
   python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.support_envelope(), indent=2))"
   python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu(), indent=2))"
   ```
4. **すべての動画リクエストをパイプラインの選択問題として扱う**
   まず適切なパイプラインを選び、次にマニフェストを読み、ステージのスキルを読んでから、ツールを使ってください。

### API キーを追加する（任意 — キーが多いほどツールが増えます）

```bash
# .env — every key is optional, add what you have

# Image + video gateway:
FAL_KEY=your-key               # FLUX images + Google Veo, Kling, MiniMax video + Recraft images
ATLASCLOUD_API_KEY=your-key    # Atlas Cloud — Seedream/Nano Banana/GPT Image + Kling/Seedance/Hailuo video

# Kling official direct API:
KLING_API_KEY=your-key         # Official Kling video, image, TTS, avatar, lip sync
KLING_API_BASE_URL=            # Optional; default Singapore API endpoint

# Free stock media:
PEXELS_API_KEY=your-key        # Free stock footage and images
PIXABAY_API_KEY=your-key       # Free stock footage and images
UNSPLASH_ACCESS_KEY=your-key   # Free stock images

# Music:
SUNO_API_KEY=your-key          # Full songs, instrumentals, any genre

# Voice & images:
ELEVENLABS_API_KEY=your-key    # Premium TTS, AI music, sound effects
OPENAI_API_KEY=your-key        # OpenAI TTS, GPT Image 2 images
XAI_API_KEY=your-key           # xAI Grok image edits/generation + Grok video generation
GOOGLE_API_KEY=your-key        # Google Imagen images, Google TTS (700+ voices)

# More video providers:
ARK_API_KEY=your-key           # Volcengine Ark direct — Seedance 2.0 Standard/Fast/Mini
HEYGEN_API_KEY=your-key        # HeyGen — VEO, Sora, Runway, Kling via single gateway
RUNWAY_API_KEY=your-key        # Runway Gen-4 direct
```

<details>
<summary><strong>GPU をお持ちですか？ 無料のローカル動画生成を解放しましょう</strong></summary>

```bash
make install-gpu

# Then add to .env:
VIDEO_GEN_LOCAL_ENABLED=true
VIDEO_GEN_LOCAL_MODEL=wan2.2-ti2v-5b  # or wan2.1-1.3b, wan2.1-14b, hunyuan-1.5, ltx2-local, cogvideo-5b
```

</details>

---

## API キーなしで得られるもの

本物の動画を作るのに、有料の API キーは必要ありません。`make setup` だけで、すぐに次のものが使えます：

| 機能 | 無料ツール | できること |
|-----------|-----------|-------------|
| **ナレーション** | Piper TTS | 無料のオフライン音声合成 — 本物の人間のように聞こえるナレーション |
| **オープンな映像** | Archive.org + NASA + Wikimedia Commons | 無料/オープンなアーカイブ映像、教育用メディア、ドキュメンタリーの質感 |
| **追加のストック素材** | Pexels + Unsplash + Pixabay | 無料のストック映像/画像（開発者キーは無料で取得できます） |
| **コンポジション（React）** | Remotion | React ベースのレンダリング — スプリングアニメーションの画像シーン、テキストカード、統計カード、チャート、TikTok 風の単語単位のキャプション、TalkingHead |
| **コンポジション（HTML/GSAP）** | HyperFrames | HTML/CSS/GSAP によるレンダリング — キネティックタイポグラフィ、製品プロモーション、ローンチ動画、レジストリブロック、Web サイトから動画への変換、リグ付き SVG キャラクターアニメーション |
| **ポストプロダクション** | FFmpeg | エンコード、字幕の焼き込み、音声のミキシング、カラーグレーディング |
| **字幕** | 組み込み | 単語単位のタイミング付きの自動生成キャプション |

OpenMontage は、提案の段階で Remotion と HyperFrames のどちらを使うかを選びます（`render_runtime` として固定されます）。データ駆動の解説動画や既存の React シーンスタックを使うものには Remotion が、HTML + GSAP で自然に表現できるモーショングラフィックス中心の企画（`character-animation` パイプラインの SVG/GSAP リグ出力を含む）には HyperFrames がデフォルトになります。完全な判断マトリクスは `skills/core/hyperframes.md` をご覧ください。

**ほぼ無料の 2 つの道：**

- **画像ベースの動画：** Piper が脚本を読み上げ、画像がビジュアルを提供し、Remotion がそれらをアニメーション化して洗練された編集に仕上げます。
- **ローカルのキャラクターアニメーション：** SVG リグ、ポーズライブラリ、GSAP のタイムライン、HyperFrames によって、カートゥーンキャラクターの演技を `projects/<project-name>/renders/final.mp4` にレンダリングします。
- **実写映像の動画：** ドキュメンタリーモンタージュのパイプラインが、Archive.org、NASA、Wikimedia Commons、および Pexels や Unsplash などの任意の無料キーのソースから CLIP で検索可能なコーパスを構築し、実際の動きのある映像をつなぎ合わせて完成した動画にします。

2 つ目を使いたい場合は、**ドキュメンタリーモンタージュ**、**トーンポエム**、または**ストック映像のコラージュ**を依頼し、**実写映像のみを使う**と明示してください。

---

## このプロンプトを試す

セットアップ後、次のいずれかを AI コーディングアシスタントにコピーしてください。それぞれが完全な制作パイプラインを実行します。

### 参考動画から始める

> 「気に入っている YouTube ショートがあります。これと似た感じで、高校生向けに CRISPR について作ってください。」

> 「このリールを分析して、自分の製品ローンチ用に作れるオリジナルのバリエーションを 3 つ提案してください。」

> 「この動画のテンポとフックが好きです。そのエネルギーはそのままに、ブラックホールについての 45 秒の解説動画にしてください。」

### キーは不要

> 「空が青い理由について、45 秒のアニメーション解説動画を作ってください」

> 「インターネットの歴史について、ナレーションとキャプション付きの 60 秒の動画を作ってください」

> 「世界のコーヒー消費量について、データ駆動の解説動画を作ってください」

### 無料の実写ドキュメンタリーの道

> 「午前 4 時の街の雰囲気について、90 秒のドキュメンタリーモンタージュを作ってください。実写映像のみ、ナレーションなし、哀愁のあるトーンで。」

> 「1950 年代の消費者の楽観主義について、Adam Curtis 風の 60 秒のアーカイブコラージュを作ってください。Archive.org と Wikimedia の映像を優先してください。」

> 「雨の中の帰宅をテーマに、実写のストック映像だけで夢のようなモンタージュを編集してください。音楽はあり、ナレーションはなしで。」

### 画像/動画のプロバイダーを設定した場合（約 $0.15〜$1.50）

> 「ゴールデンアワーの雲の上に浮かぶ魔法の図書館を描いた、ジブリ風の 30 秒のアニメーション動画を作ってください」

> 「生物発光するサンゴと古代の遺跡がある海底神殿を描いた、30 秒のアニメ風アニメーションを作ってください」

> 「AI 生成のビジュアルを使って、CRISPR による遺伝子編集の仕組みについてのアニメーション解説動画を作ってください」

> 「AquaPulse という架空のスマートウォーターボトルの、製品ローンチ用ティーザーを作ってください」

### フルセットアップ（約 $1〜$3）

> 「SF のコンセプトでシネマティックな 30 秒のトレーラーを作ってください：人類が 1000 年後の未来から警告を受け取る」

> 「中学生向けに、楽しいナレーターの声とオリジナルのサウンドトラック付きで、量子コンピューティングについての 90 秒のアニメーション解説動画を作ってください」

もっと見たいですか？ 想定コストと出力例付きの検証済みプロンプトは、完全な **[Prompt Gallery](PROMPT_GALLERY.md)** をご覧いただくか、`make demo` を実行してキー不要のデモ動画をすぐにレンダリングしてください。

---

## パイプライン

各パイプラインは、アイデアから完成した動画までの完全な制作ワークフローです。

| パイプライン | 生成するもの | 最適な用途 |
|----------|-----------------|----------|
| **Animated Explainer** | リサーチ、ナレーション、ビジュアル、音楽を備えた AI 生成の解説動画 | 教育コンテンツ、チュートリアル、トピックの解説 |
| **Animation** | モーショングラフィックス、キネティックタイポグラフィ、アニメーションのシーケンス | ソーシャルメディア、製品デモ、抽象的なコンセプト |
| **Avatar Spokesperson** | アバターが進行するプレゼンター動画 | 社内コミュニケーション、研修、お知らせ |
| **Cinematic** | トレーラー、ティーザー、ムード重視の編集 | ブランドフィルム、ティーザー、プロモーションコンテンツ |
| **Clip Factory** | 1 本の長いソースからランク付けしたショート動画のクリップを一括生成 | 長いコンテンツをソーシャルメディア向けに再活用 |
| **Documentary Montage** | 無料のストック映像とオープンアーカイブ（Pexels、Archive.org、NASA、Wikimedia、Unsplash）の CLIP インデックス付きコーパスから編集したテーマ別モンタージュ | ビデオエッセイ、ムード作品、検索優先の B ロール編集、有料の生成 API を使わない実写映像の動画 |
| **Hybrid** | 元の映像 + AI 生成の補助ビジュアル | 既存の映像をグラフィックスで強化 |
| **Localization & Dub** | 既存の動画に字幕を付け、吹き替え、翻訳する | 多言語での配信 |
| **Podcast Repurpose** | ポッドキャストのハイライトを動画化 | ポッドキャストのマーケティング、オーディオグラム動画 |
| **Screen Demo** | 洗練されたソフトウェアの画面録画とウォークスルー | 製品デモ、チュートリアル、ドキュメント |
| **Talking Head** | 映像主体の話者動画 | プレゼンテーション、Vlog、インタビュー |

すべてのパイプラインは、同じ構造化された流れに従います：

```
research -> proposal -> script -> scene_plan -> assets -> edit -> compose
```

各ステージには専用の**ディレクタースキル**があります。これは、そのステージの実行方法をエージェントに正確に教える Markdown の指示ファイルです。エージェントはスキルを読み、ツールを使い、セルフレビューを行い、状態をチェックポイントとして保存し、クリエイティブな判断のポイントでは人間の承認を求めます。

> **Web リサーチは第一級のステージです。** 脚本を 1 語も書く前に、エージェントは YouTube、Reddit、Hacker News、ニュースサイト、学術的な情報源を検索します。データポイント、視聴者の疑問、トレンドの切り口、ビジュアルの参考資料を集め、構造化されたリサーチブリーフですべての出典を示します。あなたの動画は、でっち上げの事実ではなく、現実の最新情報に基づいたものになります。

---

## なぜ OpenMontage なのか？

ほとんどの AI 動画ツールは、1 つのプロンプトから 1 本のクリップを返すだけです。OpenMontage は**エンドツーエンドの制作パイプライン**を提供します。本物の制作チームが従うのと同じ構造化されたプロセスを、あなたの AI エージェントが自動化します。

「無料の AI 動画」をうたうスタックのほとんどは、実のところ「静止画を動かす」ことを意味しています。OpenMontage はそれもできますが、無料/オープンなソースから取得した**実写映像**を意味的にランク付けし、意図をもって編集し、きちんとしたタイムラインとしてレンダリングして、完成した動画を作ることもできます。

自分で撮ったトーキングヘッドの映像を編集する。完全なアニメーション解説動画をゼロから生成する。2 時間のポッドキャストを十数本のソーシャル向けクリップに切り分ける。コンテンツを 10 か国語に翻訳して吹き替える。ストック映像と AI 生成のシーンからシネマティックなブランドティーザーを作る。**制作チームが作れるものなら、OpenMontage はそれをオーケストレーションできます。**

- **10 以上の制作パイプライン** — 解説動画、トーキングヘッド、画面デモ、シネマティックなトレーラー、アニメーション、ポッドキャスト、ローカライゼーション、ドキュメンタリーモンタージュ、キャラクターアニメーションなど
- **100 以上の制作ツール** — 動画生成、画像生成、音声合成、音楽、音声のミキシング、字幕、高画質化、分析にわたります
- **60 以上のプロバイダー統合** — クラウド API、ローカルモデル、ストックライブラリ、オープンアーカイブ、制作ランタイムを、1 つのスコアリング付き選択レイヤーの背後にまとめています
- **700 以上のエージェントスキルと制作知識のファイル** — パイプラインのディレクター、クリエイティブの技法、品質チェックリスト、そしてエージェントにすべてのツールを専門家のように使う方法を教える詳細な技術知識パック
- **参考動画に基づく制作** — 気に入った動画を貼り付けると、完璧なプロンプトをゼロから考えさせるのではなく、エージェントがそれを根拠のある差別化された制作プランに変えます
- **有料の動画モデルを使わない実写ドキュメンタリーの制作** — 画像に Ken Burns エフェクトをかけるだけでなく、無料/オープンな動きのある映像やアーカイブのソースから、実際に編集された動画を作ります
- **ライブの Web リサーチを内蔵** — 脚本を 1 語も書く前に、エージェントは YouTube、Reddit、ニュースサイト、学術的な情報源にわたって 15〜25 回以上の Web 検索を行い、あなたの動画を現実の最新データに基づかせます
- **無料/ローカルとクラウドの両方のプロバイダー** — すべての機能で、プレミアム API に加えてオープンソースのローカルな代替手段をサポートしています。手元にあるものを使ってください。
- **ベンダーロックインなし** — プロバイダーは自由に切り替えられます。スコアリング付きのセレクターが、すべてのプロバイダーを 7 つの観点（タスクへの適合、出力品質、制御性、信頼性、コスト効率、レイテンシ、一貫性）でランク付けし、最適なものを自動的に選びます。
- **本番品質のゲート** — 納品の約束の強制によってスライドショーのようなレンダリングを阻止し、コンポジション前の検証によって GPU 時間を無駄にする前に壊れたプランを見つけ、レンダリング後の必須のセルフレビュー（ffprobe + フレーム抽出 + 音声分析）によって、エージェントが質の低いものを提示しないようにします。プロバイダーの選択、スタイルの判断、フォールバックはすべて、監査可能な判断の記録に残ります。
- **予算管理を内蔵** — 実行前のコスト見積もり、支出の上限、アクションごとの承認しきい値。予想外の請求はありません。

---

## 仕組み

OpenMontage は**エージェントファーストのアーキテクチャ**を採用しています。コードのオーケストレーターはありません。あなたの AI コーディングアシスタントこそがオーケストレーターです。

```
You: "Make an explainer video about how black holes form"
 |
 v
Agent reads pipeline manifest (YAML) -- stages, tools, review criteria, success gates
 |
 v
Agent reads stage director skill (Markdown) -- HOW to execute each stage
 |
 v
Agent calls Python tools -- scored provider selection ranks every tool across 7 dimensions
 |
 v
Agent self-reviews using reviewer skill -- schema validation, playbook compliance, quality checks
 |
 v
Agent checkpoints state (JSON) -- resumable, with decision log and cost snapshot
 |
 v
Agent presents for your approval -- you stay in control at every creative decision
 |
 v
Pre-compose validation gate -- delivery promise, slideshow risk, renderer governance
 |
 v
Render (Remotion or FFmpeg) -- composition engine matched to visual grammar
 |
 v
Post-render self-review -- ffprobe, frame extraction, audio analysis, promise verification
 |
 v
Final video output -- only if self-review passes
```

**Python はツールと永続化を提供します。** クリエイティブな判断、オーケストレーションのロジック、レビューの基準、品質の基準はすべて、確認やカスタマイズができる読みやすい指示ファイル（YAML マニフェスト + Markdown スキル）にあります。すべての判断は、検討した代替案、確信度のスコア、各選択の理由とともに記録されます。

---

## アーキテクチャ

```
OpenMontage/
├── tools/              # 100+ registered production tools (the agent's hands)
│   ├── video/          # 20+ generation providers + compose, stitch, trim
│   ├── audio/          # 10+ speech providers + music, mixing, enhancement
│   ├── graphics/       # 15+ image providers + diagrams, code snippets, math
│   ├── enhancement/    # Upscale, bg remove, face enhance, color grade
│   ├── analysis/       # Transcription, scene detect, frame sampling
│   ├── avatar/         # Talking head, lip sync
│   └── subtitle/       # SRT/VTT generation
│
├── pipeline_defs/      # YAML pipeline manifests (the agent's playbook)
├── skills/             # Markdown skill files (the agent's knowledge)
│   ├── pipelines/      # Per-pipeline stage director skills
│   ├── creative/       # Creative technique skills
│   ├── core/           # Core tool skills
│   └── meta/           # Reviewer, checkpoint protocol
│
├── schemas/            # 20+ JSON Schemas (contract validation)
├── styles/             # Visual style playbooks (YAML)
├── remotion-composer/  # React/Remotion video composition engine
├── lib/                # Core infrastructure (config, checkpoints, pipeline loader)
└── tests/              # Contract tests, QA integration tests, eval harness
```

### 3 層の知識アーキテクチャ

```
Layer 1: tools/ + pipeline_defs/     "What exists" — executable capabilities + orchestration
Layer 2: skills/                     "How to use it" — OpenMontage conventions and quality bars
Layer 3: .agents/skills/             "How it works" — external technology knowledge packs
```

各ツールは、どの Layer 3 のスキルに依存しているかを宣言しています。エージェントは、何が利用できるかを知るために Layer 1 を、OpenMontage がそれをどう使ってほしいかを知るために Layer 2 を、必要に応じて詳細な技術知識を得るために Layer 3 を読みます。

---

## 対応プロバイダー

> **料金と無料枠を含む完全なセットアップガイド：** [`docs/PROVIDERS.md`](docs/PROVIDERS.md)

<details>
<summary><strong>動画生成 — 20 以上のプロバイダー</strong></summary>

| プロバイダー | 種類 | 備考 |
|----------|------|-------|
| **Kling (fal.ai)** | クラウド API | 高品質で、fal.ai ゲートウェイ経由で高速 |
| **Kling Official** | クラウド API | 別の `kling_official` プロバイダーによる公式の直接 API |
| **Atlas Cloud** | クラウド API | Seedance、MiniMax、Hunyuan などのマルチモーダルモデルのための統合ゲートウェイ |
| **Seedance 2.0 (Volcengine Ark)** | クラウド API | 別の `seedance_ark` プロバイダーによる公式の直接 API |
| **Seedance 2.5 / 2.0** | クラウド API | 対応するゲートウェイを通じた、テキスト、画像、参照ベースの動画ワークフロー |
| **Gemini Omni Flash** | クラウド API | 対話型のマルチモーダル動画生成と編集 |
| **Runway Gen-4** | クラウド API | シネマティックな品質、Gen-3 Alpha Turbo / Gen-4 Turbo / Gen-4 Aleph |
| **Google Veo 3.1** | クラウド API | Google GenAI または fal.ai 経由のプレミアムなシネマティック動画 |
| **Grok Imagine Video** | クラウド API | 参照画像からの動画生成と xAI ネイティブのショート動画生成に強い |
| **Higgsfield** | クラウド API | キャラクターの一貫性のための Soul ID を備えたマルチモデルオーケストレーター |
| **MiniMax / H3** | クラウド API | テキスト、画像、参照ベースの H3 ワークフローを含む、コスト効率の高い生成 |
| **HeyGen** | クラウド API | マルチモデルゲートウェイ |
| **WAN 2.1 / 2.2** | ローカル GPU | 無料のローカル版と、高速化された ComfyUI ワークフロー |
| **Hunyuan** | ローカル GPU | 無料、高品質 |
| **CogVideo** | ローカル GPU | 無料、2B と 5B のバリアント |
| **LTX-Video** | ローカル GPU / Modal | ローカルなら無料、またはセルフホストのクラウド |
| **Pexels** | ストック | 無料のストック映像 |
| **Pixabay** | ストック | 無料のストック映像 |
| **Wikimedia Commons** | ストック | 無料/オープンなストック映像とアーカイブ動画 |

</details>

<details>
<summary><strong>画像生成 — 15 以上のプロバイダー</strong></summary>

| プロバイダー | 種類 | 備考 |
|----------|------|-------|
| **FLUX** | クラウド API | 最先端の品質 |
| **Google Imagen** | クラウド API | Imagen 4 — 高品質、複数のアスペクト比 |
| **Grok Imagine Image** | クラウド API | 画像の編集、スタイル変換、複数画像の合成に強い |
| **GPT Image 2** | クラウド API | OpenAI の画像モデル |
| **Seedream 5.0** | クラウド API | 対応するゲートウェイを通じた、高忠実度のテキストからの画像生成と画像編集 |
| **Nano Banana 2** | クラウド API | マルチモーダルな画像生成と編集 |
| **Atlas Cloud** | クラウド API | 複数の画像生成モデルファミリーへの統合アクセス |
| **Recraft** | クラウド API | デザイン重視の生成 |
| **Kling Official** | クラウド API | Kling の画像生成と参照ワークフローのための公式の直接 API |
| **Local Diffusion** | ローカル GPU | Stable Diffusion、無料 |
| **Pexels** | ストック | 無料のストック画像 |
| **Pixabay** | ストック | 無料のストック画像 |
| **Unsplash** | ストック | 無料のストック画像 |
| **ManimCE** | ローカル | 数学的なアニメーション |

</details>

<details>
<summary><strong>音声合成 — 10 以上のプロバイダー</strong></summary>

| プロバイダー | 種類 | 備考 |
|----------|------|-------|
| **ElevenLabs** | クラウド API | プレミアムな音声品質 |
| **Google TTS** | クラウド API | 700 以上の声、50 以上の言語 — ローカライゼーションに最適 |
| **Kling Official TTS** | クラウド API | `voice_id` がわかっている場合の Kling 公式のナレーション |
| **OpenAI TTS** | クラウド API | 高速、手頃な価格 |
| **Piper** | ローカル | 完全に無料、オフライン |
| **Azure Speech** | クラウド API | 高速な多言語音声サービス |
| **DashScope / Doubao / Fish Audio** | クラウド API | 追加の多言語・表現力豊かな音声の選択肢 |

</details>

<details>
<summary><strong>音楽、サウンド、ポストプロダクション</strong></summary>

**音楽とサウンド：**

| プロバイダー | 種類 | 備考 |
|----------|------|-------|
| **Suno AI** | クラウド API | ボーカル、歌詞付きで、あらゆるジャンルの楽曲を丸ごと生成。最大 8 分。 |
| **ElevenLabs Music** | クラウド API | AI による音楽生成 |
| **ElevenLabs SFX** | クラウド API | 効果音の生成 |

**ポストプロダクション（常に利用可能、常に無料）：**

| ツール | できること |
|------|-------------|
| **FFmpeg** | 動画のコンポジション、エンコード、字幕の焼き込み、音声の多重化 |
| **Video Stitch** | 複数クリップの組み立て、クロスフェード、ピクチャーインピクチャー、空間的なレイアウト |
| **Video Trimmer** | 精密なカットと抽出 |
| **Audio Mixer** | マルチトラックのミキシング、ダッキング、フェード |
| **Audio Enhance** | ノイズ除去、ノーマライズ |
| **Color Grade** | LUT ベースのカラーグレーディング |
| **Subtitle Gen** | タイムスタンプからの SRT/VTT 生成 |

**高画質化：**

| ツール | できること |
|------|-------------|
| **Upscale** | Real-ESRGAN による画像/動画のアップスケール |
| **Background Remove** | rembg / U2Net による背景除去 |
| **Face Enhance** | 顔の品質向上 |
| **Face Restore** | CodeFormer / GFPGAN による顔の復元 |

**分析：**

| ツール | できること |
|------|-------------|
| **Transcriber** | 単語単位のタイムスタンプ付きの WhisperX による音声認識 |
| **Scene Detect** | シーンの境界の自動検出 |
| **Frame Sampler** | インテリジェントなフレーム抽出 |
| **Video Understand** | CLIP/BLIP-2 による視覚言語分析 |

**アバターとリップシンク：**

| ツール | できること |
|------|-------------|
| **Talking Head** | SadTalker / MuseTalk によるアバターアニメーション |
| **Lip Sync** | Wav2Lip による音声駆動のリップシンク |
| **Kling Avatar** | Kling 公式のクラウドによるアバタープレゼンターの生成 |
| **Kling Lip Sync** | 顔の明示的な選択を伴う、Kling 公式のクラウドによるリップシンク |

**コンポジションとレンダリング：**

| エンジン | 種類 | できること |
|--------|------|-------------|
| **Remotion** | ローカル（Node.js） | React ベースのプログラマティックな動画 — スプリングアニメーションの画像シーン、統計の表示、セクションタイトル、ヒーローカード、TikTok 風の単語ごとのキャプション、シーンのトランジション（フェード/スライド/ワイプ/フリップ）、Google Fonts、フェードカーブ付きの音声、TalkingHead のアバターコンポジション。**動画生成のプロバイダーが設定されていない場合は、エージェントが静止画を生成し、Remotion がそれを完全なアニメーション動画にします。** |
| **HyperFrames** | ローカル（Node.js ≥ 22） | HTML/CSS/GSAP によるプログラマティックな動画 — キネティックタイポグラフィ、製品プロモーション、ローンチ動画、カスタムのモーショングラフィックス、レジストリブロック（データチャート、グレインオーバーレイ、シェーダートランジション）、Web サイトから動画へのワークフロー、リグ付き SVG キャラクターアニメーション。`npx hyperframes` で利用でき、モノレポのチェックアウトは不要です。 |
| **FFmpeg** | ローカル | 中核となる動画の組み立て、エンコード、字幕の焼き込み、音声の多重化、カラーグレーディング |

ランタイムは提案の段階で選ばれ（`render_runtime`）、`edit_decisions` まで固定されます。ランタイム間で黙って切り替えることはガバナンス違反です — `skills/core/hyperframes.md` をご覧ください。

</details>

---

## スタイルシステム

スタイルのプレイブックが、制作物のビジュアル言語を定義します：

| プレイブック | 最適な用途 |
|----------|----------|
| **Clean Professional** | 企業、教育、SaaS |
| **Flat Motion Graphics** | ソーシャルメディア、TikTok、スタートアップ |
| **Minimalist Diagram** | 技術的な深掘り、アーキテクチャ |

プレイブックは、タイポグラフィ、カラーパレット、モーションのスタイル、オーディオのプロファイル、品質のルールを管理します。エージェントはプレイブックを読み、生成するすべての素材に一貫して適用します。

---

## プラットフォーム別の出力プロファイル

主要なプラットフォームすべてに対応した、組み込みのレンダリングプロファイル：

| プロファイル | 解像度 | アスペクト比 |
|---------|-----------|--------------|
| YouTube 横長 | 1920x1080 | 16:9 |
| YouTube 4K | 3840x2160 | 16:9 |
| YouTube Shorts | 1080x1920 | 9:16 |
| Instagram リール | 1080x1920 | 9:16 |
| Instagram フィード | 1080x1080 | 1:1 |
| TikTok | 1080x1920 | 9:16 |
| LinkedIn | 1920x1080 | 16:9 |
| シネマティック | 2560x1080 | 21:9 |

---

## 制作のガバナンス

OpenMontage は、動画制作を本物のエンジニアリングのように扱います。すべてのステージに品質ゲート、監査証跡、強制の仕組みがあります。

### 品質ゲート

- **人間による承認ゲートは提案ではなく強制です** — 提案、脚本、シーンプラン、生成した素材、公開のいずれも、あなたの承認を得るまで一時停止します。チェックポイントの書き込み処理は、承認が記録されていないゲート付きステージを「完了」として扱うことを拒否し、置き換えられたチェックポイントはすべてアーカイブされるため、修正を重ねても監査証跡（ゲートの遷移を含む）は残ります。レビューは [Backlot ボード](#実際に見てみる--backlot-のリビングストーリーボード)上で視覚的に行います。
- **コンポジション前の検証** — 納品の約束に違反している場合（例：静止画が 80% を占める「動き主体」の動画）、スライドショーのリスクスコアが危険な水準の場合、またはレンダラーのファミリーが欠けている場合にレンダリングを阻止します。GPU 時間を無駄にする前に、壊れたプランを見つけます。
- **レンダリング後のセルフレビュー** — レンダリングのたびに、ランタイムは ffprobe による検証を実行し、4 つの位置でフレームを抽出して黒フレームや壊れたオーバーレイを確認し、無音やクリッピングがないか音量レベルを分析し、納品の約束が守られたかを検証し、字幕の有無を確認します。レビューに失敗した場合、その動画は提示されません。
- **スライドショーのリスクスコアリング** — 6 つの観点（繰り返し、装飾的なビジュアル、弱い動き、ショットの意図、タイポグラフィへの過度の依存、根拠のないシネマティックの主張）での分析により、「アニメーション付きの PowerPoint」のような出力を防ぎます。
- **元メディアの検査** — ユーザーが自分の映像を提供した場合、システムはすべてのファイル（解像度、コーデック、音声チャンネル、尺）を調べ、クリエイティブな判断を 1 つも下す前に計画への影響を整理します。ファイル名から内容をでっち上げることはありません。

### スコアリングによるプロバイダーの選択

すべてのツールの選択（動画生成、画像生成、音声合成、音楽）は、7 つの観点のスコアリングエンジンを通ります：タスクへの適合（30%）、出力品質（20%）、制御機能（15%）、信頼性（15%）、コスト効率（10%）、レイテンシ（5%）、一貫性（5%）。選ばれたプロバイダーとそのスコアは、検討したすべての代替案とともに判断の記録に残ります。

セレクターは、スコアリングの前に大まかな企画の文脈を正規化します。エージェントが「キャラクターの一貫性がある Pixar 風のアニメーション短編」程度のことしか知らない場合でも、完全に整った `task_context` を要求するのではなく、セレクターがそれをスコアラーが扱いやすい意図とスタイルのシグナルに展開します。

セレクターの出力には、選ばれたプロバイダーの `agent_skills` も表示されるため、エージェントはプロンプトを書く前に、適切な Layer 3 のプロバイダースキルをすぐに読むことができます。

### 判断の監査証跡

プロバイダーの選択、スタイル/プレイブックの選択、楽曲、声の選択、レンダラーのファミリー、あらゆるフォールバックやダウングレードなど、主要なクリエイティブおよび技術的な選択はすべて、検討した代替案、確信度のスコア、理由とともに記録されます。累積的な判断ログはすべてのステージにわたって保持されるため、出力がなぜそのような見た目になったのかを正確にたどることができます。

### 予算管理

- 実行前に**見積もる** — コストを確認できます
- 予算を**確保する** — 呼び出しの前に資金を確保します
- 実行後に**照合する** — 実際の支出を記録します
- **設定可能なモード** — `observe`（追跡のみ）、`warn`（超過を記録）、`cap`（厳格な上限）
- **アクションごとの承認** — しきい値（デフォルト：$0.50）を超える場合は確認のために一時停止します
- **総予算の上限** — デフォルトは $10 で、自由に設定できます

予想外の請求はありません。エージェントは支出する前に、コストがいくらになるかを伝えます。

---

## エージェントとの互換性

OpenMontage は、ファイルを読んで Python を実行できるあらゆる AI コーディングアシスタントで動作します。次のプラットフォーム向けの専用の指示ファイルが含まれています：

| プラットフォーム | 設定ファイル |
|----------|------------|
| **Claude Code** | `CLAUDE.md` |
| **Cursor** | `CURSOR.md` + `.cursor/rules/` |
| **GitHub Copilot** | `COPILOT.md` + `.github/copilot-instructions.md` |
| **Codex** | `CODEX.md` |
| **Windsurf** | `.windsurfrules` |

すべてのプラットフォームのファイルは、共通の `AGENT_GUIDE.md`（運用ガイドとエージェントの契約）と `PROJECT_CONTEXT.md`（アーキテクチャのリファレンス）を参照しています。

> **近日公開：** **Ollama** と **LM Studio** によるローカル LLM のサポート — クラウドの LLM をまったく使わずに、完全な制作パイプラインを実行できます。

---

## コントリビューション

OpenMontage は拡張できるように作られています。最も一般的なコントリビューションは次の 2 つです：

### 新しいツールを追加する

1. 適切な `tools/` のサブディレクトリに Python ファイルを作成します
2. `BaseTool` を継承し、ツールの契約を実装します
3. レジストリが自動的に発見するので、手動での登録は不要です
4. ツールに使い方のガイダンスが必要な場合は、スキルファイルを追加します

### 新しいパイプラインを追加する

1. `pipeline_defs/` に YAML マニフェストを作成します
2. `skills/pipelines/<your-pipeline>/` にステージディレクターのスキルを作成します
3. 既存のツールを参照するか、必要に応じて新しいツールを追加します

完全な技術リファレンスは `docs/ARCHITECTURE.md`、完全なプロバイダーガイド（セットアップ、料金、無料枠）は `docs/PROVIDERS.md`、エージェントの契約は `AGENT_GUIDE.md` をご覧ください。

### コミュニティに参加する

作品やアイデアの共有には [GitHub Discussions](https://github.com/calesthio/OpenMontage/discussions) を使っています：

- **[Show and Tell](https://github.com/calesthio/OpenMontage/discussions/categories/show-and-tell)** — 作った動画、うまくいったプロンプト、見つけたクリエイティブなワークフローを共有してください
- **[Ideas](https://github.com/calesthio/OpenMontage/discussions/categories/ideas)** — 新しいパイプライン、ツール、スタイルのプレイブック、統合を提案してください
- **[Q&A](https://github.com/calesthio/OpenMontage/discussions/categories/q-a)** — セットアップ、パイプライン、トラブルシューティングについて質問してください

何か面白いものを作りましたか？ Show and Tell に投稿してください。あなたが作ったものを見るのを楽しみにしています。

---

## お問い合わせ

最新情報、リリース、開発の舞台裏については、[@calesthioailabs](https://x.com/calesthioailabs) をフォローしてください。

バグ、機能のリクエスト、ワークフローに関する議論には、すべてが見える状態で対応できるよう、[GitHub Issues](https://github.com/calesthio/OpenMontage/issues) と [GitHub Discussions](https://github.com/calesthio/OpenMontage/discussions) を使ってください。

---

## テスト

```bash
# Run contract tests (no API keys needed)
make test-contracts

# Run all tests
make test
```

---

## Star の推移

<a href="https://star-history.dera.page/#calesthio/OpenMontage&type=date&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=calesthio/OpenMontage&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=calesthio/OpenMontage&type=date&legend=top-left" />
    <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=calesthio/OpenMontage&type=date&legend=top-left" />
  </picture>
</a>

---

## ライセンス

[GNU AGPLv3](LICENSE)

---

**OpenMontage** — 本物の品質管理を備えた本番品質の動画を、あなたの AI アシスタントがオーケストレーションします。

このプロジェクトが役に立ちそうだと思ったら、⭐ をいただけると本当に嬉しいです。他の人が見つける助けにもなります。

さらに応援していただける場合は、[プロジェクトをスポンサー](https://github.com/sponsors/calesthio)してください。OpenMontage は夜と週末を使って開発されており、皆さんのサポートがそれを持続可能にします。
