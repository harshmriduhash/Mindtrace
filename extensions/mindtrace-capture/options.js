document.addEventListener("DOMContentLoaded", async () => {
  const stored = await chrome.storage.sync.get({
    apiBase: "http://localhost:8000/api/v1",
    token: "",
  });
  document.getElementById("apiBase").value = stored.apiBase;
  document.getElementById("token").value = stored.token;

  document.getElementById("save").addEventListener("click", async () => {
    await chrome.storage.sync.set({
      apiBase: document.getElementById("apiBase").value.trim(),
      token: document.getElementById("token").value.trim(),
    });
    document.getElementById("status").textContent = "Saved.";
  });
});
