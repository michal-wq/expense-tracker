const form = document.getElementById("expense-form");
const errorBox = document.getElementById("error");
const result = document.getElementById("result");
const amountInput = document.getElementById("amount");
const categoryInput = document.getElementById("category");

for (const input of [amountInput, categoryInput]) {
  input.addEventListener("input", () => input.setCustomValidity(""));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
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

    if (response.status !== 201) {
      throw new Error("Submission failed.");
    }

    const expense = await response.json();
    for (const field of ["amount", "category", "date", "id"]) {
      document.getElementById(`result-${field}`).textContent = expense[field];
    }
    result.hidden = false;
  } catch {
    errorBox.textContent = "Could not submit the expense. Please check your input and try again.";
    errorBox.hidden = false;
  }
});
