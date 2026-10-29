const state = { tree: null, selectedId: null, collapsed: new Set(), currentView: "explorer" };
const $ = selector => document.querySelector(selector);

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2600);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

async function refresh() {
  const [tree, stats] = await Promise.all([API.tree(), API.stats()]);
  state.tree = tree;
  renderTree();
  renderStats(stats);
  if (state.selectedId) {
    try { await selectNode(state.selectedId); }
    catch { state.selectedId = null; renderDetails(null); }
  }
}

function renderStats(stats) {
  const items = [
    ["Nodos totales", stats.weight, "◈", "Peso de la estructura"],
    ["Carpetas", stats.folders, "▰", "Nodos contenedores"],
    ["Archivos", stats.files, "▤", "Elementos terminales"],
    ["Altura", stats.height, "↕", "Niveles de profundidad"],
    ["Hojas", stats.leaves, "◇", "Nodos sin hijos"],
    ["Grado máximo", stats.max_degree, "⌘", "Mayor número de hijos"]
  ];
  const markup = items.map(([label, value, icon, note]) =>
    `<article class="stat-card"><div class="stat-top">${label}<span class="stat-icon">${icon}</span></div><div class="stat-value">${value}</div><div class="stat-note">${note}</div></article>`
  ).join("");
  $("#stats-grid").innerHTML = markup.slice(0, 0) + items.slice(0, 4).map(([label,value,icon,note]) =>
    `<article class="stat-card"><div class="stat-top">${label}<span class="stat-icon">${icon}</span></div><div class="stat-value">${value}</div><div class="stat-note">${note}</div></article>`).join("");
  $("#analytics-grid").innerHTML = markup;
}

function renderTree() {
  const container = $("#tree-area");
  container.innerHTML = renderNode(state.tree, true);
  const selected = container.querySelector(`[data-node-id="${state.selectedId}"]`);
  if (selected) selected.classList.add("selected");
}

function renderNode(node, isRoot = false) {
  const isFolder = node.type === "folder";
  const collapsed = state.collapsed.has(node.id);
  const hasChildren = node.children && node.children.length > 0;
  const icon = isFolder ? (collapsed ? "▰" : "▾") : "▤";
  const children = hasChildren && !collapsed
    ? `<div class="tree-children">${node.children.map(child => renderNode(child)).join("")}</div>` : "";
  return `<div class="tree-node">
    <div class="tree-row ${state.selectedId === node.id ? "selected" : ""}" data-node-id="${node.id}" data-folder="${isFolder}">
      <span class="tree-toggle">${hasChildren ? (collapsed ? "＋" : "−") : ""}</span>
      <span class="node-icon">${icon}</span><span class="node-name">${escapeHtml(node.name)}</span>
      <span class="node-type">${isRoot ? "RAÍZ" : isFolder ? "CARPETA" : "ARCHIVO"}</span>
    </div>${children}</div>`;
}

async function selectNode(nodeId) {
  state.selectedId = nodeId;
  const details = await API.node(nodeId);
  renderDetails(details);
  renderTree();
  $("#path-bar").textContent = details.path;
}

function renderDetails(details) {
  const content = $("#details-content"), actions = $("#quick-actions");
  if (!details) {
    content.className = "empty-details";
    content.innerHTML = `<div class="empty-icon">⌁</div><strong>Selecciona un elemento</strong><p>Sus propiedades aparecerán aquí.</p>`;
    actions.innerHTML = "";
    return;
  }
  content.className = "detail-card";
  content.innerHTML = `<div class="detail-symbol">${details.type === "folder" ? "▰" : "▤"}</div>
    <h4>${escapeHtml(details.name)}</h4><p class="muted">${details.type === "folder" ? "Carpeta" : "Archivo"} · ${escapeHtml(details.id)}</p>
    <div class="detail-list">
      ${detailLine("Ubicación", details.path)}
      ${detailLine("Elemento padre", details.parent || "Ninguno")}
      ${detailLine("Hijos directos", details.children)}
      ${detailLine("Grado", details.degree)}
      ${detailLine("Nivel", details.level)}
      ${detailLine("Tipo de nodo", details.is_leaf ? "Hoja" : "Rama")}
    </div>`;
  if (details.parent === null) { actions.innerHTML = ""; return; }
  actions.innerHTML = `<button class="small-action" data-action="folder">＋ Carpeta</button>
    <button class="small-action" data-action="file">＋ Archivo</button>
    <button class="small-action" data-action="rename">Renombrar</button>
    <button class="small-action" data-action="move">Mover</button>
    <button class="small-action" data-action="delete">Eliminar</button>`;
}

function detailLine(label, value) {
  return `<div class="detail-line"><span>${label}</span><span>${escapeHtml(value)}</span></div>`;
}

function openCreateDialog(parentId, type) {
  $("#parent-id").value = parentId;
  $("#node-type").value = type;
  $("#dialog-title").textContent = type === "folder" ? "Crear carpeta" : "Crear archivo";
  $("#dialog-description").textContent = "El elemento se agregará a la carpeta seleccionada.";
  $("#node-name").value = "";
  $("#node-dialog").showModal();
  $("#node-name").focus();
}

async function runTraversal(method) {
  const result = await API.traversal(method);
  $("#traversal-result").innerHTML = `<div class="traversal-list">${result.items.map((item, index) =>
    `<span class="traversal-chip"><b>${index + 1}</b>${escapeHtml(item.name)} <small>· N${item.level}</small></span>`
  ).join("")}</div>`;
}

$("#tree-area").addEventListener("click", async event => {
  const row = event.target.closest(".tree-row");
  if (!row) return;
  const id = row.dataset.nodeId;
  if (event.target.classList.contains("tree-toggle") || event.target.classList.contains("node-icon")) {
    const node = findNode(state.tree, id);
    if (node?.children?.length) {
      state.collapsed.has(id) ? state.collapsed.delete(id) : state.collapsed.add(id);
      renderTree();
      return;
    }
  }
  try { await selectNode(id); } catch (error) { showToast(error.message); }
});

let searchTimer = null;
$("#search-input").addEventListener("input", event => {
  window.clearTimeout(searchTimer);
  const query = event.target.value.trim();
  searchTimer = window.setTimeout(async () => {
    if (!query) { renderTree(); return; }
    try {
      const matches = await API.search(query);
      const container = $("#tree-area");
      if (!matches.length) {
        container.innerHTML = '<div class="loading">No se encontraron coincidencias.</div>';
        return;
      }
      container.innerHTML = matches.map(item => `<div class="tree-row search-result" data-node-id="${item.id}"><span class="node-icon">${item.type === "folder" ? "▰" : "▤"}</span><span class="node-name">${escapeHtml(item.name)}</span><span class="node-type">${escapeHtml(item.path)}</span></div>`).join("");
    } catch (error) { showToast(error.message); }
  }, 180);
});

function findNode(node, id) {
  if (node.id === id) return node;
  for (const child of node.children || []) {
    const found = findNode(child, id);
    if (found) return found;
  }
  return null;
}

$("#new-folder-button").addEventListener("click", () => openCreateDialog(state.tree.id, "folder"));
$("#quick-actions").addEventListener("click", async event => {
  const action = event.target.dataset.action;
  if (!action || !state.selectedId) return;
  const selected = findNode(state.tree, state.selectedId);
  try {
    if (action === "folder" || action === "file") {
      if (selected.type !== "folder") throw new Error("Selecciona una carpeta para agregar elementos.");
      openCreateDialog(selected.id, action);
    } else if (action === "rename") {
      const name = window.prompt("Escribe el nuevo nombre:", selected.name);
      if (name === null) return;
      await API.rename(selected.id, name);
      showToast("Elemento renombrado.");
      await refresh();
    } else if (action === "delete") {
      if (!window.confirm(`¿Eliminar "${selected.name}" y todo su contenido?`)) return;
      await API.remove(selected.id);
      state.selectedId = null;
      renderDetails(null);
      showToast("Elemento eliminado.");
      await refresh();
    } else if (action === "move") {
      const folders = flatten(state.tree).filter(node => node.type === "folder" && node.id !== selected.id);
      const options = folders.map(folder => `${folder.id} — ${folder.name}`).join("\n");
      const destination = window.prompt(`Introduce el ID de la carpeta de destino:\n${options}`);
      if (!destination) return;
      const id = destination.split(" — ")[0].trim();
      await API.move(selected.id, id);
      showToast("Elemento movido.");
      await refresh();
    }
  } catch (error) { showToast(error.message); }
});

function flatten(node) {
  return [node, ...(node.children || []).flatMap(flatten)];
}

$("#node-form").addEventListener("submit", async event => {
  event.preventDefault();
  try {
    const result = await API.create({
      parent_id: $("#parent-id").value,
      name: $("#node-name").value,
      type: $("#node-type").value
    });
    $("#node-dialog").close();
    state.selectedId = result.node.id;
    showToast("Elemento creado correctamente.");
    await refresh();
  } catch (error) { showToast(error.message); }
});

$("#cancel-dialog").addEventListener("click", () => $("#node-dialog").close());
$("#reset-button").addEventListener("click", async () => {
  if (!window.confirm("¿Restaurar los datos de demostración? Se perderán los cambios actuales.")) return;
  try {
    await API.reset();
    state.selectedId = null;
    state.collapsed.clear();
    renderDetails(null);
    await refresh();
    showToast("Datos de demostración restaurados.");
  } catch (error) { showToast(error.message); }
});
$("#collapse-button").addEventListener("click", () => {
  state.collapsed = new Set(flatten(state.tree).filter(node => node.children?.length).map(node => node.id));
  renderTree();
});
document.querySelectorAll("[data-traversal]").forEach(button =>
  button.addEventListener("click", () => runTraversal(button.dataset.traversal).catch(error => showToast(error.message)))
);
document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
  document.querySelectorAll(".view").forEach(view => view.classList.remove("active"));
  button.classList.add("active");
  state.currentView = button.dataset.view;
  $(`#view-${state.currentView}`).classList.add("active");
  $("#page-title").textContent = ({ explorer: "Explorador de archivos", analytics: "Análisis del árbol", traversals: "Recorridos" })[state.currentView];
}));

refresh().catch(error => showToast(error.message));
