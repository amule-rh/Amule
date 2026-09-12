/**
 * aMule — Frontend Application
 *
 * Artificial Mule
 * The decentralized mule for AI intelligence.
 *
 * Current MVP:
 * - Wallet connection
 * - Resource search
 * - File selection
 * - Resource upload
 * - Upload status
 * - Resource rendering
 *
 * Future:
 * - Semantic AI search
 * - P2P retrieval
 * - On-chain payments
 * - Access control
 * - Agent wallets
 */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL = "";


/* =========================================================
   APPLICATION STATE
========================================================= */

const state = {

    walletConnected: false,

    walletAddress: null,

    resources: [],

    searching: false,

    uploading: false

};


/* =========================================================
   DOM ELEMENTS
========================================================= */

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


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);


function initialize() {

    bindEvents();

    renderResources();

    updateResourceCount();

    detectWallet();

    console.log(
        "aMule frontend initialized."
    );
}


/* =========================================================
   EVENTS
========================================================= */

function bindEvents() {

    if (walletButton) {

        walletButton.addEventListener(
            "click",
            handleWallet
        );

    }


    if (searchButton) {

        searchButton.addEventListener(
            "click",
            performSearch
        );

    }


    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            event => {

                if (event.key === "Enter") {
                    performSearch();
                }

            }
        );

    }


    if (uploadButton) {

        uploadButton.addEventListener(
            "click",
            openUpload
        );

    }


    if (emptyUploadButton) {

        emptyUploadButton.addEventListener(
            "click",
            openUpload
        );

    }


    if (fileInput) {

        fileInput.addEventListener(
            "change",
            handleFileSelection
        );

    }

}


/* =========================================================
   WALLET
========================================================= */

async function detectWallet() {

    if (!window.ethereum) {
        return;
    }


    try {

        const accounts =
            await window.ethereum.request({
                method: "eth_accounts"
            });


        if (
            accounts &&
            accounts.length > 0
        ) {

            state.walletConnected = true;

            state.walletAddress =
                accounts[0];

            updateWalletButton();

        }

    } catch (error) {

        console.error(
            "Wallet detection failed:",
            error
        );

    }

}


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


        if (
            !accounts ||
            accounts.length === 0
        ) {
            return;
        }


        state.walletConnected = true;

        state.walletAddress =
            accounts[0];


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


/* =========================================================
   SEARCH
========================================================= */

async function performSearch() {

    if (state.searching) {
        return;
    }


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


    state.searching = true;

    setSearchLoading(true);


    try {

        /*
         * Semantic AI search will eventually call:
         *
         * GET /search?q=...
         *
         * For now we search the resources
         * already loaded in the browser.
         */

        const results =
            localSearch(query);


        if (results.length === 0) {

            showNotification(
                "No matching intelligence found.",
                "error"
            );

        } else {

            renderResources(results);

            showNotification(
                `${results.length} resource(s) found.`,
                "success"
            );

        }


    } catch (error) {

        console.error(
            "Search failed:",
            error
        );


        showNotification(
            "Search failed.",
            "error"
        );


    } finally {

        state.searching = false;

        setSearchLoading(false);

    }

}


function localSearch(query) {

    const normalizedQuery =
        query.toLowerCase();


    return state.resources.filter(
        resource => {

            const name =
                resource.name.toLowerCase();


            const type =
                resource.type.toLowerCase();


            return (
                name.includes(normalizedQuery) ||
                type.includes(normalizedQuery)
            );

        }
    );

}


function setSearchLoading(isLoading) {

    if (!searchButton) {
        return;
    }


    if (isLoading) {

        searchButton.disabled = true;

        searchButton.textContent =
            "Searching...";

    } else {

        searchButton.disabled = false;

        searchButton.textContent =
            "Search";

    }

}


/* =========================================================
   RESOURCE UPLOAD
========================================================= */

function openUpload() {

    if (!fileInput) {
        return;
    }


    if (state.uploading) {
        return;
    }


    fileInput.value = "";

    fileInput.click();

}


async function handleFileSelection(event) {

    const file =
        event.target.files[0];


    if (!file) {
        return;
    }


    await uploadResource(file);

}


async function uploadResource(file) {

    if (state.uploading) {
        return;
    }


    state.uploading = true;

    setUploadLoading(true);


    showNotification(
        `Uploading ${file.name}...`,
        "success"
    );


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/resources/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );


        let result = null;


        try {

            result =
                await response.json();

        } catch {

            result = null;

        }


        if (!response.ok) {

            const message =
                result?.detail ||
                "Unable to upload resource.";


            throw new Error(
                message
            );

        }


        const resource = {

            name:
                result.filename ||
                file.name,

            size:
                result.size ||
                file.size,

            type:
                result.content_type ||
                file.type ||
                "application/octet-stream",

            resourceId:
                result.resource_id,

            key:
                result.key,

            status:
                "stored"

        };


        state.resources.push(
            resource
        );


        updateResourceCount();

        renderResources();


        showNotification(
            `${file.name} is now stored in aMule.`,
            "success"
        );


        console.log(
            "aMule resource created:",
            {
                resourceId:
                    resource.resourceId,

                filename:
                    resource.name
            }
        );


    } catch (error) {

        console.error(
            "aMule upload failed:",
            error
        );


        showNotification(
            error.message ||
            "Unable to upload resource.",
            "error"
        );


    } finally {

        state.uploading = false;

        setUploadLoading(false);

    }

}


function setUploadLoading(isLoading) {

    if (!uploadButton) {
        return;
    }


    if (isLoading) {

        uploadButton.disabled = true;

        uploadButton.textContent =
            "Uploading...";

    } else {

        uploadButton.disabled = false;

        uploadButton.textContent =
            "+ Upload Resource";

    }

}


/* =========================================================
   RESOURCE RENDERING
========================================================= */

function renderResources(
    resources = state.resources
) {

    if (!resourceList) {
        return;
    }


    if (!resources.length) {

        resourceList.innerHTML = `
            <div class="empty-state">

                <div class="empty-icon">
                    🫏
                </div>

                <h3>No resources yet</h3>

                <p>
                    Be the first provider to bring
                    intelligence to the aMule network.
                </p>

                <button
                    id="emptyUploadButton"
                    type="button"
                >
                    Upload the first resource
                </button>

            </div>
        `;


        const button =
            document.getElementById(
                "emptyUploadButton"
            );


        if (button) {

            button.addEventListener(
                "click",
                openUpload
            );

        }


        return;
    }


    resourceList.innerHTML = "";


    resources.forEach(
        (resource, index) => {

            const card =
                document.createElement(
                    "article"
                );


            card.className =
                "resource-card";


            card.innerHTML = `

                <div class="resource-info">

                    <strong>
                        ${escapeHtml(
                            resource.name
                        )}
                    </strong>

                    <span>
                        ${formatBytes(
                            resource.size
                        )}
                    </span>

                    ${
                        resource.resourceId
                            ? `
                                <small>
                                    ${escapeHtml(
                                        shortenId(
                                            resource.resourceId
                                        )
                                    )}
                                </small>
                            `
                            : ""
                    }

                </div>

                <button
                    type="button"
                    data-resource-index="${index}"
                >
                    Acquire
                </button>

            `;


            const acquireButton =
                card.querySelector(
                    "button"
                );


            acquireButton.addEventListener(
                "click",
                () => {

                    handleAcquire(
                        resource
                    );

                }
            );


            resourceList.appendChild(
                card
            );

        }
    );

}


/* =========================================================
   RESOURCE ACQUISITION
========================================================= */

function handleAcquire(resource) {

    if (!resource) {
        return;
    }


    showNotification(
        "Resource acquisition will be enabled with the marketplace layer.",
        "success"
    );


    console.log(
        "Acquire resource:",
        resource
    );

}


/* =========================================================
   RESOURCE COUNTER
========================================================= */

function updateResourceCount() {

    if (!resourceCount) {
        return;
    }


    resourceCount.textContent =
        state.resources.length;

}


/* =========================================================
   NOTIFICATIONS
========================================================= */

function showNotification(
    message,
    type = "success"
) {

    const notification =
        document.createElement(
            "div"
        );


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


/* =========================================================
   UTILITIES
========================================================= */

function formatBytes(bytes) {

    if (
        !bytes ||
        bytes === 0
    ) {

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
        Math.min(
            Math.floor(
                Math.log(bytes) /
                Math.log(1024)
            ),
            units.length - 1
        );


    const value =
        bytes /
        Math.pow(
            1024,
            exponent
        );


    return `${value.toFixed(
        exponent === 0 ? 0 : 2
    )} ${units[exponent]}`;

}


function shortenId(id) {

    if (!id) {
        return "";
    }


    if (id.length <= 18) {
        return id;
    }


    return `${id.slice(
        0,
        10
    )}...${id.slice(-8)}`;

}


function escapeHtml(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


/* =========================================================
   WALLET EVENTS
========================================================= */

if (window.ethereum) {

    window.ethereum.on(
        "accountsChanged",
        accounts => {

            if (
                !accounts ||
                accounts.length === 0
            ) {

                state.walletConnected = false;

                state.walletAddress = null;

            } else {

                state.walletConnected = true;

                state.walletAddress =
                    accounts[0];

            }


            updateWalletButton();

        }
    );

}
