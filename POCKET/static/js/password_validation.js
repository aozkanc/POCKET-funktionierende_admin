document.addEventListener("DOMContentLoaded", function () {
    const password1 = document.getElementById("newPassword1");
    const password2 = document.getElementById("newPassword2");
    const passwordHint1 = document.getElementById("passwordHint1");
    const passwordHint2 = document.getElementById("passwordHint2");

    function validatePassword() {
        let password = password1.value;
        let errors = [];

        if (password.length < 8) {
            errors.push("🔴 Das Passwort muss mindestens 8 Zeichen lang sein.");
        }
        if (!/[A-Za-z]/.test(password)) {
            errors.push("🔴 Das Passwort muss mindestens einen Buchstaben enthalten.");
        }
        if (!/\d/.test(password)) {
            errors.push("🔴 Das Passwort muss mindestens eine Zahl enthalten.");
        }
        if (!/[@$!%*?&]/.test(password)) {
            errors.push("🔴 Das Passwort muss mindestens ein Sonderzeichen (@$!%*?&) enthalten.");
        }

        if (errors.length > 0) {
            passwordHint1.innerHTML = errors.join("<br>");
            passwordHint1.style.color = "red";
            return false;
        } else {
            passwordHint1.innerHTML = "✅ Passwort ist gültig.";
            passwordHint1.style.color = "green";
            return true;
        }
    }

    function validatePasswordMatch() {
        if (password1.value !== password2.value) {
            passwordHint2.innerHTML = "🔴 Die Passwörter stimmen nicht überein.";
            passwordHint2.style.color = "red";
            return false;
        } else {
            passwordHint2.innerHTML = "✅ Passwörter stimmen überein.";
            passwordHint2.style.color = "green";
            return true;
        }
    }

    password1.addEventListener("input", validatePassword);
    password2.addEventListener("input", validatePasswordMatch);
});
