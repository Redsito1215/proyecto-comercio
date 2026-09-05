(()=>{
  const nativeFetch=window.fetch.bind(window);
  const tokenKey='ci-access-token';
  const userKey='ci-user';
  const token=()=>sessionStorage.getItem(tokenKey);
  const isApi=input=>{const url=typeof input==='string'?input:input.url;return new URL(url,location.origin).origin===location.origin&&new URL(url,location.origin).pathname.startsWith('/api/')};
  window.ciEscape=value=>String(value??'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  window.fetch=async(input,init={})=>{
    const headers=new Headers(init.headers||(typeof input!=='string'&&input.headers)||{});
    if(isApi(input)&&token())headers.set('Authorization',`Bearer ${token()}`);
    const response=await nativeFetch(input,{...init,headers});
    if(response.status===401&&document.getElementById('auth-gate'))document.getElementById('auth-gate').hidden=false;
    return response;
  };
  function saveSession(data){sessionStorage.setItem(tokenKey,data.access_token);sessionStorage.setItem(userKey,JSON.stringify(data.user));location.reload()}
  async function submit(form,path,message){
    const fields=new FormData(form),payload=Object.fromEntries(fields.entries());
    message.className='form-message';message.textContent='Verificando…';
    const response=await nativeFetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),body=await response.json();
    if(!response.ok){message.className='form-message error';message.textContent=body.error?.message||'No se pudo completar';return null}
    return body.data;
  }
  document.addEventListener('DOMContentLoaded',()=>{
    const gate=document.getElementById('auth-gate'),message=document.getElementById('auth-message'),bootstrapDetails=document.getElementById('bootstrap-details'),stored=sessionStorage.getItem(userKey),user=stored?JSON.parse(stored):null;
    gate.hidden=Boolean(token());
    nativeFetch('/api/v1/security/bootstrap/status').then(response=>response.json()).then(body=>{bootstrapDetails.hidden=!body.data?.available}).catch(()=>{bootstrapDetails.hidden=true});
    if(user){document.getElementById('user-name').textContent=user.name;document.getElementById('user-role').textContent=(user.roles||[]).join(', ');document.getElementById('user-avatar').textContent=user.name.split(/\s+/).map(x=>x[0]).join('').slice(0,2).toUpperCase()}
    document.getElementById('login-form').onsubmit=async event=>{event.preventDefault();const data=await submit(event.currentTarget,'/api/v1/security/login',message);if(data)saveSession(data)};
    document.getElementById('bootstrap-form').onsubmit=async event=>{event.preventDefault();const form=event.currentTarget,data=await submit(form,'/api/v1/security/bootstrap',message);if(!data){const status=await nativeFetch('/api/v1/security/bootstrap/status').then(response=>response.json());bootstrapDetails.hidden=!status.data?.available;return}bootstrapDetails.hidden=true;const login=await nativeFetch('/api/v1/security/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:form.email.value,password:form.password.value})}),body=await login.json();if(login.ok)saveSession(body.data)};
    document.getElementById('logout-button').onclick=async()=>{await window.fetch('/api/v1/security/logout',{method:'POST'});sessionStorage.removeItem(tokenKey);sessionStorage.removeItem(userKey);location.reload()};
  });
})();
