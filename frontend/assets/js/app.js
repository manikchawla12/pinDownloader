document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const urlInput = document.getElementById('videoUrl');
    const errorMsg = document.getElementById('errorMsg');
    const resultSection = document.getElementById('resultSection');
    const resultThumbnail = document.getElementById('resultThumbnail');
    const resultTitle = document.getElementById('resultTitle');
    const downloadLink = document.getElementById('downloadLink');
    
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const btnIcon = document.getElementById('btnIcon');

    // API Base URL - We will use the Render backend in production.
    // Replace the default with the actual deployment URL.
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
        
        // Apply loading state
        btnText.textContent = 'Processing...';
        btnLoader.classList.remove('hidden');
        btnIcon.classList.add('hidden');
        form.querySelector('button').disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/api/download?url=${encodeURIComponent(url)}`);
            const data = await response.json();

            if (!response.ok) {
                // Return detailed error if provided, else generic message
                throw new Error(data.detail || 'Failed to extract video. Please make sure the URL is valid.');
            }

            // Populate the successful result
            resultTitle.textContent = data.title || 'Pinterest Video';
            if (data.thumbnail) {
                resultThumbnail.src = data.thumbnail;
            } else {
                resultThumbnail.src = 'https://via.placeholder.com/640x360?text=Video+Ready';
            }
            
            // Provide direct download capabilities via proxy to ensure it works on iOS
            const filename = `pinterest_video_${Date.now()}.mp4`;
            downloadLink.href = `${API_BASE_URL}/api/proxy-download?url=${encodeURIComponent(data.video_url)}&filename=${encodeURIComponent(filename)}`;
            downloadLink.download = filename;

            // Show results smoothly
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

        } catch (error) {
            errorMsg.textContent = error.message;
            errorMsg.classList.remove('hidden');
        } finally {
            // Revert loading state
            btnText.textContent = 'Download';
            btnLoader.classList.add('hidden');
            btnIcon.classList.remove('hidden');
            form.querySelector('button').disabled = false;
        }
    });
});
