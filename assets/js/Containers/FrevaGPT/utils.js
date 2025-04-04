export function replaceLinebreaks(data) {
  const formattedData = data.split("\\n").join("\n");
  return formattedData;
}

export function formatCode(mode, data) {
  let shortData = data;

  // replace first linebreak in code got from old thread
  if (data.startsWith("\\n")) {
    shortData = data.replace("\\n", "");
  }

  let codeSnippets;
  let rawCode;

  try {
    if (mode === "Code") {
      rawCode = JSON.parse(shortData).code;
    } else if (mode === "CodeOutput") {
      rawCode = shortData;
    }
    codeSnippets = rawCode.split("\\n");
  } catch (err) {
    // do something
  }

  return codeSnippets;
}

export const truncate = (value) => {
  const trunc = value.substring(0, 32) + "\u2026";
  return trunc;
};

export function getPosition() {
  const container = document.querySelector("#chatContainer");
  const position = {};

  position.atBottom =
    container.scrollTop + container.clientHeight >=
    container.scrollHeight - 200;
  position.atTop = container.scrollTop < 50;

  return position;
}

export function chatExceedsWindow() {
  const wholeWindowHeight = document.documentElement.clientHeight * 0.8;
  const inputHeight = document.getElementById("botInput").clientHeight;
  const chatHeight = document.getElementById("chatContainer").scrollHeight;

  const chatExceedsWindowHeight = wholeWindowHeight - inputHeight < chatHeight;

  return chatExceedsWindowHeight;
}

export function scrollToChatBottom() {
  document.getElementById("chatContainer").scrollTo({
    top: document.getElementById("chatContainer").scrollHeight,
    behavior: "smooth",
  });
}
