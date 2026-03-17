document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
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
            // Step 1: Fetch Metadata
            const response = await fetch(`${API_BASE_URL}/api/info?url=${encodeURIComponent(url)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to extract video.');
            }

            // Populate metadata
            resultTitle.textContent = data.title || 'Pinterest Video';
            const thumbnail = data.thumbnail || 'https://via.placeholder.com/640x360?text=Video+Ready';
            resultThumbnail.src = thumbnail;
            
            // Setup Download Link (Reliable yt-dlp based stream)
            const filename = `pinclip_${Date.now()}.mp4`;
            downloadBtn.href = `${API_BASE_URL}/api/download?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(filename)}`;
            downloadBtn.download = filename;

            // Optional: Preview (We'll try to show it if we have a direct URL, but its secondary now)
            // For now, let's just keep the thumbnail focus as the backend handles the heavy lifting
            
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
