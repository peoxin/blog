function addCopyButtonToCodeBlocks() {
    const codeBlocks = document.querySelectorAll("pre code");

    codeBlocks.forEach((codeBlock) => {
        const copyButton = document.createElement("button");
        copyButton.classList.add("copy-code-button");
        copyButton.innerHTML = "Copy";

        copyButton.addEventListener("click", () => {
            let code = codeBlock.textContent;
            navigator.clipboard.writeText(code);

            copyButton.innerHTML = "Copied!";
            setTimeout(() => {
                copyButton.innerHTML = "Copy";
            }, 1000);
        });

        codeBlock.parentNode.before(copyButton);
    });
}

// Add copy button to code blocks after a delay
setTimeout(function() {
    addCopyButtonToCodeBlocks();
}, 100);
