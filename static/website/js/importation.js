function degiro(val) {
    if (val.target.value === "Transactions") {
        document.querySelectorAll(".degiroTa").forEach(a=>a.style.display = "block");
        document.querySelectorAll(".degiroTf").forEach(a=>a.style.display = "none");
    } else if (val.target.value === "Transfers") {
        document.querySelectorAll(".degiroTa").forEach(a=>a.style.display = "none");
        document.querySelectorAll(".degiroTf").forEach(a=>a.style.display = "block");
    }
}