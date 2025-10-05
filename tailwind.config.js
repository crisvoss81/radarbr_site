/** @type {import('tailwindcss').Config} */
module.exports = {
  // CORREÇÃO: Apontando para todas as pastas de templates do seu projeto.
  content: [
    './templates/**/*.html',
    './rb_portal/templates/**/*.html',
    './rb_noticias/templates/**/*.html',
  ],

  darkMode: "class",
  theme: {
    container: { center: true, padding: "1rem" },
    extend: {
      colors: { 
        brand: { primary: "#c1121f", dark: "#111827", bg: "#f8fafc" } 
      },
      fontFamily: {
        sans: ["Inter","ui-sans-serif","system-ui","Segoe UI","Roboto","Helvetica","Arial","sans-serif"],
        serif: ["Merriweather","ui-serif","Georgia","serif"]
      }
    }
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/line-clamp"),
    require("@tailwindcss/aspect-ratio"),
  ],
}