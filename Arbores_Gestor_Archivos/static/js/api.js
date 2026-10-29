const API = {
  async request(url, options = {}) {
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Ocurrió un error en la solicitud.");
    return data;
  },
  tree: () => API.request("/api/tree"),
  stats: () => API.request("/api/stats"),
  node: id => API.request(`/api/node/${id}`),
  create: payload => API.request("/api/nodes", { method: "POST", body: JSON.stringify(payload) }),
  rename: (id, name) => API.request(`/api/nodes/${id}`, { method: "PATCH", body: JSON.stringify({ name }) }),
  remove: id => API.request(`/api/nodes/${id}`, { method: "DELETE" }),
  move: (id, parent_id) => API.request(`/api/nodes/${id}/move`, { method: "POST", body: JSON.stringify({ parent_id }) }),
  search: query => API.request(`/api/search?q=${encodeURIComponent(query)}`),
  traversal: method => API.request(`/api/traversal/${method}`),
  reset: () => API.request("/api/reset", { method: "POST" })
};
