(() => {
  const page = document.getElementById('page-inicio');
  if (!page) return;
  const money = value => new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' }).format(Number(value || 0));
  const escape = window.ciEscape || (value => String(value));

  async function loadDashboard() {
    const recent = document.getElementById('dashboard-recent');
    try {
      const response = await fetch('/api/v1/dashboard/summary', { cache: 'no-store' });
      const output = await response.json();
      if (!response.ok) throw new Error(output.error?.message || 'No se pudo cargar el resumen');
      const data = output.data;
      document.getElementById('dashboard-sales').textContent = money(data.today_sales);
      document.getElementById('dashboard-operations').textContent = data.today_operations === 1 ? '1 operación confirmada' : `${data.today_operations} operaciones confirmadas`;
      document.getElementById('dashboard-products').textContent = data.active_products;
      document.getElementById('dashboard-low-stock').textContent = data.low_stock;
      document.getElementById('dashboard-margin').textContent = data.average_margin == null ? '—' : `${Number(data.average_margin).toFixed(1)}%`;
      document.getElementById('dashboard-stock-title').textContent = data.low_stock ? `${data.low_stock} referencias por reponer` : 'Inventario abastecido';
      document.getElementById('dashboard-stock-detail').textContent = data.low_stock ? 'Revisa el módulo de inventario' : 'No hay productos bajo el umbral';
      document.getElementById('dashboard-stock-signal').className = `signal ${data.low_stock ? 'neutral' : 'ok'}`;
      recent.innerHTML = data.recent_sales.length ? data.recent_sales.map(sale => `
        <article class="campaign-row">
          <div><strong>${escape(sale.number)}</strong><small>${escape(sale.customer)} · ${new Date(sale.confirmed_at).toLocaleString('es-EC')}</small></div>
          <div><strong>${money(sale.total)}</strong><span class="status-pill">Confirmada</span></div>
        </article>`).join('') : '<div class="empty-state compact"><h3>Aún no hay ventas</h3><p>La primera operación confirmada aparecerá aquí.</p></div>';
    } catch (error) {
      recent.innerHTML = `<div class="empty-state compact"><h3>No se pudo actualizar</h3><p>${escape(error.message)}</p></div>`;
    }
  }

  window.addEventListener('ci:pagechange', event => {
    if (event.detail?.page === 'inicio') loadDashboard();
  });
  window.addEventListener('ci:authenticated', loadDashboard);
  loadDashboard();
})();
