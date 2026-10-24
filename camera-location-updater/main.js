import './style.css';

const getApiBaseUrl = () => {
  let url = import.meta.env.VITE_API_URL;
  if (url) {
    url = url.trim().replace(/\/+$/, "");
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = `https://${url}`;
    }
    if (!url.endsWith("/api/public")) {
      if (url.endsWith("/api")) {
        url += "/public";
      } else {
        url += "/api/public";
      }
    }
    return url;
  }

  // Automatic detection when hosted on Render
  if (typeof window !== "undefined" && window.location.hostname.includes("onrender.com")) {
    return "https://cctv-vms-backend.onrender.com/api/public";
  }

  return `http://${window.location.hostname}:5000/api/public`;
};

const API_BASE = getApiBaseUrl();

document.getElementById('saveBtn').addEventListener('click', async () => {
  const cameraId = document.getElementById('cameraId').value.trim();
  const locationName = document.getElementById('locationName').value.trim();
  const statusMsg = document.getElementById('statusMessage');
  const btnSave = document.getElementById('saveBtn');

  statusMsg.textContent = '';
  statusMsg.className = 'status-message';

  if (!cameraId) {
    statusMsg.textContent = 'Please enter a Camera ID.';
    statusMsg.classList.add('error');
    return;
  }

  if (!locationName) {
    statusMsg.textContent = 'Please enter a Location Name.';
    statusMsg.classList.add('error');
    return;
  }

  btnSave.disabled = true;
  btnSave.textContent = 'Saving...';

  try {
    const res = await fetch(`${API_BASE}/cameras/${cameraId}/location`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ location_name: locationName })
    });
    
    const json = await res.json();
    
    if (res.status === 404 || json.message === "Camera not found") {
      statusMsg.textContent = 'Camera ID doesn\'t exist.';
      statusMsg.classList.add('error');
    } else if (res.ok && json.status === "success") {
      statusMsg.textContent = 'Location updated successfully!';
      statusMsg.classList.add('success');
      // Clear inputs
      document.getElementById('cameraId').value = '';
      document.getElementById('locationName').value = '';
    } else {
      statusMsg.textContent = json.message || 'Failed to update location.';
      statusMsg.classList.add('error');
    }
  } catch (error) {
    console.error("Failed to update camera location", error);
    statusMsg.textContent = 'Error: Cannot connect to the server.';
    statusMsg.classList.add('error');
  } finally {
    btnSave.disabled = false;
    btnSave.textContent = 'Save';
  }
});
