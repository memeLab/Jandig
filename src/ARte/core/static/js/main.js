if ('serviceWorker' in navigator) {
  console.log("aisdjasdijdsaijdsaiasdjidsajisdajigdsjifjidjgiesjjaisrejaSJ")
  // Use the window load event to keep the page load performant
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}