const topLinkButton = document.getElementById("top-link");
window.onscroll = function () {
    if (document.body.scrollTop > 800 || document.documentElement.scrollTop > 800) {
        topLinkButton.style.visibility = "visible";
        topLinkButton.style.opacity = "1";
    } else {
        topLinkButton.style.visibility = "hidden";
        topLinkButton.style.opacity = "0";
    }
};