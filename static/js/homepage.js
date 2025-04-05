const inputBox = document.getElementById("input-box");
        const listContainer = document.getElementById("list-container");

        function AddTask() {
            if(inputBox.value === '') {
                alert("You must write something");
            }
            else {
                let li = document.createElement("li");
                li.innerHTML = inputBox.value;
                listContainer.appendChild(li);
                
                // Save the task to localStorage
                saveData();
                
                inputBox.value = ''; // Clear the input box after adding
            }
        }

        // Click event for marking tasks as complete
        listContainer.addEventListener("click", function(e) {
            if(e.target.tagName === "LI") {
                e.target.classList.toggle("checked");
                
                // If task is checked, add a fade-out effect and remove after animation
                if(e.target.classList.contains("checked")) {
                    // Add transition for fade effect
                    e.target.style.transition = "opacity 1s ease, height 1s ease, padding 1s ease, margin 1s ease";
                    
                    // Set a timeout to fade out and remove
                    setTimeout(() => {
                        e.target.style.opacity = "0";
                        e.target.style.height = "0";
                        e.target.style.padding = "0";
                        e.target.style.margin = "0";
                        
                        // Remove the element completely after animation completes
                        setTimeout(() => {
                            e.target.remove();
                            saveData();
                        }, 1000);
                    }, 500); // Small delay before starting fade
                }
                
                // Save the updated task list
                saveData();
            }
        }, false);

        // Save tasks to localStorage
        function saveData() {
            localStorage.setItem("todoData", listContainer.innerHTML);
        }

        // Load tasks from localStorage when page loads
        function showTasks() {
            listContainer.innerHTML = localStorage.getItem("todoData") || "";
        }

        // Load saved tasks when page loads
        showTasks();

        // Add ability to press Enter key to add tasks
        inputBox.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                AddTask();
            }
        });