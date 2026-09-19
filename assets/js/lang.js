/* Language switch (English / Chinese).
   Elements that carry both data-en and data-zh get switched; the text inside the tag is what shows on first load.
   A first visit follows the browser language; after that the choice is kept in localStorage. */
(function () {
  'use strict';

  var root = document.documentElement;
  var btn  = document.getElementById('langBtn');

  function read(k)    { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function write(k,v) { try { localStorage.setItem(k, v); }    catch (e) {} }

  function apply(lang) {
    var nodes = document.querySelectorAll('[data-en][data-zh]');
    for (var i = 0; i < nodes.length; i++) {
      var text = nodes[i].dataset[lang];
      if (text) nodes[i].textContent = text;
    }
    root.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
    if (btn) btn.textContent = (lang === 'zh' ? 'EN' : '中文');  // the button shows the language it switches to
    write('lang', lang);
  }

  var lang = read('lang') || (/^zh/i.test(navigator.language || '') ? 'zh' : 'en');
  apply(lang);

  // The button stays hidden without JS, so it never sits there doing nothing
  if (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      lang = (lang === 'zh' ? 'en' : 'zh');
      apply(lang);
    });
  }
})();
