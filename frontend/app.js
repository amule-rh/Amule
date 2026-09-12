/**
 * aMule — Frontend
 *
 * Handles the initial web application behaviour.
 * API integration will be enabled as the backend evolves.
 */

const state = {
    walletConnected: false,
    resources: []
};


const walletButton = document.getElementById("walletButton");
const searchButton = document.getElementById("searchButton");
const searchInput = document.getElementById("searchInput");
const uploadButton = document.getElementById("uploadButton");
const resourceList = document.getElementById("resourceList");


/* =========================
   WALLET
========================= */

walletButton.addEventListener("click", async () => {

    if (state.walletConnected) {
        disconnectWallet();
        return;
    }

    await connectWallet();
});


async function connectWallet() {

    if (!window.ethereum) {

        showNotification(
            "No compatible wallet detected.",
            "error"
        );

        return;
    }

    try {

        const accounts =
            await window.ethereum.request({
                method: "eth_requestAccounts"
            });

        if (!accounts.length) {
            return;
        }

        state.walletConnected = true;

        const address = accounts[0];

        walletButton.textContent =
            `${address.slice(0, 6)}...${address.slice(-4)}`;

        walletButton.classList.add("connected");

        showNotification(
            "Wallet connected.",
            "success"
        );

    } catch (error) {

        console.error(error);

        showNotification(
            "Wallet connection cancelled.",
            "error"
        );
    }
}


function disconnectWallet() {

    state.walletConnected = false;

    walletButton.textContent =
        "Connect Wallet";

    walletButton.classList.remove("connected");

    showNotification(
        "Wallet disconnected.",
        "success"
    );
}


/* =========================
   SEARCH
========================= */

searchButton.addEventListener(
    "click",
    performSearch
);


searchInput.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Enter") {
            performSearch();
        }

    }
);


function performSearch() {

    const query =
        searchInput.value.trim();

    if (!query) {

        showNotification(
            "Enter something to search.",
            "error"
        );

        searchInput.focus();

        return;
    }

    /*
     * AI semantic search will be connected here.
     */

    showNotification(
        `Searching the aMule network for "${query}"...`,
        "success"
    );

    console.log(
        "aMule search:",
        query
    );
}


/* =========================
   UPLOAD
========================= */

uploadButton.addEventListener(
    "click",
    openUpload
);


function openUpload() {

    showNotification(
        "Resource upload is coming in the next MVP step.",
        "success"
    );
}


/* =========================
   NOTIFICATIONS
========================= */

function showNotification(message, type = "success") {

    const notification =
        document.createElement("div");

    notification.className =
        `notification ${type}`;

    notification.textContent =
        message;

    document.body.appendChild(
        notification
    );

    requestAnimationFrame(() => {
        notification.classList.add("visible");
    });

    setTimeout(() => {

        notification.classList.remove(
            "visible"
        );

        setTimeout(() => {
            notification.remove();
        }, 250);

    }, 3000);
}


/* =========================
   RESOURCE UI
========================= */

function renderResources() {

    if (!state.resources.length) {
        return;
    }

    resourceList.innerHTML = "";

    state.resources.forEach(
        resource => {

            const element =
                document.createElement("div");

            element.className =
                "resource-card";

            element.innerHTML = `
                <div>
                    <strong>
                        ${escapeHtml(resource.name)}
                    </strong>

                    <span>
                        ${escapeHtml(resource.description)}
                    </span>
                </div>

                <button>
                    Acquire
                </button>
            `;

            resourceList.appendChild(
                element
            );
        }
    );
}


/* =========================
   SECURITY
========================= */

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================
   STARTUP
========================= */

console.log(
    "aMule frontend initialized."
);
