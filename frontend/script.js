/* ============================================================
 * PrintHub — frontend script
 *
 * IMPORTANT: This frontend has NO local fallback / mock data.
 * All catalog products, inventory materials, orders, delivery
 * options and users are loaded from the backend at runtime
 * (default: http://127.0.0.1:5000). If the backend is offline,
 * the page intentionally shows an error message and renders no
 * cards — this proves whether the backend is actually working.
 * ============================================================ */

const API_BASE = "http://127.0.0.1:5000";

// Live state populated from backend responses (empty until fetched).
let PRODUCTS = [];
let MATERIALS = [];
let PRODUCTS_LOADED = false;
let MATERIALS_LOADED = false;

// Delivery / payment options fetched from backend.
let DELIVERY_METHODS = [];
let PAYMENT_TYPES = [];

// Quality multipliers for the (client-side) price/time estimate.
const QUALITY = {
  low:    { price: 0.8, time: 0.7 },
  medium: { price: 1.0, time: 1.0 },
  high:   { price: 1.4, time: 1.6 },
};

const BACKEND_DOWN_MESSAGE =
  "Backend is not running. Please start the backend server.";

// ---------------------------- Helpers ---------------------------- //
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function formatPrice(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  // Clamp to a sane range so we never produce scientific notation like 1.33e+97.
  const safe = Math.max(0, Math.min(n, 999999));
  return "€" + safe.toFixed(2);
}
function formatTime(min) {
  const n = Number(min);
  if (!Number.isFinite(n) || n < 0) return "—";
  const safe = Math.min(n, 60 * 24 * 365); // cap at ~1 year
  const h = Math.floor(safe / 60);
  const m = Math.round(safe % 60);
  return `${h}h ${m}m`;
}

function parseQuantity(rawValue) {
  // Returns { value, error } where error is null for valid quantities.
  const trimmed = String(rawValue ?? "").trim();
  if (trimmed === "") return { value: null, error: "Quantity is required." };
  const n = Number(trimmed);
  if (!Number.isFinite(n)) return { value: null, error: "Quantity must be a number." };
  if (!Number.isInteger(n)) return { value: null, error: "Quantity must be a whole number." };
  if (n < 1) return { value: null, error: "Quantity must be at least 1." };
  if (n > 100) return { value: null, error: "Quantity must be at most 100." };
  return { value: n, error: null };
}

// ---------------------------- Auth helpers ---------------------------- //
const FORBIDDEN_MESSAGE = "You do not have permission to perform this action.";
const STORAGE_KEY = "printhub.user";

function getCurrentUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (_) {
    return null;
  }
}

function setCurrentUser(user) {
  if (user) localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  else localStorage.removeItem(STORAGE_KEY);
}

function authHeaders() {
  const u = getCurrentUser();
  if (!u) return {};
  return { "X-User-Role": String(u.role || ""), "X-User-Id": String(u.id ?? "") };
}

async function apiGet(path, opts = {}) {
  const headers = { ...(opts.auth ? authHeaders() : {}) };
  const res = await fetch(API_BASE + path, { headers });
  if (res.status === 403) {
    const e = new Error("forbidden");
    e.forbidden = true;
    throw e;
  }
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${path}`);
  return res.json();
}

async function apiSend(method, path, body) {
  const res = await fetch(API_BASE + path, {
    method,
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body == null ? undefined : JSON.stringify(body),
  });
  let data = null;
  try { data = await res.json(); } catch (_) { data = null; }
  return { res, data };
}

// ---------------------------- Backend status banner ---------------------------- //
function ensureBanner() {
  let banner = document.getElementById("backendBanner");
  if (banner) return banner;
  banner = document.createElement("div");
  banner.id = "backendBanner";
  banner.style.cssText =
    "display:none;background:#3a0d0d;color:#ffb4b4;border:1px solid #ff5252;" +
    "padding:12px 16px;margin:12px 16px;border-radius:8px;font-weight:600;" +
    "text-align:center;";
  const main = document.querySelector("main");
  if (main) main.insertBefore(banner, main.firstChild);
  else document.body.insertBefore(banner, document.body.firstChild);
  return banner;
}

function showBackendDown() {
  const banner = ensureBanner();
  banner.textContent = BACKEND_DOWN_MESSAGE;
  banner.style.display = "block";
}

function hideBackendBanner() {
  const banner = document.getElementById("backendBanner");
  if (banner) banner.style.display = "none";
}

// ---------------------------- Header / menu ---------------------------- //
function setupHamburger() {
  const btn = $("#hamburgerBtn");
  const subNav = $("#subNav");
  btn.addEventListener("click", () => {
    btn.classList.toggle("open");
    subNav.classList.toggle("collapsed");
  });
}

// ---------------------------- Catalog ---------------------------- //
function renderCatalog(filter = "") {
  const grid = $("#catalogGrid");
  const empty = $("#catalogEmpty");
  const q = filter.trim().toLowerCase();

  const list = PRODUCTS.filter(p =>
    !q ||
    (p.name || "").toLowerCase().includes(q) ||
    (p.material || "").toLowerCase().includes(q)
  );

  const user = getCurrentUser();
  const isAdmin = user && user.role === "Admin";
  const isCustomer = user && user.role === "Customer";

  grid.innerHTML = list.map(p => `
    <article class="product-card" data-id="${p.id}">
      <div class="product-thumb">🧊</div>
      <h3>${p.name ?? "Unnamed"}</h3>
      <p class="muted" style="margin:4px 0;font-size:0.85rem;">${p.description ?? ""}</p>
      <div class="product-meta">
        <span>${p.material ?? "—"}</span>
        <span class="product-price">${formatPrice(p.price ?? 0)}</span>
      </div>
      <div class="product-meta">
        <span class="muted" style="font-size:0.8rem;">${p.category ?? ""}</span>
        <span class="muted" style="font-size:0.8rem;">${p.availability ?? ""}</span>
      </div>
      ${isCustomer ? `<button type="button" data-order="${p.id}">Order</button>` : ""}
      ${isAdmin ? `
        <div class="admin-actions" style="display:flex;gap:8px;margin-top:8px;">
          <button type="button" class="btn-ghost small" data-edit="${p.id}">Edit</button>
          <button type="button" class="btn-ghost small" data-delete="${p.id}" style="color:#ffb4b4;border-color:#ff5252;">Delete</button>
        </div>` : ""}
    </article>
  `).join("");

  empty.classList.toggle("hidden", list.length !== 0);

  $$(".product-card button[data-order]").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = Number(btn.dataset.order);
      const sel = $("#orderModel");
      if (sel) sel.value = String(id);
      recalcEstimate();
      document.getElementById("order").scrollIntoView({ behavior: "smooth" });
    });
  });

  // Admin actions on cards.
  $$(".product-card button[data-edit]").forEach(btn => {
    btn.addEventListener("click", () => adminEditProduct(Number(btn.dataset.edit)));
  });
  $$(".product-card button[data-delete]").forEach(btn => {
    btn.addEventListener("click", () => adminDeleteProduct(Number(btn.dataset.delete)));
  });
}

function showCatalogError() {
  const grid = $("#catalogGrid");
  const empty = $("#catalogEmpty");
  grid.innerHTML = `
    <div class="backend-error" style="grid-column:1/-1;padding:24px;border:1px dashed #ff5252;border-radius:12px;color:#ffb4b4;text-align:center;">
      ${BACKEND_DOWN_MESSAGE}
    </div>`;
  empty.classList.add("hidden");
}

async function loadProducts() {
  try {
    const data = await apiGet("/catalog/products");
    PRODUCTS = Array.isArray(data.products) ? data.products : [];
    PRODUCTS_LOADED = true;
    renderCatalog($("#searchInput")?.value || "");
    populateOrderModelSelect();
    updateOrderFormAvailability();
    return true;
  } catch (err) {
    console.error("Failed to load /catalog/products:", err);
    PRODUCTS = [];
    PRODUCTS_LOADED = false;
    showCatalogError();
    populateOrderModelSelect();
    updateOrderFormAvailability();
    return false;
  }
}

function setupSearch() {
  const input = $("#searchInput");
  const btn = $("#searchBtn");
  const handler = () => {
    if (PRODUCTS.length === 0) return; // nothing to filter when backend is down
    renderCatalog(input.value);
  };
  input.addEventListener("input", handler);
  btn.addEventListener("click", () => {
    handler();
    document.getElementById("catalog").scrollIntoView({ behavior: "smooth" });
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handler();
      document.getElementById("catalog").scrollIntoView({ behavior: "smooth" });
    }
  });
}

// ---------------------------- Inventory ---------------------------- //
function statusKey(s) {
  const v = String(s || "").toLowerCase();
  if (v.includes("low")) return "low";
  if (v.includes("expect")) return "expected";
  return "available";
}

function renderInventory() {
  const list = $("#inventoryList");
  const labels = { available: "Available", low: "Low Stock", expected: "Expected" };

  list.innerHTML = MATERIALS.map(m => {
    const key = statusKey(m.status);
    return `
      <li class="inventory-item">
        <div>
          <div class="name">${m.name ?? "Unnamed"}</div>
          <div class="sub">${m.type ?? ""}${m.color ? " · " + m.color : ""}</div>
        </div>
        <span class="badge ${key}">${labels[key] || m.status || "—"}</span>
      </li>`;
  }).join("");
}

function showInventoryError() {
  const list = $("#inventoryList");
  list.innerHTML = `
    <li class="backend-error" style="padding:16px;border:1px dashed #ff5252;border-radius:12px;color:#ffb4b4;text-align:center;list-style:none;">
      ${BACKEND_DOWN_MESSAGE}
    </li>`;
}

async function loadMaterials() {
  try {
    const data = await apiGet("/inventory/materials");
    MATERIALS = Array.isArray(data.materials) ? data.materials : [];
    MATERIALS_LOADED = true;
    renderInventory();
    populateOrderMaterialSelect();
    updateOrderFormAvailability();
    return true;
  } catch (err) {
    console.error("Failed to load /inventory/materials:", err);
    MATERIALS = [];
    MATERIALS_LOADED = false;
    showInventoryError();
    populateOrderMaterialSelect();
    updateOrderFormAvailability();
    return false;
  }
}

// ---------------------------- Order form selects ---------------------------- //
function populateOrderModelSelect() {
  const sel = $("#orderModel");
  if (!sel) return;
  sel.innerHTML = '<option value="">— choose —</option>';
  PRODUCTS.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.name} — ${formatPrice(p.price ?? 0)}`;
    sel.appendChild(opt);
  });
}

function populateOrderMaterialSelect() {
  const sel = $("#orderMaterial");
  if (!sel) return;
  sel.innerHTML = '<option value="">— choose —</option>';
  MATERIALS.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = `${m.name}${m.type ? " (" + m.type + ")" : ""}`;
    sel.appendChild(opt);
  });
}

function clearEstimate() {
  $("#estPrice").textContent = "—";
  $("#estTime").textContent = "—";
  const ids = ["estItemsPrice", "estDelivery", "estPaySurcharge", "estDeliveryDays"];
  ids.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = "—"; });
}

function populateOrderDeliverySelect() {
  const sel = document.getElementById("orderDelivery");
  if (!sel) return;
  sel.innerHTML = '<option value="">— choose —</option>';
  DELIVERY_METHODS.forEach(d => {
    const opt = document.createElement("option");
    opt.value = d.id;
    const days = d.estimatedDeliveryDays === 0
      ? "same day"
      : `${d.estimatedDeliveryDays} day${d.estimatedDeliveryDays === 1 ? "" : "s"}`;
    opt.textContent = `${d.label} — ${formatPrice(d.price)} · ${days}`;
    sel.appendChild(opt);
  });
  // Default to first option for convenience.
  if (DELIVERY_METHODS.length > 0 && !sel.value) sel.value = DELIVERY_METHODS[0].id;
}

function populateOrderPaymentSelect() {
  const sel = document.getElementById("orderPayment");
  if (!sel) return;
  sel.innerHTML = '<option value="">— choose —</option>';
  PAYMENT_TYPES.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    const sur = Number(p.surcharge) > 0 ? ` (+${formatPrice(p.surcharge)})` : "";
    opt.textContent = `${p.label}${sur}`;
    sel.appendChild(opt);
  });
  if (PAYMENT_TYPES.length > 0 && !sel.value) sel.value = PAYMENT_TYPES[0].id;
}

async function loadOrderOptions() {
  try {
    const data = await apiGet("/orders/options");
    DELIVERY_METHODS = Array.isArray(data.deliveryMethods) ? data.deliveryMethods : [];
    PAYMENT_TYPES = Array.isArray(data.paymentTypes) ? data.paymentTypes : [];
    populateOrderDeliverySelect();
    populateOrderPaymentSelect();
    return true;
  } catch (err) {
    console.error("Failed to load /orders/options:", err);
    DELIVERY_METHODS = [];
    PAYMENT_TYPES = [];
    return false;
  }
}

function showQuantityError(msg) {
  const el = document.getElementById("orderQtyError");
  if (!el) return;
  if (msg) {
    el.textContent = msg;
    el.classList.remove("hidden");
  } else {
    el.textContent = "";
    el.classList.add("hidden");
  }
}

function recalcEstimate() {
  // Refuse to calculate anything when backend data isn't loaded.
  if (!PRODUCTS_LOADED || !MATERIALS_LOADED) {
    clearEstimate();
    return;
  }

  const modelId = Number($("#orderModel").value);
  const materialId = Number($("#orderMaterial").value);
  const quality = $("#orderQuality").value || "";
  const { value: qty, error: qtyErr } = parseQuantity($("#orderQty").value);

  showQuantityError(qtyErr);

  const product = PRODUCTS.find(p => p.id === modelId);
  const material = MATERIALS.find(m => m.id === materialId);
  const mult = QUALITY[quality];

  if (!product || !material || !mult || qty == null) {
    clearEstimate();
    return;
  }

  const basePrice = Number(product.price);
  if (!Number.isFinite(basePrice)) { clearEstimate(); return; }

  const itemsPrice = basePrice * qty * mult.price + 1.50;
  const time = 45 * qty * mult.time;

  // Pull delivery / payment selections to compute the final price + ETA.
  const deliveryId = document.getElementById("orderDelivery")?.value || "";
  const paymentId = document.getElementById("orderPayment")?.value || "";
  const delivery = DELIVERY_METHODS.find(d => d.id === deliveryId);
  const payment = PAYMENT_TYPES.find(p => p.id === paymentId);
  const deliveryPrice = delivery ? Number(delivery.price) : 0;
  const paySurcharge = payment ? Number(payment.surcharge) : 0;
  const total = itemsPrice + deliveryPrice + paySurcharge;

  $("#estItemsPrice").textContent = formatPrice(itemsPrice);
  $("#estDelivery").textContent = delivery
    ? `${formatPrice(deliveryPrice)} · ${delivery.estimatedDeliveryDays === 0 ? "same day" : delivery.estimatedDeliveryDays + " day(s)"}`
    : "—";
  $("#estPaySurcharge").textContent = payment ? formatPrice(paySurcharge) : "—";
  $("#estPrice").textContent = formatPrice(total);
  $("#estTime").textContent = formatTime(time);
  const days = delivery ? delivery.estimatedDeliveryDays : null;
  $("#estDeliveryDays").textContent = days == null
    ? "—"
    : (days === 0 ? "Same day (pickup)" : `~${days} day${days === 1 ? "" : "s"}`);
}

function updateOrderFormAvailability() {
  const form = document.getElementById("orderForm");
  const msg = document.getElementById("orderFormBackendMsg");
  if (!form) return;
  const ok = PRODUCTS_LOADED && MATERIALS_LOADED;
  const controls = form.querySelectorAll("input, select, button, textarea");
  controls.forEach(c => { c.disabled = !ok; });
  if (msg) {
    if (ok) {
      msg.classList.add("hidden");
      msg.textContent = "";
    } else {
      msg.classList.remove("hidden");
      msg.textContent = BACKEND_DOWN_MESSAGE;
    }
  }
  if (!ok) clearEstimate();
}

function renderOrderConfirmation(order) {
  // Build a richer multi-line order confirmation summarising every relevant
  // field requested by the issue (model, material, quantity, price, print
  // time, delivery method, payment type, status).
  let el = document.getElementById("orderResult");
  if (!el) {
    el = document.createElement("div");
    el.id = "orderResult";
    el.style.cssText = "margin:14px 0 0;padding:14px;border-radius:10px;font-weight:500;";
    const form = document.getElementById("orderForm");
    if (form) form.appendChild(el);
  }
  el.style.background = "#0d3a13";
  el.style.color = "#b4ffc1";
  el.style.border = "1px solid #4caf50";
  el.style.display = "block";
  if (!order || !order.id) {
    el.textContent = "✅ Order created.";
    return;
  }
  const item = (order.items && order.items[0]) || {};
  const product = PRODUCTS.find(p => p.id === item.productId);
  const material = MATERIALS.find(m => m.id === item.materialId);
  const dm = DELIVERY_METHODS.find(d => d.id === order.deliveryMethod);
  const pt = PAYMENT_TYPES.find(p => p.id === order.paymentType);
  const days = order.estimatedDeliveryDays;
  const etaTxt = days == null ? "—" : (days === 0 ? "Same day (pickup)" : `~${days} day${days === 1 ? "" : "s"}`);
  el.innerHTML = `
    <div style="font-size:1.05rem;margin-bottom:6px;">✅ <strong>Order #${order.id}</strong> created — status: <strong>${order.status || "Created"}</strong></div>
    <ul style="list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:6px 18px;">
      <li><span style="opacity:.7;">Model:</span> ${escapeHtml(product?.name ?? item.modelRef ?? "—")}</li>
      <li><span style="opacity:.7;">Material:</span> ${escapeHtml(material?.name ?? "—")}</li>
      <li><span style="opacity:.7;">Quantity:</span> ${item.quantity ?? "—"}</li>
      <li><span style="opacity:.7;">Print quality:</span> ${escapeHtml(item.precision ?? "—")}</li>
      <li><span style="opacity:.7;">Print time:</span> ${formatTime(order.estimatedTimeMin)}</li>
      <li><span style="opacity:.7;">Delivery:</span> ${escapeHtml(dm?.label ?? order.deliveryMethod ?? "—")} (${formatPrice(order.deliveryPrice ?? 0)})</li>
      <li><span style="opacity:.7;">Estimated delivery:</span> ${etaTxt}</li>
      <li><span style="opacity:.7;">Payment:</span> ${escapeHtml(pt?.label ?? order.paymentType ?? "—")}${order.paymentSurcharge ? " (+" + formatPrice(order.paymentSurcharge) + ")" : ""}</li>
      <li><span style="opacity:.7;">Total price:</span> <strong>${formatPrice(order.totalPrice)}</strong></li>
    </ul>
  `;
}

function setOrderResult(message, isError) {
  let el = document.getElementById("orderResult");
  if (!el) {
    el = document.createElement("p");
    el.id = "orderResult";
    el.style.cssText = "margin:12px 0 0;padding:10px;border-radius:8px;text-align:center;font-weight:600;";
    const form = document.getElementById("orderForm");
    if (form) form.appendChild(el);
  }
  el.textContent = message || "";
  el.style.background = isError ? "#3a0d0d" : "#0d3a13";
  el.style.color = isError ? "#ffb4b4" : "#b4ffc1";
  el.style.border = isError ? "1px solid #ff5252" : "1px solid #4caf50";
  el.style.display = message ? "block" : "none";
}

function setupOrderForm() {
  ["orderModel", "orderMaterial", "orderQuality", "orderQty", "orderDelivery", "orderPayment"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("change", recalcEstimate);
    el.addEventListener("input", recalcEstimate);
  });

  $("#recalcBtn").addEventListener("click", () => {
    if (!PRODUCTS_LOADED || !MATERIALS_LOADED) {
      setOrderResult(BACKEND_DOWN_MESSAGE, true);
      return;
    }
    recalcEstimate();
  });

  $("#orderForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    setOrderResult("", false);

    if (!PRODUCTS_LOADED || !MATERIALS_LOADED) {
      setOrderResult(BACKEND_DOWN_MESSAGE, true);
      return;
    }

    const productId = Number($("#orderModel").value) || null;
    const materialId = Number($("#orderMaterial").value) || null;
    const quality = $("#orderQuality").value || "";
    const fileEl = $("#orderFile");
    const customFileName = fileEl && fileEl.files && fileEl.files.length
      ? fileEl.files[0].name : null;
    const { value: qty, error: qtyErr } = parseQuantity($("#orderQty").value);

    showQuantityError(qtyErr);
    if (qtyErr) return;

    if (!productId && !customFileName) {
      setOrderResult("Please choose a model or upload your own 3D file.", true);
      return;
    }
    if (!materialId) {
      setOrderResult("Please pick a material.", true);
      return;
    }
    if (!QUALITY[quality]) {
      setOrderResult("Please choose a print quality.", true);
      return;
    }

    const deliveryMethod = document.getElementById("orderDelivery")?.value || "";
    const paymentType = document.getElementById("orderPayment")?.value || "";
    if (!deliveryMethod) {
      setOrderResult("Please choose a delivery method.", true);
      return;
    }
    if (!paymentType) {
      setOrderResult("Please choose a payment type.", true);
      return;
    }

    const body = {
      productId: productId,
      materialId: materialId,
      printQuality: quality,
      quantity: qty,
      customModelFileName: customFileName,
      deliveryMethod,
      paymentType,
    };

    let res, data;
    try {
      ({ res, data } = await apiSend("POST", "/orders", body));
    } catch (err) {
      console.error("Failed to POST /orders:", err);
      setOrderResult(BACKEND_DOWN_MESSAGE, true);
      return;
    }

    if (res.status === 403) {
      setOrderResult(FORBIDDEN_MESSAGE, true);
      return;
    }
    if (!res.ok) {
      const msg = (data && (data.message || data.error)) || ("Order rejected (HTTP " + res.status + ").");
      console.error("Order rejected:", res.status, data);
      setOrderResult(msg, true);
      return;
    }

    const order = (data && data.order) || {};
    renderOrderConfirmation(order);
    if (order.totalPrice != null) $("#estPrice").textContent = formatPrice(order.totalPrice);
    if (order.estimatedTimeMin != null) $("#estTime").textContent = formatTime(order.estimatedTimeMin);
    loadOrders();
    loadMyOrders();
  });

  // Inline-validate the quantity field as the user types.
  const qtyEl = document.getElementById("orderQty");
  if (qtyEl) qtyEl.addEventListener("input", () => {
    const { error } = parseQuantity(qtyEl.value);
    showQuantityError(error);
  });

  updateOrderFormAvailability();
  clearEstimate();
}

// ---------------------------- Support form ---------------------------- //
function setupSupportForm() {
  $("#supportForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      orderId: $("#supOrderId").value.trim(),
      type: $("#supType").value,
      description: $("#supMessage").value.trim(),
    };
    if (!payload.orderId || !payload.description) {
      $("#supportStatus").textContent = "❌ Please fill out all fields.";
      return;
    }
    let res, data;
    try {
      ({ res, data } = await apiSend("POST", "/support/requests", payload));
    } catch (err) {
      console.error("Failed to POST /support/requests:", err);
      $("#supportStatus").textContent = "❌ " + BACKEND_DOWN_MESSAGE;
      return;
    }
    if (res.status === 403) { $("#supportStatus").textContent = "❌ " + FORBIDDEN_MESSAGE; return; }
    if (!res.ok) {
      $("#supportStatus").textContent = "❌ " + ((data && (data.message || data.error)) || ("HTTP " + res.status));
      return;
    }
    $("#supportStatus").textContent =
      `✅ Request sent (#${data.request?.id ?? "?"}). Type: ${payload.type}, order #${payload.orderId}.`;
    $("#supportForm").reset();
    loadMySupport();
  });
}

// ---------------------------- Complaint form (Customer) ---------------------------- //
function setupComplaintForm() {
  const form = document.getElementById("complaintForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("complaintStatus");
    const payload = {
      orderId: Number(document.getElementById("complaintOrderId").value),
      reason: document.getElementById("complaintReason").value,
      description: document.getElementById("complaintDescription").value.trim(),
    };
    let res, data;
    try {
      ({ res, data } = await apiSend("POST", "/support/complaints", payload));
    } catch (err) {
      console.error("Failed to POST /support/complaints:", err);
      status.textContent = "❌ " + BACKEND_DOWN_MESSAGE;
      return;
    }
    if (res.status === 403) { status.textContent = "❌ " + FORBIDDEN_MESSAGE; return; }
    if (!res.ok) {
      status.textContent = "❌ " + ((data && (data.message || data.error)) || ("HTTP " + res.status));
      return;
    }
    status.textContent = `✅ Complaint #${data.complaint?.id ?? "?"} filed for order ${payload.orderId}.`;
    form.reset();
    loadMySupport();
  });
}

// ---------------------------- Manager forms ---------------------------- //
function setupSupplierForm() {
  const form = document.getElementById("supplierForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("supplierStatus");
    const payload = {
      name: document.getElementById("supplierName").value.trim(),
      address: document.getElementById("supplierAddress").value.trim(),
      contact: document.getElementById("supplierContact").value.trim(),
    };
    let res, data;
    try {
      ({ res, data } = await apiSend("POST", "/suppliers", payload));
    } catch (err) {
      console.error("Failed to POST /suppliers:", err);
      status.textContent = "❌ " + BACKEND_DOWN_MESSAGE;
      return;
    }
    if (res.status === 403) { status.textContent = "❌ " + FORBIDDEN_MESSAGE; return; }
    if (!res.ok) { status.textContent = "❌ HTTP " + res.status; return; }
    status.textContent = `✅ Supplier #${data.supplier?.id} registered (login: ${data.supplier?.username} / ${data.supplier?.password}).`;
    form.reset();
    loadSuppliersList();
  });
}

function setupImportForm() {
  const form = document.getElementById("importForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("importStatus");
    const sid = Number(document.getElementById("importSupplierId").value);
    const link = document.getElementById("importLink").value.trim();
    let res, data;
    try {
      ({ res, data } = await apiSend("POST", `/suppliers/${sid}/import-products`, { link }));
    } catch (err) {
      console.error("Failed to import-products:", err);
      status.textContent = "❌ " + BACKEND_DOWN_MESSAGE;
      return;
    }
    if (res.status === 403) { status.textContent = "❌ " + FORBIDDEN_MESSAGE; return; }
    if (data && data.success) {
      status.textContent = `✅ Imported ${data.imported} products from supplier #${sid}.`;
    } else {
      status.textContent = "❌ " + ((data && (data.error || data.message)) || ("HTTP " + res.status));
    }
  });
}

async function loadSuppliersList() {
  const ul = document.getElementById("suppliersList");
  if (!ul) return;
  try {
    const data = await apiGet("/suppliers");
    const items = Array.isArray(data.suppliers) ? data.suppliers : [];
    ul.innerHTML = items.map(s => `
      <li class="inventory-item">
        <div>
          <div class="name">#${s.id} ${s.name ?? ""}</div>
          <div class="sub">${s.contact ?? ""}${s.address ? " · " + s.address : ""}</div>
        </div>
        <span class="badge available">${(s.products || []).length} products</span>
      </li>`).join("") || `<li class="muted">No suppliers yet.</li>`;
  } catch (err) {
    console.error("Failed to load /suppliers:", err);
    ul.innerHTML = `<li class="muted">${BACKEND_DOWN_MESSAGE}</li>`;
  }
}

// ---------------------------- Admin: product CRUD ---------------------------- //
function adminResetForm() {
  const form = document.getElementById("adminProductForm");
  if (!form) return;
  form.reset();
  document.getElementById("adminProductId").value = "";
  document.getElementById("adminSaveBtn").textContent = "Add Product";
  document.getElementById("adminProductStatus").textContent = "";
}

function adminEditProduct(pid) {
  const p = PRODUCTS.find(x => x.id === pid);
  if (!p) return;
  document.getElementById("adminProductId").value = String(p.id);
  document.getElementById("adminProductName").value = p.name ?? "";
  document.getElementById("adminProductPrice").value = p.price ?? 0;
  document.getElementById("adminProductMaterial").value = p.material ?? "";
  document.getElementById("adminProductCategory").value = p.category ?? "";
  document.getElementById("adminProductAvailability").value = p.availability ?? "Available";
  document.getElementById("adminProductDescription").value = p.description ?? "";
  document.getElementById("adminSaveBtn").textContent = "Save Changes";
  document.getElementById("adminCatalog").scrollIntoView({ behavior: "smooth" });
}

async function adminDeleteProduct(pid) {
  const status = document.getElementById("adminProductStatus");
  if (!confirm(`Delete product #${pid}?`)) return;
  let res, data;
  try {
    ({ res, data } = await apiSend("DELETE", `/catalog/products/${pid}`, null));
  } catch (err) {
    console.error("Failed to DELETE product:", err);
    if (status) status.textContent = "❌ " + BACKEND_DOWN_MESSAGE;
    return;
  }
  if (res.status === 403) { if (status) status.textContent = "❌ " + FORBIDDEN_MESSAGE; return; }
  if (!res.ok) { if (status) status.textContent = "❌ " + ((data && (data.error || data.message)) || `HTTP ${res.status}`); return; }
  if (status) status.textContent = `✅ Product #${pid} deleted.`;
  await loadProducts();
}

function setupAdminProductForm() {
  const form = document.getElementById("adminProductForm");
  if (!form) return;
  document.getElementById("adminCancelBtn").addEventListener("click", adminResetForm);
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("adminProductStatus");
    const idRaw = document.getElementById("adminProductId").value.trim();
    const payload = {
      name: document.getElementById("adminProductName").value.trim(),
      price: Number(document.getElementById("adminProductPrice").value),
      material: document.getElementById("adminProductMaterial").value.trim() || "PLA",
      category: document.getElementById("adminProductCategory").value.trim() || "Other",
      availability: document.getElementById("adminProductAvailability").value,
      description: document.getElementById("adminProductDescription").value.trim(),
    };
    if (!payload.name || !Number.isFinite(payload.price) || payload.price < 0) {
      status.textContent = "❌ Name and a non-negative price are required.";
      return;
    }
    const isUpdate = idRaw !== "";
    const path = isUpdate ? `/catalog/products/${Number(idRaw)}` : "/catalog/products";
    const method = isUpdate ? "PUT" : "POST";
    let res, data;
    try {
      ({ res, data } = await apiSend(method, path, payload));
    } catch (err) {
      console.error("Failed admin product save:", err);
      status.textContent = "❌ " + BACKEND_DOWN_MESSAGE;
      return;
    }
    if (res.status === 403) { status.textContent = "❌ " + FORBIDDEN_MESSAGE; return; }
    if (!res.ok) { status.textContent = "❌ " + ((data && (data.error || data.message)) || `HTTP ${res.status}`); return; }
    status.textContent = isUpdate
      ? `✅ Product #${data.product?.id ?? idRaw} updated.`
      : `✅ Product #${data.product?.id ?? "?"} added.`;
    adminResetForm();
    await loadProducts();
  });
}

// ---------------------------- Role-based dashboards ---------------------------- //
function renderOrderRows(targetId, orders) {
  const ul = document.getElementById(targetId);
  if (!ul) return;
  if (!orders || orders.length === 0) {
    ul.innerHTML = `<li class="muted">No orders.</li>`;
    return;
  }
  const badgeFor = (s) => {
    if (s === "Delivered") return "available";
    if (s === "Created" || s === "Paid") return "expected";
    return "low";
  };
  ul.innerHTML = orders.map(o => {
    const dm = DELIVERY_METHODS.find(d => d.id === o.deliveryMethod);
    const pt = PAYMENT_TYPES.find(p => p.id === o.paymentType);
    const dmLabel = dm ? dm.label : (o.deliveryMethod || "—");
    const ptLabel = pt ? pt.label : (o.paymentType || "—");
    return `
    <li class="inventory-item">
      <div>
        <div class="name">Order #${o.id} — ${o.status}</div>
        <div class="sub">customer #${o.customerId} · ${formatPrice(o.totalPrice)} · ${formatTime(o.estimatedTimeMin)}</div>
        <div class="sub">${dmLabel} · ${ptLabel}</div>
      </div>
      <span class="badge ${badgeFor(o.status)}">${o.status}</span>
    </li>`;
  }).join("");
}

async function loadMyOrders() {
  const u = getCurrentUser();
  if (!u || u.role !== "Customer") return;
  try {
    const data = await apiGet(`/orders?customerId=${u.id}`);
    renderOrderRows("myOrdersList", data.orders || []);
  } catch (err) {
    console.error("Failed to load my orders:", err);
    const el = document.getElementById("myOrdersList");
    if (el) el.innerHTML = `<li class="muted">${BACKEND_DOWN_MESSAGE}</li>`;
  }
}

// Cached statuses fetched alongside lists.
let SUPPORT_REQUEST_STATUSES = [];
let SUPPORT_COMPLAINT_STATUSES = [];

// Currently open detail item, e.g. { kind: "request"|"complaint", id: 42 }.
let SUPPORT_DETAIL_OPEN = null;

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function setSupportDetailMsg(message, isError) {
  const el = document.getElementById("supportDetailMsg");
  if (!el) return;
  el.textContent = message || "";
  el.style.color = isError ? "#ffb4b4" : "#b4ffc1";
}

function renderSupportDetail(kind, record) {
  const wrap = document.getElementById("supportDetail");
  if (!wrap || !record) return;
  wrap.classList.remove("hidden");
  SUPPORT_DETAIL_OPEN = { kind, id: record.id };

  const isRequest = kind === "request";
  document.getElementById("supportDetailTitle").textContent =
    `${isRequest ? "Request" : "Complaint"} #${record.id}`;

  const typeOrReason = isRequest ? (record.type ?? "—") : (record.reason ?? "—");
  const meta = document.getElementById("supportDetailMeta");
  meta.innerHTML = `
    <div><strong>ID:</strong> ${record.id}</div>
    <div><strong>Customer ID:</strong> ${escapeHtml(record.customerId ?? "—")}</div>
    <div><strong>Order ID:</strong> ${escapeHtml(record.orderId ?? "—")}</div>
    <div><strong>${isRequest ? "Type" : "Reason"}:</strong> ${escapeHtml(typeOrReason)}</div>
    <div><strong>Message:</strong> ${escapeHtml(record.description ?? "")}</div>
    <div><strong>Current status:</strong> ${escapeHtml(record.status ?? "—")}</div>
    <div><strong>Created:</strong> ${escapeHtml(record.createdAt ?? "—")}</div>
  `;

  const history = Array.isArray(record.history) ? record.history : [];
  const histList = document.getElementById("supportDetailHistory");
  histList.innerHTML = history.length ? history.map(h => `
    <li class="inventory-item">
      <div>
        <div class="name">${escapeHtml(h.previousStatus || "—")} → ${escapeHtml(h.newStatus)}</div>
        <div class="sub">by ${escapeHtml(h.changedBy)} · ${escapeHtml(h.timestamp)}${h.comment ? " · " + escapeHtml(h.comment) : ""}</div>
      </div>
    </li>`).join("") : `<li class="muted">No history yet.</li>`;

  const statuses = isRequest ? SUPPORT_REQUEST_STATUSES : SUPPORT_COMPLAINT_STATUSES;
  const sel = document.getElementById("supportDetailStatus");
  sel.innerHTML = statuses.map(s =>
    `<option value="${escapeHtml(s)}"${s === record.status ? " selected" : ""}>${escapeHtml(s)}</option>`
  ).join("");

  document.getElementById("supportDetailComment").value = "";
  setSupportDetailMsg("", false);
}

async function openSupportDetail(kind, id) {
  const path = kind === "request" ? `/support/requests/${id}` : `/support/complaints/${id}`;
  try {
    const data = await apiGet(path, { auth: true });
    const record = kind === "request" ? data.request : data.complaint;
    renderSupportDetail(kind, record);
    document.getElementById("supportDetail").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    console.error("Failed to load detail:", err);
    setSupportDetailMsg(err.forbidden ? FORBIDDEN_MESSAGE : BACKEND_DOWN_MESSAGE, true);
  }
}

async function submitSupportDetailUpdate() {
  if (!SUPPORT_DETAIL_OPEN) return;
  const { kind, id } = SUPPORT_DETAIL_OPEN;
  const status = document.getElementById("supportDetailStatus").value;
  const comment = document.getElementById("supportDetailComment").value.trim();
  const path = kind === "request"
    ? `/support/requests/${id}/status`
    : `/support/complaints/${id}/status`;
  let res, data;
  try {
    ({ res, data } = await apiSend("PATCH", path, { status, comment }));
  } catch (err) {
    console.error("Failed to PATCH status:", err);
    setSupportDetailMsg("❌ " + BACKEND_DOWN_MESSAGE, true);
    return;
  }
  if (res.status === 403) { setSupportDetailMsg("❌ " + FORBIDDEN_MESSAGE, true); return; }
  if (!res.ok) {
    setSupportDetailMsg("❌ " + ((data && (data.message || data.error)) || ("HTTP " + res.status)), true);
    return;
  }
  setSupportDetailMsg("✅ Status updated.", false);
  // Refresh detail and the dashboard list.
  await openSupportDetail(kind, id);
  loadSupportDashboard();
}

function setupSupportDetail() {
  const closeBtn = document.getElementById("supportDetailClose");
  if (closeBtn) closeBtn.addEventListener("click", () => {
    document.getElementById("supportDetail").classList.add("hidden");
    SUPPORT_DETAIL_OPEN = null;
  });
  const updBtn = document.getElementById("supportDetailUpdateBtn");
  if (updBtn) updBtn.addEventListener("click", submitSupportDetailUpdate);
}

async function loadSupportDashboard() {
  const u = getCurrentUser();
  if (!u || u.role !== "Support") return;
  // Requests
  try {
    const data = await apiGet("/support/requests", { auth: true });
    SUPPORT_REQUEST_STATUSES = Array.isArray(data.statuses) ? data.statuses : SUPPORT_REQUEST_STATUSES;
    const list = Array.isArray(data.requests) ? data.requests : [];
    document.getElementById("supportReqList").innerHTML = list.map(r => `
      <li class="inventory-item">
        <div>
          <div class="name">Req #${r.id} — order ${escapeHtml(r.orderId ?? "—")}</div>
          <div class="sub">${escapeHtml(r.type ?? "")} · ${escapeHtml(r.description ?? "")}</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="badge ${r.status === "Resolved" || r.status === "Closed" ? "available" : "expected"}">${escapeHtml(r.status ?? "")}</span>
          <button type="button" class="btn-ghost small" data-open-req="${r.id}">Open</button>
        </div>
      </li>`).join("") || `<li class="muted">No requests.</li>`;
    $$(`#supportReqList button[data-open-req]`).forEach(btn => {
      btn.addEventListener("click", () => openSupportDetail("request", Number(btn.dataset.openReq)));
    });
  } catch (err) {
    console.error("Failed to load /support/requests:", err);
    document.getElementById("supportReqList").innerHTML = err.forbidden
      ? `<li class="muted">${FORBIDDEN_MESSAGE}</li>` : `<li class="muted">${BACKEND_DOWN_MESSAGE}</li>`;
  }
  // Complaints
  try {
    const data = await apiGet("/support/complaints", { auth: true });
    SUPPORT_COMPLAINT_STATUSES = Array.isArray(data.statuses) ? data.statuses : SUPPORT_COMPLAINT_STATUSES;
    const list = Array.isArray(data.complaints) ? data.complaints : [];
    document.getElementById("supportCmpList").innerHTML = list.map(c => `
      <li class="inventory-item">
        <div>
          <div class="name">Complaint #${c.id} — order ${escapeHtml(c.orderId ?? "—")}</div>
          <div class="sub">${escapeHtml(c.reason ?? "")} · ${escapeHtml(c.description ?? "")}</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="badge low">${escapeHtml(c.status ?? "")}</span>
          <button type="button" class="btn-ghost small" data-open-cmp="${c.id}">Open</button>
        </div>
      </li>`).join("") || `<li class="muted">No complaints.</li>`;
    $$(`#supportCmpList button[data-open-cmp]`).forEach(btn => {
      btn.addEventListener("click", () => openSupportDetail("complaint", Number(btn.dataset.openCmp)));
    });
  } catch (err) {
    console.error("Failed to load /support/complaints:", err);
    document.getElementById("supportCmpList").innerHTML = err.forbidden
      ? `<li class="muted">${FORBIDDEN_MESSAGE}</li>` : `<li class="muted">${BACKEND_DOWN_MESSAGE}</li>`;
  }
}

// ---------------------------- My Support (Customer) ---------------------------- //
async function loadMySupport() {
  const u = getCurrentUser();
  if (!u || u.role !== "Customer") return;
  const reqEl = document.getElementById("myReqList");
  const cmpEl = document.getElementById("myCmpList");
  try {
    const data = await apiGet("/support/requests", { auth: true });
    const list = Array.isArray(data.requests) ? data.requests : [];
    if (reqEl) reqEl.innerHTML = list.map(r => `
      <li class="inventory-item">
        <div>
          <div class="name">Req #${r.id} — order ${escapeHtml(r.orderId ?? "—")}</div>
          <div class="sub">${escapeHtml(r.type ?? "")} · ${escapeHtml(r.description ?? "")}</div>
        </div>
        <span class="badge ${r.status === "Resolved" || r.status === "Closed" ? "available" : "expected"}">${escapeHtml(r.status ?? "")}</span>
      </li>`).join("") || `<li class="muted">No requests yet.</li>`;
  } catch (err) {
    console.error("Failed to load my support requests:", err);
    if (reqEl) reqEl.innerHTML = `<li class="muted">${BACKEND_DOWN_MESSAGE}</li>`;
  }
  try {
    const data = await apiGet("/support/complaints", { auth: true });
    const list = Array.isArray(data.complaints) ? data.complaints : [];
    if (cmpEl) cmpEl.innerHTML = list.map(c => `
      <li class="inventory-item">
        <div>
          <div class="name">Complaint #${c.id} — order ${escapeHtml(c.orderId ?? "—")}</div>
          <div class="sub">${escapeHtml(c.reason ?? "")} · ${escapeHtml(c.description ?? "")}</div>
        </div>
        <span class="badge low">${escapeHtml(c.status ?? "")}</span>
      </li>`).join("") || `<li class="muted">No complaints yet.</li>`;
  } catch (err) {
    console.error("Failed to load my complaints:", err);
    if (cmpEl) cmpEl.innerHTML = `<li class="muted">${BACKEND_DOWN_MESSAGE}</li>`;
  }
}

async function loadManagerDashboard() {
  const u = getCurrentUser();
  if (!u || u.role !== "Manager") return;
  loadSuppliersList();
  try {
    const data = await apiGet("/orders");
    renderOrderRows("managerOrdersList", data.orders || []);
  } catch (err) {
    console.error("Failed to load /orders:", err);
  }
}

// ---------------------------- Login / logout ---------------------------- //
function renderViewByRole() {
  const user = getCurrentUser();
  const role = user ? String(user.role) : null;

  // First, fully hide every role-tagged section, then show only ones whose
  // data-role attribute (space-separated list) contains the current role.
  document.querySelectorAll(".role-section").forEach(el => {
    el.classList.add("hidden");
    if (!role) return;
    const allowed = String(el.dataset.role || "").split(/\s+/).filter(Boolean);
    if (allowed.includes(role)) el.classList.remove("hidden");
  });

  // Header user box
  const userInfo = document.getElementById("userInfo");
  const userName = document.getElementById("userName");
  const userRole = document.getElementById("userRole");
  if (user) {
    userInfo.classList.remove("hidden");
    userName.textContent = user.name || user.email || "User";
    userRole.textContent = user.role || "—";
  } else {
    userInfo.classList.add("hidden");
  }

  // CTA "Create Print Order" — only for Customer
  const cta = document.querySelector(".cta-btn");
  if (cta) cta.classList.toggle("hidden", role !== "Customer");

  // Re-render catalog so Edit/Delete buttons appear/disappear per role.
  if (PRODUCTS_LOADED) renderCatalog($("#searchInput")?.value || "");
}

function applyAuthState() {
  const user = getCurrentUser();
  document.body.classList.toggle("logged-in", !!user);
  document.body.classList.toggle("logged-out", !user);
}

async function loadAllAppData() {
  const results = await Promise.all([
    loadProducts(),
    loadMaterials(),
    loadOrders(),
    loadDeliveryOptions(),
    loadOrderOptions(),
    loadUsers(),
  ]);
  if (results.some(ok => !ok)) showBackendDown();
  else hideBackendBanner();
  loadMyOrders();
  loadMySupport();
  loadSupportDashboard();
  loadManagerDashboard();
}

function setupLoginUI() {
  document.getElementById("logoutBtn").addEventListener("click", async () => {
    try { await apiSend("POST", "/auth/logout", {}); } catch (_) {}
    setCurrentUser(null);
    applyAuthState();
    renderViewByRole();
    // Reset login form for the next user
    const errEl = document.getElementById("loginError");
    if (errEl) errEl.classList.add("hidden");
  });
  document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errEl = document.getElementById("loginError");
    errEl.classList.add("hidden");
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;
    let res, data;
    try {
      ({ res, data } = await apiSend("POST", "/auth/login", { email, password }));
    } catch (err) {
      console.error("Failed to POST /auth/login:", err);
      errEl.textContent = BACKEND_DOWN_MESSAGE;
      errEl.classList.remove("hidden");
      return;
    }
    if (!res.ok || !data || !data.success) {
      errEl.textContent = (data && (data.message || data.error)) || "Invalid credentials.";
      errEl.classList.remove("hidden");
      return;
    }
    setCurrentUser(data.user);
    applyAuthState();
    renderViewByRole();
    loadAllAppData();
  });
}

// ---------------------------- Category buttons ---------------------------- //
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (!el) return false;
  // If the section is hidden by role, fall back to home/catalog so the button
  // is never a dead end.
  if (el.classList.contains("hidden")) {
    const fallback = document.getElementById("home") || document.getElementById("catalog");
    if (fallback) fallback.scrollIntoView({ behavior: "smooth" });
    return false;
  }
  el.scrollIntoView({ behavior: "smooth" });
  return true;
}

function setupCategoryButtons() {
  $$(".cat-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.cat;
      const map = {
        materials: "inventory",
        models:    "catalog",
        orders:    "order",
        support:   "support",
      };
      const id = map[target];
      if (id) scrollToSection(id);
    });
  });
}

// Make every header / sub-nav anchor robust: always smooth-scroll to the
// matching section if it exists, even when the section was added later.
function setupNavLinks() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", (e) => {
      const href = a.getAttribute("href") || "";
      const id = href.slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return; // let browser handle (or do nothing)
      e.preventDefault();
      scrollToSection(id);
    });
  });
}

// ---------------------------- Background loaders (no UI section yet) ---------------------------- //
async function loadOrders() {
  try {
    const data = await apiGet("/orders");
    console.info("Loaded orders:", data.orders?.length ?? 0);
    return true;
  } catch (err) {
    console.error("Failed to load /orders:", err);
    return false;
  }
}

async function loadDeliveryOptions() {
  try {
    const data = await apiGet("/delivery/options");
    console.info("Loaded delivery options:", data.options?.length ?? 0);
    return true;
  } catch (err) {
    console.error("Failed to load /delivery/options:", err);
    return false;
  }
}

async function loadUsers() {
  try {
    const data = await apiGet("/users");
    console.info("Loaded users:", data.users?.length ?? 0);
    return true;
  } catch (err) {
    console.error("Failed to load /users:", err);
    return false;
  }
}

// ---------------------------- Init ---------------------------- //
document.addEventListener("DOMContentLoaded", async () => {
  setupHamburger();
  setupSearch();
  setupOrderForm();
  setupSupportForm();
  setupComplaintForm();
  setupSupplierForm();
  setupImportForm();
  setupSupportDetail();
  setupAdminProductForm();
  setupLoginUI();
  setupCategoryButtons();
  setupNavLinks();

  // Initial selects state (empty until backend responds).
  populateOrderModelSelect();
  populateOrderMaterialSelect();
  populateOrderDeliverySelect();
  populateOrderPaymentSelect();

  // Decide whether to show the login screen or the main app based on storage.
  applyAuthState();
  renderViewByRole();

  // Only fetch backend data when there is a logged-in user. If not logged in,
  // the login screen covers the page and no app data is loaded.
  if (getCurrentUser()) {
    loadAllAppData();
  }
});
