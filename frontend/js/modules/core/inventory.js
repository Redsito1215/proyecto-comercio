(() => {
  const body = document.getElementById('inventory-body');
  const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const productFilter=document.getElementById('inventory-filter-product'),locationFilter=document.getElementById('inventory-filter-location'),statusFilter=document.getElementById('inventory-filter-status'),summary=document.getElementById('inventory-filter-summary');
  let allRows=[];
  function render(){const query=productFilter.value.trim().toLowerCase(),location=locationFilter.value,status=statusFilter.value;const rows=allRows.filter(row=>{const text=`${row.product_name} ${row.sku}`.toLowerCase();const state=!status||(status==='available'&&row.available>0)||(status==='low'&&row.available>0&&row.available<=5)||(status==='empty'&&row.available===0)||(status==='expiring'&&row.expiring_lots>0);return(!query||text.includes(query))&&(!location||row.location_id===location)&&state});summary.textContent=`Mostrando ${rows.length} de ${allRows.length} registros`;body.innerHTML=rows.length?rows.map(row=>`<tr><td><strong>${escapeHtml(row.product_name)}</strong></td><td>${escapeHtml(row.sku)}</td><td>${escapeHtml(row.location_id)}</td><td>${row.available}</td><td>${row.reserved}</td><td><span class="status-pill ${row.expiring_lots?'warn':''}">${row.expiring_lots?`${row.expiring_lots} lote(s)`:'Sin alerta'}</span></td></tr>`).join(''):'<tr><td colspan="6">No hay existencias que coincidan con los filtros.</td></tr>'}
  async function loadInventory() {
    const response = await fetch('/api/v1/inventory'); const payload = await response.json();
    const rows = payload.data || [];allRows=rows;
    document.getElementById('inventory-products').textContent = rows.length;
    document.getElementById('inventory-units').textContent = rows.reduce((sum,row)=>sum+row.available,0);
    document.getElementById('inventory-low').textContent = rows.filter(row=>row.available<=5).length;
    document.getElementById('inventory-expiring').textContent = rows.reduce((sum,row)=>sum+row.expiring_lots,0);
    const current=locationFilter.value;locationFilter.innerHTML='<option value="">Todas las ubicaciones</option>'+[...new Set(rows.map(x=>x.location_id))].sort().map(x=>`<option value="${escapeHtml(x)}">${escapeHtml(x)}</option>`).join('');locationFilter.value=current;render();
  }
  document.getElementById('inventory-refresh').addEventListener('click', loadInventory);
  [productFilter,locationFilter,statusFilter].forEach(control=>control.addEventListener('input',render));
  document.getElementById('inventory-clear-filters').addEventListener('click',()=>{productFilter.value='';locationFilter.value='';statusFilter.value='';render()});
  loadInventory();
})();
