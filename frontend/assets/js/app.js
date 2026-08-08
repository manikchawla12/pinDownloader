/**
 * PinClip downloader widget.
 *
 * Shared by every page that embeds the tool. Each page supplies the same set
 * of element IDs; if the form is absent the script simply does nothing.
 */
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    if (!form) return;

    const urlInput = document.getElementById('videoUrl');
    const errorMsg = document.getElementById('errorMsg');
    const resultSection = document.getElementById('resultSection');
    const resultThumbnail = document.getElementById('resultThumbnail');
    const resultVideo = document.getElementById('resultVideo');
    const playOverlay = document.getElementById('playOverlay');
    const resultTitle = document.getElementById('resultTitle');
    const downloadBtn = document.getElementById('downloadBtn');

    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const btnIcon = document.getElementById('btnIcon');
    const submitBtn = form.querySelector('button[type="submit"], button');
    const defaultBtnLabel = btnText ? btnText.textContent : 'Download';

    const API_BASE_URL =
        window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:8000'
            : 'https://pindownloader-gvif.onrender.com';

    // Inline fallback so a missing thumbnail never shows a broken-image icon.
    const PLACEHOLDER_THUMB =
        'data:image/svg+xml;charset=utf-8,' +
        encodeURIComponent(
            '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">' +
            '<rect width="640" height="360" fill="#f3f4f6"/>' +
            '<circle cx="320" cy="170" r="46" fill="#E60023" opacity="0.12"/>' +
            '<path d="M306 148l34 22-34 22z" fill="#E60023"/>' +
            '<text x="320" y="256" font-family="Inter,Arial,sans-serif" font-size="18" ' +
            'fill="#6b7280" text-anchor="middle">Video ready to download</text></svg>'
        );

    const PINTEREST_URL = /^https?:\/\/([a-zA-Z0-9-]+\.)?(pinterest\.[a-z]{2,}(\.[a-z]{2})?|pin\.it)\/.+/i;

    /**
     * Turn backend/network failures into something a visitor can act on.
     * The API surfaces raw yt-dlp output, which is meaningless to most people.
     */
    function friendlyError(rawMessage, status) {
        const raw = (rawMessage || '').toLowerCase();

        if (raw.includes('no video formats')) {
            return 'That pin doesn’t contain a video. PinClip only works with video pins — look for the play icon on the pin before copying its link.';
        }
        if (raw.includes('404') || raw.includes('not found')) {
            return 'We couldn’t open that pin. Check the link is complete and that the pin is still public, then try again.';
        }
        if (raw.includes('private') || raw.includes('403') || raw.includes('forbidden') || raw.includes('login')) {
            return 'That pin looks private or restricted. PinClip can only access pins that are visible without logging in.';
        }
        if (raw.includes('timed out') || raw.includes('timeout')) {
            return 'Pinterest took too long to respond. Please try again in a moment.';
        }
        if (raw.includes('rate limit') || status === 429) {
            return 'You’ve made a lot of requests in a short time. Please wait a minute and try again.';
        }
        if (raw.includes('failed to fetch') || raw.includes('networkerror') || status === 0) {
            return 'We couldn’t reach the server. Check your internet connection and try again.';
        }
        if (status >= 500) {
            return 'Something went wrong on our end while processing that pin. Please try again — if it keeps failing, send us the link via the contact page.';
        }
        return 'We couldn’t process that link. Please double-check it and try again.';
    }

    function showError(message) {
        if (!errorMsg) return;
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    }

    function setLoading(isLoading) {
        if (btnText) btnText.textContent = isLoading ? 'Processing…' : defaultBtnLabel;
        if (btnLoader) btnLoader.classList.toggle('hidden', !isLoading);
        if (btnIcon) btnIcon.classList.toggle('hidden', isLoading);
        if (submitBtn) {
            submitBtn.disabled = isLoading;
            submitBtn.setAttribute('aria-busy', isLoading ? 'true' : 'false');
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = urlInput.value.trim();
        if (!url) return;

        if (!PINTEREST_URL.test(url)) {
            showError('That doesn’t look like a Pinterest link. It should start with https://www.pinterest.com/pin/ or https://pin.it/');
            return;
        }

        if (errorMsg) errorMsg.classList.add('hidden');
        if (resultSection) resultSection.classList.add('hidden');
        if (resultVideo) resultVideo.classList.add('hidden');
        if (resultThumbnail) resultThumbnail.classList.remove('hidden');
        if (playOverlay) playOverlay.classList.remove('hidden');

        setLoading(true);

        // Pinterest extraction occasionally stalls; don't hang the UI forever.
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 60000);

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/info?url=${encodeURIComponent(url)}`,
                { signal: controller.signal }
            );

            let data = {};
            try {
                data = await response.json();
            } catch (parseError) {
                data = {};
            }

            if (!response.ok) {
                throw Object.assign(new Error(data.detail || 'Failed to extract video.'), {
                    status: response.status,
                });
            }

            if (resultTitle) resultTitle.textContent = data.title || 'Pinterest Video';

            if (resultThumbnail) {
                resultThumbnail.src = data.thumbnail || PLACEHOLDER_THUMB;
                resultThumbnail.alt = data.title
                    ? `Thumbnail for ${data.title}`
                    : 'Pinterest video thumbnail';
                resultThumbnail.onerror = () => {
                    resultThumbnail.onerror = null;
                    resultThumbnail.src = PLACEHOLDER_THUMB;
                };
            }

            const filename = `pinclip_${Date.now()}.mp4`;
            if (downloadBtn) {
                downloadBtn.href =
                    `${API_BASE_URL}/api/download?url=${encodeURIComponent(url)}` +
                    `&filename=${encodeURIComponent(filename)}`;
                downloadBtn.setAttribute('download', filename);
            }

            if (resultSection) {
                resultSection.classList.remove('hidden');
                resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                showError('That request took too long. Pinterest may be slow right now — please try again.');
            } else {
                showError(friendlyError(error.message, error.status || 0));
            }
        } finally {
            clearTimeout(timeout);
            setLoading(false);
        }
    });
});
