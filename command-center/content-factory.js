/* Sahab Content Factory: draft-stage agent assignments, no simulated publication. */
(function(root){
 const roles=[["trend","باحث الترندات","حلل المصادر المقدمة وحدد الاتجاهات المدعومة بالأدلة"],["competitors","محلل المنافسين","قارن المحتوى المرجعي دون اختلاق مؤشرات"],["news","راصد الأخبار","استخرج الأخبار من المصادر المقدمة، وحدد ما يحتاج تحققًا"],["hooks","مهندس الهوكات","اقترح ثلاثة هوكات مختلفة قابلة للاختبار"],["strategy","استراتيجي المحتوى","حدد الجمهور والهدف وزاوية المحتوى"],["script","كاتب السكريبت","اكتب نصوص ريلز عربية بلهجة مناسبة وبأسلوب أصلي"],["avatar","مخرج الأفاتار","جهز تعليمات المشاهد والأفاتار ومستلزمات الموافقة"],["voice","مخرج الصوت","جهز نص التعليق وإيقاعه ومواصفات الصوت"],["edit","مهندس المونتاج","جهز قائمة لقطات وتوقيتات وتعليقات وموسيقى مرخصة"],["carousel","مصمم الكاروسيل","جهز نصوص الشرائح وتوجيه التصميم"],["variants","مهندس النسخ","اقترح ثلاث نسخ واختبار متغير واحد"],["quality","مراجع المحتوى","حدد الادعاءات التي تحتاج تحققًا وحقوق الاستخدام"],["publish","مخطط النشر","جهز وصفًا وجدولًا مقترحًا دون النشر"],["analytics","محلل الأداء","جهز فرضيات ومقاييس الاختبار دون اختلاق نتائج"]];
 function createCycle({records,makeRecord,brief,sources,mode}){
  if(!brief.trim()||brief.length>3000||sources.length>8000)throw Error('أدخل موجزًا صالحًا ومصادر ضمن الحد');
  if(!['real','avatar','faceless','carousel'].includes(mode))throw Error('نوع إنتاج غير صالح');
  const project=makeRecord({type:'project',scope:'agency',title:'مصنع المحتوى: '+brief.slice(0,120),desc:brief+'\nالمصادر المقدمة: '+sources+'\nنوع الإنتاج: '+mode,status:'progress',tags:['مصنع المحتوى'],contentCycle:true});
  const tasks=roles.map(([key,role,assignment])=>makeRecord({type:'task',scope:'agency',title:'['+role+'] '+brief.slice(0,90),desc:assignment+'\n'+brief,status:'idea',parentId:project.id,agentRole:role,contentAgent:key,executionMode:'blueprint',tags:['مصنع المحتوى','مسودة'],pendingSync:false}));
  records.unshift(project,...tasks);
  return project;
 }
 root.SahabContentFactory={roles,createCycle};
 if(typeof module!=='undefined')module.exports=root.SahabContentFactory;
})(globalThis);
