(async () => {
  const [n, text, multi] = window.__pick;
  const box = () => document.querySelectorAll('main [role=combobox]')[n];
  box().click();
  await new Promise(r => setTimeout(r, 500));
  const lb = document.getElementById(box().getAttribute('aria-controls')); const opt = Array.from((lb || document).querySelectorAll('[role=option]')).find(o => o.textContent.trim().startsWith(text));
  if (!opt) return 'no option ' + text;
  opt.scrollIntoView(); opt.click();
  await new Promise(r => setTimeout(r, 500));
  if (multi && box().getAttribute('aria-expanded') === 'true') box().click();
  await new Promise(r => setTimeout(r, 300));
  return Array.from(document.querySelectorAll('main [role=combobox]')).map(b => b.textContent.trim() + '|' + b.getAttribute('aria-expanded')).join(', ');
})()
