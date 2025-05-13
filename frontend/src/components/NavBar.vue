<script setup>
import { useRouter } from "vue-router";
import { computed } from "vue";

const router = useRouter();
const currentPath = computed(() => router.currentRoute.value.path);

const navLinkClass = (path) => {
  return path === currentPath.value
    ? "text-black font-semibold cursor-default" // Active page (no hover effect)
    : "text-gray-400 hover:text-black transition-colors duration-200"; // Non-active pages (hover effect)
};
</script>

<template>
  <nav class="fixed top-0 w-full bg-gray-200 flex items-center justify-center p-4 z-100">
    <div class="flex flex-row sm:space-x-40 space-x-2 mx-auto">
      <router-link 
        to="/downloadcode" 
        :class="navLinkClass('/downloadcode')"
      >Download/Upload Codes</router-link>

      <router-link 
        to="/managescreens" 
        :class="navLinkClass('/managescreens')"
      >Manage screens</router-link>

      <router-link 
        to="/datasources" 
        :class="navLinkClass('/datasources')"
      >Manage sources</router-link>
    </div>
  </nav>
</template>


<style scoped>
nav {
  transition: all 0.3s ease-in-out;
}
</style>
