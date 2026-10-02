let registerButton = document.querySelector("#regist");

registerButton.addEventListener("click", () => {
  const form = document.querySelector("form");
  const inputs = document.querySelectorAll("form input");
  const email = document.querySelector("#email");
  const password = document.querySelector("#password");
  const password2 = document.querySelector("#password2");

  for (let input of inputs) {
    if (input.value === "") {
      alert(input.name + "을 입력하세요.");
      input.focus();
      return;
    }
  }

  if (email.value.indexOf("@") === -1) {
    alert("이메일 형식이 아닙니다.");
    email.focus();
    return;
  }

  if (password.value !== password2.value) {
    alert("비밀번호가 일치하지 않습니다.");
    password.value = "";
    password2.value = "";
    password.focus();
    return;
  }

  form.submit();
});
