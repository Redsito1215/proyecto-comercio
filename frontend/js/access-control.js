(()=>{
  const roleNames={admin:'Administrador',cashier:'Cajero',supervisor:'Supervisor',auditor:'Auditor'};
  const pageRules={ventas:['sales.write'],inventario:['inventory.read','purchases.read'],caja:['payments.write','payments.read','sales.write','inventory.read'],devoluciones:['returns.write'],clientes:['customers.read'],precios:['products.read'],pronostico:['inventory.read'],promociones:['products.read'],gestion:['catalogs.read','security.users.read','settings.read'],informes:['reports.read'],seguridad:['security.audit.read']};
  const readUser=()=>{try{return JSON.parse(sessionStorage.getItem('ci-user')||'null')}catch{return null}};
  const permissionSet=()=>{const user=readUser(),set=new Set(user?.permissions||[]);if((user?.roles||[]).includes('admin'))set.add('*');return set};
  const can=permission=>{const set=permissionSet();return set.has('*')||set.has(permission)};
  const canAny=permissions=>permissions.some(can);
  window.ciCan=can;window.ciCanAny=canAny;
  const reportRules={sales:'sales.read',inventory:'inventory.read',margins:'products.read',customers:'customers.read',losses:'inventory.read',payments:'payments.read',forecasts:'inventory.read'};
  window.ciAllowedReportSections=()=>Object.keys(reportRules).filter(section=>can(reportRules[section]));
  function setAllowed(element,allowed){if(!element)return;element.hidden=!allowed;element.setAttribute('aria-hidden',String(!allowed));element.querySelectorAll('button,input,select,textarea').forEach(control=>control.disabled=!allowed)}
  function apply(){
    const denied=[];
    if(!can('sales.confirm'))denied.push('#confirm-sale');
    if(!can('purchases.write'))denied.push('#purchase-form');
    if(!can('purchases.receive'))denied.push('[data-receive-order]');
    if(!can('inventory.count'))denied.push('#count-form');
    if(!can('payments.write'))denied.push('#payment-form');
    if(!can('sales.write'))denied.push('#cash-open-form','#cash-movement-form');
    if(!can('inventory.adjust'))denied.push('#cash-close-form','#loss-form','.review-resolution');
    if(!can('customers.write'))denied.push('#customer-form');
    if(!can('products.write'))denied.push('#promotion-form','[data-audience]','[data-activate]','.price-form','#management-product-form');
    if(!can('catalogs.write'))denied.push('.management-form[data-kind]');
    if(!can('security.users.write'))denied.push('#management-user-form','#management-role-form');
    if(!can('settings.write'))denied.push('#business-settings-form');
    let policy=document.getElementById('ci-access-policy');if(!policy){policy=document.createElement('style');policy.id='ci-access-policy';document.head.appendChild(policy)}policy.textContent=denied.length?`${denied.join(',')}{display:none!important}`:'';
    document.querySelectorAll('.nav-item[data-page]').forEach(item=>setAllowed(item,!pageRules[item.dataset.page]||canAny(pageRules[item.dataset.page])));
    document.querySelectorAll('[data-permission]').forEach(element=>setAllowed(element,can(element.dataset.permission)));
    document.querySelectorAll('[data-permission-any]').forEach(element=>setAllowed(element,canAny(element.dataset.permissionAny.split(',').map(x=>x.trim()))));
    const rules={'#confirm-sale':'sales.confirm','#purchase-form':'purchases.write','#count-form':'inventory.count','#payment-form':'payments.write','#cash-open-form':'sales.write','#cash-movement-form':'sales.write','#cash-close-form':'inventory.adjust','#loss-form':'inventory.adjust','#customer-form':'customers.write','#promotion-form':'products.write','#management-product-form':'products.write','#management-user-form':'security.users.write','#management-role-form':'security.users.write','#business-settings-form':'settings.write'};
    Object.entries(rules).forEach(([selector,permission])=>setAllowed(document.querySelector(selector),can(permission)));
    document.querySelectorAll('.management-form[data-kind]').forEach(form=>setAllowed(form,can('catalogs.write')));
    document.querySelectorAll('[data-management-tab="catalogos"]').forEach(x=>setAllowed(x,can('catalogs.read')));
    document.querySelectorAll('[data-management-tab="usuarios"],[data-management-tab="roles"]').forEach(x=>setAllowed(x,can('security.users.read')));
    document.querySelectorAll('[data-management-tab="configuracion"]').forEach(x=>setAllowed(x,can('settings.read')));
    document.querySelectorAll('#report-form [name="sections"]').forEach(input=>{const allowed=can(reportRules[input.value]);input.checked=input.checked&&allowed;setAllowed(input.closest('label'),allowed)});
    const user=readUser(),role=document.getElementById('user-role');if(user&&role)role.textContent=(user.roles||[]).map(x=>roleNames[x]||x).join(', ');
  }
  window.ciApplyAccess=apply;
  document.addEventListener('DOMContentLoaded',apply);
})();
