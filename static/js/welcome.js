const messages = [
  "Preparing your roadmap...",
  "Fetching best courses...",
  "Almost ready..."
];
let index = 0;
const statusNode = document.getElementById("statusMessage");

const interval = setInterval(function () {
  index = (index + 1) % messages.length;
  statusNode.textContent = messages[index];
}, 800);

setTimeout(function () {
  clearInterval(interval);
  window.location.href = "/index/";
}, 2500);
