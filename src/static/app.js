document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p class="availability"><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Build participants section (no bullet points, with delete buttons)
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";
        const title = document.createElement("div");
        title.className = "participants-title";
        title.textContent = "Participants";
        participantsSection.appendChild(title);

        if (details.participants && details.participants.length > 0) {
          const ul = document.createElement("ul");
          ul.className = "participants-list";

          details.participants.forEach((p) => {
            const li = document.createElement("li");
            // participant mailto
            const a = document.createElement("a");
            a.href = `mailto:${p}`;
            a.textContent = p;

            // delete button (simple ×)
            const del = document.createElement("button");
            del.className = "delete-btn";
            del.title = "Unregister participant";
            del.setAttribute("data-email", p);
            del.textContent = "×";

            // Handle delete click
            del.addEventListener("click", async (ev) => {
              ev.preventDefault();
              ev.stopPropagation();
              const email = del.getAttribute("data-email");
              try {
                const res = await fetch(`/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(email)}`, { method: "DELETE" });
                const result = await res.json();
                if (res.ok) {
                  // remove the list item
                  li.remove();

                  // update availability text
                  const avail = activityCard.querySelector(".availability");
                  if (avail) {
                    // parse current number and increment
                    const match = avail.textContent.match(/(\d+) spots left/);
                    if (match) {
                      const current = parseInt(match[1], 10);
                      avail.innerHTML = `<strong>Availability:</strong> ${current + 1} spots left`;
                    }
                  }

                  // if no participants left, show friendly message
                  if (ul.children.length === 0) {
                    const noP = document.createElement("div");
                    noP.className = "no-participants";
                    noP.textContent = "No participants yet";
                    participantsSection.appendChild(noP);
                    ul.remove();
                  }

                  // show temporary success message
                  messageDiv.textContent = result.message || `${email} unregistered`;
                  messageDiv.className = "message success";
                  messageDiv.classList.remove("hidden");
                  setTimeout(() => messageDiv.classList.add("hidden"), 4000);
                } else {
                  messageDiv.textContent = result.detail || "Failed to unregister";
                  messageDiv.className = "message error";
                  messageDiv.classList.remove("hidden");
                }
              } catch (err) {
                console.error("Error unregistering:", err);
                messageDiv.textContent = "Failed to unregister. Please try again.";
                messageDiv.className = "message error";
                messageDiv.classList.remove("hidden");
              }
            });

            li.appendChild(a);
            li.appendChild(del);
            ul.appendChild(li);
          });

          participantsSection.appendChild(ul);
        } else {
          const noParticipants = document.createElement("div");
          noParticipants.className = "no-participants";
          noParticipants.textContent = "No participants yet";
          participantsSection.appendChild(noParticipants);
        }

        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
