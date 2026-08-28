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
    grid.addEventListener("click", function (e) {
      var img = e.target.closest ? e.target.closest("img") : null;
      if (!img) return;
      var big = dlg.querySelector("img");
      big.src = img.getAttribute("data-full") || img.src;
      big.alt = img.alt;
      dlg.querySelector(".lb-caption").textContent = img.alt;
      dlg.showModal();
    });
    dlg.querySelector(".lb-close").addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }

  /* Contact form: submit in place with a clear status message. */
  var form = document.querySelector('form[action*="web3forms"]');
  if (form && window.fetch) {
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
      status.style.color = "#22304A";
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
            status.textContent = "Thank you. Your message has been sent, and I will reply as soon as I can.";
            status.style.color = "#2F5D42";
            form.reset();
          } else {
            throw new Error(data.message || "Submission failed");
          }
        })
        .catch(function () {
          status.textContent = "Sorry, the message could not be sent just now. Please try again shortly, or message me on LinkedIn instead.";
          status.style.color = "#8C4718";
        })
        .finally(function () {
          if (button) button.disabled = false;
        });
    });
  }
})();
