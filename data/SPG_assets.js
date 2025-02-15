// This code is to be pasted is to be pasted in the browser console on the following URL
// https://www.macrotrends.net/stocks/charts/SPG/simon-property/total-assets
// Or any other total-assets page on macrotrends.net

let csvContent = "date,amount\n";

document.querySelector("#style-1 > div:nth-child(2) > table > tbody")
  .querySelectorAll("tr")
  .forEach((row) => {
    const date = row.cells[0].textContent.trim();
    const rawAmount = row.cells[1].textContent.trim();

    // number parsing, normalizing format
    const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
    const billionsValue = (millionsValue / 1000).toFixed(4);
    
    csvContent += `${date},${billionsValue}\n`;
  });

const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
const link = document.createElement("a");
link.href = URL.createObjectURL(blob);
link.download = "SPG_assets.csv";
link.click();
URL.revokeObjectURL(link.href);