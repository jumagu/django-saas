document.addEventListener("DOMContentLoaded", function () {
  const theme = localStorage.getItem("theme") ?? "light";
  setTheme(theme);
  const toggle = document.getElementById("theme-toggle");
  theme === "light" ? (toggle.checked = false) : (toggle.checked = true);
});

function onToggleChange() {
  const toggle = document.getElementById("theme-toggle");
  const theme = toggle.checked ? "dark" : "light";
  setTheme(theme);
}

function setTheme(theme) {
  localStorage.setItem("theme", theme);
  document.documentElement.setAttribute("data-theme", theme);
}
