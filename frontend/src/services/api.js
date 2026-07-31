import axios from "axios";

// Uses VITE_API_BASE_URL when set (e.g. on Vercel, pointed at your Render
// backend). Falls back to localhost for local development.
const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
});

export default API;