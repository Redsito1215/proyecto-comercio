(()=>{
  const root=document.getElementById('report-catalog');if(!root)return;
  const escape=window.ciEscape||String;
  // Las pestañas viven fuera de #report-catalog: gobiernan también el panel de
  // informes predeterminados, que es un componente aparte.
  const tabs=[...document.querySelectorAll('[data-report-tab]')],panels=[...document.querySelectorAll('[data-report-panel]')];
  const list=root.querySelector('#catalog-list'),search=root.querySelector('#catalog-search'),family=root.querySelector('#catalog-family');
  const title=root.querySelector('#catalog-title'),subtitle=root.querySelector('#catalog-subtitle'),badge=root.querySelector('#catalog-badge');
  const filters=root.querySelector('#catalog-filters'),result=root.querySelector('#catalog-result'),message=root.querySelector('#catalog-message'),pdf=root.querySelector('#catalog-pdf');
  const state={kind:'simple',catalog:{simple:[],compuesto:[]},current:null};

  const endpoint=report=>report.tipo==='compuesto'?`/api/v1/reports/compuestos/${report.id}`:`/api/v1/reports/simple/${report.id}`;

  function notify(text,kind){message.className=`form-message ${kind||''}`.trim();message.textContent=text||''}

  const FIELDS={
    date:'<label>Desde<input type="date" name="date_from"></label><label>Hasta<input type="date" name="date_to"></label>',
    search:'<label>Buscar<input type="search" name="search" placeholder="Producto, cliente, código…"></label>',
    threshold:'<label>Umbral de existencias<input type="number" name="threshold" value="10" min="0"></label>',
    days:'<label>Días de anticipación<input type="number" name="days" value="30" min="1" max="365"></label>'
  };

  function renderFilters(report){
    const declared=report.filters||[];
    filters.innerHTML=declared.map(name=>FIELDS[name]||'').join('')+'<button class="btn" type="submit">Ejecutar</button>';
    filters.hidden=false;
  }

  function query(){
    const data=new FormData(filters),params=new URLSearchParams();
    for(const [key,value] of data.entries())if(String(value).trim())params.set(key,value);
    return params;
  }

  function renderList(){
    const needle=(search.value||'').toLowerCase();
    const reports=state.catalog[state.kind].filter(report=>!needle||`${report.id} ${report.name} ${report.para_que}`.toLowerCase().includes(needle));
    if(!reports.length){list.innerHTML='<li class="catalog-empty">Sin informes disponibles para tu rol.</li>';return}
    list.innerHTML=reports.map(report=>`<li><button type="button" class="catalog-item${state.current?.id===report.id?' active':''}" data-report="${escape(report.id)}"><span class="catalog-id">${escape(report.id)}</span><strong>${escape(report.name)}</strong><small>${escape(report.para_que)}</small><em>${escape(report.quien)}</em></button></li>`).join('');
  }

  // Paleta cíclica: cuantas más series, grupos o filas distinga el gráfico, más
  // colores entran en juego. Son valores literales y no variables del tema porque
  // deben contrastar entre sí, no integrarse con el fondo.
  const PALETTE=['#2FAE9B','#3B82F6','#F59E0B','#EF4444','#8B5CF6','#EC4899','#0EA5E9','#84CC16','#F97316','#6366F1'];
  const color=index=>PALETTE[index%PALETTE.length];

  function renderChart(report,rows){
    const chart=report.chart;if(!chart||!rows.length)return '';
    const labelIndex=report.columns.indexOf(chart.x);
    const series=chart.series.map(name=>({name,index:report.columns.indexOf(name)})).filter(entry=>entry.index>=0);
    if(labelIndex<0||!series.length)return '';
    const groupIndex=chart.group?report.columns.indexOf(chart.group):-1;
    const points=rows.slice(0,12);
    const groups=groupIndex>=0?[...new Set(points.map(row=>String(row[groupIndex])))]:[];
    const peak=Math.max(...points.flatMap(row=>series.map(entry=>Math.abs(Number(row[entry.index])||0))),1);

    // Prioridad del color: primero distinguir series, luego grupos, y si no hay
    // ninguna de las dos, dar un color propio a cada fila.
    const paint=(row,rowIndex,seriesPosition)=>series.length>1?color(seriesPosition)
      :groupIndex>=0?color(groups.indexOf(String(row[groupIndex])))
      :color(rowIndex);

    const legend=series.length>1?series.map((entry,position)=>({label:entry.name,tone:color(position)}))
      :groupIndex>=0?groups.map((name,position)=>({label:name,tone:color(position)})):[];

    const bars=points.map((row,rowIndex)=>{
      const tracks=series.map((entry,position)=>{
        const value=Number(row[entry.index])||0;
        return `<span class="catalog-bar-track" title="${escape(entry.name)}: ${escape(row[entry.index])}"><span class="catalog-bar-fill" style="width:${(Math.abs(value)/peak*100).toFixed(1)}%;background:${paint(row,rowIndex,position)}"></span></span>`;
      }).join('');
      const values=series.map(entry=>`<span>${escape(row[entry.index])}</span>`).join('');
      return `<div class="catalog-bar"><span class="catalog-bar-label" title="${escape(row[labelIndex])}">${escape(row[labelIndex])}</span><span class="catalog-bar-series">${tracks}</span><span class="catalog-bar-value">${values}</span></div>`;
    }).join('');

    return `<figure class="catalog-chart"><figcaption>${escape(chart.series.join(' · '))} por ${escape(chart.x)}</figcaption>${legend.length?`<div class="catalog-legend">${legend.map(item=>`<span><i style="background:${item.tone}"></i>${escape(item.label)}</span>`).join('')}</div>`:''}${bars}${rows.length>points.length?`<figcaption class="catalog-chart-note">Gráfico limitado a las primeras ${points.length} de ${rows.length} filas.</figcaption>`:''}</figure>`;
  }

  function renderResult(payload){
    const report=payload.report,rows=payload.rows;
    const table=`<div class="table-wrap"><table class="data-table"><thead><tr>${report.columns.map(column=>`<th>${escape(column)}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.slice(0,150).map(row=>`<tr>${row.map(cell=>`<td>${escape(cell)}</td>`).join('')}</tr>`).join(''):`<tr><td colspan="${report.columns.length}">Sin datos para los filtros aplicados.</td></tr>`}</tbody></table></div>`;
    const note=rows.length>150?`<p class="filter-summary">Vista limitada a 150 de ${rows.length} filas. El PDF incluye hasta 400.</p>`:'';
    result.className='catalog-result';
    result.innerHTML=`<div class="catalog-meta"><span><small>Origen</small><strong>${escape(report.data_layer)}</strong></span><span><small>Filas</small><strong>${rows.length}</strong></span><span><small>Especificación</small><strong>${escape(report.spec)}</strong></span>${report.source_tables?`<span><small>Tablas cruzadas</small><strong>${report.source_tables.length}</strong></span>`:''}</div>${renderChart(report,rows)}${table}${note}`;
  }

  async function run(){
    if(!state.current)return;
    notify('Ejecutando el informe…','info');
    try{
      const response=await fetch(`${endpoint(state.current)}?${query()}`),body=await response.json();
      if(!response.ok)throw new Error(body.error?.message||'No se pudo ejecutar el informe');
      renderResult(body.data);pdf.disabled=false;
      notify(`Informe ${state.current.id} actualizado.`,'success');
    }catch(error){pdf.disabled=true;notify(error.message,'error')}
  }

  async function download(){
    if(!state.current)return;
    try{
      pdf.disabled=true;notify('Preparando el PDF…','info');
      const response=await fetch(`${endpoint(state.current)}/pdf?${query()}`);
      if(!response.ok){const body=await response.json();throw new Error(body.error?.message||'No se pudo generar el PDF')}
      const url=URL.createObjectURL(await response.blob()),link=document.createElement('a');
      link.href=url;link.download=`${state.current.id}.pdf`;link.click();
      setTimeout(()=>URL.revokeObjectURL(url),1500);
      notify('PDF descargado correctamente.','success');
    }catch(error){notify(error.message,'error')}finally{pdf.disabled=false}
  }

  function select(reportId){
    state.current=state.catalog[state.kind].find(report=>report.id===reportId);
    if(!state.current)return;
    badge.textContent=state.current.tipo==='compuesto'?'Informe compuesto':'Informe simple';
    title.textContent=`${state.current.id} · ${state.current.name}`;
    subtitle.textContent=`${state.current.para_que} Dirigido a: ${state.current.quien}.`;
    renderFilters(state.current);renderList();pdf.disabled=true;notify('');
    result.className='empty-state';result.innerHTML='<span class="empty-mark">▶</span><h3>Informe listo para ejecutar</h3><p>Ajusta los filtros y pulsa Ejecutar.</p>';
    run();
  }

  list.onclick=event=>{const button=event.target.closest('[data-report]');if(button)select(button.dataset.report)};
  search.oninput=renderList;
  filters.onsubmit=event=>{event.preventDefault();run()};
  pdf.onclick=download;
  tabs.forEach(tab=>tab.onclick=()=>{
    const target=tab.dataset.reportTab;
    tabs.forEach(other=>other.classList.toggle('active',other===tab));
    // Simples y compuestos comparten el mismo panel de catálogo: solo cambia la familia.
    const panel=target==='predeterminados'?'predeterminados':'catalogo';
    panels.forEach(section=>section.classList.toggle('active',section.dataset.reportPanel===panel));
    if(panel==='predeterminados')return;
    state.kind=target;state.current=null;
    filters.hidden=true;pdf.disabled=true;notify('');
    const compuesto=state.kind==='compuesto';
    family.textContent=compuesto?'Informes compuestos':'Informes simples';
    badge.textContent=family.textContent;
    title.textContent='Selecciona un informe';
    subtitle.textContent=compuesto
      ?'Agregan y cruzan varias tablas de hechos en ClickHouse; requieren que el ETL de Airflow haya corrido.'
      :'Listados operativos leídos directamente de MongoDB.';
    result.className='empty-state';result.innerHTML='<span class="empty-mark">▤</span><h3>Elige un informe del catálogo</h3><p>Cada informe declara para qué sirve y a quién va dirigido.</p>';
    renderList();
  });

  (async()=>{
    try{
      const response=await fetch('/api/v1/reports/catalog'),body=await response.json();
      if(!response.ok)throw new Error(body.error?.message||'No se pudo cargar el catálogo');
      state.catalog={simple:body.data.simples,compuesto:body.data.compuestos};
      renderList();
    }catch(error){list.innerHTML=`<li class="catalog-empty">${escape(error.message)}</li>`}
  })();
})();
