chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_CURRENT_TAB_URL") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      const url =
        tab && tab.url && !tab.url.startsWith("chrome-extension://") ? tab.url : null;
        sendResponse({ url });
    });
    return true;
  }
});
