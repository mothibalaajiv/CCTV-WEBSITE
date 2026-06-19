import axios from "axios";

const api = axios.create({
  baseURL: `http://${window.location.hostname}:5000/api`,
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
