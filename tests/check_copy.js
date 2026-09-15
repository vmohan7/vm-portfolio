#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync(new URL("../script.js", `file://${__filename}`), "utf8");
let clickHandler;
let clipboardValue = "";

const status = { textContent: "" };
const heading = { textContent: "Short bio" };
const bio = {
  textContent: "Vasanth Mohan leads developer relations and product marketing at SambaNova.",
  closest: () => ({ querySelector: () => heading }),
};
const button = {
  dataset: { copyTarget: "short-bio" },
  firstChild: { textContent: "Copy " },
  addEventListener: (event, handler) => {
    if (event === "click") clickHandler = handler;
  },
};

const context = {
  document: {
    querySelector: (selector) => (selector === "#copy-status" ? status : null),
    querySelectorAll: () => [button],
    getElementById: (id) => (id === "short-bio" ? bio : null),
  },
  navigator: {
    clipboard: {
      writeText: async (text) => {
        clipboardValue = text;
      },
    },
  },
  window: {
    isSecureContext: true,
    clearTimeout: () => {},
    setTimeout: () => 1,
  },
};

vm.runInNewContext(source, context, { filename: "script.js" });

(async () => {
  if (typeof clickHandler !== "function") throw new Error("copy click handler was not registered");
  await clickHandler();
  if (clipboardValue !== bio.textContent) throw new Error("bio text was not sent to the clipboard API");
  if (button.dataset.state !== "copied") throw new Error("button did not enter the copied state");
  if (button.firstChild.textContent !== "Copied ") throw new Error("button label was not updated");
  if (status.textContent !== "Short bio copied to clipboard.") throw new Error("live status was not announced");
  console.log("PASS  copy control writes the selected bio");
  console.log("PASS  copy control exposes visible and live-region success feedback");
})().catch((error) => {
  console.error(`FAIL  ${error.message}`);
  process.exitCode = 1;
});
