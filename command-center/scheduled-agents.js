function attachScheduledAgents({getDB, save, draw, toast, connect, fetchGoogle, isConnected, makePlan, makeRecord, sheetId, escape}) {
  const queueTab = 'مهام وكلاء المركز', resultsTab = 'نتائج وكلاء المركز';
  const base = 'https://sheets.googleapis.com/v4/spreadsheets/' + sheetId + '/values/';
  let busy = false, status = 'اربط Google لإرسال المهام ومتابعة نتائجها';
  async function ready() {
    if (!isConnected() && !await connect()) throw Error('أكمل ربط Google من الإعدادات');
  }
  async function rows(tab) {
    const response = await fetchGoogle(base + encodeURIComponent("'" + tab + "'!A2:E"));
    return response.values || [];
  }
  async function hash(role, context) {
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(role+'\n'+context));
    return Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
  }
  function setStatus(value) {
    status = value;
    const el = document.getElementById('scheduledStatus');
    if (el) el.textContent = value;
  }
  async function sync() {
    if (busy || !getDB() || !isConnected()) return;
    busy = true;
    const db = getDB();
    try {
      const [events, requests] = await Promise.all([rows(resultsTab),rows(queueTab)]);
      const latest = new Map(events.map(row=>[row[0],row]));
      if (getDB() !== db) return;
      let changed = false;
      for (const row of requests) {
        if(row.length<4||db.records.some(x=>x.scheduledJob===row[0]))continue;
        let context;
        try{context=JSON.parse(row[3]);}catch{continue;}
        const project=db.records.find(x=>['project','idea','study'].includes(x.type)&&x.title===context.title);
        const existing=db.records.find(x=>x.id===row[1]) || db.records.find(x=>project&&x.parentId===project.id&&x.agentRole===row[2]);
        const task=existing || makeRecord({type:'task',title:context.assignment||context.question||row[2],desc:context.brief||context.question||'',agentRole:row[2],parentId:project?.id,status:'progress'});
        task.scheduledJob=row[0];
        if(!existing)db.records.push(task);
        changed=true;
      }
      for (const task of db.records.filter(x=>x.scheduledJob)) {
        const result = latest.get(task.scheduledJob);
        if (!result || task.scheduledUpdated === result[3]) continue;
        Object.assign(task,{scheduledState:result[1],scheduledUpdated:result[3],updated:result[3]});
        if (result[1]==='done' && result[2]) {
          task.desc=result[2];task.status='done';
        } else if (['failed','review'].includes(result[1])) {
          task.status='wait';
          task.desc='يحتاج الطلب إلى مراجعة. '+(result[4]||'');
        }
        changed = true;
      }
      if (changed) {await save();draw();}
      const pending=db.records.filter(x=>x.scheduledJob&&x.status!=='done').length;
      setStatus('تمت قراءة سجل النتائج · '+pending+' طلب بانتظار الإكمال');
    } finally {busy=false;}
  }
  async function submit(project, question) {
    await ready();
    if (busy || !getDB()) return;
    busy=true;
    const db=getDB();
    try {
      let tasks;
      if(project){makePlan(project);tasks=db.records.filter(x=>x.parentId===project.id&&x.agentRole);}
      else {
        if(!question)throw Error('اكتب توجيهك أولًا');
        tasks=[makeRecord({type:'task',title:question.slice(0,160),desc:question,agentRole:'العقل المركزي',origin:'brain',status:'progress'})];
      }
      const existing=new Set((await rows(queueTab)).map(row=>row[0]));
      if(getDB()!==db)return;
      const additions=[], assignments=[];
      for(const task of tasks) {
        const context=JSON.stringify(project?{title:project.title,brief:project.desc,assignment:task.title}:{question,records:db.records.filter(x=>!x.agentRole).map(x=>({title:x.title,status:x.status,desc:x.desc?.slice(0,240)}))});
        if(context.length>32000)throw Error('السياق أكبر من حد الطلب. استخدم مشروعًا محددًا.');
        const id=await hash(task.agentRole,context);
        if(!existing.has(id)) {
          additions.push([id,task.id,task.agentRole,context,new Date().toISOString()]);
          existing.add(id);
        }
        assignments.push({task,id});
      }
      if(additions.length) {
        await fetchGoogle(base+encodeURIComponent("'"+queueTab+"'!A:E")+':append?valueInputOption=RAW&insertDataOption=INSERT_ROWS',
          {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({values:additions})});
      }
      if(getDB()!==db)return;
      for(const {task,id} of assignments){task.scheduledJob=id;if(task.status!=='done')task.status='progress';}
      if(!project&&!db.records.some(x=>x.scheduledJob===tasks[0].scheduledJob))db.records.unshift(tasks[0]);
      await save();draw();
      setStatus('سُجّل الطلب في السجل الخاص. التنفيذ ينتظر دورة GitHub وإعداد اتصالاتها.');
      toast('تم حفظ الطلب في سجل الوكلاء');
    } finally {busy=false;}
  }
  document.addEventListener('click',e=>{
    const button=e.target.closest('button');
    if(!button||!getDB())return;
    const run=async()=>{
      if(button.id==='scheduledSync'){await ready();await sync();}
      else if(button.dataset.centerRun) {
        const project=getDB().records.find(x=>x.id===button.dataset.centerRun);
        if(project)await submit(project);
      } else if(button.id==='centerAsk')await submit(null,document.getElementById('brainText')?.value.trim());
    };
    run().catch(err=>{setStatus(err.message);toast(err.message);});
  });
  setInterval(()=>sync().catch(()=>setStatus('تعذرت قراءة النتائج. أعد ربط Google.')),60000);
  return {panel:()=>'<section class="panel"><h2>تشغيل الوكلاء عبر GitHub</h2><p id="scheduledStatus">'+escape(status)+'</p><p>دورة كل 15 دقيقة بعد إعداد الاتصال، بحد 24 مسودة خلال 24 ساعة. تبقى المهام والنتائج في السجل الخاص.</p><button class="subbtn" id="scheduledSync">ربط Google وتحديث النتائج</button><a class="subbtn" href="https://github.com/sahabagency/sahabagency.github.io/actions/workflows/command-center-agents.yml" target="_blank" rel="noopener">حالة دورات التشغيل</a></section>'};
}
