// 초기 데이터
let mockData = [
  { id: 0, isDone: false, content: "React study", date: new Date().getTime() },
  { id: 1, isDone: false, content: "친구만나기", date: new Date().getTime() },
  { id: 2, isDone: false, content: "낮잠자기", date: new Date().getTime() },
];

// 요일 출력을 위한 배열
let day = ["일", "월", "화", "수", "목", "금", "토"];

//// 전체 출력 기능
const initData = (printData) => {
  // 현재 날짜를 년 월 일 요일로 출력
  const today = new Date();

  const year = today.getFullYear();
  const month = today.getMonth() + 1;
  const date = today.getDate();
  const week = day[today.getDay()];

  let thisday = document.querySelector(".Header h1");

  thisday.innerHTML = `${year}년 ${month}월 ${date}일 ${week}요일`;

  const todoWrapper = document.querySelector(".todos_wrapper");

  // 초기화
  todoWrapper.innerHTML = "";

  // todoitem 초기 아이템 입력
  printData.forEach((todo) => {
    // todoitem 추가
    const todoItem = document.createElement("div");
    todoItem.className = "TodoItem";

    // 체크박스 생성
    const checkBox = document.createElement("input");
    checkBox.type = "checkbox";
    checkBox.checked = todo.isDone;
    checkBox.dataset.id = todo.id;
    checkBox.setAttribute("onchange", `onUpdate(${todo.id})`);

    // 내용 생성
    const content = document.createElement("div");
    content.className = "content";
    content.innerHTML = todo.content;

    // 날짜 생성
    const date = document.createElement("div");
    date.className = "date";
    date.innerHTML = new Date(todo.date).toLocaleString();

    // 삭제 버튼 생성
    const delbtn = document.createElement("button");
    delbtn.name = todo.id;
    delbtn.type = "button";
    delbtn.setAttribute("onclick", "todoDel(this)");
    delbtn.innerHTML = "삭제";

    todoItem.append(checkBox, content, date, delbtn);
    todoWrapper.appendChild(todoItem);
  });
};

// mockData 리스트에 추가
initData(mockData);

//// todo 추가 기능
const todoBtn = document.querySelector(".Editor button");
const todoInput = document.querySelector(".Editor input");

// 추가 버튼 클릭 시 mockData에 추가
todoBtn.addEventListener("click", function (e) {
  e.preventDefault();

  let content = todoInput.value;
  if (content === "") return;
  let nextId =
    mockData.length === 0
      ? 0
      : Math.max(...mockData.map((todo) => todo.id)) + 1;

  mockData.push({
    id: nextId,
    isDone: false,
    content: content,
    date: new Date().getTime(),
  });

  // 새로운 mockData 리스트에 출력 및 입력창 초기화
  initData(mockData);
  todoInput.value = "";
});

//// 수정 기능
const onUpdate = (targetId) => {
  // todoItem에서 호출할 때 전달한 id가 같은 mockData 레코드 찾기
  let todos = mockData
    .map((todo) => {
      if (todo.id === targetId) {
        return todo;
      }

      return null;
    })
    .filter((todo) => todo !== null);

  // 해당 checkbox의 체크 여부 판단
  let checkBox = document.querySelectorAll(".TodoItem input")[targetId];

  // 해당하는 todo isDone 수정
  let todo = todos[0];
  todo.isDone = checkBox.checked;
  initData(mockData);
};

//// 삭제 기능
const todoDel = (th) => {
  mockData = mockData.filter((todo) => todo.id != th.name);
  initData(mockData);
};

//// 검색 기능
document.querySelector("#keyword").addEventListener("keyup", (e) => {
  let searchedTodos = getFilterData(e.target.value);

  initData(searchedTodos);
});

const getFilterData = (search) => {
  // 검색어가 없으면 mockdata를 리턴
  if (search === "") {
    return mockData;
  }

  // filter 함수를 이용해서 search(검색어)를 포함하고 있는 todo들을 받는다.
  let filteredData = mockData.filter((todo) => {
    return todo.content.includes(search);
  });
  // filter의 결과를 리턴
  return filteredData;
};
