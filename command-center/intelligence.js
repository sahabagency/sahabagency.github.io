/* Local executive intelligence: no network calls, no personal data in source. */
(function(root){
  function words(value){
    return String(value||'').toLowerCase().normalize('NFKC').replace(/[\u064b-\u065f]/g,'').replace(/[أإآ]/g,'ا').match(/[\p{L}\p{N}]+/gu)?.filter(x=>x.length>=3)||[];
  }
  function priority(record,day){
    return (record.due&&record.due<day?500:0)+(record.due===day?300:0)+({critical:120,high:80,normal:40,low:10}[record.priority]||40)+(record.status==='wait'?-15:0);
  }
  function focus(records,day){
    return records.filter(r=>r.type==='task'&&r.status!=='done'&&!r.agentRole).slice().sort((a,b)=>priority(b,day)-priority(a,day)||String(a.due||'9999').localeCompare(String(b.due||'9999'))).slice(0,3);
  }
  function context(question,records,scope){
    const terms=new Set(words(question));
    const ranked=records.filter(r=>!r.agentRole&&(!scope||r.scope===scope)).map(r=>{
      const title=words(r.title), all=words([r.title,r.desc,...(r.tags||[])].join(' '));
      const score=title.filter(w=>terms.has(w)).length*4+all.filter(w=>terms.has(w)).length;
      return {r,score};
    }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||String(b.r.updated||'').localeCompare(String(a.r.updated||'')));
    const selected=ranked.slice(0,12).map(({r})=>({type:r.type,title:String(r.title||'').slice(0,160),status:r.status,desc:String(r.desc||'').slice(0,600),updated:r.updated}));
    return {question:String(question).slice(0,6000),scope:scope||'all',records:selected,contextNote:'Only relevant records from selected scope; no external access or execution.'};
  }
  const api={focus,context,priority};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.CenterIntelligence=api;
})(typeof globalThis!=='undefined'?globalThis:this);
