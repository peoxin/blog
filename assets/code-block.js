document.addEventListener("DOMContentLoaded", function () {
  const codeBlocks = document.querySelectorAll("pre > code");

  codeBlocks.forEach(function (codeBlock) {
    const pre = codeBlock.parentElement;

    if (!pre) return;

    // Avoid adding multiple copy buttons to the same code block
    if (pre.querySelector(".code-copy-btn")) return;

    // Create the copy button
    const copyButton = document.createElement("button");
    copyButton.className = "code-copy-btn";
    copyButton.textContent = "Copy";

    // Add click event listener to the copy button
    copyButton.addEventListener("click", function () {
      const codeText = codeBlock.innerText;

      navigator.clipboard
        .writeText(codeText)
        .then(function () {
          const originalText = copyButton.textContent;
          copyButton.textContent = "Copied!";
          copyButton.classList.add("copied");

          setTimeout(function () {
            copyButton.textContent = originalText;
            copyButton.classList.remove("copied");
          }, 500);
        })
        .catch(function (err) {
          console.error("Failed to copy code: ", err);
          copyButton.textContent = "Error";
        });
    });

    pre.appendChild(copyButton);
  });
});
