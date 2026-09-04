(() => {
  const body = document.getElementById('inventory-body');
  const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  async function loadInventory() {
    const response = await fetch('/api/v1/inventory'); const payload = await response.json();
    const rows = payload.data || [];
    document.getElementById('inventory-products').textContent = rows.length;
    document.getElementById('inventory-units').textContent = rows.reduce((sum,row)=>sum+row.available,0);
    document.getElementById('inventory-low').textContent = rows.filter(row=>row.available<=5).length;
    document.getElementById('inventory-expiring').textContent = rows.reduce((sum,row)=>sum+row.expiring_lots,0);
    body.innerHTML = rows.length ? rows.map(row=>`<tr><td><strong>${escapeHtml(row.product_name)}</strong></td><td>${escapeHtml(row.sku)}</td><td>${escapeHtml(row.location_id)}</td><td>${row.available}</td><td>${row.reserved}</td><td><span class="status-pill ${row.expiring_lots?'warn':''}">${row.expiring_lots ? `${row.expiring_lots} lote(s)` : 'Sin alerta'}</span></td></tr>`).join('') : '<tr><td colspan="6">Aún no existen recepciones de inventario.</td></tr>';
  }
  document.getElementById('inventory-refresh').addEventListener('click', loadInventory);
  loadInventory();
})();
