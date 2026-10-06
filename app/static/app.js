const form = document.getElementById("expense-form");
const errorBox = document.getElementById("error");
const result = document.getElementById("result");
const amountInput = document.getElementById("amount");
const categoryInput = document.getElementById("category");
const submitButton = form.querySelector('button[type="submit"]');

for (const input of [amountInput, categoryInput]) {
  input.addEventListener("input", () => input.setCustomValidity(""));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (submitButton.disabled) return;
  errorBox.hidden = true;

  const amount = amountInput.value.replace(",", ".");
  const validAmount = /^[0-9]+(?:\.[0-9]{1,2})?$/.test(amount) && /[1-9]/.test(amount);
  amountInput.setCustomValidity(
    validAmount ? "" : "Enter a positive amount with up to two decimal places. Use a comma or period.",
  );
  categoryInput.setCustomValidity(
    categoryInput.value.trim() ? "" : "Enter a category, not just spaces.",
  );
  if (!form.reportValidity()) return;

  submitButton.disabled = true;
  submitButton.textContent = "Submitting…";

  try {
    const response = await fetch("/api/expenses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount,
        category: categoryInput.value,
        date: document.getElementById("date").value,
      }),
    });

    const body = await response.json().catch(() => null);
    if (response.status !== 201) {
      const labels = { amount: "Amount", category: "Category", date: "Date" };
      const fieldErrors = body?.error?.fields;
      const details = fieldErrors && typeof fieldErrors === "object"
        ? Object.entries(fieldErrors)
          .filter(([, message]) => typeof message === "string")
          .map(([field, message]) => `${labels[field] || field}: ${message}`)
          .join(" ")
        : "";
      const message = typeof body?.error?.message === "string" ? body.error.message : "";
      throw new Error(details || message || `Submission failed (HTTP ${response.status}). Please try again.`);
    }

    const fields = ["amount", "category", "date", "id"];
    if (!body || fields.some((field) => typeof body[field] !== "string")) {
      throw new Error("The server returned an unexpected response. Please try again.");
    }
    for (const field of fields) {
      document.getElementById(`result-${field}`).textContent = body[field];
    }
    result.hidden = false;
  } catch (error) {
    errorBox.textContent = error instanceof TypeError
      ? "Unable to reach the server. Check your connection and try again."
      : error.message;
    errorBox.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Create expense";
  }
});
