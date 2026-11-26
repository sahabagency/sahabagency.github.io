// Private single-owner runtime, served from the same origin as the dashboard.
function attachCenter({scheduled, snapshot, restore, seed, save, records, draw, toast, steps, escape}) {
  let token = '', busy = false, epoch = 0, connected = false;
  let message = 'أدخل رمز الخادم لربط الخزنة', ai = false;
  const baseKey = 'center-last-sync-v1';
  const box = () => localStorage.getItem('sahab-command-center-v1');
  async function digest(value) {
    const data = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value || ''));
    return Array.from(new Uint8Array(data), v => v.toString(16).padStart(2,'0')).join('');
  }
  async function api(path, body) {
    const r = await fetch('/api/' + path, {method:body ? 'POST':'GET', cache:'no-store',
      headers:{Authorization:'Bearer ' + token,'Content-Type':'application/json'},
      body:body ? JSON.stringify(body):undefined});
    if (!r.ok) throw Error(({401:'رمز الخادم غير صحيح',404:'افتح نسخة مركز القيادة المستضافة مع الخادم',409:'تغيّرت نسخة الخادم، أعد المزامنة',503:'اضبط مفتاح مزود الذكاء على الخادم'})[r.status] || 'تعذر الاتصال بالخادم');
    return r.json();
  }
  function status(s) {
    message = s;
    const node = document.getElementById('centerStatus');
    if (node) node.textContent = s;
  }
  async function sync(manual = false) {
    if (!token || busy || !snapshot()) return;
    busy = true;
    const session = epoch;
    try {
      const remote = await api('state');
      if (epoch !== session) return;
      ai = remote.ai;
      const base = JSON.parse(localStorage.getItem(baseKey) || 'null');
      let current = box();
      if (!remote.rev && remote.inventory.length) {
        seed(remote.inventory);
        await save();
        current = box();
      }
      if (remote.rev && base?.rev !== remote.rev) {
        const dirty = !base || base.hash !== await digest(current);
        if (dirty && (!manual || !confirm('توجد نسخة مركزية ونسخة محلية. هل حفظت نسخة احتياطية وتريد تحميل نسخة الخادم بدل المحلية؟'))) {
          throw Error('نسختان مختلفتان. صدّر النسخة المحلية ثم اضغط ربط ومزامنة لاختيار نسخة الخادم.');
        }
        await restore(remote.box, current, session, () => epoch);
        localStorage.setItem(baseKey, JSON.stringify({rev:remote.rev, hash:await digest(box())}));
        draw();
      } else if (!base || !remote.rev || base.hash !== await digest(current)) {
        const saved = await api('state',{rev:remote.rev,box:JSON.parse(current)});
        if (epoch !== session) return;
        localStorage.setItem(baseKey,JSON.stringify({rev:saved.rev,hash:await digest(current)}));
      }
      connected = true;
      for (const task of records().filter(x=>x.centerJob && !x.centerResult && x.centerState!=='failed')) {
        const job = await api('jobs/' + task.centerJob);
        if (epoch !== session) return;
        if (job.state !== task.centerState) {
          task.centerState = job.state;
          if (job.state==='done' && job.result) {
            task.centerResult = job.result;
            task.desc = job.result;
            task.status = 'done';
          }
          await save();
          draw();
        }
      }
      status(ai ? 'الخزنة متصلة · مزود الذكاء مضبوط' : 'الخزنة متصلة · مفتاح الذكاء غير مضبوط');
    } finally { busy = false; }
  }
  function panel(){
    if (scheduled) return scheduled.panel();
    return '<section class="panel"><h2>الخادم الخاص</h2><p id="centerStatus">'+escape(message)+'</p><input type="password" id="centerToken" autocomplete="off" placeholder="رمز الخادم"><button class="subbtn" id="centerConnect">ربط ومزامنة</button></section>';
  }
  async function click(e) {
    const el=e.target.closest('button');
    if (!el || !snapshot()) return;
    if (scheduled && (el.dataset.centerRun || el.id==='centerAsk')) return;
    if (el.id==='centerConnect') {
      const field=document.getElementById('centerToken');
      if(field.value){ token=field.value.trim(); field.value=''; }
      if(!token) throw Error('أدخل رمز الخادم');
      await sync(true);
    }
    if (!el.dataset.centerRun && el.id!=='centerAsk') return;
    if (!connected || !ai) throw Error('اربط الخادم بمزود الذكاء أولًا');
    const session = epoch;
    const project = records().find(x=>x.id===el.dataset.centerRun);
    const q = document.getElementById('brainText')?.value.trim();
    if (!project && !q) throw Error('اكتب توجيهك أولًا');
    const tasks = project ? steps(project) : [];
    if (!project) {
      const context=JSON.stringify({question:q,records:records().filter(x=>!x.agentRole).map(x=>[x.title,x.status,x.desc?.slice(0,240)])});
      if(context.length>32000) throw Error('السياق أكبر من حد الطلب. نفّذ خطة مشروع محدد.');
      const job=await api('jobs',{role:'العقل المركزي',context,retry:true});
      if(session!==epoch)return;
      if(!records().some(x=>x.centerJob===job.id))records().unshift({id:crypto.randomUUID(),type:'task',scope:'agency',title:q.slice(0,160),desc:'بانتظار مسودة العقل المركزي',tags:[],status:'progress',origin:'brain',updated:new Date().toISOString(),centerJob:job.id});
    } else {
      for (const task of tasks.filter(x=>!x.centerJob || x.centerState==='failed')) {
        const context=JSON.stringify({title:project.title,brief:project.desc,assignment:task.title});
        const job=await api('jobs',{role:task.agentRole,context,retry:true});
        if(session!==epoch)return;
        Object.assign(task,{centerJob:job.id,centerState:'queued',status:'progress'});
        await save();
      }
    }
    await save(); draw(); await sync(); toast('تم تسجيل الطلب على الخادم');
  }
  document.addEventListener('click',e=>click(e).catch(err=>{status(err.message);toast(err.message);}));
  setInterval(()=>{if(connected)sync().catch(err=>status(err.message));},10000);
  return {panel,lock(){epoch++; token='';connected=false;ai=false;message='أدخل رمز الخادم لربط الخزنة';}};
}
