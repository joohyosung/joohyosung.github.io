const links = document.querySelectorAll(".floating-nav a");

links.forEach((link) => {
  link.addEventListener("click", () => {
    links.forEach((item) => item.classList.remove("active"));
    link.classList.add("active");
  });
});

const expectedLabel = document.querySelector("#expected");
const cutoffDate = new Date(2027, 1, 1); // 월은 0부터 시작하므로 1은 2월

function updateExpectedLabel() {
  if (!expectedLabel) return;

  const now = new Date();

  if (now >= cutoffDate) {
    expectedLabel.remove();
    return;
  }

  const nextMidnight = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate() + 1,
  );

  setTimeout(updateExpectedLabel, nextMidnight.getTime() - now.getTime());
}

updateExpectedLabel();
