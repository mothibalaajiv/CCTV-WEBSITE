import axios from "axios";

const getApiBaseUrl = () => {
  let url = import.meta.env.VITE_API_URL;
  if (url) {
    url = url.trim().replace(/\/+$/, "");
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = `https://${url}`;
    }
    if (!url.endsWith("/api")) {
      url += "/api";
    }
    return url;
  }

  // Automatic detection when hosted on Render
  if (typeof window !== "undefined" && window.location.hostname.includes("onrender.com")) {
    return "https://cctv-vms-backend.onrender.com/api";
  }

  return `http://${window.location.hostname}:5000/api`;
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    "Content-Type": "application/json"
  }
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to unwrap data
api.interceptors.response.use(
  (response) => {
    // If the backend returns our standard {"status": "success", "data": ...} format
    if (response.data && response.data.status === "success" && response.data.data !== undefined) {
      response.data = response.data.data;
    }
    return response;
  },
  (error) => {
    // Handle unauthorized or invalid token format globally
    if (error.response && (error.response.status === 401 || error.response.status === 422)) {
      localStorage.removeItem("token");
    }
    return Promise.reject(error);
  }
);

export default api;
