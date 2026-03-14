import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export const logbookClient = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export const subscriptionClient = axios.create({
  baseURL: "/api/sub",
  headers: { "Content-Type": "application/json" },
});

// Attach JWT access token to every request
[logbookClient, subscriptionClient].forEach((client) => {
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });
});
