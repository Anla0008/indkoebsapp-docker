// This code runs in the browser. Python handles the database on the server.
const toDoList = document.querySelector("#taskList");
const doneList = document.querySelector("#doneList");
const nameInput = document.querySelector("#new-task");
const quantityInput = document.querySelector("#quantity");
const message = document.querySelector("#message");

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || `Serveren svarede med ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function showError(error) {
  message.textContent = error.message || "Noget gik galt. Prøv igen.";
}

function renderItem(item) {
  const li = document.createElement("li");
  li.className = item.is_bought ? "colorDone" : "colorToDo";

  // textContent keeps product names as text, even if they contain HTML signs.
  const label = document.createElement("label");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = Boolean(item.is_bought);
  checkbox.addEventListener("change", async () => {
    try {
      message.textContent = "";
      await api(`/api/items/${item.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_bought: checkbox.checked }),
      });
      await loadItems();
    } catch (error) {
      checkbox.checked = !checkbox.checked;
      showError(error);
    }
  });
  label.append(checkbox, document.createTextNode(` ${item.name} (antal: ${item.quantity})`));

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.textContent = "Slet";
  deleteButton.addEventListener("click", async () => {
    try {
      message.textContent = "";
      await api(`/api/items/${item.id}`, { method: "DELETE" });
      await loadItems();
    } catch (error) {
      showError(error);
    }
  });

  li.append(label, deleteButton);
  (item.is_bought ? doneList : toDoList).appendChild(li);
}

async function loadItems() {
  try {
    const items = await api("/api/items");
    toDoList.replaceChildren();
    doneList.replaceChildren();
    items.forEach(renderItem);
    message.textContent = "";
  } catch (error) {
    showError(error);
  }
}

document.querySelector("#add-task").addEventListener("click", async () => {
  const name = nameInput.value.trim();
  const quantity = Number(quantityInput.value);
  if (!name || !Number.isInteger(quantity) || quantity < 1 || quantity > 9999) {
    message.textContent = "Skriv en vare og et antal mellem 1 og 9999.";
    return;
  }

  try {
    message.textContent = "";
    await api("/api/items", {
      method: "POST",
      body: JSON.stringify({ name, quantity }),
    });
    nameInput.value = "";
    quantityInput.value = "1";
    await loadItems();
    nameInput.focus();
  } catch (error) {
    showError(error);
  }
});

loadItems();
