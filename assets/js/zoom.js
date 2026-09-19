/* Click a figure to zoom in.
   Click an image: a translucent backdrop appears and the image is enlarged and centered; click again (or press Esc) to close.
   On desktop the image is scaled to fit the window; on phones it is shown at least at its natural size, and you can swipe sideways if it is wider than the screen. */
(function () {
  'use strict';

  var imgs = document.querySelectorAll('.article img');
  if (!imgs.length) return;

  var root = document.documentElement;
  var overlay = null;
  var opener = null;

  function onKey(e) {
    if (e.key === 'Escape') close();
  }

  function close() {
    if (!overlay) return;
    overlay.parentNode.removeChild(overlay);
    overlay = null;
    root.classList.remove('zoom-open');
    document.removeEventListener('keydown', onKey);
    if (opener) opener.focus({ preventScroll: true });
  }

  function open(img) {
    // Take the height from the on-page aspect ratio: naturalWidth can be 0 before an SVG has loaded, and this keeps it from distorting
    var rect = img.getBoundingClientRect();
    var ratio = rect.width ? rect.height / rect.width : 0.4;
    var w = img.naturalWidth || rect.width;
    var h = w * ratio;
    var vw = window.innerWidth, vh = window.innerHeight;
    var scale = Math.min(vw * 0.96 / w, vh * 0.9 / h);
    if (vw < 700) scale = Math.max(scale, 1);

    var big = document.createElement('img');
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    big.style.width = Math.round(w * scale) + 'px';
    big.style.height = Math.round(h * scale) + 'px';

    overlay = document.createElement('div');
    overlay.className = 'zoom';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    if (img.alt) overlay.setAttribute('aria-label', img.alt);
    overlay.appendChild(big);
    overlay.addEventListener('click', close);

    opener = img;
    document.body.appendChild(overlay);
    root.classList.add('zoom-open');
    document.addEventListener('keydown', onKey);
    // Add the class on the next frame so the fade-in transition runs
    requestAnimationFrame(function () {
      if (overlay) overlay.classList.add('zoom--in');
    });
  }

  Array.prototype.forEach.call(imgs, function (img) {
    img.classList.add('zoomable');
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.addEventListener('click', function () { open(img); });
    img.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(img); }
    });
  });
})();
