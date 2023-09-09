// app.js

var ageFilter = ""
var genderFilter = ""
var dateFilter = ""

function createGenderChart(data) {
    var maleCount = 0;
    var femaleCount = 0;

    // Calculate the counts of male and female persons
    data.forEach(function (person) {
        if (person[1] === 'Male') {
            maleCount++;
        } else if (person[1] === 'Female') {
            femaleCount++;
        }
    });

    var ctx = document.getElementById('gender-chart').getContext('2d');

    var genderChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Male', 'Female'],
            datasets: [{
                data: [maleCount, femaleCount],
                backgroundColor: ['#3498db', '#e74c3c'],
            }]
        }
    });
}

function createAgeDistributionChart(data) {
    // Define the age ranges and initialize counts
    var ageRanges = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)'];
    var ageCounts = Array(ageRanges.length).fill(0);

    // Count the number of people in each age range
    data.forEach(function (person) {
        var age = person[0];
        var ageIndex = ageRanges.indexOf(age);
        if (ageIndex !== -1) {
            ageCounts[ageIndex]++;
        }
    });

    var ctx = document.getElementById('age-distribution-chart').getContext('2d');

    var ageDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ageRanges,
            datasets: [{
                label: 'Number of People',
                data: ageCounts,
                backgroundColor: ['#3498db', '#e74c3c', '#9b59b6', '#2ecc71', '#f1c40f', '#34495e', '#d35400', '#7f8c8d'],
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
}


$('#dateToFilter').on('change', function (e) {
    dateFilter = e.target.value

});


$('#resetDate').on('click', function (e) {
    document.getElementById("dateToFilter").value = ""
    dateFilter = ""
});

$('#searchButton').on('click', function (e) {
    $.getJSON('/get_person_data_filter?date=' + dateFilter + "&gender=" + genderFilter + "&age=" + ageFilter, function (data) {
        var personList = $('#person-list');
        personList.empty();
        $.each(data, function (index, person) {
            var listItem = $('<li>').text('Age: ' + person[0] + ', Gender: ' + person[1] + ', Created at :' + person[2]);
            personList.append(listItem);
        });

        createGenderChart(data);
        createAgeDistributionChart(data);
    });
});

$('#genderToFilter').on('change', function (e) {
    genderFilter = e.target.value
});

$('#ageToFilter').on('change', function (e) {
    ageFilter = e.target.value;
});

function fetchDataAndRefresh() {
    $.getJSON('/get_person_data', function (data) {
        var personList = $('#person-list');
        personList.empty();
        $.each(data, function (index, person) {
            var listItem = $('<li>').text('Age: ' + person[0] + ', Gender: ' + person[1] + ', Created at :' + person[2]);
            personList.append(listItem);
        });

        createGenderChart(data);
        createAgeDistributionChart(data);
    });
}
fetchDataAndRefresh();

$('#refresh-button').click(function () {
    fetchDataAndRefresh();
});

$('#download').click(function () {
    $.getJSON('/get_person_data_filter?date=' + dateFilter + "&gender=" + genderFilter + "&age=" + ageFilter, function (data) {
            downloadCSV(data, 'data.csv')
        
    })

})

function downloadCSV(data, filename) {
    // Create a CSV-formatted string from the 
    data=[["age","gender","created_at"],...data]
    const csv = data.map(row => row.join(',')).join('\n');
    
    // Create a Blob object with the CSV data
    const blob = new Blob([csv], { type: 'text/csv' });

    // Create a download link
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;

    // Trigger the download
    link.click();

    // Clean up
    URL.revokeObjectURL(link.href);
}

// setInterval(fetchDataAndRefresh, 10000);
function deleteAllData() {
    // Send a DELETE request to the server
    fetch('/delete_all_data', {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response from the server
        if (data.message) {
            alert(data.message); // Show a success message
            fetchDataAndRefresh()
        } else if (data.error) {
            alert('Error: ' + data.error); // Show an error message
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Attach the function to a button click event
document.getElementById('delete-button').addEventListener('click', deleteAllData);
