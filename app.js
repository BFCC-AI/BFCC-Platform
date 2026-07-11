
const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
let state={portfolio:null, orders:[], logs:[]};

async function loadData(){
  try{
    const r=await fetch('data/portfolio.json'); state.portfolio=await r.json();
  }catch(e){
    state.portfolio=window.EMBEDDED_PORTFOLIO;
  }
  renderAll();
}
function money(v){return Number(v).toLocaleString('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2})}
function positionValue(p){return p.qty*p.price}
function pnl(p){return p.qty*(p.price-p.avg)}
function pct(p){return ((p.price/p.avg)-1)*100}
function concentration(p){return positionValue(p)/state.portfolio.total_assets*100}
function riskScore(p){
  let s=25;
  if(concentration(p)>25)s+=30;
  if(pct(p)<-20)s+=25;
  if(p.role.includes('تخارج'))s+=15;
  return Math.min(100,s);
}
function decision(p){
  const change=pct(p), conc=concentration(p);
  if(p.role.includes('تخارج')) return {label:'تخفيف مرحلي', cls:'amber'};
  if(conc>35) return {label:'لا زيادة / خفض التركّز', cls:'red'};
  if(change<-15) return {label:'مراجعة الفرضية', cls:'red'};
  if(change>8) return {label:'احتفاظ مع جني مرحلي', cls:'green'};
  return {label:'احتفاظ ومراقبة', cls:'cyan'};
}
function levels(p){
  const vol = p.symbol==='NXB'?0.10:p.symbol==='EU'?0.06:0.045;
  const entry1=p.price*(1-vol*.55), entry2=p.price*(1-vol);
  const stop=p.price*(1-vol*1.65);
  const t1=p.price*(1+vol*1.4), t2=p.price*(1+vol*2.4);
  return {entry1,entry2,stop,t1,t2};
}
function renderAll(){renderMetrics();renderPortfolio();renderOrders();renderCapital()}
function renderMetrics(){
  const p=state.portfolio, invested=p.positions.reduce((a,x)=>a+positionValue(x),0);
  $('#total').textContent=money(p.total_assets); $('#cash').textContent=money(p.cash);
  $('#working').textContent=((invested/p.total_assets)*100).toFixed(1)+'%';
  const risk=Math.round(p.positions.reduce((a,x)=>a+riskScore(x)*concentration(x),0)/100);
  $('#risk').textContent=risk+'/100';
}
function renderPortfolio(){
 const tbody=$('#portfolioBody'); tbody.innerHTML='';
 state.portfolio.positions.forEach((p,i)=>{
   const d=decision(p), l=levels(p);
   const tr=document.createElement('tr');
   tr.innerHTML=`<td><b>${p.symbol}</b><div class="muted">${p.account}</div></td>
   <td><input data-i="${i}" data-k="qty" value="${p.qty}"></td>
   <td><input data-i="${i}" data-k="avg" value="${p.avg}"></td>
   <td><input data-i="${i}" data-k="price" value="${p.price}"></td>
   <td class="${pnl(p)>=0?'green':'red'}">${money(pnl(p))}<div>${pct(p).toFixed(1)}%</div></td>
   <td>${concentration(p).toFixed(1)}%</td>
   <td>${money(l.entry1)} / ${money(l.entry2)}</td>
   <td class="red">${money(l.stop)}</td><td>${money(l.t1)} / ${money(l.t2)}</td>
   <td class="action ${d.cls}">${d.label}</td>`;
   tbody.appendChild(tr);
 });
 $$('input[data-i]').forEach(el=>el.onchange=e=>{
   const i=+e.target.dataset.i,k=e.target.dataset.k;
   state.portfolio.positions[i][k]=+e.target.value; renderAll();
 });
}
function log(msg,cls=''){state.logs.push({msg,cls,time:new Date().toLocaleTimeString('ar-SA')});$('#log').innerHTML=state.logs.map(x=>`<div class="${x.cls}">[${x.time}] ${x.msg}</div>`).join('');$('#log').scrollTop=99999}
const managers=[
 ['CSRO','مدير البحث والاستراتيجية'],['CIO','مدير الاستثمار'],['CRO','مدير المخاطر'],
 ['COO','مدير الفرص'],['CCRO','مدير تدوير رأس المال'],['CPO','مدير المحافظ'],['CWO','مدير الثروة'],['CEO','الرئيس التنفيذي']
];
async function runBoard(){
 state.orders=[];state.logs=[];renderOrders(); $('#runBtn').disabled=true;
 for(let i=0;i<managers.length;i++){
   const [id,name]=managers[i], card=$(`[data-manager="${id}"]`);
   card.classList.add('running'); card.querySelector('.status').textContent='يعمل الآن';
   log(`${name}: بدأ التحليل...`,'cyan');
   await new Promise(r=>setTimeout(r,500));
   if(id==='CSRO') log('تم تصنيف الفرص إلى: لحظية، أسبوعية، شهرية، استراتيجية.');
   if(id==='CIO') log(`السيولة المتاحة ${money(state.portfolio.cash)}، وتم تقييم أفضل استخدام للدولار القادم.`);
   if(id==='CRO') {
     const high=state.portfolio.positions.sort((a,b)=>riskScore(b)-riskScore(a))[0];
     log(`أعلى مخاطرة حالية: ${high.symbol} بدرجة ${riskScore(high)}/100.`,'amber');
   }
   if(id==='COO') log('تمت مقارنة فرص النمو مع الدخل وDRIP والتدوير.');
   if(id==='CCRO') log('تم تحديد الأصول المرشحة لتحرير السيولة وإعادة توزيعها.');
   if(id==='CPO') log('تم تحديث متوسطات الدخول، مستويات الوقف، والأهداف لكل أصل.');
   if(id==='CWO') log('تم ربط القرارات بهدف الأسبوع وصندوق الثروة.');
   if(id==='CEO'){buildOrders();log('تم اعتماد الأوامر التنفيذية وإغلاق اجتماع المجلس.','green')}
   card.classList.remove('running');card.classList.add('done');card.querySelector('.status').textContent='اكتمل';
 }
 $('#runBtn').disabled=false; renderOrders();
}
function buildOrders(){
 const positions=state.portfolio.positions;
 const nxb=positions.find(x=>x.symbol==='NXB');
 const eu=positions.find(x=>x.symbol==='EU');
 const nxe=positions.find(x=>x.symbol==='NXE');
 const l=levels(nxe);
 state.orders=[
  {title:'NXB — تخفيف مرحلي مشروط',body:`بيع 200 سهم عند منطقة ${money(nxb.price*1.03)}–${money(nxb.price*1.08)}. السيولة المتوقعة ${money(200*nxb.price*1.05)}؛ 50% نمو، 30% Income/DRIP، 20% احتياطي.`},
  {title:'EU — منع زيادة التركّز',body:`المركز يمثل تقريبًا ${concentration(eu).toFixed(1)}% من إجمالي الأصول. لا زيادة جديدة قبل انخفاض التركّز أو تحسن العائد المعدل بالمخاطر.`},
  {title:'NXE — خطة بناء تدريجي',body:`منطقة الإضافة الأولى ${money(l.entry1)} والثانية ${money(l.entry2)}. وقف مرجعي ${money(l.stop)}. أهداف ${money(l.t1)} ثم ${money(l.t2)}. حجم التنفيذ لا يتجاوز 25% من السيولة الحالية لكل دفعة.`},
  {title:'السيولة — مهمة واضحة',body:`تخصيص مبدئي: 45% فرص نمو، 25% Income/DRIP، 30% احتياطي حتى تتأكد إشارة السوق.`}
 ];
}
function renderOrders(){
 $('#orders').innerHTML=state.orders.length?state.orders.map(o=>`<div class="order"><strong>${o.title}</strong><span class="muted">${o.body}</span></div>`).join(''):'<div class="notice">اضغط «تشغيل مجلس المديرين» لإنتاج أوامر تنفيذية من بيانات المحفظة.</div>';
}
function renderCapital(){
 const p=state.portfolio;
 $('#capitalBars').innerHTML=[
  ['فرص نمو',45],['Income & DRIP',25],['احتياطي سيولة',30]
 ].map(x=>`<div style="margin:11px 0"><div style="display:flex;justify-content:space-between"><span>${x[0]}</span><b>${money(p.cash*x[1]/100)}</b></div><div class="progress"><i style="width:${x[1]}%"></i></div></div>`).join('');
}
function exportJSON(){
 const blob=new Blob([JSON.stringify({portfolio:state.portfolio,orders:state.orders,logs:state.logs},null,2)],{type:'application/json'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='omega-session.json';a.click();
}
$$('nav button').forEach(b=>b.onclick=()=>{$$('nav button').forEach(x=>x.classList.remove('active'));b.classList.add('active');$$('.view').forEach(v=>v.classList.add('hidden'));$('#'+b.dataset.view).classList.remove('hidden')});
window.EMBEDDED_PORTFOLIO={"snapshot_date": "2026-07-11", "currency": "USD", "total_assets": 26920.81, "cash": 873.29, "weekly_target_sar": 5000, "positions": [{"symbol": "NXE", "name": "NexGen Energy", "qty": 250, "avg": 9.387, "price": 9.52, "role": "نمو/يورانيوم", "account": "Moomoo"}, {"symbol": "DNN", "name": "Denison Mines", "qty": 1000, "avg": 3.062, "price": 3.04, "role": "نمو/يورانيوم", "account": "Moomoo"}, {"symbol": "EU", "name": "enCore Energy", "qty": 10000, "avg": 1.391, "price": 1.36, "role": "استراتيجي/يورانيوم", "account": "Moomoo"}, {"symbol": "SPCX", "name": "SpaceX Private Shares", "qty": 20, "avg": 193.1225, "price": 193.1225, "role": "ثروة طويلة الأجل", "account": "Private"}, {"symbol": "NXB", "name": "NextBoat", "qty": 1200, "avg": 3.1, "price": 2.5563, "role": "تدوير/تخارج مرحلي", "account": "TradeStation"}]};
$('#runBtn').onclick=runBoard;$('#exportBtn').onclick=exportJSON;loadData();
