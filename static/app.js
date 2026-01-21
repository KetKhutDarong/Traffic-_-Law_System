// Global JavaScript functions for the application

// Format currency
function formatCurrency(amount) {
  return amount.toLocaleString() + " ៛"
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

// Show loading spinner
function showLoading() {
  const spinner = document.createElement("div")
  spinner.id = "loadingSpinner"
  spinner.className = "text-center my-4"
  spinner.innerHTML =
    '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>'
  return spinner
}

// Smooth scroll to element
function scrollToElement(elementId) {
  const element = document.getElementById(elementId)
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "nearest" })
  }
}

// Validate form inputs
function validateSpeed(speed) {
  return speed >= 0 && speed <= 200
}

// Calculate fine in USD
function calculateUSD(riel) {
  const exchangeRate = 4000
  return (riel / exchangeRate).toFixed(2)
}

// Display notification
function showNotification(message, type = "info") {
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  const container = document.querySelector(".container")
  container.insertBefore(alertDiv, container.firstChild)

  setTimeout(() => {
    alertDiv.remove()
  }, 5000)
}

// Export data to CSV
function exportToCSV(data, filename) {
  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: "text/csv" })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
}

function convertToCSV(data) {
  const headers = Object.keys(data[0])
  const rows = data.map((obj) => headers.map((header) => obj[header]))
  return [headers, ...rows].map((row) => row.join(",")).join("\n")
}

// Initialize tooltips
document.addEventListener("DOMContentLoaded", () => {
  // Bootstrap tooltip initialization
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  const bootstrap = window.bootstrap // Declare the bootstrap variable
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
})

// Print functionality
function printPage() {
  window.print()
}

// Theme toggle (if needed in future)
function toggleTheme() {
  document.body.classList.toggle("dark-mode")
  localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light")
}
