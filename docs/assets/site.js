
document.addEventListener("input", (event) => {
  const input = event.target.closest("[data-filter-input]");
  if (!input) return;
  const list = document.querySelector("[data-filter-list]");
  const query = input.value.trim().toLowerCase();
  for (const item of list.querySelectorAll(".card")) {
    item.hidden = query && !item.textContent.toLowerCase().includes(query);
  }
});
