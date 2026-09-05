(() => {
  const form = document.getElementById('purchase-form');
  const select = document.getElementById('purchase-product');
  const body = document.getElementById('purchase-body');
  const message = document.getElementById('purchase-message');
  const money = value => new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' }).format(Number(value));
  const header = body.closest('table').querySelector('thead tr');
  if (!header.querySelector('[data-purchase-actions]')) header.insertAdjacentHTML('beforeend', '<th data-purchase-actions>Acción</th>');

  async function loadProducts() {
    const response = await fetch('/api/v1/products');
    const payload = await response.json();
    select.innerHTML = (payload.data || []).map(product => `<option value="${product.id}">${product.name} · ${product.sku}</option>`).join('');
  }

  async function loadOrders() {
    const response = await fetch('/api/v1/purchase-orders');
    const payload = await response.json();
    const rows = payload.data || [];
    body.innerHTML = rows.length ? rows.map(order => {
      const receivable = ['sent', 'partially_received'].includes(order.status) && (order.items || []).some(item => item.pending_quantity > 0);
      return `<tr><td><strong>${order.number}</strong></td><td>${order.supplier_name}</td><td><span class="status-pill">${order.status}</span></td><td>${money(order.total)}</td><td>${new Date(order.created_at).toLocaleDateString('es-EC')}</td><td>${receivable ? `<button class="btn" type="button" data-receive-order="${order.id}">Recibir todo</button>` : '<span class="status-pill">Completada</span>'}</td></tr>`;
    }).join('') : '<tr><td colspan="6">Sin órdenes.</td></tr>';
    body.querySelectorAll('[data-receive-order]').forEach(button => button.addEventListener('click', () => receiveOrder(button.dataset.receiveOrder, rows.find(order => order.id === button.dataset.receiveOrder), button)));
  }

  async function receiveOrder(orderId, order, button) {
    button.disabled = true;
    button.textContent = 'Recibiendo…';
    const suffix = Date.now().toString(36).toUpperCase();
    const items = (order.items || []).filter(item => item.pending_quantity > 0).map(item => ({
      product_id: item.product_id,
      lot_number: `${order.number}-${suffix}`,
      quantity: item.pending_quantity,
      unit_cost: item.unit_cost,
      expires_at: null
    }));
    const response = await fetch(`/api/v1/purchase-orders/${orderId}/receipts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': `purchase-${orderId}-${suffix}` },
      body: JSON.stringify({ items })
    });
    const payload = await response.json();
    message.className = `form-message ${response.ok ? 'success' : 'error'}`;
    message.textContent = response.ok ? `Orden ${order.number} recibida; inventario actualizado.` : (payload.error?.message || 'No se pudo recibir la orden');
    if (response.ok) {
      await loadOrders();
      document.getElementById('inventory-refresh').click();
      window.dispatchEvent(new CustomEvent('ci:inventorychange'));
    } else {
      button.disabled = false;
      button.textContent = 'Recibir todo';
    }
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const data = new FormData(form);
    const payload = { supplier_name: data.get('supplier_name'), items: [{ product_id: data.get('product_id'), quantity: Number(data.get('quantity')), unit_cost: data.get('unit_cost') }] };
    const response = await fetch('/api/v1/purchase-orders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const result = await response.json();
    message.className = `form-message ${response.ok ? 'success' : 'error'}`;
    message.textContent = response.ok ? `Orden ${result.data.number} creada.` : (result.error?.message || 'No se pudo crear');
    if (response.ok) { form.reset(); await init(); }
  });

  async function init() { await Promise.all([loadProducts(), loadOrders()]); }
  window.addEventListener('ci:pagechange', event => { if (event.detail?.page === 'inventario') init(); });
  init();
})();
