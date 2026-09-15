(() => {
  "use strict";

  const status = document.querySelector("#copy-status");
  const buttons = document.querySelectorAll("[data-copy-target]");
  let resetTimer;

  function legacyCopy(text) {
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    field.style.pointerEvents = "none";
    document.body.appendChild(field);
    field.select();

    let copied = false;
    try {
      copied = document.execCommand("copy");
    } catch (_) {
      copied = false;
    }

    field.remove();
    return copied;
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (_) {
        return legacyCopy(text);
      }
    }
    return legacyCopy(text);
  }

  function announce(button, message, copied) {
    window.clearTimeout(resetTimer);
    status.textContent = message;
    button.dataset.state = copied ? "copied" : "failed";
    button.firstChild.textContent = copied ? "Copied " : "Copy ";

    resetTimer = window.setTimeout(() => {
      status.textContent = "";
      button.dataset.state = "";
      button.firstChild.textContent = "Copy ";
    }, 3200);
  }

  buttons.forEach((button) => {
    button.addEventListener("click", async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) {
        announce(button, "That bio is unavailable.", false);
        return;
      }

      const copied = await copyText(target.textContent.trim());
      announce(
        button,
        copied ? `${target.closest(".bio-block").querySelector("h4").textContent.trim()} copied to clipboard.` : "Copy failed. Select the bio text and copy it manually.",
        copied
      );
    });
  });
})();
