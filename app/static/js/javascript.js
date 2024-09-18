document.addEventListener('DOMContentLoaded', function() {
  let currentTab = 0; // Set the initial tab
  showTab(currentTab); // Display the current tab

  function showTab(n) {
      let x = document.getElementsByClassName("tab");

      // Hide all tabs
      for (let i = 0; i < x.length; i++) {
          x[i].style.display = "none";
      }

      // Display the specified tab
      x[n].style.display = "block";

      // Hide/Show buttons based on the current tab
      document.getElementById("prevBtn").style.display = n === 0 ? "none" : "inline";
      document.getElementById("nextBtn").innerHTML = n === (x.length - 1) ? "Submit" : "Next";

      // Update the step indicators
      fixStepIndicator(n);
  }

  function nextPrev(n) {
      let x = document.getElementsByClassName("tab");

      // Validate the current tab before moving forward, skip Page 4 validation
      if (n === 1 && !validateForm()) return false;

      // Hide the current tab
      x[currentTab].style.display = "none";

      // Increase or decrease the current tab by n
      currentTab += n;

      // If you have reached the end of the form, submit the form
      if (currentTab >= x.length) {
          document.querySelector("form").submit(); // Submit the form
          return false;
      }

      // Otherwise, display the correct tab
      showTab(currentTab);
  }

  function validateForm() {
      let x, y, i, valid = true;
      x = document.getElementsByClassName("tab");

      // Skip validation for Page 4 (assuming Page 4 is at index 3)
      if (currentTab === 3) {
          return true; // Skip validation for this page
      }

      // Validate the inputs of the current tab
      y = x[currentTab].getElementsByTagName("input");
      for (i = 0; i < y.length; i++) {
          if (y[i].value === "" && y[i].type === "text") {
              y[i].className += " invalid"; // Mark the field as invalid
              valid = false;
          }
      }

      return valid; // return the valid status
  }

  function fixStepIndicator(n) {
      let i, x = document.getElementsByClassName("step");
      for (i = 0; i < x.length; i++) {
          x[i].className = x[i].className.replace(" active", "");
      }
      x[n].className += " active";

      for (i = 0; i < n; i++) {
          x[i].className += " finish";
      }
  }

  function fetchOccupations(type) {
      fetch('/get_occupations', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ type: type })
      })
      .then(response => response.json())
      .then(data => {
          populateOccupations(data);
      })
      .catch(error => {
          console.error('Error fetching occupations:', error);
      });
  }

  function populateOccupations(occupations) {
      let dropdown = document.getElementById('occupations');
      let selectedValue = dropdown.value; // Preserve selected value
      console.log('Selected value before update:', selectedValue);

      // Clear existing options
      dropdown.innerHTML = '<option value="">-- Select Occupation --</option>'; 

      if (occupations.length > 0) {
          occupations.forEach(occupation => {
              let option = document.createElement('option');
              option.value = occupation;
              option.textContent = occupation;
              dropdown.appendChild(option);
          });
      } else {
          let option = document.createElement('option');
          option.value = '';
          option.textContent = 'No occupations found';
          dropdown.appendChild(option);
      }

      // Restore selected value
      dropdown.value = selectedValue;
      console.log('Selected value after update:', dropdown.value);
  }

  function handleOccupationListChange() {
      let selectedSubclass = document.querySelector('input[name="visa-subclass"]:checked');
      let occupationType = '';

      if (selectedSubclass) {
          if (selectedSubclass.value === '190') {
              let selectedList = document.querySelector('input[name="occupation-list-190"]:checked');
              occupationType = selectedList ? selectedList.value : '';
              fetchOccupations(occupationType);
          } else if (selectedSubclass.value === '491') {
              let selectedList = document.querySelector('input[name="occupation-list-491"]:checked');
              occupationType = selectedList ? selectedList.value : '';
              fetchOccupations(occupationType);
          } else if (selectedSubclass.value === '189') {
              occupationType = 'MLTSSL'; // Automatically set to MLTSSL for subclass 189
              fetchOccupations(occupationType);
          }
      }
  }

  // Event listener for form changes
  document.querySelector('form').addEventListener('change', function(e) {
      let selectedSubclass = document.querySelector('input[name="visa-subclass"]:checked');
      document.querySelectorAll('.occupation-section').forEach(section => section.style.display = 'none');
      document.getElementById('occupation-dropdown-section').style.display = 'block'; // Always show dropdown

      if (selectedSubclass) {
          if (selectedSubclass.value === '189') {
              document.getElementById('question-189').style.display = 'block';
              document.getElementById('occupation-dropdown-section').style.display = 'block'; // Ensure dropdown is visible
              handleOccupationListChange(); // Automatically set to MLTSSL
          } else if (selectedSubclass.value === '190') {
              document.getElementById('question-190').style.display = 'block';
              handleOccupationListChange();
          } else if (selectedSubclass.value === '491') {
              document.getElementById('question-491').style.display = 'block';
              handleOccupationListChange();
          }
      }

      // Handle English test score sections
      if (e.target.name === "english-test") {
          const scoreSections = document.querySelectorAll('.score-section');
          scoreSections.forEach(section => section.style.display = "none");

          const selectedTest = e.target.value;
          if (selectedTest === "IELTS") {
              document.getElementById("ielts-score").style.display = "block";
          } else if (selectedTest === "PTE") {
              document.getElementById("pte-score").style.display = "block";
          } else if (selectedTest === "CAE") {
              document.getElementById("cae-score").style.display = "block";
          } else if (selectedTest === "OET") {
              document.getElementById("oet-score").style.display = "block";
          } else if (selectedTest === "TOEFL") {
              document.getElementById("toefl-score").style.display = "block";
          }
      }
  });

  document.getElementById("prevBtn").addEventListener("click", function() {
      nextPrev(-1);
  });

  document.getElementById("nextBtn").addEventListener("click", function() {
      nextPrev(1);
  });
});

        // Function to fetch the country list from RestCountries API and populate both dropdowns
        async function populateDropdowns() {
          try {
              // Fetching country data from RestCountries API
              const response = await fetch('https://restcountries.com/v3.1/all');
              const countries = await response.json();

              // Sorting countries by name
              countries.sort((a, b) => a.name.common.localeCompare(b.name.common));

              // Getting the dropdown elements
              const countryDropdown = document.getElementById('current-country');
              const nationalityDropdown = document.getElementById('nationality');

              // Loop through the country data and populate both dropdowns
              countries.forEach(country => {
                  const countryName = country.name.common;

                  // Create an <option> element for the country
                  const countryOption = document.createElement('option');
                  countryOption.value = countryName.toLowerCase();  // Set the value as lowercase of country name
                  countryOption.textContent = countryName;          // Set the visible text as the country name
                  
                  // Clone the option for use in the nationality dropdown
                  const nationalityOption = countryOption.cloneNode(true);

                  // Append the options to both dropdowns
                  countryDropdown.appendChild(countryOption);
                  nationalityDropdown.appendChild(nationalityOption);
              });
          } catch (error) {
              console.error('Error fetching countries:', error);
          }
      }

      // Populate dropdowns on page load
      document.addEventListener('DOMContentLoaded', populateDropdowns);

      document.addEventListener('DOMContentLoaded', function() {
        // Replace with the actual endpoint URL where the results are fetched
        const apiUrl = '/api/get_results'; 
    
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                // Assuming the API response contains 'total_score' and 'predicted_pr_probability'
                document.getElementById('total-score').textContent = data.total_score;
                document.getElementById('pr-probability').textContent = data.predicted_pr_probability.toFixed(2) + '%';
            })
            .catch(error => {
                console.error('Error fetching results:', error);
            });
    });
      // Condition for page 8
  function showFollowUp(isYes) {
    const followUpSection = document.getElementById("followUpSection");
    if (isYes) {
        followUpSection.classList.remove("hidden");
    } else {
        followUpSection.classList.add("hidden");
    }
}
    
