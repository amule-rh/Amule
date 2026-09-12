/**
 * aMule — Frontend Application
 *
 * The web interface for the aMule network.
 *
 * Current MVP:
 * - Wallet detection
 * - Network search interaction
 * - Resource file selection
 * - Resource state management
 *
 * Backend upload and blockchain transactions
 * will be connected in subsequent iterations.
 */


const state = {
    walletConnected: false,
    walletAddress: null,
    resources: []
};


/* =========================
   DOM
========================= */

const walletButton =
    document.getElementById("walletButton");

const searchButton =
    document.getElementById("searchButton");

const searchInput =
    document.getElementById("searchInput");

const uploadButton =
    document.getElementById("uploadButton");

const emptyUploadButton =
    document.getElementById("emptyUploadButton");

const fileInput =
    document.getElementById("fileInput");

const resourceList =
    document.getElementById("resourceList");

const resourceCount =
    document.getElementById("resourceCount");


/* =========================
   WALLET
========================= */

walletButton.addEventListener(
    "click",
    handleWallet
);


async function handleWallet() {

    if (state.walletConnected) {
        disconnectWallet();
        return;
    }

    await connectWallet();
}


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


        if (!accounts || accounts.length === 0) {
            return;
        }


        state.walletConnected = true;
        state.walletAddress = accounts[0];


        updateWalletButton();


        showNotification(
            "Wallet connected.",
            "success"
        );

    } catch (error) {

        console.error(
            "Wallet connection failed:",
            error
        );

        showNotification(
            "Wallet connection cancelled.",
            "error"
        );
    }
}


function disconnectWallet() {

    state.walletConnected = false;
    state.walletAddress = null;

    updateWalletButton();

    showNotification(
        "Wallet disconnected.",
        "success"
    );
}


function updateWalletButton() {

    if (
        state.walletConnected &&
        state.walletAddress
    ) {

        const address =
            state.walletAddress;

        walletButton.textContent =
            `${address.slice(0, 6)}...${address.slice(-4)}`;

        walletButton.classList.add(
            "connected"
        );

        return;
    }


    walletButton.textContent =
        "Connect Wallet";

    walletButton.classList.remove(
        "connected"
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
    event => {

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
     * AI semantic search will be connected
     * to the aMule API here.
     */

    console.log(
        "aMule search query:",
        query
    );


    showNotification(
        `Searching for "${query}"...`,
        "success"
    );
}


/* =========================
   RESOURCE UPLOAD
========================= */

uploadButton.addEventListener(
    "click",
    openUpload
);


emptyUploadButton.addEventListener(
    "click",
    openUpload
);


fileInput.addEventListener(
    "change",
    handleFileSelection
);


function openUpload() {

    fileInput.value = "";

    fileInput.click();
}


function handleFileSelection(event) {

    const file =
        event.target.files[0];


    if (!file) {
        return;
    }


    const resource = {
        name: file.name,
        size: file.size,
        type: file.type || "application/octet-stream",
        file: file
    };


    state.resources.push(
        resource
    );


    updateResourceCount();

    renderResources();


    showNotification(
        `${file.name} selected.`,
        "success"
    );


    console.log(
        "Selected resource:",
        {
            name: file.name,
            size: file.size,
            type: file.type
        }
    );


    /*
     * NEXT STEP:
     *
     * Send the file to:
     *
     * POST /resources/upload
     *
     * The backend will then:
     *
     * 1. Encrypt the resource
     * 2. Calculate its content hash
     * 3. Store the encrypted blob
     * 4. Return the Resource ID
     */
}


/* =========================
   RESOURCE LIST
========================= */

function renderResources() {

    if (state.resources.length === 0) {

        resourceList.innerHTML = `
            <div class="empty-state">

                <div class="empty-icon">
                    🫏
                </div>

                <h3>No resources yet</h3>

                <p>
                    Be the first provider to bring intelligence
                    to the aMule network.
                </p>

                <button
                    id="emptyUploadButton"
                    type="button"
                >
                    Upload the first resource
                </button>

            </div>
        `;


        document
            .getElementById("emptyUploadButton")
            .addEventListener(
                "click",
                openUpload
            );

        return;
    }


    resourceList.innerHTML = "";


    state.resources.forEach(
        (resource, index) => {

            const card =
                document.createElement("article");

            card.className =
                "resource-card";


            card.innerHTML = `
                <div class="resource-info">

                    <strong>
                        ${escapeHtml(resource.name)}
                    </strong>

                    <span>
                        ${formatBytes(resource.size)}
                    </span>

                </div>

                <button
                    type="button"
                    data-resource-index="${index}"
                >
                    Acquire
                </button>
            `;


            resourceList.appendChild(
                card
            );
        }
    );
}


/* =========================
   RESOURCE COUNTER
========================= */

function updateResourceCount() {

    resourceCount.textContent =
        state.resources.length;
}


/* =========================
   UTILITIES
========================= */

function formatBytes(bytes) {

    if (bytes === 0) {
        return "0 Bytes";
    }


    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB",
        "TB"
    ];


    const exponent =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );


    const value =
        bytes /
        Math.pow(1024, exponent);


    return `${value.toFixed(
        exponent === 0 ? 0 : 2
    )} ${units[exponent]}`;
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================
   NOTIFICATIONS
========================= */

function showNotification(
    message,
    type = "success"
) {

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

        notification.classList.add(
            "visible"
        );

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
   STARTUP
========================= */

renderResources();
updateResourceCount();

console.log(
    "aMule frontend initialized."
);
