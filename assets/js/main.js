/* Progressive enhancement only. The site works fully without JavaScript. */
(function () {
  "use strict";

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Dossier pages: a reading progress hairline, one reveal per section, and
     a contents rail that marks where the reader currently is. */
  var dossier = document.querySelector(".dossier");
  if (dossier) {
    var rule = document.createElement("div");
    rule.className = "reading-rule";
    rule.setAttribute("aria-hidden", "true");
    document.body.appendChild(rule);
    var onScroll = function () {
      var el = document.scrollingElement || document.documentElement;
      var max = el.scrollHeight - el.clientHeight;
      rule.style.width = (max > 40 ? (el.scrollTop / max) * 100 : 0) + "%";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    var sections = [].slice.call(dossier.querySelectorAll(".dossier-body > section"));

    if (!reduced && window.IntersectionObserver) {
      sections.forEach(function (s) { s.setAttribute("data-reveal", ""); });
      var revealer = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add("in");
          revealer.unobserve(e.target);
        });
      }, { rootMargin: "0px 0px -12% 0px", threshold: 0.05 });
      sections.forEach(function (s) { revealer.observe(s); });
    }

    var railLinks = [].slice.call(dossier.querySelectorAll(".dossier-rail a"));
    if (railLinks.length && window.IntersectionObserver) {
      var marker = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          railLinks.forEach(function (a) {
            if (a.getAttribute("href") === "#" + e.target.id) {
              a.setAttribute("aria-current", "true");
            } else {
              a.removeAttribute("aria-current");
            }
          });
        });
      }, { rootMargin: "-25% 0px -65% 0px" });
      sections.forEach(function (s) { if (s.id) marker.observe(s); });
    }
  }

  /* Native share button and copy link (share row). */
  var nativeBtn = document.querySelector(".share-native");
  if (nativeBtn && navigator.share) {
    nativeBtn.hidden = false;
    nativeBtn.addEventListener("click", function () {
      navigator.share({
        title: document.title,
        url: window.location.href
      }).catch(function () {});
    });
  }
  var copyBtn = document.querySelector(".share-copy");
  if (copyBtn && navigator.clipboard) {
    copyBtn.hidden = false;
    copyBtn.addEventListener("click", function () {
      navigator.clipboard.writeText(window.location.href).then(function () {
        var old = copyBtn.textContent;
        copyBtn.textContent = "Link copied";
        setTimeout(function () { copyBtn.textContent = old; }, 2000);
      });
    });
  }

  /* Gallery lightbox. */
  var grid = document.querySelector(".gallery-grid");
  if (grid && window.HTMLDialogElement) {
    var dlg = document.createElement("dialog");
    dlg.className = "lightbox";
    dlg.innerHTML = '<div class="lb-bar"><span class="lb-caption"></span><button type="button" class="lb-close">Close</button></div><img alt="">';
    document.body.appendChild(dlg);
    var opener = null;
    /* The lightbox is script-built, so the affordances that make it reachable
       from a keyboard are script-added too. Without JavaScript there is no
       lightbox and the plain images are correct as they are. */
    Array.prototype.forEach.call(grid.querySelectorAll("img"), function (img) {
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      img.setAttribute("aria-label", "View a larger version: " + (img.alt || "photograph"));
    });
    grid.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " ") return;
      var img = e.target.closest ? e.target.closest("img") : null;
      if (!img) return;
      e.preventDefault();
      img.click();
    });
    grid.addEventListener("click", function (e) {
      var img = e.target.closest ? e.target.closest("img") : null;
      if (!img) return;
      opener = img;
      var big = dlg.querySelector("img");
      big.src = img.getAttribute("data-full") || img.src;
      big.alt = img.alt;
      dlg.querySelector(".lb-caption").textContent = img.alt;
      dlg.showModal();
    });
    dlg.querySelector(".lb-close").addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    /* Send focus back where it came from, including on Escape. */
    dlg.addEventListener("close", function () {
      if (opener && opener.focus) { opener.focus(); }
    });
  }

  /* Contact form: submit in place with a clear status message. */
  var forms = document.querySelectorAll('form[action*="web3forms"]');
  if (window.fetch) Array.prototype.forEach.call(forms, function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".form-status");
      if (!status) {
        status = document.createElement("p");
        status.className = "form-status";
        status.setAttribute("role", "status");
        status.style.fontWeight = "600";
        form.appendChild(status);
      }
      status.textContent = "Sending your message...";
      status.style.color = "var(--ink)";
      var button = form.querySelector('button[type="submit"]');
      if (button) button.disabled = true;
      fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" }
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            status.textContent = form.getAttribute("data-success") ||
              "Thank you. Your message has been sent, and I will reply as soon as I can.";
            status.style.color = "var(--indigo)";
            form.reset();
          } else {
            throw new Error(data.message || "Submission failed");
          }
        })
        .catch(function () {
          status.textContent = "Sorry, the message could not be sent just now. Please try again shortly, or message me on LinkedIn instead.";
          status.style.color = "var(--clay)";
        })
        .finally(function () {
          if (button) button.disabled = false;
        });
    });
  });
})();
