let countdown = 30;
let timer = null;

function updateQR() {
    const qrImage = document.getElementById('qr');
    fetch('/qr?_=' + Date.now())
        .then(response => {
            if (!response.ok) throw new Error('Failed to load QR code');
            return response.blob();
        })
        .then(blob => {
            qrImage.src = URL.createObjectURL(blob);
        })
        .catch(err => {
            console.error('QR load failed:', err);
        })
        .finally(() => {
            resetCountdown(); // Always restart countdown, even on error
        });
}

function resetCountdown() {
    if (timer) clearInterval(timer);
    countdown = 30;
    updateCountdownDisplay();
    timer = setInterval(() => {
        countdown--;
        if (countdown <= 0) {
            updateQR();
        } else {
            updateCountdownDisplay();
        }
    }, 1000);
}

function updateCountdownDisplay() {
    document.getElementById('countdown').textContent = countdown;
    document.getElementById('countdown-text').textContent = countdown;
}

// Auto-start when page loads
document.addEventListener('DOMContentLoaded', updateQR);

// Reset if tab becomes visible again
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) updateQR();
});
