chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_CURRENT_TAB_URL") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      const url =
        tab && tab.url && !tab.url.startsWith("chrome-extension://")
          ? tab.url
          : null;
      sendResponse({ url });
    });
    return true;
  }
});

chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const tab = await chrome.tabs.get(activeInfo.tabId);
  if (tab.url && !tab.url.startsWith("chrome-extension://")) {
    chrome.runtime.sendMessage({ type: "TAB_UPDATED", url: tab.url });
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.active && changeInfo.status === "complete") {
    if (tab.url && !tab.url.startsWith("chrome-extension://")) {
      chrome.runtime.sendMessage({ type: "TAB_UPDATED", url: tab.url });
    }
  }
  if (changeInfo.status === "complete" && /^https?:/.test(tab.url)) {
    chrome.runtime.sendMessage({ type: "RESET_SCAN_BUTTON" });
  }
});

chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "src/sidepanel/index.html",
    enabled: true,
  });
  chrome.sidePanel.open({ tabId: tab.id });
});