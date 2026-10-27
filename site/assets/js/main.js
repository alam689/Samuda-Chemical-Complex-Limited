/* Samuda Chemical — site interactions (no dependencies) */
(function () {
  "use strict";

  var doc = document.documentElement;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var store = {
    get: function (k, fallback) {
      try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
    },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };

  /* ---------------- header state ---------------- */
  function onScroll() { doc.classList.toggle("is-scrolled", window.scrollY > 24); }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------------- dropdowns ---------------- */
  var dropItems = $$(".nav__item--drop");
  function closeDrops(except) {
    dropItems.forEach(function (item) {
      if (item === except) return;
      item.classList.remove("is-open");
      var b = $(".nav__link", item); if (b) b.setAttribute("aria-expanded", "false");
    });
  }
  dropItems.forEach(function (item) {
    var btn = $(".nav__link", item);
    btn.addEventListener("click", function (ev) {
      ev.stopPropagation();
      var open = !item.classList.contains("is-open");
      closeDrops(item);
      item.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
    item.addEventListener("mouseleave", function () {
      item.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
    });
  });
  document.addEventListener("click", function () { closeDrops(); });
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    var open = $(".nav__item--drop.is-open .nav__link");
    closeDrops();
    if (open) open.focus();
    if (doc.classList.contains("menu-open")) toggleMenu(false);
  });

  /* ---------------- mobile drawer ---------------- */
  var toggle = $("[data-menu-toggle]");
  var drawer = $("[data-drawer]");
  function toggleMenu(force) {
    var open = typeof force === "boolean" ? force : !doc.classList.contains("menu-open");
    doc.classList.toggle("menu-open", open);
    drawer.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    $(".sr-only", toggle).textContent = open ? "Close menu" : "Open menu";
    if (open) { var first = $("a", drawer); if (first) first.focus(); } else { toggle.focus(); }
  }
  if (toggle && drawer) {
    toggle.addEventListener("click", function () { toggleMenu(); });
    window.addEventListener("resize", function () { if (window.innerWidth > 1100 && doc.classList.contains("menu-open")) toggleMenu(false); });
  }

  /* ---------------- reveal on scroll ---------------- */
  $$(".reveal-words").forEach(function (el) {
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var s = document.createElement("span");
            s.className = "w"; s.textContent = part; s.style.transitionDelay = (i++ * 28) + "ms";
            frag.appendChild(s);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) { walk(child); }
      });
    })(el);
  });

  var revealEls = $$(".reveal, .reveal-words, [data-count]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        if (entry.target.hasAttribute("data-count")) countUp(entry.target);
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    var start = null, dur = 1600;
    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))).toLocaleString("en-US");
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* ---------------- toast ---------------- */
  var toastEl = $("[data-toast]"), toastTimer;
  function toast(html) {
    if (!toastEl) return;
    toastEl.innerHTML = html;
    toastEl.classList.add("is-shown");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-shown"); }, 3600);
  }

  /* ---------------- inquiry list ---------------- */
  var KEY = "sccl-inquiry";
  var basket = store.get(KEY, []);
  var contactHref = ($("[data-basket-link]") || {}).getAttribute ? $("[data-basket-link]").getAttribute("href") : "contact.html#rfq";

  function saveBasket() { store.set(KEY, basket); renderBasket(); }
  function renderBasket() {
    $$("[data-basket-count]").forEach(function (n) { n.textContent = basket.length; });
    $$("[data-basket-link]").forEach(function (l) {
      l.classList.toggle("has-items", basket.length > 0);
      l.setAttribute("aria-label", "Inquiry list, " + basket.length + " product" + (basket.length === 1 ? "" : "s"));
    });
    $$("[data-add-inquiry]").forEach(function (b) {
      var on = basket.indexOf(b.getAttribute("data-add-inquiry")) > -1;
      b.classList.toggle("is-added", on);
      b.setAttribute("aria-pressed", String(on));
      var label = $("span", b);
      if (label && b.classList.contains("add-btn")) label.textContent = on ? "Added" : "Inquiry";
    });
    renderPicked();
  }
  function addProduct(name) {
    if (name && basket.indexOf(name) === -1) basket.push(name);
    saveBasket();
  }
  function removeProduct(name) {
    basket = basket.filter(function (n) { return n !== name; });
    saveBasket();
  }
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-add-inquiry]");
    if (!btn) return;
    var name = btn.getAttribute("data-add-inquiry");
    if (basket.indexOf(name) > -1) {
      removeProduct(name);
      toast("Removed " + escapeHtml(name) + " from your inquiry list");
    } else {
      addProduct(name);
      toast(escapeHtml(name) + " added to your inquiry list · <a href=\"" + contactHref + "\">Request quote</a>");
      $$("[data-basket-link]").forEach(function (l) { l.classList.remove("bump"); void l.offsetWidth; l.classList.add("bump"); });
    }
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }

  /* picked products on the RFQ form */
  var picked = $("[data-picked]");
  function renderPicked() {
    if (!picked) return;
    picked.innerHTML = "";
    basket.forEach(function (name) {
      var chip = document.createElement("span");
      chip.className = "picked__chip";
      chip.innerHTML = escapeHtml(name) + ' <button type="button" aria-label="Remove ' + escapeHtml(name) + '">&times;</button>';
      $("button", chip).addEventListener("click", function () { removeProduct(name); });
      picked.appendChild(chip);
    });
    var hidden = $("[data-picked-input]");
    if (hidden) hidden.value = basket.join(", ");
  }
  var pickSelect = $("[data-pick-select]");
  if (pickSelect) {
    pickSelect.addEventListener("change", function () {
      if (pickSelect.value) addProduct(pickSelect.value);
      pickSelect.value = "";
      var f = pickSelect.closest(".field"); if (f) f.classList.remove("has-error");
    });
  }

  /* URL parameters: ?product=…&doc=TDS */
  var params = new URLSearchParams(window.location.search);
  if (params.get("product")) addProduct(params.get("product"));
  var docReq = params.get("doc");
  var msg = $("#rfq-message");
  if (docReq && msg && !msg.value) {
    msg.value = "Please share the " + (docReq === "SDS" ? "Safety Data Sheet (SDS)" : "Technical Data Sheet (TDS)") + " for " + (params.get("product") || "the selected product") + ".";
  }
  renderBasket();

  /* ---------------- tabs ---------------- */
  $$("[data-tabs]").forEach(function (tabs) {
    var btns = $$("[role=tab]", tabs);
    function select(btn, focus) {
      btns.forEach(function (b) {
        var on = b === btn;
        b.setAttribute("aria-selected", String(on));
        b.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(b.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
      if (focus) btn.focus();
    }
    btns.forEach(function (b, i) {
      b.addEventListener("click", function () { select(b); });
      b.addEventListener("keydown", function (ev) {
        if (ev.key === "ArrowRight" || ev.key === "ArrowLeft") {
          var next = btns[(i + (ev.key === "ArrowRight" ? 1 : btns.length - 1)) % btns.length];
          select(next, true);
        }
      });
    });
    var hash = window.location.hash.replace("#", "");
    var initial = btns.filter(function (b) { return b.getAttribute("data-hash") === hash; })[0];
    if (initial) select(initial);
  });

  /* ---------------- catalogue filtering ---------------- */
  var catalogue = $("[data-catalogue]");
  if (catalogue) {
    var cards = $$("[data-product-card]", catalogue);
    var search = $("[data-search]");
    var indSel = $("[data-filter-industry]");
    var catBtns = $$("[data-filter-category]");
    var countEl = $("[data-result-count]");
    var emptyEl = $("[data-empty]");
    var activeCat = params.get("category") || "";
    if (params.get("industry") && indSel) indSel.value = params.get("industry");

    function apply() {
      var q = (search.value || "").trim().toLowerCase();
      var ind = indSel ? indSel.value : "";
      var shown = 0;
      cards.forEach(function (c) {
        var ok = (!activeCat || c.getAttribute("data-category") === activeCat) &&
          (!ind || c.getAttribute("data-industries").split(" ").indexOf(ind) > -1) &&
          (!q || c.getAttribute("data-name").indexOf(q) > -1 || c.textContent.toLowerCase().indexOf(q) > -1);
        c.hidden = !ok;
        if (ok) shown++;
      });
      catBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filter-category") === activeCat)); });
      var all = $("[data-filter-all]"); if (all) all.setAttribute("aria-pressed", String(!activeCat));
      countEl.textContent = shown + (shown === 1 ? " product" : " products");
      emptyEl.classList.toggle("is-shown", shown === 0);
      var url = new URL(window.location.href);
      activeCat ? url.searchParams.set("category", activeCat) : url.searchParams.delete("category");
      ind ? url.searchParams.set("industry", ind) : url.searchParams.delete("industry");
      history.replaceState(null, "", url);
    }
    catBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var c = b.getAttribute("data-filter-category");
        activeCat = activeCat === c ? "" : c; apply();
      });
    });
    var allBtn = $("[data-filter-all]");
    if (allBtn) allBtn.addEventListener("click", function () { activeCat = ""; apply(); });
    search.addEventListener("input", apply);
    if (indSel) indSel.addEventListener("change", apply);
    $$("[data-reset]").forEach(function (b) {
      b.addEventListener("click", function () { activeCat = ""; search.value = ""; if (indSel) indSel.value = ""; apply(); search.focus(); });
    });
    apply();
  }

  /* ---------------- industry panels (tap support) ---------------- */
  $$(".panel").forEach(function (p) {
    p.addEventListener("mouseenter", function () { $$(".panel").forEach(function (o) { o.classList.toggle("is-active", o === p); }); });
  });

  /* ---------------- forms ---------------- */
  var MESSAGES = {
    valueMissing: "This field is required.",
    typeMismatch: "Please enter a valid email address.",
    patternMismatch: "Please check the format of this field.",
    tooShort: "Please add a little more detail."
  };

  function fieldError(input) {
    if (input.type === "file" && input.files && input.files[0]) {
      var f = input.files[0];
      var max = parseInt(input.getAttribute("data-max-mb") || "5", 10);
      var okTypes = (input.getAttribute("accept") || "").split(",").map(function (s) { return s.trim().toLowerCase(); });
      var ext = "." + f.name.split(".").pop().toLowerCase();
      if (okTypes.length && okTypes[0] && okTypes.indexOf(ext) === -1) return "Please upload a PDF or Word document.";
      if (f.size > max * 1024 * 1024) return "File is larger than " + max + " MB.";
    }
    if (input.hasAttribute("data-phone") && input.value.trim() && !/^[0-9+()\-\s]{7,20}$/.test(input.value.trim())) {
      return input.getAttribute("data-msg") || "Please enter a valid phone number.";
    }
    if (input.validity.valid) return "";
    if (input.validity.valueMissing && input.type !== "checkbox" && input.type !== "file") return MESSAGES.valueMissing;
    for (var k in MESSAGES) { if (input.validity[k]) return input.getAttribute("data-msg") || MESSAGES[k]; }
    return "Please check this field.";
  }

  function showError(input, text) {
    var field = input.closest(".field") || input.closest(".consent");
    if (!field) return;
    var err = $(".field__error", field);
    field.classList.toggle("has-error", !!text);
    if (err) err.textContent = text;
    input.setAttribute("aria-invalid", text ? "true" : "false");
  }

  function makeRef(prefix) {
    var d = new Date();
    var ymd = d.getFullYear() + String(d.getMonth() + 1).padStart(2, "0") + String(d.getDate()).padStart(2, "0");
    var rand = Math.random().toString(36).slice(2, 6).toUpperCase();
    return "SCCL-" + prefix + "-" + ymd + "-" + rand;
  }

  $$("form[data-form]").forEach(function (form) {
    var inputs = $$("input, select, textarea", form).filter(function (i) { return i.type !== "hidden" && !i.hasAttribute("data-pick-select"); });
    inputs.forEach(function (input) {
      input.addEventListener("blur", function () { if (input.value || input.type === "checkbox") showError(input, fieldError(input)); });
      input.addEventListener("input", function () { if (input.getAttribute("aria-invalid") === "true") showError(input, fieldError(input)); });
      if (input.type === "file") {
        input.addEventListener("change", function () {
          var label = $("[data-file-label]", form);
          if (label) label.textContent = input.files[0] ? input.files[0].name : "Upload your CV";
          showError(input, fieldError(input));
        });
      }
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var firstBad = null;
      inputs.forEach(function (input) {
        var msg = fieldError(input);
        showError(input, msg);
        if (msg && !firstBad) firstBad = input;
      });
      if (form.hasAttribute("data-needs-products") && basket.length === 0) {
        var ps = $("[data-pick-select]", form);
        var pf = ps.closest(".field");
        pf.classList.add("has-error");
        $(".field__error", pf).textContent = "Please add at least one product.";
        if (!firstBad) firstBad = ps;
      }
      var alertEl = $(".form-alert", form);
      if (firstBad) {
        if (alertEl) { alertEl.textContent = "Please review the highlighted fields and try again."; alertEl.classList.add("is-shown"); }
        firstBad.focus();
        return;
      }
      if (alertEl) alertEl.classList.remove("is-shown");

      var btn = $("button[type=submit]", form);
      btn.classList.add("is-loading");
      var ref = makeRef(form.getAttribute("data-prefix") || "INQ");
      var endpoint = form.getAttribute("data-endpoint");
      var payload = new FormData(form);
      payload.append("reference", ref);
      payload.append("submittedAt", new Date().toISOString());

      var send = endpoint
        ? fetch(endpoint, { method: "POST", body: payload }).then(function (r) { if (!r.ok) throw new Error(r.status); })
        : new Promise(function (resolve) { setTimeout(resolve, 900); }); // no backend configured yet

      send.then(function () {
        var success = document.getElementById(form.getAttribute("data-success"));
        $("[data-ref]", success).textContent = ref;
        form.hidden = true;
        success.classList.add("is-shown");
        success.setAttribute("tabindex", "-1");
        success.focus();
        if (form.hasAttribute("data-needs-products")) { basket = []; saveBasket(); }
      }).catch(function () {
        if (alertEl) { alertEl.textContent = "Sorry — we couldn't send your message. Please try again or email info@scclbd.com."; alertEl.classList.add("is-shown"); }
      }).then(function () { btn.classList.remove("is-loading"); });
    });
  });

  $$("[data-form-reset]").forEach(function (b) {
    b.addEventListener("click", function () {
      var success = b.closest(".success");
      var form = document.querySelector("form[data-success='" + success.id + "']");
      form.reset(); form.hidden = false; success.classList.remove("is-shown");
      renderBasket();
      var first = $("input, select, textarea", form); if (first) first.focus();
    });
  });

  /* ---------------- language toggle (policy page) ---------------- */
  $$("[data-lang-scope]").forEach(function (scope) {
    var btns = $$("[data-lang-set]", scope);
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        scope.setAttribute("data-lang", b.getAttribute("data-lang-set"));
        btns.forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      });
    });
  });

  /* ---------------- policy index filter ---------------- */
  var policyList = $("[data-policy-list]");
  if (policyList) {
    var pItems = $$("[data-policy]", policyList);
    var pSearch = $("[data-policy-search]");
    var pChips = $$("[data-policy-group]");
    var pEmpty = $("[data-policy-empty]");
    var pGroup = "";
    var allCount = $("[data-group-count]");
    if (allCount) allCount.textContent = "(" + pItems.length + ")";
    function filterPolicies() {
      var q = (pSearch.value || "").trim().toLowerCase(), shown = 0;
      pItems.forEach(function (li) {
        var ok = (!pGroup || li.getAttribute("data-policy") === pGroup) && (!q || li.textContent.toLowerCase().indexOf(q) > -1);
        li.hidden = !ok; if (ok) shown++;
      });
      pChips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.getAttribute("data-policy-group") === pGroup)); });
      pEmpty.classList.toggle("is-shown", shown === 0);
    }
    pChips.forEach(function (c) { c.addEventListener("click", function () { pGroup = c.getAttribute("data-policy-group"); filterPolicies(); }); });
    pSearch.addEventListener("input", filterPolicies);
  }

  /* ---------------- back to top ---------------- */
  $$("[data-to-top]").forEach(function (a) {
    a.addEventListener("click", function (ev) { ev.preventDefault(); window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" }); });
  });
})();
