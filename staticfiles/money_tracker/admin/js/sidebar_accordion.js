document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector("#nav-sidebar");

    if (!sidebar) {
        return;
    }

    const modules = sidebar.querySelectorAll(".module");

    modules.forEach(function (module, index) {
        const title = module.querySelector("caption, h2");

        if (!title) {
            return;
        }

        const titleText = title.textContent.trim();
        const key = "mt_sidebar_module_" + titleText.toLowerCase().replace(/\s+/g, "_");

        title.classList.add("mt-sidebar-title");
        title.setAttribute("role", "button");
        title.setAttribute("tabindex", "0");

        const savedState = localStorage.getItem(key);

        if (savedState === "closed") {
            module.classList.add("mt-sidebar-collapsed");
        } else if (savedState === "open") {
            module.classList.remove("mt-sidebar-collapsed");
        } else {
            // Default: keep Money Tracker open, others collapsed
            if (!titleText.toLowerCase().includes("money tracker")) {
                module.classList.add("mt-sidebar-collapsed");
            }
        }

        function toggleModule() {
            module.classList.toggle("mt-sidebar-collapsed");

            if (module.classList.contains("mt-sidebar-collapsed")) {
                localStorage.setItem(key, "closed");
            } else {
                localStorage.setItem(key, "open");
            }
        }

        title.addEventListener("click", toggleModule);

        title.addEventListener("keydown", function (event) {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                toggleModule();
            }
        });
    });
});