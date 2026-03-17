document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const urlInput = document.getElementById('videoUrl');
    const errorMsg = document.getElementById('errorMsg');
    const resultSection = document.getElementById('resultSection');
    const resultThumbnail = document.getElementById('resultThumbnail');
    const resultVideo = document.getElementById('resultVideo');
    const playOverlay = document.getElementById('playOverlay');
    const resultTitle = document.getElementById('resultTitle');
    const downloadFast = document.getElementById('downloadFast');
    const downloadReliable = document.getElementById('downloadReliable');
    
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const btnIcon = document.getElementById('btnIcon');

    const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : 'https://pindownloader-gvif.onrender.com';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        
        if (!url) return;

        // Reset UI
        errorMsg.classList.add('hidden');
        resultSection.classList.add('hidden');
        resultVideo.classList.add('hidden');
        resultThumbnail.classList.remove('hidden');
        playOverlay.classList.remove('hidden');
        
        // Apply loading state
        btnText.textContent = 'Processing...';
        btnLoader.classList.remove('hidden');
        btnIcon.classList.add('hidden');
        form.querySelector('button').disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/api/download?url=${encodeURIComponent(url)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to extract video.');
            }

            // Populate metadata
            resultTitle.textContent = data.title || 'Pinterest Video';
            const thumbnail = data.thumbnail || 'https://via.placeholder.com/640x360?text=Video+Ready';
            resultThumbnail.src = thumbnail;
            
            // Setup Video Player
            if (data.video_url) {
                resultVideo.src = data.video_url;
                resultVideo.poster = thumbnail;
                
                // On some platforms, direct Pinterest URLs might not play due to CORS
                // So we show the player but keep the thumbnail as a fallback
                resultVideo.oncanplay = () => {
                    resultVideo.classList.remove('hidden');
                    resultThumbnail.classList.add('hidden');
                    playOverlay.classList.add('hidden');
                };
            }

            const filename = `pinclip_${Date.now()}.mp4`;

            // Download (Fast) -> Standard Proxy
            downloadFast.href = `${API_BASE_URL}/p?url=${encodeURIComponent(data.video_url)}&filename=${encodeURIComponent(filename)}`;
            downloadFast.download = filename;

            // Download (Reliable) -> yt-dlp Backend
            downloadReliable.href = `${API_BASE_URL}/api/reliable-download?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(filename)}`;
            downloadReliable.download = filename;

            // Show results
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

        } catch (error) {
            errorMsg.textContent = error.message;
            errorMsg.classList.remove('hidden');
        } finally {
            btnText.textContent = 'Download';
            btnLoader.classList.add('hidden');
            btnIcon.classList.remove('hidden');
            form.querySelector('button').disabled = false;
        }
    });
});
