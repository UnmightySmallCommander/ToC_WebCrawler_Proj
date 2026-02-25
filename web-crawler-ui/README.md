# Web Crawler UI

This folder contains the frontend interface for the K-pop Wikipedia web crawler project.

The UI allows users to input a Wikipedia page URL of a K-pop artist or select a random artist. The request is sent to the Python backend crawler, which extracts structured data from the page and returns it to the interface for display.

## Purpose

The frontend provides a simple and interactive way to run the crawler and visualize the results without using the command line.

It communicates with the backend API and displays extracted artist information such as:

* Stage name
* Full name
* Birth year
* Nationality
* Group affiliation
* Other metadata parsed from the Wikipedia infobox

## Technologies Used

* React
* Vite (development server and build tool)
* Tailwind CSS (UI styling)
* Fetch API (communication with backend)

## How It Works

1. The user enters a Wikipedia URL or selects the random option.
2. The frontend sends a POST request to the backend crawler API.

Example request:

POST `/crawl`

```
{
  "url": "https://en.wikipedia.org/wiki/Jennie_(singer)"
}
```

3. The backend processes the page and returns structured JSON data.
4. The UI receives the data and renders the results in a formatted card layout.

## Development

Install dependencies:

```
npm install
```

Start the development server:

```
npm run dev
```

The interface will run at:

```
http://localhost:5173
```

The backend crawler must also be running for the system to function.

## Backend Dependency

This frontend connects to the Python crawler backend running with Flask at:

```
http://localhost:5000
```

The backend is responsible for:

* Fetching Wikipedia pages
* Extracting structured artist information
* Returning the results as JSON

## Notes

This interface is intended for development and demonstration of the web crawler system. It focuses on visualizing extracted data rather than performing the crawling itself.

