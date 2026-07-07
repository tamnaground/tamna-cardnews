/* 성읍민속마을 다국어 안내 웹앱 — 탐라그라운드 */
(function () {
  'use strict';

  var LANGS = [
    { code: 'je', label: '제주어', tts: 'ko-KR' },
    { code: 'ko', label: '한국어', tts: 'ko-KR' },
    { code: 'en', label: 'English', tts: 'en-US' },
    { code: 'zh', label: '中文', tts: 'zh-CN' },
    { code: 'ja', label: '日本語', tts: 'ja-JP' },
    { code: 'es', label: 'Español', tts: 'es-ES' }
  ];
  var LANG_CODES = LANGS.map(function (l) { return l.code; });

  var UI = {
    je: {
      appTitle: '성읍민속마을', appSubtitle: '혼저옵서예! 이디가 성읍이우다',
      chooseSpot: '보고 싶은 디를 골라봅서', back: '목록으로', listen: '들어봅서',
      stop: '그만 듣기', facts: '알아두민 좋은 거', tips: '구경 팁',
      jeNote: '제주어 아래에 표준어를 같이 적었수다.',
      ttsNote: '음성은 표준어 발음 기준으로 읽어집니다.',
      prev: '이전', next: '다음', notFound: '이런 디는 어신디예…', goHome: '처음으로 갑서',
      heritageLabel: '문화재', motto: '제주어, 같이 지켜요 — 탐라그라운드'
    },
    ko: {
      appTitle: '성읍민속마을', appSubtitle: '조선시대 정의현의 살아있는 읍성 마을',
      chooseSpot: '둘러볼 곳을 선택하세요', back: '목록으로', listen: '듣기',
      stop: '멈추기', facts: '알고 가면 좋은 것', tips: '관람 팁',
      jeNote: '', ttsNote: '',
      prev: '이전', next: '다음', notFound: '해당 안내를 찾을 수 없습니다.', goHome: '처음으로',
      heritageLabel: '문화재', motto: '제주어, 같이 지켜요 — 탐라그라운드'
    },
    en: {
      appTitle: 'Seongeup Folk Village', appSubtitle: 'A living walled town of Joseon-era Jeju',
      chooseSpot: 'Choose a spot to explore', back: 'All spots', listen: 'Listen',
      stop: 'Stop', facts: 'Good to know', tips: 'Visitor tips',
      jeNote: '', ttsNote: '',
      prev: 'Prev', next: 'Next', notFound: 'This guide page was not found.', goHome: 'Go home',
      heritageLabel: 'Heritage', motto: 'Keeping the Jeju language alive — Tamnaground'
    },
    zh: {
      appTitle: '城邑民俗村', appSubtitle: '朝鲜时代旌义县的活态邑城村落',
      chooseSpot: '请选择想参观的景点', back: '返回列表', listen: '收听',
      stop: '停止', facts: '小知识', tips: '参观提示',
      jeNote: '', ttsNote: '',
      prev: '上一个', next: '下一个', notFound: '未找到该导览页面。', goHome: '返回首页',
      heritageLabel: '文化遗产', motto: '一起守护济州语 — Tamnaground'
    },
    ja: {
      appTitle: '城邑民俗村', appSubtitle: '朝鮮時代・旌義県の面影が残る邑城の村',
      chooseSpot: 'ご覧になるスポットをお選びください', back: '一覧へ', listen: '聞く',
      stop: '停止', facts: '豆知識', tips: '見学のヒント',
      jeNote: '', ttsNote: '',
      prev: '前へ', next: '次へ', notFound: 'ご案内ページが見つかりません。', goHome: 'ホームへ',
      heritageLabel: '文化財', motto: '済州語をいっしょに守ろう — Tamnaground'
    },
    es: {
      appTitle: 'Aldea Folclórica de Seongeup', appSubtitle: 'Un pueblo amurallado vivo del Jeju de la era Joseon',
      chooseSpot: 'Elija un punto para explorar', back: 'Todos los puntos', listen: 'Escuchar',
      stop: 'Detener', facts: 'Bueno saber', tips: 'Consejos de visita',
      jeNote: '', ttsNote: '',
      prev: 'Anterior', next: 'Siguiente', notFound: 'No se encontró esta página de la guía.', goHome: 'Ir al inicio',
      heritageLabel: 'Patrimonio', motto: 'Cuidemos juntos la lengua de Jeju — Tamnaground'
    }
  };

  var FLOWER_SVG =
    '<svg class="flower" viewBox="0 0 48 48" aria-hidden="true">' +
    ['M24 6', 'M24 42', 'M8.4 15', 'M39.6 15', 'M8.4 33', 'M39.6 33'].map(function (_, i) {
      var a = (Math.PI / 3) * i - Math.PI / 2;
      var cx = 24 + Math.cos(a) * 11, cy = 24 + Math.sin(a) * 11;
      return '<circle cx="' + cx.toFixed(1) + '" cy="' + cy.toFixed(1) + '" r="7.5" fill="#E8622D" opacity="0.9"/>';
    }).join('') +
    '<circle cx="24" cy="24" r="6" fill="#FFCC5C"/></svg>';

  var app = document.getElementById('app');
  var DATA = window.SPOTS_DATA || { spots: [] };
  var SPOTS = (DATA.spots || []).slice().sort(function (a, b) { return (a.order || 0) - (b.order || 0); });

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function detectLang() {
    try {
      var saved = localStorage.getItem('sg_lang');
      if (saved && LANG_CODES.indexOf(saved) !== -1) return saved;
    } catch (e) { /* private mode */ }
    var nav = (navigator.languages || [navigator.language || 'ko']).join(',').toLowerCase();
    if (nav.indexOf('ko') === 0 || nav.indexOf(',ko') !== -1) return 'ko';
    if (/(^|,)zh/.test(nav)) return 'zh';
    if (/(^|,)ja/.test(nav)) return 'ja';
    if (/(^|,)es/.test(nav)) return 'es';
    if (/(^|,)en/.test(nav)) return 'en';
    return 'ko';
  }

  var state = {
    lang: detectLang(),
    spot: null
  };

  function readUrl() {
    var p = new URLSearchParams(location.search);
    var lang = p.get('lang');
    if (lang && LANG_CODES.indexOf(lang) !== -1) {
      state.lang = lang;
      try { localStorage.setItem('sg_lang', lang); } catch (e) {}
    }
    state.spot = p.get('spot');
  }

  function urlFor(spot, lang) {
    var p = new URLSearchParams();
    if (spot) p.set('spot', spot);
    p.set('lang', lang || state.lang);
    return location.pathname + '?' + p.toString();
  }

  function navigate(spot, push) {
    stopSpeech();
    state.spot = spot;
    var url = urlFor(spot, state.lang);
    if (push === false) history.replaceState({}, '', url);
    else history.pushState({}, '', url);
    render();
    window.scrollTo(0, 0);
  }

  function setLang(lang) {
    stopSpeech();
    state.lang = lang;
    try { localStorage.setItem('sg_lang', lang); } catch (e) {}
    history.replaceState({}, '', urlFor(state.spot, lang));
    document.documentElement.lang = lang === 'je' ? 'ko' : lang;
    render();
  }

  function t(key) {
    return (UI[state.lang] && UI[state.lang][key]) || UI.ko[key] || key;
  }

  function spotText(spot, lang) {
    return (spot.i18n && spot.i18n[lang]) || (spot.i18n && spot.i18n.ko) || null;
  }

  /* ---------- TTS ---------- */
  var speaking = false;

  function ttsSupported() {
    return 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  }

  function stopSpeech() {
    if (ttsSupported()) window.speechSynthesis.cancel();
    speaking = false;
    var btn = document.querySelector('.tts-btn');
    if (btn) {
      btn.dataset.speaking = 'false';
      btn.textContent = '🔊 ' + t('listen');
    }
  }

  function buildSpeechText(spot) {
    var lang = state.lang;
    var tx = spotText(spot, lang);
    if (!tx) return '';
    var parts = [tx.name];
    if (lang === 'je' && Array.isArray(tx.body)) {
      tx.body.forEach(function (pair) { parts.push(pair.je); });
    } else if (Array.isArray(tx.body)) {
      parts = parts.concat(tx.body);
    }
    return parts.join('. ');
  }

  function toggleSpeech(spot) {
    if (!ttsSupported()) return;
    if (speaking) { stopSpeech(); return; }
    var text = buildSpeechText(spot);
    if (!text) return;
    var langDef = LANGS.filter(function (l) { return l.code === state.lang; })[0];
    var u = new SpeechSynthesisUtterance(text);
    u.lang = langDef.tts;
    u.rate = 0.95;
    var voices = window.speechSynthesis.getVoices() || [];
    var match = voices.filter(function (v) { return v.lang && v.lang.replace('_', '-').indexOf(langDef.tts.split('-')[0]) === 0; })[0];
    if (match) u.voice = match;
    u.onend = stopSpeech;
    u.onerror = stopSpeech;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
    speaking = true;
    var btn = document.querySelector('.tts-btn');
    if (btn) {
      btn.dataset.speaking = 'true';
      btn.textContent = '⏹ ' + t('stop');
    }
  }

  /* ---------- views ---------- */
  function langBarHtml() {
    return '<nav class="lang-bar" aria-label="Language">' + LANGS.map(function (l) {
      return '<button type="button" data-lang="' + l.code + '"' +
        (l.code === 'je' ? ' class="je-tab"' : '') +
        ' aria-pressed="' + (state.lang === l.code) + '">' + esc(l.label) + '</button>';
    }).join('') + '</nav>';
  }

  function footerHtml() {
    return '<footer class="site-footer">' +
      '<div class="motto">' + esc(t('motto')) + '</div>' +
      '<div>@tamnaground</div></footer>';
  }

  function homeHtml() {
    var cards = SPOTS.map(function (s) {
      var tx = spotText(s, state.lang) || {};
      return '<li><a class="spot-card" href="' + esc(urlFor(s.slug, state.lang)) + '" data-spot="' + esc(s.slug) + '">' +
        '<span class="icon" aria-hidden="true">' + esc(s.icon || '📍') + '</span>' +
        '<span class="meta"><span class="name">' + esc(tx.name || s.slug) + '</span><br>' +
        '<span class="tagline">' + esc(tx.tagline || '') + '</span></span></a></li>';
    }).join('');
    return '<header class="site-header">' + FLOWER_SVG +
      '<h1>' + esc(t('appTitle')) + '</h1>' +
      '<div class="subtitle">' + esc(t('appSubtitle')) + '</div>' +
      '<span class="brand-badge">@tamnaground</span></header>' +
      langBarHtml() +
      '<p class="home-intro">' +
      (state.lang === 'je' ? '<span class="je-greet">혼저옵서예!</span><br>' : '') +
      esc(t('chooseSpot')) + '</p>' +
      '<ul class="spot-grid">' + cards + '</ul>' + footerHtml();
  }

  function spotHtml(spot) {
    var lang = state.lang;
    var tx = spotText(spot, lang);
    var ko = spotText(spot, 'ko') || {};
    if (!tx) return notFoundHtml();

    var idx = SPOTS.indexOf(spot);
    var prev = SPOTS[idx - 1], next = SPOTS[idx + 1];

    var bodyHtml;
    if (lang === 'je' && Array.isArray(tx.body) && tx.body.length && typeof tx.body[0] === 'object') {
      bodyHtml = '<div class="je-note">🌿 ' + esc(t('jeNote')) + '</div>' +
        tx.body.map(function (pair) {
          return '<div class="je-pair"><div class="je-line">' + esc(pair.je) + '</div>' +
            '<div class="ko-line">' + esc(pair.ko) + '</div></div>';
        }).join('');
    } else {
      bodyHtml = (tx.body || []).map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('');
    }

    var facts = (tx.facts && tx.facts.length ? tx.facts : (lang === 'je' ? ko.facts : null)) || [];
    var tips = (tx.tips && tx.tips.length ? tx.tips : (lang === 'je' ? ko.tips : null)) || [];
    var heritage = (spot.heritage && (spot.heritage[lang === 'je' ? 'ko' : lang] || spot.heritage.ko)) || '';

    return '<a class="back-link" href="' + esc(urlFor(null, lang)) + '" data-spot="">← ' + esc(t('back')) + '</a>' +
      langBarHtml() +
      '<section class="spot-hero">' +
      '<div class="icon" aria-hidden="true">' + esc(spot.icon || '📍') + '</div>' +
      '<div class="category">' + esc((spot.category && (spot.category[lang === 'je' ? 'ko' : lang] || spot.category.ko)) || '') + '</div>' +
      '<h2>' + esc(tx.name) + '</h2>' +
      (lang !== 'ko' && lang !== 'je' ? '<div class="name-ko-sub">' + esc(ko.name || '') + '</div>' : '') +
      (heritage ? '<div class="heritage">🏛 ' + esc(heritage) + '</div>' : '') +
      '</section>' +
      (ttsSupported()
        ? '<button type="button" class="tts-btn" data-speaking="false">🔊 ' + esc(t('listen')) + '</button>' +
          (lang === 'je' && t('ttsNote') ? '<div class="tts-note">' + esc(t('ttsNote')) + '</div>' : '')
        : '') +
      '<section class="section-card"><h3>📖 ' + esc(tx.name) + '</h3>' + bodyHtml + '</section>' +
      (facts.length ? '<section class="section-card"><h3>💡 ' + esc(t('facts')) + '</h3><ul>' +
        facts.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join('') + '</ul></section>' : '') +
      (tips.length ? '<section class="section-card"><h3>🚶 ' + esc(t('tips')) + '</h3><ul>' +
        tips.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join('') + '</ul></section>' : '') +
      '<nav class="spot-nav">' +
      (prev
        ? '<a href="' + esc(urlFor(prev.slug, lang)) + '" data-spot="' + esc(prev.slug) + '"><span class="dir">← ' + esc(t('prev')) + '</span>' +
          esc((spotText(prev, lang) || {}).name || '') + '</a>'
        : '<span class="spacer"></span>') +
      (next
        ? '<a class="next" href="' + esc(urlFor(next.slug, lang)) + '" data-spot="' + esc(next.slug) + '"><span class="dir">' + esc(t('next')) + ' →</span>' +
          esc((spotText(next, lang) || {}).name || '') + '</a>'
        : '<span class="spacer"></span>') +
      '</nav>' + footerHtml();
  }

  function notFoundHtml() {
    return langBarHtml() +
      '<div class="not-found"><div class="icon">🌊</div><p>' + esc(t('notFound')) + '</p>' +
      '<p><a href="' + esc(urlFor(null, state.lang)) + '" data-spot="">' + esc(t('goHome')) + '</a></p></div>' +
      footerHtml();
  }

  function render() {
    var spot = state.spot
      ? SPOTS.filter(function (s) { return s.slug === state.spot; })[0]
      : null;
    if (state.spot && !spot) {
      app.innerHTML = notFoundHtml();
    } else if (spot) {
      app.innerHTML = spotHtml(spot);
      document.title = ((spotText(spot, state.lang) || {}).name || '') + ' — ' + t('appTitle');
    } else {
      app.innerHTML = homeHtml();
      document.title = t('appTitle') + ' — 탐라그라운드';
    }
    if (!spot) document.title = t('appTitle') + ' — 탐라그라운드';
  }

  /* ---------- events (delegation) ---------- */
  app.addEventListener('click', function (e) {
    var langBtn = e.target.closest('button[data-lang]');
    if (langBtn) { setLang(langBtn.dataset.lang); return; }
    var ttsBtn = e.target.closest('.tts-btn');
    if (ttsBtn) {
      var spot = SPOTS.filter(function (s) { return s.slug === state.spot; })[0];
      if (spot) toggleSpeech(spot);
      return;
    }
    var link = e.target.closest('a[data-spot]');
    if (link) {
      e.preventDefault();
      navigate(link.dataset.spot || null);
    }
  });

  window.addEventListener('popstate', function () {
    stopSpeech();
    readUrl();
    render();
  });

  /* ---------- init ---------- */
  readUrl();
  document.documentElement.lang = state.lang === 'je' ? 'ko' : state.lang;
  render();

  if ('serviceWorker' in navigator && location.protocol === 'https:') {
    navigator.serviceWorker.register('sw.js').catch(function () { /* offline support is best-effort */ });
  }
})();
