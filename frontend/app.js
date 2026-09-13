const resources = [];

const resourceCount = document.getElementById("resourceCount");
const resourcesEl = document.getElementById("resources");
const fileInput = document.getElementById("fileInput");
const connectBtn = document.getElementById("connect");

function render() {
  resourceCount.textContent = resources.length;

  if (!resources.length) {
    resourcesEl.className = "empty";
    resourcesEl.innerHTML = `
      <img src="/assets/amule-mascot.png" alt="">
      <h3>No resources indexed yet</h3>
      <p>Upload a resource to create the first aMule resource.</p>`;
    return;
  }

  resourcesEl.className = "resource-list";
  resourcesEl.innerHTML = resources.map(r => `
    <article class="resource">
      <strong>${escapeHtml(r.filename)}</strong>
      <small>${escapeHtml(r.contentType)} · ${r.size} bytes</small>
      <code>${escapeHtml(r.resourceId)}</code>
    </article>`).join("");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));
}

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  const body = new FormData();
  body.append("file", file);

  try {
    const response = await fetch("/resources/upload", {
      method: "POST",
      body
    });

    if (!response.ok) throw new Error(await response.text());

    const result = await response.json();
    resources.unshift(result);
    render();
  } catch (error) {
    alert(`Upload failed: ${error.message}`);
  } finally {
    fileInput.value = "";
  }
});

connectBtn.addEventListener("click", async () => {
  if (!window.ethereum) {
    alert("Install an EVM wallet such as MetaMask to connect.");
    return;
  }

  try {
    const accounts = await window.ethereum.request({
      method: "eth_requestAccounts"
    });
    connectBtn.textContent = accounts[0]
      ? `${accounts[0].slice(0, 6)}…${accounts[0].slice(-4)}`
      : "Connect Wallet";
  } catch {
    // User rejected connection.
  }
});

render();
