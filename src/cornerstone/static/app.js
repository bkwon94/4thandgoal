/* Toggles the recap panel of one matchup row.
   It is the only script on the page, so the page works without it except for the recaps. */
// aria-expanded tells a screen reader the state that the open class shows on screen.
document.querySelectorAll('.recap-btn').forEach(b => b.addEventListener('click', () => {
  b.setAttribute('aria-expanded', b.closest('.mu').classList.toggle('open'))
}))
