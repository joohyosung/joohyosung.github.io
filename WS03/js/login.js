let loginButton = document.querySelector("#login");

loginButton.addEventListener("click", (event) => {
  const id = document.querySelector("#id");
  const password = document.querySelector("#password");

  if (id.value === "") {
    event.preventDefault();
    alert("아이디를 입력하세요.");
    id.focus();
    return;
  }

  if (password.value === "") {
    event.preventDefault();
    alert("비밀번호를 입력하세요.");
    password.focus();
    return;
  }

  alert("입력유무체크 완료");
});
