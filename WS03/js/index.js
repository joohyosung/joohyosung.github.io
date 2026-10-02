let bannerList = [
  "국민의 은행이 되겠습니다.",
  "5060 웰컴패키지, 최대 7만원 혜택을 드립니다.",
  "타행이체, 자동이체 수수료 면제",
  "저녁 6시까지 영업합니다.",
];

const banner = document.querySelector("#banner");

let index = 0;

setInterval(() => {
  banner.textContent = bannerList[index];
  index++;

  if (index === bannerList.length) {
    index = 0;
  }
}, 2000);

const btns = document.querySelectorAll(".main-item-btn");

btns.forEach((btn) => {
  btn.addEventListener("click", () => {
    console.log(btn.parentElement.dataset.mainItemId);
  });
});
