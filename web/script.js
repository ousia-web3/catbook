const parts = [
  {
    label: "웃다가 배우는 고양이 생활",
    shortLabel: "생활",
    summary:
      "고양이의 웃긴 장면을 그대로 소비하지 않고, 그 뒤에 숨어 있는 몸의 균형과 환경 변화를 읽는 첫 파트.",
    focus: "귀여움과 관찰의 균형",
    reader: "웃다가 놓치던 작은 신호를 다시 보게 된다.",
    tone: "가볍게 시작하지만 끝은 정확하게",
    badges: ["우다다", "기록 욕심", "새 물건", "비교", "이름", "관찰"],
    closing: "이 파트는 책의 문을 여는 장이다. 웃음은 유지하되, 고양이의 몸이 먼저 말한 것을 놓치지 않게 만든다.",
    chapters: [
      { title: "츄르는 왜 갑자기 뛰었을까", detail: "우다다를 놀이, 배변 후 리듬, 소리 자극, 몸의 불편함까지 전후 맥락으로 본다." },
      { title: "웃긴 장면 뒤에 남은 신호", detail: "사진을 찍고 싶은 순간에도 귀, 꼬리, 자세가 말하는 불편함을 먼저 확인한다." },
      { title: "집사의 상처받는 속도", detail: "새 방석을 거절한 고양이를 탓하지 않고 냄새와 시간, 접근권으로 다시 소개한다." },
      { title: "고양이 과시대회의 뒤끝", detail: "다른 집 고양이와 비교하지 않고, 내 고양이가 선택한 거리의 신뢰를 읽는다." },
      { title: "이름을 바꾸면 운명도 바뀔까", detail: "이름보다 중요한 것은 이름 뒤에 붙는 경험이라는 사실을 장면으로 보여준다." },
      { title: "귀여움이 관찰을 가릴 때", detail: "귀여운 행동을 귀여움으로만 끝내지 않고 반복 여부와 생활 변화를 함께 기록한다." },
    ],
  },
  {
    label: "집 안에 놓는 안심",
    shortLabel: "안심",
    summary:
      "고양이가 마음을 놓을 수 있는 집은 예쁜 집이 아니라 숨을 곳, 먹을 곳, 마실 곳, 화장실이 정확히 놓인 집이다.",
    focus: "환경 설계와 선택권",
    reader: "오늘 집에서 바로 바꿀 수 있는 배치 기준을 얻는다.",
    tone: "조용하고 실용적인 생활 지도",
    badges: ["숨을 곳", "밥그릇", "물그릇", "화장실", "이동장", "출근 전"],
    closing: "이 파트는 집 자체를 고양이의 언어로 번역한다. 큰 공사보다 작은 위치 조정이 더 큰 안심을 만든다.",
    chapters: [
      { title: "소파 밑 38센티미터", detail: "숨어 있는 고양이를 꺼내지 않고 나올 수 있는 길과 시간을 마련하는 법을 다룬다." },
      { title: "밥그릇보다 먼저 놓아야 할 것", detail: "식사 공간이 안정적이어야 밥그릇도 의미가 있다는 순서를 보여준다." },
      { title: "물그릇 세 개의 정치학", detail: "물을 잘 마시게 하는 것은 강요가 아니라 위치, 재질, 동선의 문제로 본다." },
      { title: "화장실은 집의 중심이다", detail: "화장실을 매일 도착하는 건강 편지로 보고 모래와 위치, 청결을 점검한다." },
      { title: "이동장은 감옥이 아니라 방이어야 한다", detail: "병원 가는 날만 등장하는 물건이 아니라 평소부터 열려 있는 방으로 만든다." },
      { title: "출근 전 30초", detail: "바쁜 아침에도 물, 밥, 화장실, 닫힌 문을 확인하는 짧은 루틴을 만든다." },
    ],
  },
  {
    label: "마음의 속도를 맞추는 일",
    shortLabel: "마음",
    summary:
      "고양이의 마음은 말보다 거리와 속도로 드러난다. 이 파트는 좋아함, 싫음, 불안, 신뢰를 사람의 욕심 없이 읽는다.",
    focus: "거리의 요청과 신뢰의 속도",
    reader: "다가가는 손보다 멈추는 손이 더 필요할 때를 알게 된다.",
    tone: "다정하지만 고양이 편에 선 문장",
    badges: ["인사", "하악질", "놀이", "꼬리", "호감", "거절권"],
    closing: "이 파트는 고양이를 더 빨리 친하게 만드는 법이 아니라, 고양이가 믿을 수 있는 속도로 사람이 느려지는 법을 말한다.",
    chapters: [
      { title: "이름을 부르지 않는 인사", detail: "눈인사와 손등, 몸의 방향처럼 고양이가 부담 없이 받을 수 있는 인사를 다룬다." },
      { title: "하악질의 번역", detail: "하악질을 나쁜 성격이 아니라 거리와 시간을 요청하는 신호로 다시 읽는다." },
      { title: "우다다는 혼난 뒤가 아니라 비운 뒤에 온다", detail: "야단보다 놀이 설계와 에너지 배출이 먼저라는 생활 리듬을 보여준다." },
      { title: "꼬리가 먼저 말한 날", detail: "꼬리 끝의 속도와 방향으로 고양이의 긴장과 호기심을 구분한다." },
      { title: "고양이가 나를 좋아한다는 증거", detail: "무릎 위 사진보다 같은 방에 남는 선택, 느린 눈, 등을 보이는 신뢰를 읽는다." },
      { title: "잠깐 싫어할 권리", detail: "싫다는 신호를 관계의 실패가 아니라 관계를 지키는 경계로 받아들인다." },
    ],
  },
  {
    label: "몸이 보내는 작은 알림",
    shortLabel: "몸",
    summary:
      "건강 파트는 병명을 맞히는 장이 아니라 변화를 알아차리는 장이다. 배변, 식욕, 물, 구토, 체중을 기록의 언어로 바꾼다.",
    focus: "관찰, 기록, 상담 기준",
    reader: "걱정만 하던 보호자가 병원에 가져갈 정보를 정리하게 된다.",
    tone: "차분하고 안전한 건강 메모",
    badges: ["배변", "발톱", "진료 기록", "음수", "구토", "체중"],
    closing: "이 파트는 진단서가 아니다. 대신 보호자가 오늘 본 변화를 놓치지 않고 안전하게 다음 행동으로 옮기게 한다.",
    chapters: [
      { title: "똥을 보고 쓰는 일기", detail: "화장실 기록을 부끄러운 일이 아니라 몸이 남긴 가장 정직한 문장으로 본다." },
      { title: "발톱깎이는 가위가 아니라 약속", detail: "한 번에 끝내는 기술보다 짧은 접촉과 보상으로 신뢰를 쌓는 과정을 다룬다." },
      { title: "병원에 가져갈 세 줄", detail: "언제부터, 무엇이, 얼마나 달라졌는지를 세 줄로 정리하는 진료 준비법이다." },
      { title: "물을 많이 마신 날", detail: "물을 많이 마시는 변화를 단순 습관으로 넘기지 않고 날짜와 양을 기록한다." },
      { title: "토한 뒤에 해야 할 일", detail: "구토 후 당황보다 횟수, 내용물, 활력, 식욕을 차분히 확인하는 순서를 제안한다." },
      { title: "살이 찐 건 귀여움이 아니다", detail: "체중을 외모 평가가 아니라 관절과 움직임, 생활 질의 문제로 바라본다." },
    ],
  },
  {
    label: "같이 산다는 것의 거리",
    shortLabel: "관계",
    summary:
      "새 고양이, 아이, 가족 변화는 사랑만으로 해결되지 않는다. 공간과 동선, 각자의 시간을 다시 설계하는 파트.",
    focus: "동거의 규칙과 갈등 완충",
    reader: "좋은 마음이 고양이에게 부담이 되지 않도록 관계의 순서를 배운다.",
    tone: "감정은 따뜻하게, 구조는 냉정하게",
    badges: ["합사", "둘째", "아이", "싸움 후", "외로움", "가족 변화"],
    closing: "이 파트는 함께 산다는 말을 예쁘게 포장하지 않는다. 대신 모두가 덜 다치기 위한 거리와 순서를 만든다.",
    chapters: [
      { title: "합사는 사랑보다 동선이다", detail: "첫 만남의 감동보다 냄새, 문, 밥자리, 도망갈 길을 먼저 설계한다." },
      { title: "둘째를 들이기 전 첫째에게 묻는 법", detail: "사람의 외로움이 첫째 고양이의 생활을 무너뜨리지 않도록 질문을 바꾼다." },
      { title: "아기와 고양이 사이의 규칙", detail: "아이의 호기심과 고양이의 안전을 함께 지키는 접촉 규칙을 제안한다." },
      { title: "싸움이 끝난 뒤 사람이 해야 할 일", detail: "싸움 직후 야단보다 분리, 안정, 원인 기록이 먼저라는 순서를 보여준다." },
      { title: "외로움이라는 사람의 오해", detail: "혼자 있는 시간을 전부 불행으로 해석하지 않고 생활 리듬을 함께 본다." },
      { title: "가족이 늘어날 때 고양이가 잃는 것", detail: "새 가족이 생길 때 고양이가 잃는 자리, 냄새, 시간을 보완하는 법이다." },
    ],
  },
  {
    label: "오래 같이 살기 위한 책임",
    shortLabel: "책임",
    summary:
      "고양이를 오래 사랑한다는 말은 예방, 안전, 노화, 마지막 순간까지 포함한다. 조금 무거운 주제를 부드럽게 정리한다.",
    focus: "예방과 윤리, 오래 사는 준비",
    reader: "불안한 상상을 실제 준비와 점검으로 바꾸게 된다.",
    tone: "담담하고 책임감 있는 안내",
    badges: ["실종 예방", "길고양이", "위험물", "노묘", "마지막", "질문"],
    closing: "이 파트는 겁을 주기 위한 장이 아니다. 미리 준비한 사람만이 더 오래, 덜 후회하며 사랑할 수 있다는 사실을 말한다.",
    chapters: [
      { title: "실종을 상상하기 전에 할 일", detail: "문, 창문, 방충망, 인식표처럼 상상보다 먼저 점검할 예방 목록을 다룬다." },
      { title: "길고양이를 본 날의 순서", detail: "감정에 끌려 바로 데려오기보다 관찰, 구조 판단, 전문가 연결 순서를 본다." },
      { title: "위험한 물건은 귀엽지 않다", detail: "끈, 비닐, 식물, 작은 물건처럼 집 안 위험을 생활 동선에서 제거한다." },
      { title: "노묘의 느린 대답", detail: "느려진 고양이를 게으름으로 보지 않고 몸의 시간과 편의로 다시 배치한다." },
      { title: "마지막을 준비한다는 말", detail: "무겁지만 필요한 돌봄의 끝을 죄책감보다 기록과 상의의 언어로 다룬다." },
      { title: "모르면 묻는 용기", detail: "검색으로 버티지 말고 기록을 들고 상담하는 용기를 마지막 태도로 제안한다." },
    ],
  },
  {
    label: "고양이라는 종을 더 정확히 보기",
    shortLabel: "지식",
    summary:
      "묘종, 외모, 털, 유전 같은 호기심을 생활 관찰로 연결한다. 예쁜 정보보다 실제로 함께 사는 데 필요한 지식을 고른다.",
    focus: "품종 정보와 개체 관찰의 균형",
    reader: "고양이를 이름표가 아니라 생활 반응으로 설명하게 된다.",
    tone: "호기심은 살리고 단정은 줄이는 지식",
    badges: ["묘종", "유전", "피부", "새끼", "생활", "마무리"],
    closing: "이 파트는 책의 마지막에 독자를 다시 집 안으로 돌려보낸다. 지식은 밖에서 얻지만 답은 오늘의 고양이에게서 확인한다.",
    chapters: [
      { title: "묘종백과를 읽는 법", detail: "품종 정보를 재미로 읽되 내 고양이의 실제 생활 반응을 더 우선한다." },
      { title: "예쁜 외모 뒤의 유전 이야기", detail: "외모의 매력을 건강과 관리 책임까지 포함해 바라보는 균형을 다룬다." },
      { title: "털과 피부가 보내는 힌트", detail: "털 빠짐과 피부 변화를 미용 문제가 아니라 생활과 몸의 신호로 본다." },
      { title: "작은 고양이와 작은 오해", detail: "새끼 고양이를 장난감처럼 보지 않고 빠르게 변하는 몸으로 관찰한다." },
      { title: "품종보다 먼저 보는 생활", detail: "품종 설명보다 좋아하는 자리, 싫어하는 상황, 매일의 리듬을 기록한다." },
      { title: "오늘도 츄르는 나를 훈련시킨다", detail: "책 전체의 결론처럼 고양이가 사람을 더 정확한 보호자로 바꾸는 과정을 닫는다." },
    ],
  },
];

const chapterList = document.querySelector("#chapter-list");
const tabButtons = Array.from(document.querySelectorAll(".tab-button"));
const partOpeners = Array.from(document.querySelectorAll("[data-part-open]"));
const modal = document.querySelector("#part-modal");
const modalPanel = modal.querySelector(".modal-panel");
const modalCloseControls = Array.from(modal.querySelectorAll("[data-modal-close]"));
const modalKicker = document.querySelector("#part-modal-kicker");
const modalTitle = document.querySelector("#part-modal-title");
const modalSummary = document.querySelector("#part-modal-summary");
const modalFocus = document.querySelector("#part-modal-focus");
const modalReader = document.querySelector("#part-modal-reader");
const modalTone = document.querySelector("#part-modal-tone");
const modalBadges = document.querySelector("#part-modal-badges");
const modalUnits = document.querySelector("#part-modal-units");
const modalClosing = document.querySelector("#part-modal-closing");
const modalLink = document.querySelector("#part-modal-link");

let lastFocusedElement = null;
let activePartIndex = -1;

function protectGeneratedMedia() {
  const generatedImages = Array.from(document.querySelectorAll('img[src*="assets/generated/"]'));

  generatedImages.forEach((image) => {
    const media = image.closest("figure, picture, .hero-media, .chapter-visual") || image.parentElement;
    if (media) {
      media.classList.add("ai-generated-media");
      media.dataset.aiLabel = "AI 생성";
    }

    image.dataset.aiGenerated = "true";
    image.draggable = false;
    image.setAttribute("draggable", "false");
    image.addEventListener("dragstart", (event) => event.preventDefault());
  });

  document.addEventListener("contextmenu", (event) => {
    event.preventDefault();
  });
}

function isValidPartIndex(index) {
  return Number.isInteger(index) && index >= 0 && index < parts.length;
}

function renderPart(index) {
  const part = parts[index];
  const fragment = document.createDocumentFragment();

  part.chapters.forEach((chapter, chapterIndex) => {
    const chapterNumber = index * 6 + chapterIndex + 1;
    const button = document.createElement("button");
    const meta = document.createElement("span");
    const title = document.createElement("strong");

    button.className = "chapter-item";
    button.type = "button";
    button.dataset.part = String(index);
    button.dataset.chapter = String(chapterNumber);
    button.setAttribute("aria-label", `${chapterNumber}장 ${chapter.title}. ${part.label} 파트 상세 열기`);

    meta.textContent = `Chapter ${String(chapterNumber).padStart(2, "0")}`;
    title.textContent = chapter.title;

    button.append(meta, title);
    fragment.append(button);
  });

  chapterList.replaceChildren(fragment);
}

function setActivePart(index) {
  if (!isValidPartIndex(index)) {
    return;
  }

  tabButtons.forEach((button) => {
    const isActive = Number(button.dataset.part) === index;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
    button.tabIndex = isActive ? 0 : -1;
  });

  chapterList.setAttribute("aria-labelledby", `part-tab-${index}`);

  if (activePartIndex !== index || !chapterList.childElementCount) {
    renderPart(index);
  }

  activePartIndex = index;
}

function renderModal(index) {
  if (!isValidPartIndex(index)) {
    return;
  }

  const part = parts[index];
  modalKicker.textContent = `Part ${index + 1} · ${part.shortLabel}`;
  modalTitle.textContent = part.label;
  modalSummary.textContent = part.summary;
  modalFocus.textContent = part.focus;
  modalReader.textContent = part.reader;
  modalTone.textContent = part.tone;
  modalClosing.textContent = part.closing;
  modalLink.href = `./manuscript.html#chapter-${index * 6 + 1}`;

  const badgeFragment = document.createDocumentFragment();
  part.badges.forEach((badge) => {
    const badgeElement = document.createElement("span");
    badgeElement.textContent = badge;
    badgeFragment.append(badgeElement);
  });
  modalBadges.replaceChildren(badgeFragment);

  const unitFragment = document.createDocumentFragment();
  part.chapters.forEach((chapter, chapterIndex) => {
    const article = document.createElement("article");
    const number = document.createElement("span");
    const title = document.createElement("strong");
    const detail = document.createElement("p");

    article.className = "modal-unit";
    number.className = "unit-number";
    number.textContent = String(index * 6 + chapterIndex + 1).padStart(2, "0");
    title.textContent = chapter.title;
    detail.textContent = chapter.detail;

    article.append(number, title, detail);
    unitFragment.append(article);
  });
  modalUnits.replaceChildren(unitFragment);
}

function openPartModal(index) {
  if (!isValidPartIndex(index)) {
    return;
  }

  renderModal(index);
  lastFocusedElement = document.activeElement;
  modal.hidden = false;
  modal.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
  modalPanel.focus();
}

function closePartModal() {
  if (modal.classList.contains("modal-closing") || modal.hidden) {
    return;
  }
  modal.classList.add("modal-closing");
  
  const handleAnimationEnd = (event) => {
    if (event.target !== modal) {
      return;
    }
    modal.classList.remove("modal-closing");
    modal.hidden = true;
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    if (lastFocusedElement?.isConnected) {
      lastFocusedElement.focus();
    }
    modal.removeEventListener("animationend", handleAnimationEnd);
  };
  
  modal.addEventListener("animationend", handleAnimationEnd);
}

function trapModalFocus(event) {
  if (event.key !== "Tab" || modal.hidden) {
    return;
  }

  const focusable = modal.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])');
  if (!focusable.length) {
    return;
  }

  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const index = Number(button.dataset.part);
    setActivePart(index);
  });

  button.addEventListener("keydown", (event) => {
    const currentIndex = tabButtons.indexOf(button);
    let nextIndex = currentIndex;

    if (event.key === "ArrowRight") {
      nextIndex = (currentIndex + 1) % tabButtons.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (currentIndex - 1 + tabButtons.length) % tabButtons.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = tabButtons.length - 1;
    } else {
      return;
    }

    event.preventDefault();
    const nextPart = Number(tabButtons[nextIndex].dataset.part);
    setActivePart(nextPart);
    tabButtons[nextIndex].focus();
  });
});

partOpeners.forEach((opener) => {
  opener.addEventListener("click", () => {
    const index = Number(opener.dataset.partOpen);
    if (!Number.isInteger(index) || index < 0 || index >= parts.length) {
      return;
    }
    setActivePart(index);
    openPartModal(index);
  });
});

chapterList.addEventListener("click", (event) => {
  const chapter = event.target.closest(".chapter-item");
  if (!chapter) {
    return;
  }
  openPartModal(Number(chapter.dataset.part));
});

modalCloseControls.forEach((control) => {
  control.addEventListener("click", closePartModal);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modal.hidden) {
    closePartModal();
  }
  trapModalFocus(event);
});

const searchParams = new URLSearchParams(window.location.search);
const requestedPart = Number(searchParams.get("part"));
if (searchParams.has("part") && isValidPartIndex(requestedPart)) {
  setActivePart(requestedPart);
  openPartModal(requestedPart);
} else {
  setActivePart(0);
}

protectGeneratedMedia();
