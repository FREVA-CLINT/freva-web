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
