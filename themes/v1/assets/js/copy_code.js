function addCopyButtonToCodeBlocks() {
    const codeBlocks = document.querySelectorAll("pre code");

    codeBlocks.forEach((codeBlock) => {
        const copyButton = document.createElement("button");
        copyButton.classList.add("copy-code-button");
        copyButton.innerHTML = "copy";

        copyButton.addEventListener("click", () => {
            let codeToCopy = codeBlock.textContent;
            navigator.clipboard.writeText(codeToCopy);
            console.log(codeToCopy);

            copyButton.innerHTML = "copied!";
            setTimeout(() => {
                copyButton.innerHTML = "copy";
            }, 1000);
        });

        codeBlock.parentNode.before(copyButton);
    });
}

setTimeout(function() {
    addCopyButtonToCodeBlocks();
    }, 100
);