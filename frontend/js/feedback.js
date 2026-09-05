(()=>{
  const labels={
    'inventory-refresh':['Actualizando inventario…','Inventario actualizado.'],
    'control-refresh':['Actualizando controles…','Controles actualizados.'],
    'pricing-refresh':['Actualizando márgenes…','Márgenes actualizados.'],
    'forecast-refresh':['Actualizando pronóstico…','Pronóstico actualizado.'],
    'promotion-refresh':['Actualizando campañas…','Campañas actualizadas.'],
    'security-refresh':['Actualizando auditoría…','Auditoría actualizada.'],
    'management-users-refresh':['Actualizando usuarios…','Usuarios actualizados.'],
    'management-roles-refresh':['Actualizando roles…','Roles actualizados.'],
    'management-products-refresh':['Actualizando productos…','Productos actualizados.']
  };
  const clean=value=>String(value||'').replace(/[a-f\d]{24}/gi,'el registro seleccionado').replace(/\b(provider|token|gateway|stack|trace)\b/gi,'servicio').slice(0,220);
  let region;
  const notify=(title,detail='',type='success',duration=3200)=>{
    const toast=document.createElement('div');toast.className=`app-toast ${type}`;toast.setAttribute('role',type==='error'?'alert':'status');toast.innerHTML=`<span class="toast-icon" aria-hidden="true">${type==='error'?'!':type==='info'?'i':'✓'}</span><div><strong>${window.ciEscape?.(title)||title}</strong>${detail?`<small>${window.ciEscape?.(clean(detail))||clean(detail)}</small>`:''}</div><button type="button" aria-label="Cerrar mensaje">×</button>`;
    const close=()=>{toast.classList.add('leaving');setTimeout(()=>toast.remove(),180)};toast.querySelector('button').onclick=close;region.append(toast);setTimeout(close,duration);return toast;
  };
  window.ciNotify=notify;
  window.ciFriendlyError=(body,fallback='No se pudo completar la acción.')=>clean(body?.error?.message||body?.message||fallback);
  region=document.createElement('div');region.className='toast-region';region.setAttribute('aria-live','polite');region.setAttribute('aria-atomic','true');document.body.append(region);
  const prepareMessage=element=>{if(!element?.classList?.contains('form-message'))return;element.setAttribute('role',element.classList.contains('error')?'alert':'status');element.setAttribute('aria-live',element.classList.contains('error')?'assertive':'polite');const safe=clean(element.textContent);if(safe!==element.textContent)element.textContent=safe};
  document.querySelectorAll('.form-message').forEach(prepareMessage);
  new MutationObserver(records=>records.forEach(record=>{prepareMessage(record.target);record.addedNodes.forEach(node=>{if(node.nodeType===1){prepareMessage(node);node.querySelectorAll?.('.form-message').forEach(prepareMessage)}})})).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class']});

  const originalFetch=window.fetch.bind(window);let current=null;
  const finish=context=>{
    if(!context||--context.pending>0)return;
    const {button,original,pair,failed}=context;button.disabled=false;button.removeAttribute('aria-busy');button.textContent=original;
    if(pair)notify(failed?'No se pudo actualizar':pair[1],failed?'Revisa la conexión e inténtalo nuevamente.':'Los datos visibles corresponden al último estado.',failed?'error':'success');
  };
  window.fetch=async(input,init={})=>{
    const context=current;
    if(context){context.pending+=1;if(context.pending===1){context.button.disabled=true;context.button.setAttribute('aria-busy','true');context.button.textContent=context.pair?.[0]||'Procesando…'}}
    try{const response=await originalFetch(input,init);if(context&&!response.ok)context.failed=true;return response}catch(error){if(context)context.failed=true;throw error}finally{if(context)finish(context)}
  };
  document.addEventListener('click',event=>{
    const button=event.target.closest('button');if(!button)return;
    const pair=labels[button.id]||(button.hasAttribute('data-audit-pdf')?['Generando PDF…','PDF de auditoría descargado.']:null);
    const tracked=pair||button.matches('[data-audience],[data-activate],[data-metrics]');
    if(tracked){current={button,original:button.textContent,pair,pending:0,failed:false};setTimeout(()=>{current=null},0)}
    if(button.id==='theme-toggle')setTimeout(()=>notify('Apariencia actualizada',document.documentElement.dataset.theme==='dark'?'Tema oscuro activado.':'Tema claro activado.','info'),0);
    if(button.id==='inventory-clear-filters')setTimeout(()=>notify('Filtros limpiados','Se muestran nuevamente todas las existencias.','info'),0);
    if(button.id==='sale-clear-filters')setTimeout(()=>notify('Filtros limpiados','El catálogo volvió a su selección inicial.','info'),0);
    if(button.hasAttribute('data-clear-audit'))setTimeout(()=>notify('Filtros limpiados','Se muestran nuevamente todos los eventos de auditoría.','info'),0);
    if(button.hasAttribute('data-report-preset'))setTimeout(()=>notify('Plantilla aplicada',`${button.textContent.trim()} seleccionada.`,'info',2200),0);
    if(button.hasAttribute('data-report-all'))setTimeout(()=>notify('Selección actualizada','Se incluyeron todas las secciones.','info',2200),0);
    if(button.hasAttribute('data-report-none'))setTimeout(()=>notify('Selección vacía','Selecciona al menos una sección para continuar.','info',2600),0);
  },true);
  document.addEventListener('submit',event=>{
    const button=event.submitter||event.target.querySelector('button[type="submit"],button:not([type])');
    if(!button||button.id==='report-pdf')return;
    current={button,original:button.textContent,pair:null,pending:0,failed:false};setTimeout(()=>{current=null},0);
  },true);
})();
