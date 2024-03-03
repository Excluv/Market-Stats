const dropdown = document.querySelector(".dropdown");
const dropdown_list = document.querySelector(".dropdown-menu");

dropdown.addEventListener("mouseover", () => {
    dropdown_list.style.display = "block";
})

dropdown.addEventListener("mouseout", () => {
    dropdown_list.style.display = "none";
})

const filterBtn = document.querySelector(".filter-button");
const filterBox = document.querySelector(".filter-box");

filterBtn.addEventListener("click", () => {
    if (filterBox.style.display === "block") {
        filterBox.style.display = "none";
    }
    else {
        filterBox.style.display = "block";
    }
})
