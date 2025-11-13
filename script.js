async function searchImages() {
  const query = document.getElementById("queryInput").value;
  const response = await fetch(`/search/${query}`);
  const images = await response.json();

  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";
  images.forEach(url => {
    const img = document.createElement("img");
    img.src = url;
    img.style.width = "200px";
    img.style.margin = "10px";
    resultsDiv.appendChild(img);
  });
}
