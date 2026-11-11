const API_BASE = 'http://127.0.0.1:8000';

function getToken() {
  return localStorage.getItem('token');
}

async function downloadPdfReport(predictionId, buttonElement) {
  const token = getToken();
  if (!token) {
    window.location.href = 'login.html';
    return;
  }

  const originalText = buttonElement ? buttonElement.innerHTML : '';
  if (buttonElement) {
    buttonElement.disabled = true;
    buttonElement.innerHTML = '⏳ Downloading...';
  }

  try {
    const response = await fetch(`${API_BASE}/download-report/${predictionId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error('PDF download failed');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report_${predictionId}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert('Unable to download the PDF report right now.');
  } finally {
    if (buttonElement) {
      buttonElement.disabled = false;
      buttonElement.innerHTML = originalText;
    }
  }
}
