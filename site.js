(function () {
  var root = document.documentElement;

  // Contents menu (narrow screens)
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    var setOpen = function (open) {
      root.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Close" : "Contents";
    };
    toggle.addEventListener("click", function () {
      setOpen(!root.classList.contains("nav-open"));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });
    window.addEventListener("resize", function () {
      if (root.classList.contains("nav-open") && !toggle.offsetParent) setOpen(false);
    });
  }

  // Investor login is a shell until a portal is wired
  var form = document.querySelector(".investor-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
    });
  }

  // Watermark: shows in a pool of light under the cursor
  var mark = document.querySelector(".watermark");
  if (mark && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    var x = 0;
    var y = 0;
    var queued = false;
    var paint = function () {
      queued = false;
      mark.style.setProperty("--mx", x + "px");
      mark.style.setProperty("--my", y + "px");
      mark.classList.add("lit");
    };
    document.addEventListener("pointermove", function (e) {
      x = e.clientX;
      y = e.clientY;
      if (!queued) {
        queued = true;
        requestAnimationFrame(paint);
      }
    });
    root.addEventListener("mouseleave", function () {
      mark.classList.remove("lit");
    });
  }
})();
