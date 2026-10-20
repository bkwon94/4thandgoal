/* Toggles the recap panel of one matchup row.
   It is the only script on the page, so the page works without it except for the recaps. */
document.querySelectorAll('.recap-btn').forEach(b => b.addEventListener('click', () => b.closest('.mu').classList.toggle('open')))
