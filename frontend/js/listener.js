/**
 * Listener: enables/disables the Translate button based on source field content.
 * No product/domain logic — only input state.
 * For N fields: attach similar logic per field or use a single handler that checks
 * all source fields (e.g. querySelectorAll('.source-text')) and enables button
 * when at least one has non-empty trimmed value.
 */

const sourceField = document.getElementById("source-text");
const translateBtn = document.getElementById("translate-btn");

if (sourceField && translateBtn) {
  function updateButtonState() {
    const hasText = sourceField.value.trim().length > 0;
    translateBtn.disabled = !hasText;
  }

  sourceField.addEventListener("input", updateButtonState);
  sourceField.addEventListener("change", updateButtonState);
  updateButtonState();
}
