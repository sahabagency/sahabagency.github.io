const assert=require('node:assert/strict');
const {focus,context}=require('./intelligence.js');
const rows=[
{id:'a',type:'task',scope:'agency',title:'متابعة المتجر',due:'2026-11-25',priority:'normal',status:'progress'},
{id:'b',type:'task',scope:'agency',title:'مهمة عاجلة',priority:'critical',status:'progress'},
{id:'c',type:'task',scope:'agency',title:'منجزة',priority:'critical',status:'done'},
{id:'d',type:'task',scope:'agency',title:'وكيل',priority:'critical',agentRole:'agent',status:'progress'},
{id:'e',type:'memory',scope:'personal',title:'المتجر الخاص',desc:'private'},
{id:'f',type:'memory',scope:'agency',title:'قرار المتجر',desc:'معلومة'},
];
assert.deepEqual(focus(rows,'2026-11-26').map(r=>r.id),['a','b']);
assert.deepEqual(context('المتجر',rows,'agency').records.map(r=>r.title).sort(),['قرار المتجر','متابعة المتجر'].sort());
assert.equal(context('غيرموجود',rows,'agency').records.length,0);
assert.equal(context('المتجر',rows,'agency').records.some(r=>r.desc==='private'),false);
console.log('4 assertions passed');
