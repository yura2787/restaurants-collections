(function () {
  "use strict";

  // ── Toast ──
  function toast(message, type) {
    var c = document.getElementById("toast-container");
    if (!c) return;
    var el = document.createElement("div");
    el.className = "toast-msg toast-msg--" + (type || "info");
    el.textContent = message;
    c.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("toast-msg--show"); });
    setTimeout(function () {
      el.classList.remove("toast-msg--show");
      setTimeout(function () { el.remove(); }, 300);
    }, 2600);
  }

  // ── Theme toggle ──
  var toggle = document.getElementById("theme-toggle");
  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || "light";
  }
  function syncIcon() {
    if (toggle) toggle.textContent = currentTheme() === "dark" ? "☀️" : "🌙";
  }
  syncIcon();
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      syncIcon();
    });
  }

  // ── Favorites toggle ──
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".fav-btn");
    if (!btn) return;
    e.preventDefault();
    var id = btn.getAttribute("data-id");
    btn.disabled = true;
    fetch("/toggle_favorite/" + id, { method: "POST", headers: { "X-Requested-With": "fetch" } })
      .then(function (r) {
        if (r.status === 401) { toast("Sign in to save favourites", "info"); return null; }
        return r.json();
      })
      .then(function (data) {
        if (!data) return;
        if (data.is_favorite) {
          btn.classList.add("fav-btn--active");
          btn.textContent = "♥";
          toast("Added to favourites ♥", "success");
        } else {
          btn.classList.remove("fav-btn--active");
          btn.textContent = "♡";
          toast("Removed from favourites", "info");
          if (document.body.getAttribute("data-page") === "favorites") {
            var card = btn.closest(".r-card");
            if (card) card.remove();
          }
        }
      })
      .catch(function () { toast("Something went wrong. Please try again", "error"); })
      .finally(function () { btn.disabled = false; });
  });

  // ── Sort select ──
  var sortSel = document.getElementById("sort-select");
  if (sortSel) {
    sortSel.addEventListener("change", function () {
      var parts = sortSel.value.split("|");
      var cuisine = sortSel.getAttribute("data-cuisine") || "";
      var url = "/?sort=" + parts[0] + "&direction=" + parts[1];
      if (cuisine) url += "&cuisine=" + encodeURIComponent(cuisine);
      window.location.href = url;
    });
  }

  // ── Lightbox ──
  var lightbox = document.getElementById("lightbox");
  if (lightbox) {
    var lbImg = document.getElementById("lightbox-img");
    document.addEventListener("click", function (e) {
      var img = e.target.closest(".lightbox-img");
      if (img) {
        lbImg.src = img.src;
        lightbox.classList.add("lightbox--open");
        return;
      }
      if (e.target === lightbox || e.target.classList.contains("lightbox-close")) {
        lightbox.classList.remove("lightbox--open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") lightbox.classList.remove("lightbox--open");
    });
  }
})();
