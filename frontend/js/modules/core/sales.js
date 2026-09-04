(() => {
  const search = document.getElementById('sale-search');
  const results = document.getElementById('product-results');
  const cartRoot = document.getElementById('cart-lines');
  const totalRoot = document.getElementById('sale-total');
  const countRoot = document.getElementById('cart-count');
  const confirmButton = document.getElementById('confirm-sale');
  const message = document.getElementById('sale-message');
  const cart = new Map();
  let timer;

  const money = value => new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' }).format(Number(value));
  const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

  async function loadProducts() {
    const query = search.value.trim();
    const response = await fetch(`/api/v1/products?q=${encodeURIComponent(query)}`);
    const payload = await response.json();
    const products = payload.data || [];
    results.innerHTML = products.length ? products.map(product => `
      <div class="product-row">
        <div><strong>${escapeHtml(product.name)}</strong><small>${escapeHtml(product.sku)} · ${money(product.current_price)}</small></div>
        <div class="product-action"><span class="stock-pill">${product.available} disp.</span><button class="btn add-product" data-id="${product.id}" ${product.available < 1 ? 'disabled' : ''}>Agregar</button></div>
      </div>`).join('') : '<div class="empty-state compact"><p>No se encontraron productos disponibles.</p></div>';
    results.querySelectorAll('.add-product').forEach(button => button.addEventListener('click', () => {
      const product = products.find(item => item.id === button.dataset.id);
      const current = cart.get(product.id);
      if (!current || current.quantity < product.available) cart.set(product.id, { ...product, quantity: (current?.quantity || 0) + 1 });
      renderCart();
    }));
  }

  function renderCart() {
    const lines = [...cart.values()];
    cartRoot.innerHTML = lines.length ? lines.map(item => `<div class="cart-line"><div><strong>${escapeHtml(item.name)}</strong><small>${money(item.current_price)} c/u</small></div><div class="cart-quantity"><button data-action="minus" data-id="${item.id}">−</button><b>${item.quantity}</b><button data-action="plus" data-id="${item.id}">+</button></div></div>`).join('') : '<div class="empty-state compact"><p>Agrega productos para comenzar.</p></div>';
    const units = lines.reduce((sum, item) => sum + item.quantity, 0);
    const total = lines.reduce((sum, item) => sum + Number(item.current_price) * item.quantity, 0);
    countRoot.textContent = units; totalRoot.textContent = money(total); confirmButton.disabled = !lines.length;
    cartRoot.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      const item = cart.get(button.dataset.id);
      if (button.dataset.action === 'plus' && item.quantity < item.available) item.quantity += 1;
      if (button.dataset.action === 'minus') item.quantity -= 1;
      if (item.quantity < 1) cart.delete(item.id); else cart.set(item.id, item);
      renderCart();
    }));
  }

  confirmButton.addEventListener('click', async () => {
    confirmButton.disabled = true; message.className = 'form-message'; message.textContent = 'Confirmando venta…';
    try {
      const draft = await fetch('/api/v1/sales', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({location_id:'main',items:[...cart.values()].map(item=>({product_id:item.id,quantity:item.quantity}))}) });
      const draftPayload = await draft.json(); if (!draft.ok) throw new Error(draftPayload.error?.message || 'No se pudo crear la venta');
      const confirmed = await fetch(`/api/v1/sales/${draftPayload.data.id}/confirm`, { method:'POST', headers:{'Idempotency-Key':crypto.randomUUID()} });
      const payload = await confirmed.json(); if (!confirmed.ok) throw new Error(payload.error?.message || 'No se pudo confirmar');
      message.className = 'form-message success'; message.textContent = `Venta ${payload.data.number} confirmada correctamente.`; cart.clear(); renderCart(); loadProducts();
    } catch (error) { message.className = 'form-message error'; message.textContent = error.message; confirmButton.disabled = false; }
  });

  search.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(loadProducts, 250); });
  loadProducts(); renderCart();
})();
