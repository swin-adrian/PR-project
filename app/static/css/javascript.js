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
      if (n === 0) {
        document.getElementById("prevBtn").style.display = "none";
      } else {
        document.getElementById("prevBtn").style.display = "inline";
      }
      
      if (n === (x.length - 1)) {
        document.getElementById("nextBtn").innerHTML = "Submit";
      } else {
        document.getElementById("nextBtn").innerHTML = "Next";
      }
      
      // Update the step indicators
      fixStepIndicator(n);
    }
  
    function nextPrev(n) {
      let x = document.getElementsByClassName("tab");
      
      // Validate the current tab before moving forward, skip Page 4 validation
      if (n == 1 && !validateForm()) return false;
  
      // Hide the current tab
      x[currentTab].style.display = "none";
  
      // Increase or decrease the current tab by n
      currentTab = currentTab + n;
  
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
        if (y[i].value === "") {
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
  
    document.getElementById("prevBtn").addEventListener("click", function() {
      nextPrev(-1);
    });
  
    document.getElementById("nextBtn").addEventListener("click", function() {
      nextPrev(1);
    });
  
    // Condition for page 2
    document.querySelector('form').addEventListener('change', function(e) {
      let selectedSubclass = document.querySelector('input[name="visa-subclass"]:checked');
      document.querySelectorAll('.occupation-section').forEach(section => section.style.display = 'none');
      if (selectedSubclass) {
          if (selectedSubclass.value === '189') {
              document.getElementById('mltssl-section-189').style.display = 'block';
          } else if (selectedSubclass.value === '190') {
              document.getElementById('question-190').style.display = 'block';
          } else if (selectedSubclass.value === '491') {
              document.getElementById('question-491').style.display = 'block';
          }
      }
  
      if (e.target.name === "occupation-list-190") {
          if (e.target.value === 'mltssl') {
              document.getElementById('mltssl-section-190').style.display = 'block';
              document.getElementById('stsol-section-190').style.display = 'none';
          } else if (e.target.value === 'stsol') {
              document.getElementById('mltssl-section-190').style.display = 'none';
              document.getElementById('stsol-section-190').style.display = 'block';
          }
      }
  
      if (e.target.name === "occupation-list-491") {
          if (e.target.value === 'mltssl') {
              document.getElementById('mltssl-section-491').style.display = 'block';
              document.getElementById('stsol-section-491').style.display = 'none';
              document.getElementById('rol-section-491').style.display = 'none';
          } else if (e.target.value === 'stsol') {
              document.getElementById('mltssl-section-491').style.display = 'none';
              document.getElementById('stsol-section-491').style.display = 'block';
              document.getElementById('rol-section-491').style.display = 'none';
          } else if (e.target.value === 'rol') {
              document.getElementById('mltssl-section-491').style.display = 'none';
              document.getElementById('stsol-section-491').style.display = 'none';
              document.getElementById('rol-section-491').style.display = 'block';
          }
      }
  });
    // Condition for page 4 
    document.getElementById("english-test").addEventListener("change", function() {
      // Hide all score sections initially
      const scoreSections = document.querySelectorAll('.score-section');
      scoreSections.forEach(section => section.style.display = "none");
      
      // Show the relevant score section based on the selected test
      const selectedTest = this.value;
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
    });
  });
  