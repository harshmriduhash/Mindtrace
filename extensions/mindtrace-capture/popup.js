async function getConfig() {
  return chrome.storage.sync.get({
    apiBase: "http://localhost:8000/api/v1",
    token: "",
  });
}

async function currentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function getSelection(tabId) {
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => window.getSelection()?.toString() || "",
  });
  return result || "";
}

document.addEventListener("DOMContentLoaded", async () => {
  const titleEl = document.getElementById("page-title");
  const textEl = document.getElementById("text");
  const statusEl = document.getElementById("status");
  const tab = await currentTab();
  titleEl.textContent = tab?.title || "Current page";
  if (tab?.id) {
    try {
      textEl.value = await getSelection(tab.id);
    } catch {
      /* restricted pages */
    }
  }

  document.getElementById("save").addEventListener("click", async () => {
    statusEl.textContent = "Saving…";
    const { apiBase, token } = await getConfig();
    if (!token) {
      statusEl.textContent = "Set your extension token in settings first.";
      return;
    }
    const body = {
      title: tab?.title || "Captured page",
      url: tab?.url || null,
      selected_text: textEl.value || null,
      fetch_page: document.getElementById("fetch-page").checked,
    };
    try {
      const res = await fetch(`${apiBase.replace(/\/$/, "")}/extension/capture`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        statusEl.textContent = data?.error?.message || `Failed (${res.status})`;
        return;
      }
      statusEl.textContent = `Saved. Concepts ready: ${data.concepts_ready ? "yes" : "pending"}. Open Learn to approve.`;
    } catch (err) {
      statusEl.textContent = String(err);
    }
  });
});
