/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}", "./siteapp/**/*.{html,py}"],
  darkMode: "class",
  theme: {
    container: { center: true, padding: "1rem" },
    extend: {
      colors: { brand: { primary: "#0ea5e9", dark: "#111827", bg: "#f8fafc" } },
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
