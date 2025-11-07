// Basic JS helpers
document.addEventListener('click', function(e){
  const t = e.target;
  if(t.closest && t.closest('[aria-disabled="true"], .disabled')){
    e.preventDefault();
    return;
  }
  if(t.matches('[data-confirm]')){
    if(!confirm(t.getAttribute('data-confirm'))){
      e.preventDefault();
    }
  }
});

// Parallax float for hero visuals
(function(){
  const container = document.getElementById('heroVisual');
  if(!container) return;
  const items = Array.from(container.querySelectorAll('.floaty')).map(el=>({
    el,
    speed: parseFloat(el.getAttribute('data-speed') || '1'),
    baseX: el.offsetLeft,
    baseY: el.offsetTop
  }));

  let mx = 0, my = 0, tx = 0, ty = 0;
  const lerp = (a,b,t)=>a+(b-a)*t;

  function onMove(e){
    const rect = container.getBoundingClientRect();
    const cx = rect.left + rect.width/2;
    const cy = rect.top + rect.height/2;
    mx = (e.clientX - cx) / rect.width;
    my = (e.clientY - cy) / rect.height;
  }

  function animate(){
    tx = lerp(tx, mx, 0.08);
    ty = lerp(ty, my, 0.08);
    items.forEach(({el, speed, baseX, baseY})=>{
      const dx = tx * 18 * speed;
      const dy = ty * 18 * speed;
      el.style.transform = `translate(${dx}px, ${dy}px) rotate(${dx*0.4}deg)`;
    });
    requestAnimationFrame(animate);
  }

  container.addEventListener('mousemove', onMove);
  container.addEventListener('mouseleave', ()=>{ mx = my = 0; });
  animate();
})();

// Mobile nav toggle
(function(){
  const btn = document.getElementById('navToggle');
  const menu = document.getElementById('navMenu');
  if(!btn || !menu) return;
  btn.addEventListener('click', function(){
    const open = menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();

