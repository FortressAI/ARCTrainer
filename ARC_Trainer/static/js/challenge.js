document.addEventListener("DOMContentLoaded", function() {
    class ChallengeProcessor {
        constructor() {
            this.initChallengeButton();
        }

        initChallengeButton() {
            document.getElementById("generate-challenge-btn").addEventListener("click", () => this.generateChallenge());
        }

        generateChallenge() {
            API.request("/api/generate-challenge")
            .then(data => {
                document.getElementById("challenge-output").textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                Logger.error("Challenge Generation Error:", error);
                UIHelpers.showAlert("Failed to generate challenge.", "error");
            });
        }
    }

    new ChallengeProcessor();
});
