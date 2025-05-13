import { createApp } from "vue";
import App from "./App.vue";
import router from "./router"; // Ensure correct path
import "@fortawesome/fontawesome-free/css/all.css";
import "./styles.css"
import axios from 'axios'


async function injectFonts() {
    const res = await axios.get("/api/fonts");
    let fonts = res.data;
  
    // make sure fonts is an array
    if (!Array.isArray(fonts)) {
      console.warn("Expected an array from /api/fonts, got:", fonts);
      if (Array.isArray(fonts.fonts)) {
        fonts = fonts.fonts;
      } else {
        throw new TypeError("`/api/fonts` did not return an array");
      }
    }
  
    const style = document.createElement("style");
    style.type = "text/css";
  
    fonts.forEach(f => {
      // detect "italic" in filename (or family) and set style accordingly
      const isItalic = /italic/i.test(f.filename);
      style.appendChild(document.createTextNode(`
  @font-face {
    font-family: '${f.family}';
    src: url('/static/fonts/${f.filename}') format('truetype-variations');
    font-weight: 100 900;       /* wght axis goes from 100 to 900 */
    font-style: ${isItalic ? 'italic' : 'normal'};
  }`));
    });
  
    document.head.appendChild(style);
  }
  
  await injectFonts()
    .catch(err => console.error("Font injection failed:", err));
  
createApp(App).use(router).mount("#app")