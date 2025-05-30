const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const countdown = document.getElementById("countdown");

if (countdown) {
	const endtime = countdown.dataset.endtime;
	let remaining = updateCountdown();

	const interval = setInterval(() => {
		if (remaining / 1000 < 1) {
			countdown.remove();
			clearInterval(interval);
			location.reload();
			return;
		}

		remaining = updateCountdown();
	}, 1000);

	function updateCountdown() {
		const remaining = endtime - Date.now();
		countdown.textContent = new Date(remaining).toTimeString().slice(3, 8);
		return remaining;
	}
}

if (startBtn) {
	startBtn.addEventListener("click", async () => {
		startBtn.textContent = "starting...";
		startBtn.setAttribute("disabled", "true");

		const res = await fetch("/start_instance", {
			method: "POST",
			credentials: "include",
		});
		const data = await res.json();

		if (!res.ok) {
			reset();
			return alert(data.error);
		}

		location.reload();
	});
}

if (stopBtn) {
	stopBtn.addEventListener("click", async () => {
		stopBtn.textContent = "stopping...";
		stopBtn.setAttribute("disabled", "true");

		const res = await fetch("/stop_instance", {
			method: "POST",
			credentials: "include",
		});
		const data = await res.json();

		if (!res.ok) {
			return alert(data.error);
		}

		location.reload();
	});
}

function reset() {
	startBtn.textContent = "Start Instance";
	startBtn.removeAttribute("disabled");
}
