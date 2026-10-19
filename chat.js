/* Studio33 chat: a simple rule-based helper (no external service). */
(function () {
  "use strict";

  var CONTACT = location.pathname.match(/(^|\/)(index\.html)?$/) ? "#contact" : "./#contact";

  var TOPICS = {
    start: {
      text: "こんにちは。Studio33 の自動チャットです。\nネットやパソコンのお困りごと、料金や対応エリアについてお答えします。どれについて知りたいですか？",
      chips: ["net", "price", "area", "pc", "contact"]
    },
    net: {
      label: "ネットがつながらない・遅い",
      text: "ネットの不調は、Studio33 のいちばんの得意分野です。\nどんな症状に近いですか？",
      chips: ["net_slow", "net_room", "net_none", "net_device"]
    },
    net_slow: {
      label: "夜や特定の時間に遅い",
      text: "時間帯で遅くなる場合、ルーターの性能や設定、回線の混雑が原因のことが多いです。\n\nまず試せること：\n・ルーターの電源を抜いて30秒待ち、差し直す\n・パソコンやスマホも再起動する\n\nそれでも直らなければ、「ネット不調まるごとパック」（8,800円・税込）で、原因の診断からルーターの設定までまとめて対応します。",
      chips: ["pack", "contact", "start"]
    },
    net_room: {
      label: "2階や奥の部屋だけ弱い",
      text: "部屋によって電波が弱いのは、壁や床、ルーターの置き場所が原因のことが多いです。\n\nルーターを床から少し高い所に置き、まわりの物をどけるだけで改善することもあります。届かない部屋には中継機やメッシュWi-Fiが効果的です。\n\n中継機やメッシュWi-Fiの設置は 4,400円〜（機器代は別）。訪問基本料 3,300円と合わせて、合計 7,700円〜が目安です。",
      chips: ["contact", "price", "start"]
    },
    net_none: {
      label: "まったくつながらない",
      text: "まったくつながらない場合は、まず次を確かめてみてください。\n\n・ルーターやモデムのランプが赤や消灯になっていないか\n・ルーターとモデムの電源を抜いて30秒待ち、モデム→ルーターの順に差し直す\n・ほかのスマホやパソコンでもつながらないか\n\nそれでも直らない場合は、お気軽にご相談ください。回線側の障害かどうかの切り分けからお手伝いします。",
      chips: ["contact", "pack", "start"]
    },
    net_device: {
      label: "プリンターやテレビがつながらない",
      text: "プリンターやテレビのネット接続は、1台 3,300円（税込）で設定します。\n動画サービスの設定もお手伝いします。訪問基本料 3,300円が別にかかります。",
      chips: ["contact", "price", "start"]
    },
    pack: {
      label: "まるごとパックとは？",
      text: "「ネット不調まるごとパック」は 8,800円（税込）です。\n\n・訪問基本料（世田谷区内・出張費込み）\n・ネット・Wi-Fiの不調の診断と調整\n・Wi-Fiルーターの設定（端末3台まで）\n・作業後の速度チェックと使い方のご説明\n\n別々に頼むと11,000円のところ、まとめて8,800円です（作業60分まで）。",
      chips: ["contact", "price_page", "start"]
    },
    price: {
      label: "料金を知りたい",
      text: "主な料金です（すべて税込）。\n\n・訪問基本料 3,300円（世田谷区内は出張費込み）\n・ネット不調まるごとパック 8,800円\n・ネット・Wi-Fiの不調診断 3,300円〜\n・ルーター設定 4,400円\n・パソコンの初期設定 6,600円〜\n・データ移行 6,600円〜\n・延長 30分ごと 2,200円\n\nご相談・お見積もりは無料です。作業の前に必ず金額をお伝えします。",
      chips: ["price_page", "pack", "contact"]
    },
    price_page: {
      label: "料金ページを見る",
      link: "pricing.html"
    },
    area: {
      label: "対応エリア",
      text: "世田谷区の5つの地域すべてに対応しています。\n\n・世田谷地域（三軒茶屋・桜新町・用賀 など）\n・北沢地域（下北沢・梅ヶ丘・明大前 など）\n・玉川地域（二子玉川・等々力・駒沢 など）\n・砧地域（成城・千歳船橋・経堂 など）\n・烏山地域（千歳烏山・芦花公園・八幡山 など）\n\n世田谷区内は出張費込みです。区外の方も、まずはご相談ください（別に交通費をいただく場合があります）。",
      chips: ["contact", "price", "start"]
    },
    pc: {
      label: "パソコンの困りごと",
      text: "パソコンのことも、まるごとお任せください。どれに近いですか？",
      chips: ["pc_trouble", "pc_setup", "pc_data", "pc_security", "pc_lesson"]
    },
    pc_trouble: {
      label: "起動しない・遅い・エラー",
      text: "トラブルの診断は 3,300円〜（税込）です。原因を調べて、直し方をご提案します。\n\n大切なデータが入っている場合は、無理に何度も電源を入れ直さず、そのままの状態でご相談ください。",
      chips: ["contact", "price", "start"]
    },
    pc_setup: {
      label: "新しいパソコンの設定",
      text: "パソコンの初期設定は 6,600円〜（税込）です。メールやプリンター、よく使うソフトの準備までお手伝いします。\n古いパソコンからのデータ移行（6,600円〜）もあわせて承ります。",
      chips: ["contact", "price", "start"]
    },
    pc_data: {
      label: "データの移行・バックアップ",
      text: "写真・書類・メールを新しいパソコンへ移すデータ移行は 6,600円〜（税込）です。量によって変わるので、作業の前に金額をお伝えします。",
      chips: ["contact", "price", "start"]
    },
    pc_security: {
      label: "ウイルス・怪しい警告",
      text: "画面に「ウイルスに感染しました」「電話してください」と出ても、表示された番号には電話しないでください。多くはサポート詐欺です。\n\nセキュリティ対策や設定の見直しは 3,300円〜（税込）。不安なときはお気軽にご相談ください。",
      chips: ["contact", "start"]
    },
    pc_lesson: {
      label: "使い方を教えてほしい",
      text: "使い方レッスンは60分 3,300円（税込）です。基本操作から仕事で使うソフトまで、ペースに合わせてご説明します。",
      chips: ["contact", "start"]
    },
    contact: {
      label: "相談を申し込む",
      text: "ありがとうございます。ページ下のお問い合わせフォームに、症状をそのままご記入ください。うまく説明できなくても大丈夫です。\nご相談・お見積もりは無料です。",
      chips: ["go_form", "start"]
    },
    go_form: {
      label: "フォームへ移動",
      link: CONTACT
    },
    unknown: {
      text: "ごめんなさい、うまくお答えできませんでした。\n下のボタンから選ぶか、お問い合わせフォームから直接ご相談ください。",
      chips: ["net", "price", "area", "pc", "contact"]
    }
  };
  TOPICS.start.label = "最初に戻る";

  var RULES = [
    [/パック|まるごと/, "pack"],
    [/料金|値段|価格|いくら|費用|円|お金|見積/, "price"],
    [/プリンタ|テレビ|tv|ファイヤー|クロームキャスト/i, "net_device"],
    [/2階|二階|奥の部屋|部屋|電波.*弱|届かない|中継|メッシュ/, "net_room"],
    [/まったく|全く|全然|つながらない|繋がらない|ランプ|圏外/, "net_none"],
    [/夜|夕方|時間帯|遅い|おそい|重い|切れる|途切れ|止まる/, "net_slow"],
    [/ネット|wi-?fi|ワイファイ|無線|ルーター|回線|プロバイダ/i, "net"],
    [/ウイルス|ウィルス|詐欺|警告|セキュリティ|ハッキング|乗っ取/, "pc_security"],
    [/データ|移行|引っ越し|バックアップ|写真/, "pc_data"],
    [/初期設定|セットアップ|新しいパソコン|買い替え|買った/, "pc_setup"],
    [/起動|電源|動かない|固まる|フリーズ|エラー|故障|壊れ|修理/, "pc_trouble"],
    [/使い方|教えて|レッスン|操作|分からない|わからない/, "pc_lesson"],
    [/エリア|地域|区外|世田谷|出張|訪問|来て|三軒茶屋|下北沢|二子玉川|成城|経堂|用賀|桜新町|千歳|烏山|駒沢|等々力|梅ヶ丘|明大前|豪徳寺|松陰|上町|若林|太子堂|池尻|代沢|奥沢|尾山台|九品仏|深沢|上野毛|祖師|喜多見|砧|芦花|八幡山|上北沢|給田/, "area"],
    [/パソコン|pc|ノート|mac|windows/i, "pc"],
    [/相談|申し込|申込|予約|問い合わせ|問合せ|連絡|依頼|お願い/, "contact"],
    [/こんにちは|こんばんは|はじめまして|もしもし/, "start"]
  ];

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  var root = el("div", "chatbot");
  var launcher = el("button", "chat-launcher");
  launcher.type = "button";
  launcher.setAttribute("aria-label", "チャットで質問する");
  launcher.innerHTML = '<span class="chat-launcher-icon" aria-hidden="true">💬</span><span class="chat-launcher-text">チャットで質問</span>';

  var panel = el("div", "chat-panel");
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Studio33 チャット");
  panel.hidden = true;

  var head = el("div", "chat-head");
  head.innerHTML = '<span class="brand-mark">S</span><div><strong>Studio33 チャット</strong><small>自動でお答えします</small></div>';
  var close = el("button", "chat-close", "×");
  close.type = "button";
  close.setAttribute("aria-label", "閉じる");
  head.appendChild(close);

  var log = el("div", "chat-log");
  log.setAttribute("aria-live", "polite");
  var form = el("form", "chat-input");
  var input = el("input");
  input.type = "text";
  input.placeholder = "例）夜になるとWi-Fiが遅い";
  input.setAttribute("aria-label", "質問を入力");
  var send = el("button", null, "送信");
  send.type = "submit";
  form.appendChild(input);
  form.appendChild(send);

  panel.appendChild(head);
  panel.appendChild(log);
  panel.appendChild(form);
  root.appendChild(panel);
  root.appendChild(launcher);

  var bubble = el("div", "chat-hint", "ネットの不調、チャットで質問できます");
  root.appendChild(bubble);

  function scroll() { log.scrollTop = log.scrollHeight; }

  function addMsg(who, text) {
    var m = el("div", "chat-msg " + who, text);
    log.appendChild(m);
    scroll();
  }

  function addChips(keys) {
    var wrap = el("div", "chat-chips");
    keys.forEach(function (k) {
      var t = TOPICS[k];
      var b = el("button", "chat-chip", t.label);
      b.type = "button";
      b.addEventListener("click", function () {
        wrap.remove();
        choose(k, true);
      });
      wrap.appendChild(b);
    });
    log.appendChild(wrap);
    scroll();
  }

  function clearChips() {
    var c = log.querySelectorAll(".chat-chips");
    for (var i = 0; i < c.length; i++) c[i].remove();
  }

  function reply(key) {
    var t = TOPICS[key];
    var typing = el("div", "chat-msg bot typing", "…");
    log.appendChild(typing);
    scroll();
    setTimeout(function () {
      typing.remove();
      addMsg("bot", t.text);
      if (t.chips) addChips(t.chips);
    }, 450);
  }

  function choose(key, echo) {
    var t = TOPICS[key];
    if (echo) addMsg("user", t.label);
    if (t.link) {
      if (t.link.charAt(0) === "#") {
        setOpen(false);
        location.hash = t.link;
      } else {
        location.href = t.link;
      }
      return;
    }
    reply(key);
  }

  function match(text) {
    for (var i = 0; i < RULES.length; i++) {
      if (RULES[i][0].test(text)) return RULES[i][1];
    }
    return "unknown";
  }

  var started = false;
  function setOpen(open) {
    panel.hidden = !open;
    root.classList.toggle("open", open);
    bubble.remove();
    if (open && !started) {
      started = true;
      reply("start");
    }
    if (open) setTimeout(function () { input.focus({ preventScroll: true }); }, 50);
  }

  launcher.addEventListener("click", function () { setOpen(panel.hidden); });
  close.addEventListener("click", function () { setOpen(false); });
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text) return;
    input.value = "";
    clearChips();
    addMsg("user", text);
    reply(match(text));
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) setOpen(false);
  });

  setTimeout(function () { if (bubble.isConnected) bubble.classList.add("show"); }, 2500);

  document.body.appendChild(root);
})();
