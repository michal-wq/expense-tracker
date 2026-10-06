const form = document.getElementById("expense-form");
const errorBox = document.getElementById("error");
const result = document.getElementById("result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;

  try {
    const response = await fetch("/api/expenses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: document.getElementById("amount").value,
        category: document.getElementById("category").value,
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
