async function loadFlights() {
    const res = await fetch("/api/flights");
    const data = await res.json();

    const list = document.getElementById("flightList");
    list.innerHTML = "";

    data.forEach(f => {
        const li = document.createElement("li");
        li.textContent = `${f.flight_no} | ${f.source} -> ${f.destination} | ${f.status} | Fuel: ${f.fuel}`;
        list.appendChild(li);
    });
}

async function addFlight() {
    const flight_no = document.getElementById("flight_no").value;
    const source = document.getElementById("source").value;
    const destination = document.getElementById("destination").value;
    const status = document.getElementById("status").value;
    const fuel = document.getElementById("fuel").value;

    const res = await fetch("/api/flights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ flight_no, source, destination, status, fuel })
    });

    if (res.ok) {
        loadFlights();
    } else {
        alert("Failed to add flight");
    }
}

async function simulate() {
    const res = await fetch("/api/simulate", { method: "POST" });
    if (res.ok) {
        loadFlights();
    } else {
        alert("Simulation failed");
    }
}

loadFlights();