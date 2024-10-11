document.getElementById('upload-form').onsubmit = async function(e) {
    e.preventDefault();  // Prevent the default form submission
    
    const formData = new FormData();
    const fileInput = document.getElementById('file');

    const button = document.querySelector('button');
    const container = document.querySelector('.container');

    
    
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
        
        // Display the uploaded image
        const file = fileInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            const imgElement = document.getElementById('uploaded-image');
            imgElement.src = e.target.result;
            imgElement.style.display = 'block';  // Show the image once uploaded
        };
        button.addEventListener('click', function() {
            // Adjust the container's height based on its content
            container.style.minHeight = 'auto';  // Remove fixed minimum height
            container.style.height = 'auto';  // Let it grow to fit content
        });
        reader.readAsDataURL(file);
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }

            const data = await response.json();  // Expect JSON response

            if (data.prediction) {
                const details = data.details;

                // Display the result
                document.getElementById('result').style.display = 'block';  // Show result container
                document.getElementById('result').innerHTML = `
                    <h2>Predicted Disease: ${data.prediction}</h2>
                    <p><strong>Description:</strong> ${details.description}</p>
                    <p><strong>Symptoms:</strong> ${details.symptoms || 'No symptoms provided.'}</p>
                    <p><strong>Causes:</strong> ${details.causes || 'No causes provided.'}</p>
                    <p><strong>Impact:</strong> ${details.impact}</p>
                    <p><strong>Control Measures:</strong> ${details.control}</p>
                `;
                
                // Generate chart for confidence levels
                const ctx = document.getElementById('disease-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Confidence Levels',
                            data: data.confidence_levels,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            } else if (data.error) {
                document.getElementById('result').innerText = 'Error: ' + data.error;
            } else {
                document.getElementById('result').innerText = 'Error: Unknown response format';
            }

        } catch (error) {
            document.getElementById('result').innerText = 'Error: ' + error.message;
        }

    } else {
        alert('Please select a file to upload.');
    }
};
