/**
 * PinClip cookie consent.
 *
 * Google Consent Mode v2 defaults are set inline in <head> of every page
 * (before the AdSense tag loads) so that no ad/analytics storage is written
 * until the visitor makes a choice. This file only renders the banner and
 * pushes the consent update once they do.
 *
 * Required for AdSense traffic from the EEA, UK and Switzerland.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'pinclip_consent';

    function readConsent() {
        try {
            return window.localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    function writeConsent(value) {
        try {
            window.localStorage.setItem(STORAGE_KEY, value);
        } catch (e) {
            /* storage blocked — the choice simply won't persist */
        }
    }

    function updateGoogleConsent(state) {
        if (typeof window.gtag !== 'function') return;
        window.gtag('consent', 'update', {
            ad_storage: state,
            ad_user_data: state,
            ad_personalization: state,
            analytics_storage: state
        });
    }

    function buildBanner() {
        var banner = document.createElement('div');
        banner.id = 'cookieConsent';
        banner.setAttribute('role', 'dialog');
        banner.setAttribute('aria-live', 'polite');
        banner.setAttribute('aria-label', 'Cookie consent');
        banner.innerHTML =
            '<div class="consent-inner">' +
            '<p style="margin:0;max-width:52rem;">' +
            'We use cookies to run this site and, with your permission, to show personalised ads through Google AdSense. ' +
            'You can decline and still use every feature of PinClip. Read our ' +
            '<a href="/cookie-policy">Cookie Policy</a> and <a href="/privacy-policy">Privacy Policy</a>.' +
            '</p>' +
            '<div class="consent-actions">' +
            '<button type="button" class="consent-btn consent-btn--reject" id="consentReject">Decline</button>' +
            '<button type="button" class="consent-btn consent-btn--accept" id="consentAccept">Accept all</button>' +
            '</div>' +
            '</div>';
        return banner;
    }

    function decide(state, banner) {
        writeConsent(state);
        updateGoogleConsent(state);
        if (banner && banner.parentNode) {
            banner.parentNode.removeChild(banner);
        }
    }

    function init() {
        var stored = readConsent();

        if (stored === 'granted' || stored === 'denied') {
            // Defaults were already seeded from storage in <head>; re-affirm
            // so any tag that loaded late picks up the right state.
            updateGoogleConsent(stored);
            return;
        }

        var banner = buildBanner();
        document.body.appendChild(banner);

        document.getElementById('consentAccept').addEventListener('click', function () {
            decide('granted', banner);
        });
        document.getElementById('consentReject').addEventListener('click', function () {
            decide('denied', banner);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
