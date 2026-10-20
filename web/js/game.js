/* ==========================================================================
   Dangandle — daily Danganronpa deduction puzzle
   Pure front-end, no dependencies. The dataset lives in js/characters.js.
   ========================================================================== */
(function () {
  "use strict";

  var CHARACTERS = window.DANGANDLE_CHARACTERS || [];
  var POOL = CHARACTERS.filter(function (c) { return c.pool; });
  var MAX_ATTEMPTS = 10;
  var STORAGE_KEY = "dangangle.state.v1";
  var STATS_KEY = "dangangle.stats.v1";
  var EPOCH = Date.UTC(2024, 0, 1);

  var ATTRS = [
    { key: "title", label: "Title", type: "text" },
    { key: "gender", label: "Gender", type: "exact" },
    { key: "height", label: "Height", type: "number", unit: "cm" },
    { key: "weight", label: "Weight", type: "number", unit: "kg" },
    { key: "status", label: "Status", type: "exact" },
    { key: "talent", label: "Talent", type: "exact" },
    { key: "likes", label: "Likes", type: "set" },
    { key: "dislikes", label: "Dislikes", type: "set" },
    { key: "appearance", label: "Debut", type: "game" }
  ];

  var EMOJI_KEY = [
    ["\u{1F4F1}", "Social / phones"], ["\u{1F37D}\uFE0F", "Meals"], ["\u{1F369}", "Snacks"],
    ["\u{1F4BB}", "Computers"], ["\u{1F3AC}", "Entertainment"], ["\u{1F3A7}", "Sound / music"],
    ["\u{1F3C3}", "Physical activity"], ["\u{1F4DA}", "Books"], ["\u{1F415}", "Animals"],
    ["\u{1F33F}", "Plants"], ["\u{1F6CF}\uFE0F", "Rooms / furniture"], ["\u{1F455}", "Clothes"],
    ["\u{1F379}", "Alcohol / drugs"], ["\u{26C5}", "Weather"], ["\u{1F3C1}\uFE0F", "Countries"],
    ["\u{1F467}", "Girls"], ["\u{1F466}", "Boys"], ["\u{1F3B1}", "Billiards"]
  ];

  /* ------------------------------------------------------------------ utils */

  function $(sel) { return document.querySelector(sel); }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }
  function slug(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function todayKey() {
    var d = new Date();
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }
  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function parseDateKey(key) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(key || "");
    if (!m) return null;
    var d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
    if (d.getUTCFullYear() !== +m[1] || d.getUTCMonth() !== +m[2] - 1 || d.getUTCDate() !== +m[3]) return null;
    return d;
  }
  function puzzleNumber(key) {
    var d = parseDateKey(key);
    if (!d) return 0;
    return Math.floor((d.getTime() - EPOCH) / 86400000) + 1;
  }
  function formatDate(key) {
    var d = parseDateKey(key);
    if (!d) return key;
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  }

  /* deterministic PRNG so everybody gets the same puzzle on the same day */
  function hashString(text) {
    var h = 2166136261;
    for (var i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function dailyTarget(dateKey) {
    var rnd = mulberry32(hashString("dangandle:" + dateKey));
    return POOL[Math.floor(rnd() * POOL.length)];
  }

  /* ------------------------------------------------------------ comparison */

  var STOP_WORDS = { ultimate: 1, the: 1, of: 1, at: 1, a: 1, an: 1, and: 1, "s": 1, "l": 1, li: 1 };

  function titleTokens(titles) {
    var tokens = {};
    (titles || []).forEach(function (title) {
      slug(title).split(" ").forEach(function (word) {
        if (!word || STOP_WORDS[word]) return;
        tokens[word] = true;
      });
    });
    return tokens;
  }
  function intersects(a, b) {
    for (var key in a) { if (b[key]) return true; }
    return false;
  }
  function sameSet(a, b) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (b.indexOf(a[i]) === -1) return false;
    }
    return true;
  }
  function tolerance(value) { return Math.max(4, Math.round(value * 0.05)); }

  function compareAttr(attr, guess, target) {
    var g, t, i, diff;
    switch (attr.type) {
      case "text":
        g = titleTokens(guess[attr.key]);
        t = titleTokens(target[attr.key]);
        if (slug((guess[attr.key] || []).join(" | ")) === slug((target[attr.key] || []).join(" | "))) {
          return { state: "exact" };
        }
        if (intersects(g, t)) return { state: "close" };
        return { state: "none" };

      case "exact":
        g = guess[attr.key];
        t = target[attr.key];
        if (!t) return { state: "unknown" };
        return { state: g === t ? "exact" : "none" };

      case "number":
        g = guess[attr.key];
        t = target[attr.key];
        if (t === null || t === undefined) return { state: "unknown" };
        if (g === null || g === undefined) return { state: "none" };
        if (g === t) return { state: "exact" };
        diff = t - g;
        if (Math.abs(diff) <= tolerance(t)) return { state: "close", hint: diff > 0 ? "↑" : "↓" };
        return { state: "none", hint: diff > 0 ? "↑" : "↓" };

      case "set":
        g = guess[attr.key] || [];
        t = target[attr.key] || [];
        if (!t.length) return { state: "unknown" };
        if (sameSet(g, t)) return { state: "exact" };
        for (i = 0; i < g.length; i++) {
          if (t.indexOf(g[i]) !== -1) {
            return { state: "close", hits: t.filter(function (x) { return g.indexOf(x) !== -1; }) };
          }
        }
        return { state: "none" };

      case "game":
        if (guess[attr.key] === target[attr.key]) return { state: "exact" };
        if (guess.series === target.series) return { state: "close" };
        return { state: "none" };
    }
    return { state: "none" };
  }

  function compare(guess, target) {
    var out = {};
    ATTRS.forEach(function (attr) { out[attr.key] = compareAttr(attr, guess, target); });
    return out;
  }

  /* --------------------------------------------------------------- filtering
     Keeps only the characters that are still compatible with a clue.        */

  function filterCandidates(candidates, guess, fb) {
    ATTRS.forEach(function (attr) {
      var state = fb[attr.key].state;
      if (state === "unknown") return;
      var g = guess[attr.key];

      if (attr.type === "text") {
        var gt = titleTokens(g);
        candidates = candidates.filter(function (c) {
          var ct = titleTokens(c[attr.key]);
          if (state === "exact") return slug((c[attr.key] || []).join(" | ")) === slug((g || []).join(" | "));
          if (state === "close") return intersects(gt, ct);
          return !intersects(gt, ct);
        });
      } else if (attr.type === "exact") {
        candidates = candidates.filter(function (c) {
          if (!c[attr.key]) return true;
          return state === "exact" ? c[attr.key] === g : c[attr.key] !== g;
        });
      } else if (attr.type === "number") {
        if (g === null || g === undefined) return;
        var tol = tolerance(g);
        candidates = candidates.filter(function (c) {
          var v = c[attr.key];
          if (v === null || v === undefined) return true;
          if (state === "exact") return v === g;
          if (state === "close") return Math.abs(v - g) <= tol;
          return fb[attr.key].hint === "↑" ? v > g : v < g;
        });
      } else if (attr.type === "set") {
        var gs = g || [];
        if (!gs.length) return;
        candidates = candidates.filter(function (c) {
          var cs = c[attr.key] || [];
          var overlap = cs.some(function (x) { return gs.indexOf(x) !== -1; });
          if (state === "exact") return sameSet(cs, gs);
          if (state === "close") return overlap;
          return !overlap;
        });
      } else if (attr.type === "game") {
        candidates = candidates.filter(function (c) {
          if (state === "exact") return c[attr.key] === g;
          if (state === "close") return c.series === guess.series;
          return c.series !== guess.series;
        });
      }
    });
    return candidates;
  }

  function remainingCandidates() {
    var candidates = POOL.slice();
    state.guesses.forEach(function (guess) {
      candidates = filterCandidates(candidates, guess, compare(guess, state.target));
    });
    return candidates;
  }

  /* ------------------------------------------------------------------ state */

  var state = {
    dateKey: todayKey(),
    target: null,
    guesses: [],
    status: "playing"
  };

  function characterById(id) {
    for (var i = 0; i < CHARACTERS.length; i++) {
      if (CHARACTERS[i].id === id) return CHARACTERS[i];
    }
    return null;
  }

  function loadState() {
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch (e) { raw = null; }
    var params = new URLSearchParams(window.location.search);
    var requested = params.get("d");

    if (raw && raw.dateKey && (!requested || raw.dateKey === requested)) {
      var sameDay = raw.dateKey === todayKey();
      if (!sameDay && requested) sameDay = true; /* archived puzzle */
      var target = characterById(raw.targetId);
      if (target && sameDay) {
        state.dateKey = raw.dateKey;
        state.target = target;
        state.guesses = (raw.guessIds || []).map(characterById).filter(Boolean);
        state.status = raw.status || "playing";
        return;
      }
    }
    startNewGame(requested);
  }

  function startNewGame(dateKey) {
    state.guesses = [];
    state.status = "playing";
    state.dateKey = dateKey && parseDateKey(dateKey) ? dateKey : todayKey();
    state.target = dailyTarget(state.dateKey);
    saveState();
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        dateKey: state.dateKey,
        targetId: state.target ? state.target.id : null,
        guessIds: state.guesses.map(function (g) { return g.id; }),
        status: state.status
      }));
    } catch (e) { /* storage unavailable — the game still works */ }
  }

  /* ------------------------------------------------------------------ stats */

  function loadStats() {
    try {
      var raw = JSON.parse(localStorage.getItem(STATS_KEY));
      if (raw && typeof raw === "object") return raw;
    } catch (e) { /* ignore */ }
    return { played: 0, wins: 0, streak: 0, best: 0, dist: {} };
  }
  function saveStats(stats) {
    try { localStorage.setItem(STATS_KEY, JSON.stringify(stats)); } catch (e) { /* ignore */ }
  }
  function recordResult(won) {
    var stats = loadStats();
    var attempts = state.guesses.length;
    if (won) {
      stats.played += 1;
      stats.wins += 1;
      stats.streak += 1;
      stats.best = Math.max(stats.best || 0, stats.streak);
      stats.dist[attempts] = (stats.dist[attempts] || 0) + 1;
    } else {
      stats.played += 1;
      stats.streak = 0;
      stats.dist["x"] = (stats.dist["x"] || 0) + 1;
    }
    saveStats(stats);
  }

  /* --------------------------------------------------------------- rendering */

  function portrait(character, className) {
    if (character.image) {
      var img = el("img", className || null);
      img.src = character.image;
      img.alt = character.name;
      img.loading = "lazy";
      img.width = 120;
      img.height = 120;
      return img;
    }
    var fallback = el("div", "portrait-fallback" + (className ? " " + className : ""),
      character.name.split(" ").map(function (p) { return p[0]; }).join(""));
    fallback.setAttribute("role", "img");
    fallback.setAttribute("aria-label", character.name);
    return fallback;
  }

  function displayValue(attr, character) {
    var value = character[attr.key];
    switch (attr.type) {
      case "text": return (value || []).join(", ");
      case "number": return value === null || value === undefined ? "Unknown" : value + " " + attr.unit;
      case "set": return (value || []).length ? value.join(" ") : "Unknown";
      case "game": return value;
      default:
        if (attr.key === "talent" && value === "NAN") return "Unassigned";
        return value || "Unknown";
    }
  }

  function buildGuessRow(guess) {
    var row = el("div", "guess" + (guess.id === state.target.id ? " is-win" : ""));
    var fb = compare(guess, state.target);

    var pic = el("div", "guess-cell pic");
    pic.appendChild(portrait(guess));
    row.appendChild(pic);

    var name = el("div", "guess-cell name");
    name.appendChild(el("span", null, guess.name));
    row.appendChild(name);

    ATTRS.forEach(function (attr) {
      var cell = el("div", "guess-cell clue-" + fb[attr.key].state + (attr.type === "text" ? " title" : ""));
      if (attr.type === "set") {
        var items = guess[attr.key] || [];
        if (!items.length) {
          cell.appendChild(el("span", null, "Unknown"));
        } else {
          items.forEach(function (item) {
            var chip = el("span", "emo", item);
            if (fb[attr.key].hits && fb[attr.key].hits.indexOf(item) !== -1) chip.classList.add("hit");
            cell.appendChild(chip);
          });
        }
      } else {
        cell.appendChild(el("span", null, displayValue(attr, guess)));
      }
      if (fb[attr.key].hint) cell.appendChild(el("span", "hint", fb[attr.key].hint));
      row.appendChild(cell);
    });

    return row;
  }

  function renderGuesses() {
    var box = $("#guesses");
    box.innerHTML = "";
    /* newest guess first */
    state.guesses.slice().reverse().forEach(function (guess) {
      box.appendChild(buildGuessRow(guess));
    });
  }

  function renderInfo() {
    $("#puzzle-date").textContent = formatDate(state.dateKey);
    $("#attempts-left").textContent = state.guesses.length + " / " + MAX_ATTEMPTS;
  }

  function renderCandidates() {
    var node = $("#candidates");
    if (state.status !== "playing") {
      node.textContent = "— case closed";
      node.classList.remove("is-low");
      return;
    }
    var count = remainingCandidates().length;
    node.textContent = count + (count === 1 ? " candidate left" : " candidates left");
    node.classList.toggle("is-low", count <= 8);
  }

  function render() {
    renderInfo();
    renderGuesses();
    renderCandidates();
    var over = state.status !== "playing";
    $("#guess-input").disabled = over;
    $("#guess-form").querySelector(".primary-btn").disabled = over;
    $("#giveup-btn").disabled = over;
  }

  /* ------------------------------------------------------------- result modal */

  function openModal(id) {
    var modal = $(id);
    modal.hidden = false;
    document.addEventListener("keydown", escHandler);
  }
  function closeModal(id) {
    $(id).hidden = true;
  }
  function escHandler(event) {
    if (event.key === "Escape") {
      document.querySelectorAll(".modal").forEach(function (m) { m.hidden = true; });
      document.removeEventListener("keydown", escHandler);
    }
  }

  function showResult() {
    var won = state.status === "won";
    var target = state.target;

    $("#result-kicker").textContent = won ? "Case closed — correct!" : "Case closed — you ran out of attempts";
    $("#result-title").textContent = target.name;
    $("#result-sub").textContent = (target.title || []).join(" · ") + " · " + target.appearanceLabel;

    var box = document.getElementById("result-portrait-box");
    if (box) {
      box.innerHTML = "";
      box.appendChild(portrait(target, "result-portrait"));
    }

    var table = $("#result-table");
    table.innerHTML = "";
    ATTRS.forEach(function (attr) {
      var row = el("tr");
      row.appendChild(el("td", null, attr.label));
      var valueCell = el("td", "value");
      valueCell.textContent = attr.type === "game" ? target.appearanceLabel : displayValue(attr, target);
      row.appendChild(valueCell);
      table.appendChild(row);
    });

    $("#share-hint").textContent = "";
    openModal("#result-modal");
  }

  function shareText() {
    var lines = [];
    lines.push("Dangandle #" + puzzleNumber(state.dateKey) + " (" + formatDate(state.dateKey) + ")");
    state.guesses.forEach(function (guess) {
      var fb = compare(guess, state.target);
      var row = ATTRS.map(function (attr) {
        var s = fb[attr.key].state;
        if (s === "exact") return "🟩";
        if (s === "close") return "🟨";
        if (s === "unknown") return "⬜";
        return "🟥";
      }).join("");
      lines.push(row);
    });
    var attempts = state.status === "won" ? state.guesses.length : "X";
    lines.push(attempts + "/" + MAX_ATTEMPTS);
    lines.push(window.location.origin + window.location.pathname);
    return lines.join("\n");
  }

  function copyShare() {
    var text = shareText();
    var hint = $("#share-hint");
    var done = function () { hint.textContent = "Result copied to the clipboard."; };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  }
  function fallbackCopy(text, done) {
    var area = el("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    try { document.execCommand("copy"); done(); } catch (e) { /* ignore */ }
    document.body.removeChild(area);
  }

  /* ------------------------------------------------------------------- stats */

  function renderStats() {
    var stats = loadStats();
    var grid = $("#stats-grid");
    grid.innerHTML = "";
    var winRate = stats.played ? Math.round((stats.wins / stats.played) * 100) : 0;
    [
      [stats.played, "Played"], [winRate + "%", "Win rate"],
      [stats.streak || 0, "Streak"], [stats.best || 0, "Best streak"]
    ].forEach(function (pair) {
      var box = el("div", "stat");
      box.appendChild(el("b", null, pair[0]));
      box.appendChild(el("span", null, pair[1]));
      grid.appendChild(box);
    });

    var dist = $("#distribution");
    dist.innerHTML = "";
    var rows = [];
    for (var i = 1; i <= MAX_ATTEMPTS; i++) rows.push([i, stats.dist[i] || 0]);
    rows.push(["X", stats.dist["x"] || 0]);
    var max = Math.max.apply(null, rows.map(function (r) { return r[1]; }).concat([1]));
    rows.forEach(function (row) {
      var line = el("div", "dist-row");
      line.appendChild(el("i", null, row[0]));
      var bar = el("div", "dist-bar");
      var fill = el("b");
      fill.style.width = Math.round((row[1] / max) * 100) + "%";
      bar.appendChild(fill);
      line.appendChild(bar);
      line.appendChild(el("i", null, row[1]));
      dist.appendChild(line);
    });
  }

  /* ---------------------------------------------------------------- guessing */

  function toast(message) {
    var old = document.querySelector(".toast");
    if (old) old.remove();
    var node = el("div", "toast", message);
    $("#guess-form").parentNode.insertBefore(node, $("#guess-form").nextSibling);
    setTimeout(function () { if (node.parentNode) node.remove(); }, 3200);
  }

  function submitGuess(character) {
    if (state.status !== "playing") return;
    if (!character) {
      toast("Pick a character from the list.");
      return;
    }
    if (state.guesses.some(function (g) { return g.id === character.id; })) {
      toast(character.name + " was already guessed.");
      return;
    }
    if (state.guesses.length >= MAX_ATTEMPTS) return;

    state.guesses.push(character);
    if (character.id === state.target.id) {
      state.status = "won";
      recordResult(true);
    } else if (state.guesses.length >= MAX_ATTEMPTS) {
      state.status = "lost";
      recordResult(false);
    }
    saveState();
    render();

    var input = $("#guess-input");
    input.value = "";
    hideSuggestions();

    if (state.status !== "playing") {
      setTimeout(showResult, 420);
    }
  }

  function findCharacter(text) {
    var query = slug(text);
    if (!query) return null;
    var best = null;
    var bestScore = -1;
    CHARACTERS.forEach(function (c) {
      var names = [c.name].concat(c.aliases || []);
      names.forEach(function (name) {
        var key = slug(name);
        var score = -1;
        if (key === query) score = 100;
        else if (key.indexOf(query) === 0) score = 80 - (key.length - query.length) * 0.1;
        else if (key.indexOf(" " + query) !== -1) score = 60;
        else if (key.indexOf(query) !== -1) score = 40;
        if (score > bestScore) { bestScore = score; best = c; }
      });
    });
    return bestScore >= 0 ? best : null;
  }

  /* ------------------------------------------------------------- suggestions */

  var activeSuggestion = -1;

  function suggestionsFor(query) {
    var q = slug(query);
    if (!q) return [];
    var list = [];
    CHARACTERS.forEach(function (c) {
      var names = [c.name].concat(c.aliases || []);
      var match = null;
      var label = "";
      names.forEach(function (name) {
        var key = slug(name);
        if (!match && key.indexOf(q) === 0) { match = 100 - key.length * 0.1; label = name; }
        else if (!match && key.indexOf(" " + q) !== -1) { match = 60; label = name; }
        else if (!match && key.indexOf(q) !== -1) { match = 40; label = name; }
      });
      if (match !== null) list.push({ character: c, score: match, label: label });
    });
    list.sort(function (a, b) { return b.score - a.score || a.character.name.localeCompare(b.character.name); });
    return list.slice(0, 8);
  }

  function renderSuggestions() {
    var list = $("#suggestions");
    list.innerHTML = "";
    activeSuggestion = -1;
    var query = $("#guess-input").value;
    if (!query.trim()) return;

    var matches = suggestionsFor(query);
    matches.forEach(function (match, index) {
      var item = el("li");
      item.setAttribute("role", "option");
      item.appendChild(portrait(match.character));
      item.appendChild(el("span", null, match.character.name));
      item.appendChild(el("small", null, match.label !== match.character.name ? "aka " + match.label : match.character.appearance));
      item.addEventListener("mousedown", function (event) {
        event.preventDefault();
        submitGuess(match.character);
      });
      item.dataset.index = index;
      list.appendChild(item);
    });
    if (!matches.length) {
      var none = el("li", null, "No matching character");
      none.style.cursor = "default";
      none.style.color = "var(--text-faint)";
      list.appendChild(none);
    }
  }

  function hideSuggestions() {
    $("#suggestions").innerHTML = "";
    activeSuggestion = -1;
  }

  function moveActive(step) {
    var items = Array.prototype.slice.call($("#suggestions").querySelectorAll("li[data-index]"));
    if (!items.length) return;
    activeSuggestion = (activeSuggestion + step + items.length) % items.length;
    items.forEach(function (item, i) { item.classList.toggle("is-active", i === activeSuggestion); });
    items[activeSuggestion].scrollIntoView({ block: "nearest" });
  }

  /* ------------------------------------------------------------------- wiring */

  function bind() {
    var input = $("#guess-input");
    var form = $("#guess-form");

    input.addEventListener("input", renderSuggestions);
    input.addEventListener("focus", renderSuggestions);

    input.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown") { event.preventDefault(); moveActive(1); }
      else if (event.key === "ArrowUp") { event.preventDefault(); moveActive(-1); }
      else if (event.key === "Escape") { hideSuggestions(); }
      else if (event.key === "Enter") {
        var items = $("#suggestions").querySelectorAll("li[data-index]");
        if (activeSuggestion >= 0 && items[activeSuggestion]) {
          event.preventDefault();
          var character = suggestionsFor(input.value)[activeSuggestion].character;
          submitGuess(character);
        }
      }
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var value = input.value.trim();
      if (!value) return;
      var exact = suggestionsFor(value)[0];
      submitGuess(exact ? exact.character : findCharacter(value));
    });

    document.addEventListener("click", function (event) {
      if (!event.target.closest(".input-wrap")) hideSuggestions();
    });

    $("#giveup-btn").addEventListener("click", function () {
      if (state.status !== "playing") return;
      if (!window.confirm("Reveal the secret character? This counts as a loss.")) return;
      state.status = "lost";
      recordResult(false);
      saveState();
      render();
      showResult();
    });

    $("#share-btn").addEventListener("click", copyShare);
    $("#result-dismiss").addEventListener("click", function () { closeModal("#result-modal"); });
    $("#result-close").addEventListener("click", function () { closeModal("#result-modal"); });

    $("#stats-btn").addEventListener("click", function () { renderStats(); openModal("#stats-modal"); });
    $("#stats-close").addEventListener("click", function () { closeModal("#stats-modal"); });
    $("#stats-reset").addEventListener("click", function () {
      saveStats({ played: 0, wins: 0, streak: 0, best: 0, dist: {} });
      renderStats();
    });

    $("#help-btn").addEventListener("click", function () { openModal("#help-modal"); });
    $("#help-close").addEventListener("click", function () { closeModal("#help-modal"); });

    document.querySelectorAll(".modal").forEach(function (modal) {
      modal.addEventListener("click", function (event) {
        if (event.target === modal) modal.hidden = true;
      });
    });
  }

  function buildEmojiKey() {
    var key = $("#emoji-key");
    if (!key) return;
    key.innerHTML = "";
    EMOJI_KEY.forEach(function (pair) {
      var item = el("li");
      item.appendChild(el("b", null, pair[0]));
      item.appendChild(el("span", null, pair[1]));
      key.appendChild(item);
    });
  }

  /* -------------------------------------------------------------------- init */

  buildEmojiKey();
  bind();
  loadState();
  render();
  if (state.status !== "playing") setTimeout(showResult, 250);

  /* Debug helpers, only exposed when the page is opened with ?debug=1 */
  if (window.location.search.indexOf("debug=1") !== -1) {
    window.Dangandle = {
      state: state,
      compare: compare,
      remainingCandidates: remainingCandidates,
      dailyTarget: dailyTarget,
      startNewGame: startNewGame,
      submitGuess: submitGuess,
      shareText: shareText
    };
  }
})();
