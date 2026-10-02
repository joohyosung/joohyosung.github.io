const renderCart = () => {
  // content 초기화
  let content = document.querySelector("#content");
  content.innerHTML = "";

  // localstorage 내 값 불러오기
  let items = [];

  for (let i = 0; i < localStorage.length; i += 1) {
    let key = localStorage.key(i);

    items.push({
      key: key,
      value: localStorage.getItem(key),
    });
  }

  // 정렬
  items.sort((a, b) => {
    return Number(a.key) - Number(b.key);
  });

  // localstorage 값 영역별 나누기
  let total = 0;
  items.forEach((item) => {
    let parts = item.value.split(",");
    if (parts.length < 3) return;

    let name = parts[0];
    let imgsrc = parts[1];
    let price = Number(parts[2]);

    // 표 생성
    let row = document.createElement("tr");
    let imageCell = document.createElement("td");
    let image = document.createElement("img");

    // 이미지 셀 생성
    image.className = "poster";
    image.src = imgsrc;
    image.alt = name;
    imageCell.appendChild(image);

    // 상품코드 셀 생성
    let idCell = document.createElement("td");
    idCell.textContent = item.key;

    // 상품명 셀 생성
    let nameCell = document.createElement("td");
    nameCell.textContent = name;

    // 가격 셀 생성
    let priceCell = document.createElement("td");
    priceCell.textContent = price.toLocaleString() + "원";

    // 삭제 버튼 생성
    let deleteCell = document.createElement("td");
    let deleteButton = document.createElement("button");

    deleteButton.type = "button";
    deleteButton.textContent = "삭제";

    deleteCell.appendChild(deleteButton);

    // 찜목록 표 생성
    row.append(imageCell, idCell, nameCell, priceCell, deleteCell);
    content.appendChild(row);

    // 총 금액 계산
    total += price;

    // 버튼 클릭 시 localstorage 값 삭제 및 표 내 값 삭제
    deleteButton.addEventListener("click", () => {
      localStorage.removeItem(item.key);
      renderCart();
    });
  });

  document.querySelector("#price").textContent =
    "총 금액: " + total.toLocaleString() + "원";
};

onload = renderCart;
