const flightListEl = document.getElementById("flightList");
const flightCountEl = document.getElementById("flightCount");

// Fetch and render flights
async function loadFlights() {
    try {
        const res = await fetch("/api/flights");
        const flights = await res.json();

        flightListEl.innerHTML = "";

        flights.forEach(f => {
            const tr = document.createElement("tr");

            const tdNo = document.createElement("td");
            tdNo.textContent = f.flight_no || "N/A";

            const tdRoute = document.createElement("td");
            tdRoute.textContent = `${f.source || "?"} → ${f.destination || "?"}`;

            const tdStatus = document.createElement("td");
            tdStatus.textContent = f.status || "Unknown";

            const tdFuel = document.createElement("td");
            tdFuel.textContent = (f.fuel !== undefined ? f.fuel : "—") + "%";

            const tdActions = document.createElement("td");
            const delBtn = document.createElement("button");
            delBtn.textContent = "Delete";
            delBtn.style.padding = "6px 10px";
            delBtn.style.borderRadius = "8px";
            delBtn.style.border = "1px solid #ef4444";
            delBtn.style.background = "transparent";
            delBtn.style.color = "#ef4444";
            delBtn.style.cursor = "pointer";

            delBtn.onmouseenter = () => {
                delBtn.style.background = "#ef4444";
                delBtn.style.color = "#020617";
            };
            delBtn.onmouseleave = () => {
                delBtn.style.background = "transparent";
                delBtn.style.color = "#ef4444";
            };

            delBtn.onclick = () => deleteFlight(f.flight_no);

            tdActions.appendChild(delBtn);

            tr.appendChild(tdNo);
            tr.appendChild(tdRoute);
            tr.appendChild(tdStatus);
            tr.appendChild(tdFuel);
            tr.appendChild(tdActions);

            flightListEl.appendChild(tr);
        });

        // Update badge
        if (flightCountEl) {
            flightCountEl.textContent = `${flights.length} flights`;
        }

    } catch (err) {
        console.error("Failed to load flights:", err);
        flightListEl.innerHTML = `
      <tr>
        <td colspan="5">Error loading flights</td>
      </tr>
    `;
    }
}

// Delete flight
async function deleteFlight(flightNo) {
    if (!confirm(`Delete flight ${flightNo}?`)) return;

    const res = await fetch("/api/flights", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ flight_no: flightNo })
    });

    const data = await res.json();

    if (res.ok) {
        // Refresh list
        loadFlights();
    } else {
        alert(data.error || "Failed to delete flight");
    }
}

// Optional: expose simulate helper here too
async function simulate() {
    const res = await fetch("/api/simulate", { method: "POST" });
    const data = await res.json();
    alert(data.message || "Simulation triggered");
    loadFlights(); // refresh after simulation
}

// Load on page start
document.addEventListener("DOMContentLoaded", () => {
    loadFlights();
});