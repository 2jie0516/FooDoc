const nav = document.getElementById("gnb");
const layer = document.getElementById("layer");
const btnShowMenu = document.getElementById("btn-menu");
const btnHideMenu = document.getElementById("btn-close_menu");

function openMenu() {
    nav.classList.add("active");
    layer.classList.add("active");
}
function closeMenu() {
    nav.classList.remove("active");
    layer.classList.remove("active");
}

(() => {
    btnShowMenu.addEventListener("click", openMenu);
    btnHideMenu.addEventListener("click", closeMenu);
    layer.addEventListener("click", closeMenu);
})();