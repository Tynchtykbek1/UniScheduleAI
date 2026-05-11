(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        const alerts = document.querySelectorAll(".alert");
        alerts.forEach(function (alert) {
            window.setTimeout(function () {
                if (window.bootstrap && window.bootstrap.Alert) {
                    window.bootstrap.Alert.getOrCreateInstance(alert).close();
                } else {
                    alert.remove();
                }
            }, 5000);
        });

        const forms = document.querySelectorAll("form");
        forms.forEach(function (form) {
            form.addEventListener("submit", function (event) {
                const action = (form.getAttribute("action") || "").toLowerCase();

                if (action.includes("delete")) {
                    const confirmed = window.confirm("Are you sure you want to delete this item?");
                    if (!confirmed) {
                        event.preventDefault();
                        return;
                    }
                }

                const loadingButton = form.querySelector("button[type='submit'][data-loading-text]");
                if (loadingButton) {
                    loadingButton.dataset.originalText = loadingButton.textContent;
                    loadingButton.textContent = loadingButton.dataset.loadingText;
                    loadingButton.disabled = true;
                    loadingButton.classList.add("is-loading");
                }
            });
        });
    });
})();
