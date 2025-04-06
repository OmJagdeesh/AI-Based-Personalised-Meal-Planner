document.addEventListener('DOMContentLoaded', function() {
    const mealForm = document.getElementById('mealForm');
    const loadingElement = document.getElementById('loading');
    const resultsElement = document.getElementById('results');
    const errorAlert = document.getElementById('errorAlert');
    const mealPlanElement = document.getElementById('mealPlan');
    const bmiValueElement = document.getElementById('bmiValue');
    const bmiCategoryElement = document.getElementById('bmiCategory');
    const displayHeightElement = document.getElementById('displayHeight');
    const displayWeightElement = document.getElementById('displayWeight');

    mealForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading, hide results and errors
        loadingElement.style.display = 'block';
        resultsElement.style.display = 'none';
        errorAlert.style.display = 'none';
        
        // Get form values
        const formData = {
            height: document.getElementById('height').value,
            weight: document.getElementById('weight').value,
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            activity_level: document.getElementById('activity_level').value,
            carbs: document.getElementById('carbs').value,
            protein: document.getElementById('protein').value,
            fat: document.getElementById('fat').value,
            meal_type: document.getElementById('meal_type').value,
            cuisine_type: document.getElementById('cuisine_type').value,
            dietary_restrictions: document.getElementById('dietary_restrictions').value || 'none'
        };
        
        // Display personal info
        displayHeightElement.textContent = formData.height;
        displayWeightElement.textContent = formData.weight;
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Display results
            mealPlanElement.innerHTML = data.meal_plan;
            bmiValueElement.textContent = data.bmi;
            bmiCategoryElement.textContent = data.bmi_category;
            
            // Show results
            loadingElement.style.display = 'none';
            resultsElement.style.display = 'block';
            
            // Scroll to results
            resultsElement.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            loadingElement.style.display = 'none';
            errorAlert.textContent = error.message;
            errorAlert.style.display = 'block';
            errorAlert.scrollIntoView({ behavior: 'smooth' });
        }
    });
    
    // Initialize with loading hidden
    loadingElement.style.display = 'none';

    // Smooth scrolling for navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});