function degiro(val) {
    if (val.target.value === "Transactions") {
        document.querySelectorAll(".degiroTa").forEach(a=>a.style.display = "block");
        document.querySelectorAll(".degiroTf").forEach(a=>a.style.display = "none");
    } else if (val.target.value === "Transfers") {
        document.querySelectorAll(".degiroTa").forEach(a=>a.style.display = "none");
        document.querySelectorAll(".degiroTf").forEach(a=>a.style.display = "block");
    }
}

function binance(val) {
    if (val.target.value === "CryptoDeposit" | val.target.value === "CryptoWithdrawal" | val.target.value === "FiatDeposit" | val.target.value === "FiatWithdrawal") {
        document.querySelectorAll(".binanceTf").forEach(a=>a.style.display = "block");
        document.querySelectorAll(".binanceTa").forEach(a=>a.style.display = "none");
    } else {
        document.querySelectorAll(".binanceTf").forEach(a=>a.style.display = "none");
        document.querySelectorAll(".binanceTa").forEach(a=>a.style.display = "block");
    }
}

function gateio(val) {
    if (val.target.value === "CryptoDeposit" | val.target.value === "CryptoWithdrawal" | val.target.value === "FiatDeposit" | val.target.value === "FiatWithdrawal") {
        document.querySelectorAll(".gateioTf").forEach(a=>a.style.display = "block");
        document.querySelectorAll(".gateioTa").forEach(a=>a.style.display = "none");
    } else {
        document.querySelectorAll(".gateioTf").forEach(a=>a.style.display = "none");
        document.querySelectorAll(".gateioTa").forEach(a=>a.style.display = "block");
    }
}

function ffts(val) {
    if (val.target.value === "Transactions") {
        document.querySelectorAll(".fftsTa").forEach(a=>a.style.display = "block");
        document.querySelectorAll(".fftsTf").forEach(a=>a.style.display = "none");
    } else if (val.target.value === "Transfers") {
        document.querySelectorAll(".fftsTa").forEach(a=>a.style.display = "none");
        document.querySelectorAll(".fftsTf").forEach(a=>a.style.display = "block");
    }
}