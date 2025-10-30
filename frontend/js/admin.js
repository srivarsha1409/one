// admin.js

document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("resumeFile");
    const resultDiv = document.getElementById("result");
    const loader = document.getElementById("loader");

    uploadForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        resultDiv.innerHTML = "";
        loader.style.display = "block";

        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a resume file to upload.");
            loader.style.display = "none";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:8000/admin/upload_resume", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const result = await response.json();
            const data = result.data || {}; // ✅ Extract real data
            loader.style.display = "none";
            displayResults(data);
        } catch (error) {
            console.error(error);
            loader.style.display = "none";
            resultDiv.innerHTML = `<p style="color:red;">Error uploading or analyzing resume.</p>`;
        }
    });

    function displayResults(data) {
        resultDiv.innerHTML = `
            <h3>📄 Resume Analysis</h3>
            <div class="analysis-section">
                <h4>👤 Personal Information</h4>
                <p><b>Name:</b> ${data.name || "-"}</p>
                <p><b>Email:</b> ${data.email || "-"}</p>
                <p><b>Phone:</b> ${data.phone || "-"}</p>
                <p><b>LinkedIn:</b> ${data.linkedin || "-"}</p>
                <p><b>GitHub:</b> ${data.github || "-"}</p>
            </div>

            <div class="analysis-section">
                <h4>🧠 Summary</h4>
                <p>${data.summary || "No summary available"}</p>
            </div>

            <div class="analysis-section">
                <h4>🧩 Skills Analysis</h4>
                <p><b>Technical:</b> ${data.skills?.technical?.join(", ") || "-"}</p>
                <p><b>Soft:</b> ${data.skills?.soft?.join(", ") || "-"}</p>
            </div>

            <div class="analysis-section">
                <h4>🌐 Languages</h4>
                <p>${data.languages?.join(", ") || "-"}</p>
            </div>

            <div class="analysis-section">
                <h4>📊 ATS Analysis</h4>
                <p><b>ATS Score:</b> ${data.ats_score || "0"}%</p>
                <p><b>Role Match:</b> ${data.role_match || "General"}</p>
                <p><b>Word Count:</b> ${data.word_count || "0"}</p>
                <p><b>Criteria Used:</b> Experience, Skills, Keywords, Summary, Structure</p>
            </div>
        `;
    }
});
