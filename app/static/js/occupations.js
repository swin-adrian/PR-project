document.addEventListener("DOMContentLoaded", function() {
    // Get modal elements
    var occupationModal = document.getElementById("occupationModal");
    var modifyModal = document.getElementById("modifyModal");

    // Get open modal buttons
    var openModalBtn = document.getElementById("openModalBtn");
    var closeModalBtns = document.querySelectorAll(".close");

    // Open Add Occupation modal
    openModalBtn.addEventListener("click", function() {
        occupationModal.style.display = "block";
    });

    // Close modals
    closeModalBtns.forEach(function(btn) {
        btn.addEventListener("click", function() {
            occupationModal.style.display = "none";
            modifyModal.style.display = "none";
        });
    });

    // Close modals on outside click
    window.addEventListener("click", function(event) {
        if (event.target == occupationModal) {
            occupationModal.style.display = "none";
        }
        if (event.target == modifyModal) {
            modifyModal.style.display = "none";
        }
    });

    // Listen for modify button clicks
    document.querySelectorAll('.modify-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var occupationId = this.getAttribute('data-occupation-id');
            var occupationName = this.getAttribute('data-occupation-name');
            var anzscoCode = this.getAttribute('data-anzsco-code');
            var industry = this.getAttribute('data-industry');
            var occupationType = this.getAttribute('data-occupation-type');

            // Set the values in the modify form
            document.getElementById('modifyOccupationId').value = occupationId;
            document.getElementById('modifyOccupation').value = occupationName;
            document.getElementById('modifyANZSCOCode').value = anzscoCode;
            document.getElementById('modifyIndustry').value = industry;
            document.getElementById('modifyType').value = occupationType;

            // Open the modify modal
            modifyModal.style.display = 'block';
        });
    });

    // Handle Modify Occupation form submission
    document.getElementById('modifyOccupationForm').addEventListener('submit', function(event) {
        event.preventDefault();

        var occupationId = document.getElementById('modifyOccupationId').value;
        var occupationName = document.getElementById('modifyOccupation').value;
        var anzscoCode = document.getElementById('modifyANZSCOCode').value;
        var industry = document.getElementById('modifyIndustry').value;
        var occupationType = document.getElementById('modifyType').value;

        // Create a form data object
        var formData = new URLSearchParams();
        formData.append('occupation', occupationName);
        formData.append('anzsco_code', anzscoCode);
        formData.append('industry', industry);
        formData.append('occupation_type', occupationType);

        // AJAX request to modify occupation
        fetch(`/modify_occupation_ajax/${occupationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        }).then(response => response.json()).then(data => {
            if (data.success) {
                // Update the table with the new occupation details
                var occupationRow = document.getElementById(`occupation-row-${occupationId}`);
                occupationRow.querySelector('td:nth-child(1)').innerText = occupationName; // Update occupation name
                occupationRow.querySelector('td:nth-child(2)').innerText = anzscoCode; // Update ANZSCO code
                occupationRow.querySelector('td:nth-child(3)').innerText = industry; // Update industry
                occupationRow.querySelector('td:nth-child(4)').innerText = occupationType; // Update occupation type

                alert('Occupation modified successfully!');
                modifyModal.style.display = 'none';
            } else {
                alert('Failed to modify occupation: ' + data.message);
            }
        }).catch(error => console.error('Error:', error));
    });

    // Listen for delete button clicks
    document.querySelectorAll('.delete-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var occupationId = this.getAttribute('data-occupation-id');

            if (confirm('Are you sure you want to delete this occupation?')) {
                // AJAX request to delete occupation
                fetch(`/delete_occupation/${occupationId}`, {
                    method: 'POST'
                }).then(response => response.json()).then(data => {
                    if (data.success) {
                        alert('Occupation deleted successfully!');
                        document.getElementById(`occupation-row-${occupationId}`).remove();
                    } else {
                        alert('Failed to delete occupation.');
                    }
                }).catch(error => console.error('Error:', error));
            }
        });
    });
});

// Function to update occupation summary
function updateOccupationSummary() {
    $.ajax({
        url: "/get_occupation_summary",
        method: "GET",
        success: function(data) {
            $("#occupation-summary").html(`
                <p>Total Occupations: ${data.total_occupations}</p>
                <p>Agriculture: ${data.agriculture_count}</p>
                <p>Beekeeping: ${data.beekeeping_count}</p>
                <p>Other: ${data.other_count}</p>
            `);
        },
        error: function(xhr, status, error) {
            console.error("Failed to fetch occupation summary:", error);
        }
    });
}

$(document).ready(function() {
    updateOccupationSummary();
});
