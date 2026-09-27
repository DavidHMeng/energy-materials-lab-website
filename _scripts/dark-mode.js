/*
  manages light/dark mode.
*/

{
  const saved = window.localStorage.getItem("color-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const dark = saved ? saved === "dark" : prefersDark;
  document.documentElement.dataset.dark = String(dark);
  document.documentElement.style.colorScheme = dark ? "dark" : "light";

  window.toggleTheme = () => {
    const next = document.documentElement.dataset.dark !== "true";
    document.documentElement.dataset.dark = String(next);
    document.documentElement.style.colorScheme = next ? "dark" : "light";
    window.localStorage.setItem("color-theme", next ? "dark" : "light");
  };
}
