export function fetchData(URL, setData) {
  const request = new Request(URL);
  fetch(request)
    .then((response) => response.json())
    .then((jsonData) => setData(jsonData))
    .catch((error) => console.log(error));
}
