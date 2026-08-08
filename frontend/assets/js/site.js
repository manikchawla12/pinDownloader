/** Shared site chrome: mobile navigation and current-page highlighting. */
(function () {
    'use strict';

    function init() {
        var btn = document.getElementById('mobileMenuBtn');
        var menu = document.getElementById('mobileMenu');

        if (btn && menu) {
            btn.addEventListener('click', function () {
                var open = menu.classList.toggle('hidden') === false;
                btn.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
        }

        // Highlight whichever nav entry matches the page we're on.
        var path = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
        if (path.length > 1 && path.charAt(path.length - 1) === '/') {
            path = path.slice(0, -1);
        }
        if (path === '') path = '/';

        var links = document.querySelectorAll('[data-nav]');
        for (var i = 0; i < links.length; i++) {
            var href = links[i].getAttribute('href');
            var match = href === path || (href !== '/' && path.indexOf(href) === 0);
            if (match) {
                links[i].classList.remove('text-gray-600', 'text-gray-700');
                links[i].classList.add('text-pinterest');
                links[i].setAttribute('aria-current', 'page');
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
