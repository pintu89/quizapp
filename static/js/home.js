document.addEventListener("DOMContentLoaded", () => {
    // 🔹 Quiz Form
    const quizForm = document.getElementById("quizForm");
    if (quizForm) {
        quizForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const formData = new FormData(quizForm);

            try {
                const response = await fetch(quizForm.action, {
                    method: "POST",
                    body: formData,
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });

                const result = await response.json();

                if (result.status === "success") {
                    result.data.results.forEach(r => {
                        if (r.status === "Correct") {
                            alert(`✅ Correct!\nQ: ${r.question}\nNote: ${r.special_note}`);
                        } else {
                            alert(`❌ Wrong!\nQ: ${r.question}\nYour Answer: ${r.selected}\nCorrect Answer: ${r.correct}\nNote: ${r.special_note}`);
                        }
                    });

                    alert(`🎯 Final Score: ${result.data.score}`);
                } else {
                    alert(`⚠️ Error: ${result.message}`);
                }
            } catch (err) {
                console.error("Error submitting quiz:", err);
                alert("⚠️ Something went wrong!");
            }
        });
    }

    // 🔹 Add Player Form
    const addPlayerForm = document.getElementById("add-player-form");
    if (addPlayerForm) {
        addPlayerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            let response = await fetch("/add_player/", {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            if (response.ok) {
                alert("✅ Player added successfully!");
                this.reset();
            } else {
                alert("❌ Failed to add player");
            }
        });
    }

    // 🔹 Add Bulk Players Form
    const bulkPlayerForm = document.getElementById("add-bulk-player-form");
    if (bulkPlayerForm) {
        bulkPlayerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            let response = await fetch("/add_bulk_player/", {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            if (response.ok) {
                alert("✅ Bulk players uploaded successfully!");
                this.reset();
            } else {
                alert("❌ Failed to upload bulk players");
            }
        });
    }

    // 🔹 Add Bulk Questions Form
    const bulkQuesForm = document.getElementById("bulk_ques_form");
    if (bulkQuesForm) {
        bulkQuesForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(this);

            let response = await fetch("/add_bulk_questions/", {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            if (response.ok) {
                alert("✅ Questions uploaded successfully!");
                this.reset();
            } else {
                alert("❌ Failed to upload questions");
            }
        });
    }
});
