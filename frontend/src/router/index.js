import { createWebHistory, createRouter } from "vue-router";
import EditContents from "../views/EditContents.vue";
import DataSources from "../views/DataSources.vue";
import DownloadCode from "../views/DownloadCode.vue";
import ManageScreens from "../views/ManageScreens.vue";

const routes = [
  { path: "/", redirect: "/managescreens" },
  { path: "/managescreens", component: ManageScreens },
  { path: "/datasources", component: DataSources },
  { path: "/downloadcode", component: DownloadCode},
  { path: "/editcontents/:id", component: EditContents },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Ensures Vite handles routing correctly
  routes,
});

export default router;
