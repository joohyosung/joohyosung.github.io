// 찜하기 버튼 클릭 시 localstorage에 data-info 값 저장
document.querySelectorAll('button[name="cartinsert"]').forEach((btn) => {
  btn.addEventListener("click", () => {
    let id = 1001;

    for (let i = 0; i < localStorage.length; i += 1) {
      const key = Number(localStorage.key(i));
      if (Number.isInteger(key) && key >= id) {
        id = key + 1;
      }
    }

    localStorage.setItem(id, btn.dataset.info);
    alert("찜 목록에 추가했습니다.");
  });
});

// 미리보기 버튼 클릭 시 비디오 재생
document.querySelectorAll('button[name="vplay"]').forEach((btn) => {
  btn.addEventListener("click", () => {
    const video = document.querySelector("#video");
    video.src = btn.dataset.mediaSrc;
    video.load();
    video.play();
  });
});
