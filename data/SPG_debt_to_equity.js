// This code is to be pasted in the browser console on the following URL
// https://www.macrotrends.net/stocks/charts/SPG/simon-property/debt-equity-ratio
// Or any other total-assets page on macrotrends.net

let csvContent = "date,debttoequityratio\n";

document.querySelector("#style-1 > table > tbody")
  .querySelectorAll("tr")
  .forEach((row) => {
    const date = row.cells[0].textContent.trim();
    const ratio = row.cells[3].textContent.trim();
    
    csvContent += `${date},${ratio}\n`;
  });

// This approach allows you to trigger a download immediately without having to add the link to the DOM
const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' }); // blob is created from the csv content
const link = document.createElement("a"); // <a> (anchor) element is dynamically created
link.href = URL.createObjectURL(blob); // creates a temporary url that points to the blob's data
link.download = "SPG_debt_to_equity.csv"; // specifies the name of the file to be downloaded
link.click(); // programmatically simulate a click on the anchor element, which starts the download process
URL.revokeObjectURL(link.href); // revokes the temporary URL, freeing up memory