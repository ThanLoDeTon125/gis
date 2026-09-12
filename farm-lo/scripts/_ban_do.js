'use strict';
const D = window.__M, LO = D.lo, TH = D.thangs, IDS = Object.keys(LO).sort();
const [IW, IH] = D.geo.anh_px, M_NGANG = D.geo.m_ngang;

/* ── bảng dịch: thuật ngữ → tiếng người dùng ───────────────────────── */
const RAMP = ['#4a7d55','#40a165','#5ec077','#96dc95','#cdf0be'];
const BANDS = [
  {min:0.70, ten:'Rất xanh',   i:4, mo:'tán kín, cây phát triển mạnh'},
  {min:0.55, ten:'Xanh tốt',   i:3, mo:'cây phủ đều, sinh trưởng bình thường'},
  {min:0.40, ten:'Trung bình', i:2, mo:'cây phủ chưa kín mặt đất'},
  {min:0.25, ten:'Cây thưa',   i:1, mo:'ít lá xanh, có nhiều khoảng trống'},
  {min:-1,   ten:'Đất trống',  i:0, mo:'gần như không có cây'},
];
const band = v => v == null ? null : BANDS.find(b => v >= b.min);
const NHOM_MAU = {duoc_lieu:'var(--sm1)', ho_dau:'var(--sm2)', lau_nam:'var(--sm3)', vuon_uom:'var(--sm4)'};
const NHOM_TEN = {duoc_lieu:'Cây dược liệu', ho_dau:'Cây họ đậu luân canh',
                  lau_nam:'Cây lâu năm', vuon_uom:'Vườn ươm giống'};
const NHOM_IC  = {duoc_lieu:'i-la', ho_dau:'i-mam', lau_nam:'i-la', vuon_uom:'i-mam'};
const PHA = {ini:'Vừa xuống giống', dev:'Đang lớn', mid:'Đang sung sức', end:'Đang thu hoạch'};
const TT_LO = {da_giao:'Đã giao khách', da_niem_ho_so:'Đã chốt hồ sơ', cho_kiem_nghiem:'Chờ kiểm nghiệm',
               dang_dong_goi:'Đang đóng gói', dang_phan_loai:'Đang phân loại',
               dang_say:'Đang sấy', dang_thu_hoach:'Đang thu hoạch'};
const KQ = {xac_nhan:['ok','Ảnh vệ tinh xác nhận đúng'],
            xac_nhan_bang_radar:['ok','Ảnh radar xác nhận đúng'],
            can_nguoi_xac_minh:['bd','Cần người ra lô xác minh'],
            chua_ket_luan_duoc:['wr','Chưa đủ ảnh để kiểm'],
            khong_ap_dung:['nu','Vệ tinh không kiểm được việc này']};
const LUAT = {
  R1:{ten:'Thiếu nước', lam:'Tưới bù cho lô này. Chia 2–3 lần trong tuần, tưới sáng sớm hoặc chiều mát cho đỡ bốc hơi.'},
  R2:{ten:'Cây xuống đột ngột', lam:'Ra lô xem thực tế. Nếu đã thu hoạch hoặc phát dọn thì ghi bổ sung vào nhật ký để lần sau hệ thống không báo nữa.'},
  R3:{ten:'Mây che, không có ảnh', lam:'Không phải làm gì. Trời nhiều mây nên vệ tinh không chụp được ruộng; hệ thống tự cập nhật khi có ảnh mới.'},
  R4:{ten:'Kém hơn các lô khác', lam:'So lại đất, nước và giống của lô này với các lô bên cạnh. Kém đều nhiều tháng thường là do đất hoặc do tưới, không phải do thời tiết.'},
  R5:{ten:'Nhật ký không khớp ảnh', lam:'Đối chiếu lại phiếu cân và ảnh chụp của đợt thu này. Có thể chỉ thu một phần lô, cũng có thể ghi nhầm ngày.'},
  R6:{ten:'Nắng hạn kéo dài', lam:'Chuẩn bị nước tưới cho các lô đang ra hoa hoặc nuôi quả — đây là giai đoạn thiếu nước thiệt hại nặng nhất.'},
};
const MUC = {cao:['cao','Gấp'], trung_binh:['trung_binh','Cần chú ý'], thap:['thap','Ghi nhận']};
const THANG_VN = ['Tháng 1','Tháng 2','Tháng 3','Tháng 4','Tháng 5','Tháng 6',
                  'Tháng 7','Tháng 8','Tháng 9','Tháng 10','Tháng 11','Tháng 12'];

const fd = s => { const p = s.split('-'); return `${+p[2]}/${+p[1]}/${p[0]}`; };
const fdn = s => { const p = s.split('-'); return `${+p[2]}/${+p[1]}/${p[0].slice(2)}`; };
const nf = (v,d=1) => v == null ? '—' : v.toFixed(d).replace('.', ',');
// Câu cảnh báo do rule-engine sinh ra mang thuật ngữ kỹ thuật. Người vận hành HTX
// không đọc "NDVI" hay "quan trắc" — dịch trước khi hiện ra màn hình.
const TU_DIEN = [
  [/\bNDVI\b/g, 'độ xanh'], [/\bNDMI\b/g, 'độ ẩm lá'],
  [/quan trắc quang học|ảnh quang học|quang học/gi, 'ảnh vệ tinh thường'],
  [/lần quan trắc|quan trắc/gi, 'lần chụp ảnh'],
  [/thấp hơn mặt bằng farm ≥ [\d,.]+/gi, 'lô này xanh kém hơn mặt bằng chung của 12 lô'],
  [/mặt bằng farm|mặt bằng chung của farm/gi, 'mặt bằng chung 12 lô'],
  [/Lệch trung bình cả kỳ của lô này là/gi, 'Tính cả năm, lô này kém mặt bằng chung'],
  [/cả farm/gi, 'cả vùng trồng'], [/toàn farm/gi, 'toàn vùng trồng'],
  [/của lô này: /g, 'của lô này là '],
  [/ETc dồn/g, 'lượng nước cây cần'], [/mưa hiệu quả/g, 'lượng mưa thấm được'],
  [/\bET0\b/g, 'lượng bốc hơi'], [/Kc ([\d.,]+) cho /g, 'cho '],
  [/lượt radar Sentinel-1|ngày radar Sentinel-1/g, 'ngày có ảnh radar'],
  [/Sentinel-1|Sentinel-2/g, 'vệ tinh'],
  [/đủ để bám xu hướng/g, 'vẫn đủ để theo dõi'],
  [/chưa đủ để kết luận/g, 'chưa đủ để kết luận chắc'],
  [/tán giảm/g, 'lá cây giảm'],
];
function viet(x){
  let s = String(x ?? '');
  for (const [a,b] of TU_DIEN) s = s.replace(a,b);
  s = s.replace(/(\d{4})-(\d{2})-(\d{2})/g, (_,y,m,d) => `${+d}/${+m}/${y}`);
  s = s.replace(/(\d)\.(\d)/g, '$1,$2');
  return s;
}
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const ic = (n,st='') => `<svg class="ic" ${st?`style="${st}"`:''}><use href="#${n}"/></svg>`;
const svgNS = 'http://www.w3.org/2000/svg';
const mk = (t,a) => { const e = document.createElementNS(svgNS,t); for (const k in a) e.setAttribute(k,a[k]); return e; };

let LAYER = 'ndvi', MI = TH.length - 1, SEL = null, timer = null, hinted = false;

/* ═══ Bản đồ ═══════════════════════════════════════════════════════ */
const wrap = document.getElementById('mapwrap'), stage = document.getElementById('stage');
const ov = document.getElementById('ov'), tip = document.getElementById('tip');
let z = 1, zBase = 1, tx = 0, ty = 0;

function build(){
  ov.setAttribute('viewBox', `0 0 ${IW} ${IH}`);
  IDS.forEach(id => {
    const pts = D.geo.poly[id].map(([a,b]) => `${(a/100*IW).toFixed(1)},${(b/100*IH).toFixed(1)}`).join(' ');
    const p = mk('polygon', {points:pts, class:'plot', 'data-id':id, tabindex:'0', role:'button',
      'vector-effect':'non-scaling-stroke', 'aria-label':`Lô ${id}, ${LO[id].ten}`});
    ov.appendChild(p);
    const c = D.geo.poly[id];
    const cx = c.reduce((s,q)=>s+q[0],0)/c.length/100*IW, cy = c.reduce((s,q)=>s+q[1],0)/c.length/100*IH;
    ov.appendChild(Object.assign(mk('text',{x:cx.toFixed(1), y:(cy+4).toFixed(1), class:'lbl'}),
      {textContent:id}));
  });
}
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function fillFor(id, t){
  const m = LO[id].thang[t];
  if (LAYER === 'anh') return [null, 0];
  if (LAYER === 'ndvi'){ const b = band(m.ndvi);
    return b ? [RAMP[b.i], m.src === 'noi_suy' ? .36 : .6] : ['#7b8271', .3]; }
  if (LAYER === 'cay') return m.nhom ? [cssv(NHOM_MAU[m.nhom].slice(4,-1)), .6] : ['#7b8271', .22];
  const n = LO[id].canh_bao.filter(c => c.ngay.slice(0,7) === t);
  const w = n.some(c=>c.muc==='cao') ? '--crit' : n.some(c=>c.muc==='trung_binh') ? '--serious' : n.length ? '--warn' : null;
  return w ? [cssv(w), .62] : ['#7b8271', .14];
}
function paint(){
  const t = TH[MI];
  IDS.forEach(id => {
    const p = ov.querySelector(`polygon[data-id="${id}"]`), [f,o] = fillFor(id,t);
    p.setAttribute('fill', f || 'none'); p.setAttribute('fill-opacity', o);
    const s = SEL === id;
    p.setAttribute('stroke', s ? '#ffc94d' : 'rgba(255,255,255,.88)');
    p.setAttribute('stroke-width', s ? '4' : '1.5');
    p.style.filter = s ? 'drop-shadow(0 0 4px rgba(0,0,0,.9))' : '';
  });
  const [y,mo] = t.split('-');
  document.getElementById('tm-b').textContent = THANG_VN[+mo-1];
  document.getElementById('tm-i').textContent = y;
  const k = D.khi_hau[t];
  document.getElementById('wx').innerHTML = k ? `
    <span>${ic('i-mua')} ${nf(k.mua)} mm · ${k.ngay_mua} ngày</span>
    <span>${ic('i-nhiet')} ${nf(k.tmin)}–${nf(k.tmax)} °C</span>` : '';
  legend(); SEL ? detail(SEL) : overview();
  updateTimeTicks();
}
function applyT(){
  stage.style.transform = `translate(${tx}px,${ty}px) scale(${z})`;
  const fs = 14/z, sw = 3.2/z;
  ov.querySelectorAll('.lbl').forEach(e => { e.style.fontSize = fs+'px'; e.style.strokeWidth = sw+'px'; });
  const mpp = M_NGANG/(IW*z), nice = [10,20,25,50,100,150,200,300]
    .reduce((a,b) => Math.abs(b-120*mpp) < Math.abs(a-120*mpp) ? b : a);
  document.getElementById('sb-b').style.width = (nice/mpp).toFixed(0)+'px';
  document.getElementById('sb-t').textContent = nice+' m';
}
function fit(){ const w = wrap.clientWidth, h = wrap.clientHeight;
  zBase = z = Math.max(w/IW, h/IH); stage.style.width = IW+'px';
  tx = (w-IW*z)/2; ty = (h-IH*z)/2; applyT(); }
function clamp(){ const w = wrap.clientWidth, h = wrap.clientHeight, dw = IW*z, dh = IH*z;
  tx = dw<=w ? (w-dw)/2 : Math.min(0, Math.max(w-dw, tx));
  ty = dh<=h ? (h-dh)/2 : Math.min(0, Math.max(h-dh, ty)); }
function zoomAt(cx,cy,f){ const nz = Math.min(zBase*6, Math.max(zBase, z*f)); if (nz===z) return;
  tx = cx-(cx-tx)*(nz/z); ty = cy-(cy-ty)*(nz/z); z = nz; clamp(); applyT(); }

wrap.addEventListener('wheel', e => { e.preventDefault(); const r = wrap.getBoundingClientRect();
  zoomAt(e.clientX-r.left, e.clientY-r.top, e.deltaY<0 ? 1.18 : 1/1.18); }, {passive:false});
let drag = false, sx = 0, sy = 0, mv = 0;
wrap.addEventListener('pointerdown', e => { drag = true; mv = 0; sx = e.clientX-tx; sy = e.clientY-ty;
  wrap.classList.add('drag'); wrap.setPointerCapture(e.pointerId); });
wrap.addEventListener('pointermove', e => { if (!drag) return;
  mv += Math.abs(e.clientX-tx-sx)+Math.abs(e.clientY-ty-sy);
  tx = e.clientX-sx; ty = e.clientY-sy; clamp(); applyT(); });
wrap.addEventListener('pointerup', e => { drag = false; wrap.classList.remove('drag');
  if (mv < 5 && e.target.tagName !== 'polygon') select(null); });
document.getElementById('zin').onclick = () => zoomAt(wrap.clientWidth/2, wrap.clientHeight/2, 1.45);
document.getElementById('zout').onclick = () => zoomAt(wrap.clientWidth/2, wrap.clientHeight/2, 1/1.45);
document.getElementById('zfit').onclick = fit;

ov.addEventListener('pointerover', e => { if (e.target.tagName!=='polygon') return;
  const id = e.target.dataset.id, L = LO[id], m = L.thang[TH[MI]], b = band(m.ndvi);
  tip.innerHTML = `<b>${id} · ${esc(L.ten)}</b><div class="s">${esc(m.cay)}${m.pha?' · '+PHA[m.pha]:''}<br>
    Độ xanh ${nf(m.ndvi,2)} — ${b?b.ten.toLowerCase():'chưa có ảnh'} · ${nf(L.ha,2)} ha</div>`;
  tip.style.opacity = 1; });
ov.addEventListener('pointermove', e => { const r = wrap.getBoundingClientRect();
  const x = e.clientX-r.left, y = e.clientY-r.top;
  tip.style.left = Math.max(8, Math.min(r.width-tip.offsetWidth-8, x+16))+'px';
  tip.style.top = Math.max(8, y-tip.offsetHeight-12)+'px'; });
ov.addEventListener('pointerout', () => tip.style.opacity = 0);
ov.addEventListener('click', e => { if (e.target.tagName==='polygon') select(e.target.dataset.id); });
ov.addEventListener('keydown', e => { if ((e.key==='Enter'||e.key===' ') && e.target.tagName==='polygon'){
  e.preventDefault(); select(e.target.dataset.id); }});

/* ═══ Chú giải ═════════════════════════════════════════════════════ */
function legend(){
  const L = document.getElementById('legend');
  if (LAYER === 'ndvi') L.innerHTML = `<h4>Độ xanh của cây · ${THANG_VN[+TH[MI].slice(5)-1].toLowerCase()}</h4>
    <div class="lg-ramp">${RAMP.map(c=>`<i style="background:${c}"></i>`).join('')}</div>
    <div class="lg-lbl"><span>Đất trống</span><span>Tán kín</span></div>
    <div class="lg-row" style="margin-top:7px"><span class="sw" style="background:#7b8271"></span>tháng này không có ảnh</div>`;
  else if (LAYER === 'cay') L.innerHTML = `<h4>Loại cây đang trồng</h4>` +
    Object.keys(NHOM_TEN).map(k=>`<div class="lg-row"><span class="sw" style="background:${NHOM_MAU[k]}"></span>${NHOM_TEN[k]}</div>`).join('') +
    `<div class="lg-row"><span class="sw" style="background:#7b8271;opacity:.4"></span>đất nghỉ hoặc công trình</div>`;
  else if (LAYER === 'canh_bao') L.innerHTML = `<h4>Lô cần chú ý trong tháng</h4>
    <div class="lg-row"><span class="sw" style="background:var(--crit)"></span>gấp — nên xử lý ngay</div>
    <div class="lg-row"><span class="sw" style="background:var(--serious)"></span>cần chú ý</div>
    <div class="lg-row"><span class="sw" style="background:var(--warn)"></span>chỉ ghi nhận</div>
    <div class="lg-row"><span class="sw" style="background:#7b8271;opacity:.35"></span>không có gì</div>`;
  else L.innerHTML = `<h4>Ảnh vệ tinh gốc</h4><div class="lg-row">Bỏ màu, chỉ giữ đường ranh 12 lô.</div>`;
}

/* ═══ Tình trạng lô, viết bằng tiếng thường ════════════════════════ */
function tinhTrang(id, t){
  const L = LO[id], m = L.thang[t], i = TH.indexOf(t);
  const truoc = i > 0 ? L.thang[TH[i-1]].ndvi : null;
  const dl = (m.ndvi != null && truoc != null) ? m.ndvi - truoc : null;
  const cbT = L.canh_bao.filter(c => c.ngay.slice(0,7) === t);
  const gap = cbT.filter(c => c.muc === 'cao');
  if (L.muc_dich === 'cong_trinh')
    return {c:'nu', i:'i-hop', t:'Khu công trình', d:'Nhà lưới, sân phơi và kho — lô này không canh tác.', dl};
  if (gap.length)
    return {c:'bd2', i:'i-canhbao', t:'Cần ra lô kiểm tra',
            d:`${gap.length} việc gấp trong tháng: ${gap.map(g=>LUAT[g.luat].ten.toLowerCase()).join(', ')}.`, dl};
  if (m.thieu >= 40)
    return {c:'wr', i:'i-nuoc', t:'Đang thiếu nước',
            d:`Cây cần thêm khoảng ${nf(m.thieu,0)} mm nước trong tháng này, tương đương ${nf(m.tuoi,0)} m³ cho cả lô.`, dl};
  if (m.pha === 'end')
    return {c:'ok', i:'i-keo', t:'Đang thu hoạch', d:`Đang trong đợt thu ${esc(m.cay.toLowerCase())}.`, dl};
  if (m.pha === 'ini')
    return {c:'ok', i:'i-mam', t:'Vừa xuống giống', d:`Cây mới trồng, chưa phủ kín mặt đất là bình thường.`, dl};
  if (dl != null && dl > 0.06)
    return {c:'ok', i:'i-tang', t:'Cây đang lên xanh', d:`Độ xanh tăng ${nf(dl,2)} so với tháng trước.`, dl};
  if (dl != null && dl < -0.06)
    return {c:'wr', i:'i-giam', t:'Cây đang xuống',
            d:`Độ xanh giảm ${nf(Math.abs(dl),2)} so với tháng trước. Nếu không phải do thu hoạch thì nên ra lô xem.`, dl};
  if (!m.vu)
    return {c:'nu', i:'i-lich', t:'Đất đang nghỉ', d:'Giữa hai vụ, chưa xuống giống lại.', dl};
  return {c:'ok', i:'i-ok', t:'Bình thường', d:'Không có gì bất thường trong tháng này.', dl};
}

/* ═══ Hình vẽ nhỏ ══════════════════════════════════════════════════ */
function shape(id, s=46){
  const c = D.geo.poly[id];
  const xs = c.map(p=>p[0]), ys = c.map(p=>p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const k = Math.max(x1-x0, y1-y0) || 1, pad = s*0.16;
  const pts = c.map(([a,b]) => `${(pad+(a-x0)/k*(s-2*pad)).toFixed(1)},${(pad+(b-y0)/k*(s-2*pad)).toFixed(1)}`).join(' ');
  return `<svg class="shape" viewBox="0 0 ${s} ${s}" aria-hidden="true"><polygon points="${pts}"
    fill="var(--accent)" fill-opacity=".18" stroke="var(--accent)" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
}
function bandInfo(v) {
  if (v >= 0.7) return 'Rất xanh';
  if (v >= 0.55) return 'Xanh tốt';
  if (v >= 0.4) return 'Trung bình';
  if (v >= 0.25) return 'Thưa thớt';
  return 'Đất trống / nghỉ';
}
function chart(id){
  const L = LO[id], W = 380, H = 118, pl = 26, pr = 8, pt = 10, pb = 20;
  const x = i => pl + i/(TH.length-1)*(W-pl-pr);
  const y = v => pt + (1-(v-0.1)/0.85)*(H-pt-pb);
  const vals = TH.map(t => L.thang[t]);
  let d = '', open = false;
  vals.forEach((m,i) => { if (m.ndvi == null){ open = false; return; }
    d += (open?'L':'M') + x(i).toFixed(1) + ',' + y(m.ndvi).toFixed(1); open = true; });
  const bands = [[0.70,0.95,4],[0.55,0.70,3],[0.40,0.55,2],[0.25,0.40,1],[0.10,0.25,0]];
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img"
      aria-label="Độ xanh của lô ${id} qua 13 tháng">
    ${bands.map(([a,b,i]) => `<rect x="${pl}" y="${y(b).toFixed(1)}" width="${W-pl-pr}"
      height="${(y(a)-y(b)).toFixed(1)}" fill="${RAMP[i]}" opacity=".1"/>`).join('')}
    ${[0.25,0.55,0.85].map(v=>`<text x="${pl-5}" y="${(y(v)+3.5).toFixed(1)}" font-size="9"
      fill="var(--muted)" text-anchor="end" font-family="var(--f-m)">${nf(v,2)}</text>`).join('')}
    ${L.vu.flatMap(v => { const a = TH.indexOf(v.thu_tu.slice(0,7)), b = TH.indexOf(v.thu_den.slice(0,7));
      return (a<0&&b<0) ? [] : [`<rect x="${x(Math.max(0,a)).toFixed(1)}" y="${pt}"
        width="${Math.max(4,(x(b<0?TH.length-1:b)-x(Math.max(0,a)))).toFixed(1)}" height="${H-pt-pb}"
        fill="var(--accent)" opacity=".1"/>`]; }).join('')}
    <line x1="${x(MI).toFixed(1)}" y1="${pt}" x2="${x(MI).toFixed(1)}" y2="${H-pb}"
      stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="3 3"/>
    <path d="${d}" fill="none" stroke="var(--ink)" stroke-width="2" stroke-linejoin="round" opacity=".75"/>
    ${vals.map((m,i) => m.ndvi==null ? '' : `<circle class="chart-node" data-month="${TH[i]}" data-val="${nf(m.ndvi,3)}" data-band="${bandInfo(m.ndvi)}" data-src="${m.src==='noi_suy'?'Nối suy':'Vệ tinh'}" cx="${x(i).toFixed(1)}" cy="${y(m.ndvi).toFixed(1)}"
      r="${m.src==='noi_suy'?2.6:3.6}" fill="${m.src==='noi_suy'?'var(--panel)':'var(--ink)'}"
      stroke="var(--ink)" stroke-width="1.6"/>`).join('')}
    ${vals[MI].ndvi!=null ? `<circle cx="${x(MI).toFixed(1)}" cy="${y(vals[MI].ndvi).toFixed(1)}" r="6"
      fill="var(--accent)" stroke="var(--card)" stroke-width="2.5"/>` : ''}
    ${TH.map((t,i) => i%2===0 ? `<text x="${x(i).toFixed(1)}" y="${H-5}" font-size="9" fill="var(--muted)"
      text-anchor="middle" font-family="var(--f-m)">${+t.slice(5)}</text>` : '').join('')}
  </svg>`;
}

/* ═══ Bảng bên: toàn farm ══════════════════════════════════════════ */
function overview(){
  const t = TH[MI], k = D.khi_hau[t];
  const tong = IDS.reduce((a,i)=>a+LO[i].ha,0);
  const trong = IDS.filter(i => LO[i].thang[t].vu).length;
  const chuY = IDS.filter(i => LO[i].canh_bao.some(c => c.ngay.slice(0,7)===t));
  const gap = IDS.filter(i => LO[i].canh_bao.some(c => c.ngay.slice(0,7)===t && c.muc==='cao'));
  document.getElementById('ph').innerHTML = `
    <div class="kicker"><span>Toàn hợp tác xã</span></div>
    <div class="row"><div><h2>Tất cả 12 lô</h2>
      <div class="sub">${THANG_VN[+t.slice(5)-1]} ${t.slice(0,4)} · Trường Yên, Hoa Lư, Ninh Bình</div></div></div>`;
  document.getElementById('pb').innerHTML = `
    <div class="sec"><div class="card hero ${gap.length?'bd2':chuY.length?'wr':'ok'}">
      <span class="ico">${ic(gap.length||chuY.length?'i-canhbao':'i-ok')}</span>
      <div><b>${gap.length ? `${gap.length} lô cần xử lý gấp`
                : chuY.length ? `${chuY.length} lô cần chú ý` : 'Không có lô nào cần chú ý'}</b>
        <p>${gap.length ? 'Bấm vào lô có viền đỏ trên bản đồ để xem nên làm gì.'
             : chuY.length ? `Lô ${chuY.join(', ')} có ghi nhận trong tháng này.`
             : 'Cả 12 lô đều bình thường trong tháng này.'}</p></div></div></div>

    <div class="sec"><div class="stats">
      <div class="stat"><div class="v">${trong}<u>/12 lô</u></div><div class="k">Đang canh tác</div></div>
      <div class="stat"><div class="v">${nf(tong,2)}<u>ha</u></div><div class="k">Tổng diện tích</div></div>
      <div class="stat"><div class="v">${nf(k.mua,0)}<u>mm</u></div><div class="k">Mưa trong tháng · ${k.ngay_mua} ngày</div></div>
      <div class="stat ${chuY.length?'al':''}"><div class="v">${IDS.reduce((a,i)=>a+LO[i].canh_bao.filter(c=>c.ngay.slice(0,7)===t).length,0)}</div>
        <div class="k">Việc ghi nhận trong tháng</div></div>
    </div></div>

    <div class="sec"><h3>${ic('i-lop')} Danh sách lô — bấm để xem chi tiết</h3>
      <div class="lots">${IDS.map(id => { const L = LO[id], m = L.thang[t], b = band(m.ndvi);
        const n = L.canh_bao.filter(c=>c.ngay.slice(0,7)===t);
        const g = n.some(c=>c.muc==='cao');
        const st = tinhTrang(id,t);
        const col = st.c==='bd2'?'var(--crit)':st.c==='wr'?'var(--serious)':st.c==='nu'?'var(--line-2)':'var(--good)';
        return `<button class="lot" data-go="${id}">
          <span class="stripe" style="background:${col}"></span>
          <span class="id">${id}</span>
          <span class="nm"><b>${esc(m.cay)}</b><i>${esc(L.ten)} · ${nf(L.ha,2)} ha</i></span>
          <span class="rt">${n.length?`<span class="badge">${ic('i-canhbao')}${n.length}</span>`:''}
            <span class="xn"><b>${nf(m.ndvi,2)}</b><i>${b?b.ten.toLowerCase():'—'}</i></span></span>
        </button>`; }).join('')}</div></div>

    <div class="sec"><div class="note">${ic('i-cham')}<div>
      <b>Loại cây và nhật ký là dữ liệu dựng để xem thử.</b> Ranh giới lô, độ xanh, mưa và nhiệt độ
      thì là số đo thật từ vệ tinh. Bấm <b>Hướng dẫn</b> ở góc trên để xem chi tiết cái gì thật,
      cái gì mô phỏng.</div></div></div>`;
  bind();
}

/* ═══ Bảng bên: một lô ═════════════════════════════════════════════ */
let showAllCb = false, showAllNk = false, showAllLh = false;
function detail(id){
  const L = LO[id], t = TH[MI], m = L.thang[t], b = band(m.ndvi);
  const vu = L.vu.find(v => v.id === m.vu);
  const st = tinhTrang(id, t);
  const cbT = L.canh_bao.filter(c => c.ngay.slice(0,7) === t);
  const cbHien = showAllCb ? L.canh_bao : (cbT.length ? cbT : L.canh_bao.slice(0,2));
  const nkHien = showAllNk ? L.nhat_ky : L.nhat_ky.slice(0,5);
  const lhHien = showAllLh ? L.lo_hang : L.lo_hang.slice(0,4);
  const hue = m.nhom ? NHOM_MAU[m.nhom] : 'var(--muted)';

  document.getElementById('ph').innerHTML = `
    <div class="kicker"><span>Lô ${id} · ${THANG_VN[+t.slice(5)-1].toLowerCase()} ${t.slice(0,4)}</span>
      <button class="x" id="pc">${ic('i-ve')} Tất cả lô</button></div>
    <div class="row">${shape(id)}<div><h2>${esc(L.ten)}</h2>
      <div class="sub">${nf(L.ha,4)} ha · chu vi ${nf(L.chu_vi,0)} m · cao ${nf(L.cao)} m · dốc ${nf(L.doc,2)}°</div></div></div>`;
  document.getElementById('pc').onclick = () => select(null);

  const dl = st.dl;
  const mui = dl == null ? 'i-ngang' : dl > 0.02 ? 'i-tang' : dl < -0.02 ? 'i-giam' : 'i-ngang';
  const mut = dl == null ? 'chưa so được với tháng trước'
    : Math.abs(dl) < 0.02 ? 'gần như không đổi so với tháng trước'
    : `${dl>0?'tăng':'giảm'} ${nf(Math.abs(dl),2)} so với tháng trước`;

  document.getElementById('pb').innerHTML = `
    <div class="sec"><div class="card hero ${st.c}">
      <span class="ico">${ic(st.i)}</span>
      <div><b>${st.t}</b><p>${st.d}</p></div></div></div>

    <div class="sec"><h3>${ic('i-mam')} Đang trồng gì</h3>
      <div class="card crop" style="--cr:${hue}">
        <span class="dot">${ic(m.nhom?NHOM_IC[m.nhom]:'i-lich')}</span>
        <span><b>${esc(m.cay)}</b><i>${m.pha ? PHA[m.pha]
          : L.muc_dich==='cong_trinh' ? 'Không canh tác' : 'Đất nghỉ giữa hai vụ'}</i></span>
      </div>
      ${vu ? `<div class="card crop-meta" style="border-left:0;margin-top:-1px;border-radius:0 0 var(--r) var(--r)">
        <div><span>Ngày xuống giống</span><b>${fd(vu.gieo)}</b></div>
        <div><span>Dự kiến thu</span><b>${fdn(vu.thu_tu)} – ${fdn(vu.thu_den)}</b></div>
        <div><span>Chiếm bao nhiêu lô</span><b>${Math.round(vu.ti_le*100)} %</b></div>
        ${vu.kho_tan > 0 ? `<div><span>${vu.cay==='CHA'?'Quả tươi dự kiến':'Sản lượng khô dự kiến'}</span>
          <b>${Math.round(vu.kho_tan*1000).toLocaleString('vi-VN')} kg</b></div>`
        : `<div><span>Mục đích</span><b>${vu.cay==='DAU'?'Cày vùi làm phân xanh':'Xuất cây giống'}</b></div>`}
      </div>` : ''}</div>

    <div class="sec"><h3>${ic('i-la')} Cây xanh tới đâu</h3>
      <div class="card xanh">
        <div class="big">${nf(m.ndvi,2)}</div>
        <div class="band" style="color:${b?RAMP[Math.max(1,b.i)]:'var(--muted)'}">${b?b.ten:'Chưa có ảnh'}</div>
        <div class="cmp">${ic(mui)} ${mut}</div>
        <div class="ramp5">${RAMP.map((c,i)=>`<i style="background:${c};color:${c}" class="${b&&b.i===i?'on':''}"></i>`).join('')}</div>
        <div class="ramp5x">${['Trống','Thưa','Vừa','Tốt','Rậm'].map(x=>`<span>${x}</span>`).join('')}</div>
        ${b?`<div class="cmp" style="margin-top:9px;color:var(--muted)">${b.mo}</div>`:''}
      </div>
      <div class="card" style="margin-top:9px;padding:8px 10px 4px">${chart(id)}
        <div class="cmp" style="font-size:11.5px;color:var(--muted);margin:0 0 8px">
          Vệt hồng = các đợt thu hoạch · vòng tròn rỗng = tháng không có ảnh, giá trị suy ra từ hai tháng kề</div></div>
    </div>

    <div class="sec"><h3>${ic('i-nuoc')} Nước trong tháng</h3>
      <div class="card water">
        ${[['Cây cần', m.etc, 'var(--sm3)'], ['Mưa cho được', m.mua_hq, 'var(--sm2)'],
           ['Phải tưới bù', m.thieu, m.thieu>0?'var(--crit)':'var(--line-2)']].map(([lb,v,c]) =>
          `<div class="wrow"><span class="lb">${lb}</span>
            <span class="tr"><i style="width:${Math.min(100,(v||0)/Math.max(1,m.etc,m.mua_hq)*100)}%;background:${c}"></i></span>
            <span class="nm">${nf(v,0)} mm</span></div>`).join('')}
        ${m.thieu>0 ? `<div class="cmp" style="justify-content:flex-start;color:var(--ink-2);margin-top:2px">
          ${ic('i-nuoc')} Tương đương <b style="margin:0 3px">${Math.round(m.tuoi).toLocaleString('vi-VN')} m³</b> nước cho cả lô.</div>` : ''}
      </div></div>

    <div class="sec"><h3>${ic('i-mat')} Số đo khác của tháng này</h3>
      <div class="kv">
        <div><div class="k">Độ ẩm trong lá <span class="q" title="Lá còn mọng nước hay đã bắt đầu héo. Báo thiếu nước sớm hơn độ xanh vài tuần. Tên khoa học: NDMI.">?</span></div>
          <div class="v">${nf(m.ndmi,2)}</div></div>
        <div><div class="k">Mặt đất được cây che</div><div class="v">${nf(m.che_phu,0)}<u>%</u></div></div>
        <div><div class="k">Nhiệt mặt đất <span class="q" title="Ước tính nhiệt ngay trên mặt ruộng lúc nắng gắt nhất — không phải số đo.">?</span></div>
          <div class="v">${nf(m.lst)}<u>°C</u></div></div>
        <div><div class="k">Số ngày có ảnh <span class="q" title="Ngày trời quang, vệ tinh chụp được ruộng. Ngày nhiều mây thì không có.">?</span></div>
          <div class="v">${m.anh}</div></div>
      </div></div>

    ${cbHien.length ? `<div class="sec"><h3>${ic('i-canhbao')} Cần chú ý${cbT.length?` · ${cbT.length} việc trong tháng`:''}</h3>
      ${cbHien.map(c => `<div class="al-item ${c.muc}">
        <div class="hd"><span class="t">${LUAT[c.luat].ten}</span><span class="dt">${fd(c.ngay)}</span></div>
        <div class="ds">${esc(viet(c.tieu_de))}.<br><span style="color:var(--muted)">${esc(viet(c.chi_tiet))}</span></div>
        <div class="do">${ic('i-tay')}<span>${LUAT[c.luat].lam}</span></div></div>`).join('')}
      ${L.canh_bao.length > cbHien.length ? `<button class="more" data-t="cb">Xem cả ${L.canh_bao.length} ghi nhận của lô này</button>` : ''}
    </div>` : ''}

    ${L.doi_chieu.length ? `<div class="sec"><h3>${ic('i-ok')} Vệ tinh có xác nhận đợt thu không</h3>
      ${L.doi_chieu.map(d => { const [c,l] = KQ[d.kq];
        return `<div class="al-item ${c==='ok'?'thap':c==='bd'?'cao':'trung_binh'}"
            style="border-left-color:${c==='ok'?'var(--good)':c==='bd'?'var(--crit)':c==='nu'?'var(--line-2)':'var(--serious)'}">
          <div class="hd"><span class="t">${esc(d.cay||'—')} · ${fdn(d.tu)}–${fdn(d.den)}</span></div>
          <div class="ds">${l}.${d.sut!=null?` Sau đợt thu, độ xanh ${d.sut<0?'giảm':'tăng'} ${nf(Math.abs(d.sut),2)}.`:''}</div></div>`;
      }).join('')}
      <div class="note" style="margin-top:9px">${ic('i-cham')}<div>Hệ thống so ngày thu hoạch ghi trong
        nhật ký với ảnh vệ tinh. Thu hoạch thật thì tán cây phải giảm — nếu ảnh không thấy giảm,
        có thể chỉ thu một phần lô, hoặc ghi nhầm ngày.</div></div>
    </div>` : ''}

    ${lhHien.length ? `<div class="sec"><h3>${ic('i-hop')} Lô hàng đã ra từ lô đất này · ${L.lo_hang.length}</h3>
      <ul class="tl">${lhHien.map(x => `<li>
        <span class="bul">${ic('i-hop')}</span>
        <div class="hd"><span class="t">${nf(x.tuoi,0)} kg tươi${x.kho?` → ${nf(x.kho,0)} kg khô`:''}</span>
          <span class="dt">${fdn(x.tu)}–${fdn(x.den)}</span></div>
        <div class="ds">${esc(x.cay)} · ${TT_LO[x.tt]||x.tt}${x.bich?` · ${x.bich.toLocaleString('vi')} bịch 20 g`:''}</div>
        <div class="ev"><i>${x.id}</i>${x.ndvi_hai!=null?`<i>độ xanh lúc hái ${nf(x.ndvi_hai,2)}</i>`:''}<i>cả vụ ${nf(x.mua_vu,0)} mm mưa</i></div>
      </li>`).join('')}</ul>
      ${L.lo_hang.length > lhHien.length ? `<button class="more" data-t="lh">Xem cả ${L.lo_hang.length} lô hàng</button>` : ''}
    </div>` : ''}

    ${nkHien.length ? `<div class="sec"><h3>${ic('i-lich')} Nhật ký đồng ruộng</h3>
      <ul class="tl">${nkHien.map(r => `<li><span class="bul">${ic('i-'+r.icon)}</span>
        <div class="hd"><span class="t">${esc(r.viec)}</span><span class="dt">${fd(r.ngay)}</span></div>
        <div class="ds">${esc(r.mo_ta)}</div>
        <div class="ev"><i>${esc(r.nguoi)}</i>${r.bang_chung.map(x=>`<i>${esc(x)}</i>`).join('')}</div></li>`).join('')}</ul>
      ${L.nhat_ky.length > nkHien.length ? `<button class="more" data-t="nk">Xem thêm ${L.nhat_ky.length-nkHien.length} việc nữa</button>` : ''}
    </div>` : ''}

    <div class="sec"><h3>${ic('i-cham')} Vì sao biết lô này trồng cây đó</h3>
      <details><summary>Căn cứ từ ảnh vệ tinh <span class="ch">${ic('i-xuong')}</span></summary>
        <div class="dc"><p>${esc(L.mo_ta)}</p><ul>${L.can_cu.map(c=>`<li>${esc(c)}</li>`).join('')}</ul>
        <p style="color:var(--muted);margin:9px 0 0">Máy tự phân loại lô này là: ${esc(L.phan_loai)}</p></div></details>
      <details><summary>Cả năm lô này thế nào <span class="ch">${ic('i-xuong')}</span></summary>
        <div class="dc"><p>Độ xanh trung bình cả năm <b>${nf(L.ndvi_tb,2)}</b>, thấp nhất
        ${nf(L.ndvi_min,2)}, cao nhất ${nf(L.ndvi_max,2)}. Mùa khô ${nf(L.kho,2)} so với mùa mưa ${nf(L.mua,2)}.</p>
        <p>So với mặt bằng chung 12 lô, lô này ${L.lech<0?'kém hơn':'hơn'} <b>${nf(Math.abs(L.lech),2)}</b>.
        Cả kỳ có ${L.ngay_quang} ngày chụp được ảnh thường và ${L.ngay_radar} ngày ảnh radar.</p></div></details>
      <details><summary>Diện tích đo lại ra sao <span class="ch">${ic('i-xuong')}</span></summary>
        <div class="dc"><p>Chủ farm vẽ tay ranh giới lô này ra ${nf(L.dt_ve_tay,4)} ha. Sau khi nắn lại
        theo mép thửa nhìn thấy trên ảnh vệ tinh thì còn <b>${nf(L.ha,4)} ha</b> —
        chênh ${L.chenh_dt>0?'+':''}${nf(L.chenh_dt)} %.</p>
        <p style="color:var(--muted)">Sai số ranh giới khoảng ±2,9 m. Không dùng con số này cho hồ sơ địa chính.</p></div></details>
    </div>`;
  bind();
}
function bind(){
  document.querySelectorAll('[data-go]').forEach(e => e.onclick = () => select(e.dataset.go));
  document.querySelectorAll('[data-t]').forEach(e => e.onclick = () => {
    if (e.dataset.t === 'cb') showAllCb = true;
    if (e.dataset.t === 'nk') showAllNk = true;
    if (e.dataset.t === 'lh') showAllLh = true;
    detail(SEL); });
}
function select(id, quiet){
  SEL = id; showAllCb = showAllNk = showAllLh = false;
  if (!quiet) history.replaceState(null, '', location.pathname + location.search + (id ? '#'+id : ''));
  paint();
  const panel = document.getElementById('panel');
  panel.scrollTop = 0;
  if (id && matchMedia('(max-width:480px)').matches){
    panel.classList.remove('peek');
  }
  if (id) ov.querySelector(`polygon[data-id="${id}"]`)?.focus({preventScroll:true});
  if (!hinted){ hinted = true; document.getElementById('hint').style.opacity = 0; }
}

/* ═══ Điều khiển ═══════════════════════════════════════════════════ */
document.querySelectorAll('#layers button').forEach(b => b.onclick = () => {
  LAYER = b.dataset.l;
  document.querySelectorAll('#layers button').forEach(x => x.setAttribute('aria-pressed', x===b));
  paint(); });
const sl = document.getElementById('slider');
sl.max = TH.length-1; sl.value = MI;
sl.oninput = () => { MI = +sl.value; paint(); };
document.getElementById('play').onclick = e => {
  const btn = e.currentTarget;
  if (timer){ clearInterval(timer); timer = null; btn.innerHTML = ic('i-chay'); return; }
  btn.innerHTML = ic('i-dung');
  timer = setInterval(() => { MI = (MI+1) % TH.length; sl.value = MI; paint(); }, 950); };
addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'Escape'){ if (help.hasAttribute('open')) closeHelp(); else select(null); }
  if (e.key === 'ArrowLeft' && MI > 0){ MI--; sl.value = MI; paint(); }
  if (e.key === 'ArrowRight' && MI < TH.length-1){ MI++; sl.value = MI; paint(); } });

const help = document.getElementById('help');
const openHelp = () => { help.setAttribute('open',''); document.getElementById('help-close').focus(); };
const closeHelp = () => { help.removeAttribute('open'); document.getElementById('help-open').focus(); };
document.getElementById('help-open').onclick = openHelp;
document.getElementById('help-close').onclick = closeHelp;
help.onclick = e => { if (e.target === help) closeHelp(); };

build(); fit();

function buildTimeTicks() {
  const container = document.getElementById('time-ticks');
  if (!container) return;
  container.innerHTML = TH.map((t, i) => {
    const label = t.endsWith('-01') ? `T1/${t.slice(2,4)}` : `T${+t.slice(5)}`;
    return `<span class="tick ${i===MI?'active':''}" data-idx="${i}">${label}</span>`;
  }).join('');
  container.querySelectorAll('.tick').forEach(el => {
    el.onclick = () => {
      MI = +el.dataset.idx;
      sl.value = MI;
      paint();
    };
  });
}

function updateTimeTicks() {
  const ticks = document.querySelectorAll('#time-ticks .tick');
  ticks.forEach((el, i) => {
    el.classList.toggle('active', i === MI);
  });
}

function setupChartTooltip() {
  const tip = document.getElementById('chart-tip');
  if (!tip) return;
  document.addEventListener('mouseover', (e) => {
    const node = e.target.closest('.chart-node');
    if (node) {
      const { month, val, band, src } = node.dataset;
      tip.innerHTML = `<b>Tháng ${month}</b><div>NDVI: <b>${val}</b> (${band})</div><div>Nguồn: ${src}</div>`;
      tip.style.display = 'block';
    }
  });
  document.addEventListener('mousemove', (e) => {
    if (tip.style.display === 'block') {
      const rect = document.getElementById('mapwrap').getBoundingClientRect();
      tip.style.left = (e.clientX - rect.left) + 'px';
      tip.style.top = (e.clientY - rect.top) + 'px';
    }
  });
  document.addEventListener('mouseout', (e) => {
    if (e.target.closest('.chart-node')) {
      tip.style.display = 'none';
    }
  });
}

function setupCompare() {
  const modal = document.getElementById('compare-modal');
  const btnOpen = document.getElementById('compare-open');
  const btnClose = document.getElementById('compare-close');
  const selA = document.getElementById('sel-plot-a');
  const selB = document.getElementById('sel-plot-b');
  if (!modal || !btnOpen) return;

  const plotKeys = Object.keys(LO);
  const optionsHtml = plotKeys.map(k => `<option value="${k}">${k} - ${LO[k].ten}</option>`).join('');
  selA.innerHTML = optionsHtml;
  selB.innerHTML = optionsHtml;
  if (plotKeys.length > 1) selB.value = plotKeys[1];

  btnOpen.onclick = () => {
    modal.setAttribute('open', '');
    renderCompare();
  };
  btnClose.onclick = () => modal.removeAttribute('open');
  modal.onclick = (e) => { if (e.target === modal) modal.removeAttribute('open'); };

  selA.onchange = renderCompare;
  selB.onchange = renderCompare;
}

function renderCompare() {
  const idA = document.getElementById('sel-plot-a').value;
  const idB = document.getElementById('sel-plot-b').value;
  const container = document.getElementById('cmp-content');
  if (!idA || !idB || !LO[idA] || !LO[idB]) return;

  const a = LO[idA], b = LO[idB];
  const t = TH[MI];
  const mA = a.thang[t], mB = b.thang[t];

  container.innerHTML = `
    <div class="cmp-grid">
      <div class="cmp-card">
        <h4>${a.id} - ${a.ten}</h4>
        <div class="cmp-rows">
          <div class="cmp-r"><span>Diện tích:</span><b>${a.ha} ha</b></div>
          <div class="cmp-r"><span>Cây trồng:</span><b>${TEN[mA.cay] || mA.cay || 'Đất nghỉ'}</b></div>
          <div class="cmp-r"><span>Độ xanh (NDVI):</span><b>${mA.ndvi != null ? nf(mA.ndvi,3) : '--'}</b></div>
          <div class="cmp-r"><span>Độ ẩm lá (NDMI):</span><b>${mA.ndmi != null ? nf(mA.ndmi,3) : '--'}</b></div>
          <div class="cmp-r"><span>Nhiệt độ đất (LST):</span><b>${mA.lst != null ? nf(mA.lst,1) + ' °C' : '--'}</b></div>
          <div class="cmp-r"><span>Nước thiếu:</span><b>${mA.thieu != null ? nf(mA.thieu,0) + ' mm' : '--'}</b></div>
        </div>
      </div>
      <div class="cmp-card">
        <h4>${b.id} - ${b.ten}</h4>
        <div class="cmp-rows">
          <div class="cmp-r"><span>Diện tích:</span><b>${b.ha} ha</b></div>
          <div class="cmp-r"><span>Cây trồng:</span><b>${TEN[mB.cay] || mB.cay || 'Đất nghỉ'}</b></div>
          <div class="cmp-r"><span>Độ xanh (NDVI):</span><b>${mB.ndvi != null ? nf(mB.ndvi,3) : '--'}</b></div>
          <div class="cmp-r"><span>Độ ẩm lá (NDMI):</span><b>${mB.ndmi != null ? nf(mB.ndmi,3) : '--'}</b></div>
          <div class="cmp-r"><span>Nhiệt độ đất (LST):</span><b>${mB.lst != null ? nf(mB.lst,1) + ' °C' : '--'}</b></div>
          <div class="cmp-r"><span>Nước thiếu:</span><b>${mB.thieu != null ? nf(mB.thieu,0) + ' mm' : '--'}</b></div>
        </div>
      </div>
    </div>
    <div class="cmp-chart-sec">
      <h4>Diễn biến Độ xanh (NDVI 13 tháng)</h4>
      ${renderDualChart(idA, idB)}
    </div>
  `;
}

function renderDualChart(idA, idB) {
  const W = 720, H = 140, pl = 30, pr = 10, pt = 10, pb = 24;
  const a = LO[idA], b = LO[idB];
  const x = i => pl + i/(TH.length-1)*(W-pl-pr);
  const y = v => pt + (1-(v-0.1)/0.85)*(H-pt-pb);

  const getPath = (L) => {
    let d = '', open = false;
    TH.forEach((t, i) => {
      const v = L.thang[t].ndvi;
      if (v == null) { open = false; return; }
      d += (open ? 'L' : 'M') + x(i).toFixed(1) + ',' + y(v).toFixed(1);
      open = true;
    });
    return d;
  };

  return `
    <svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;">
      ${[0.25,0.55,0.85].map(v => `<line x1="${pl}" y1="${y(v)}" x2="${W-pr}" y2="${y(v)}" stroke="var(--line)" stroke-dasharray="2 2"/><text x="${pl-6}" y="${y(v)+3}" font-size="9" fill="var(--muted)" text-anchor="end">${v}</text>`).join('')}
      <path d="${getPath(a)}" fill="none" stroke="#2e7d32" stroke-width="2.5"/>
      <path d="${getPath(b)}" fill="none" stroke="#d84315" stroke-width="2.5" stroke-dasharray="4 2"/>
      <legend style="display:flex;gap:12px;font-size:11px;margin-top:4px;">
        <span style="color:#2e7d32">━ ${a.id}</span>
        <span style="color:#d84315">┈ ${b.id}</span>
      </legend>
    </svg>
  `;
}

function setupBottomSheet() {
  const handle = document.getElementById('sheet-handle');
  const panel = document.getElementById('panel');
  if (!handle || !panel) return;
  if (matchMedia('(max-width:480px)').matches) panel.classList.add('peek');
  panel.querySelector('.ph')?.addEventListener('click', () => {
    if (panel.classList.contains('peek')) panel.classList.remove('peek');
  });

  let startY = 0, startH = 0, dragging = false;
  handle.onpointerdown = (e) => {
    dragging = true;
    startY = e.clientY;
    startH = panel.offsetHeight;
    handle.setPointerCapture(e.pointerId);
  };
  handle.onpointermove = (e) => {
    if (!dragging) return;
    const dy = startY - e.clientY;
    const newH = Math.max(72, Math.min(window.innerHeight * 0.88, startH + dy));
    panel.style.height = newH + 'px';
  };
  handle.onpointerup = (e) => {
    if (!dragging) return;
    dragging = false;
    handle.releasePointerCapture(e.pointerId);
    panel.style.height = '';
    const h = panel.offsetHeight;
    if (h > window.innerHeight * 0.6) {
      panel.classList.remove('peek');
      panel.classList.add('expand');
    } else if (h < 120) {
      panel.classList.remove('expand');
      panel.classList.add('peek');
    } else {
      panel.classList.remove('expand', 'peek');
    }
  };
}

buildTimeTicks();
setupChartTooltip();
setupCompare();
setupBottomSheet();

const h0 = decodeURIComponent(location.hash.slice(1)).toUpperCase();
if (LO[h0]){ SEL = h0; hinted = true; document.getElementById('hint').style.display = 'none'; }
paint();
if (!hinted) setTimeout(() => { if (!hinted) document.getElementById('hint').style.opacity = 0; }, 6500);
addEventListener('hashchange', () => { const h = decodeURIComponent(location.hash.slice(1)).toUpperCase();
  select(LO[h] ? h : null, true); });
let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(fit, 160); });

