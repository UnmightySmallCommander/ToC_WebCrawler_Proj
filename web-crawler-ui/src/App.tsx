import { useState } from "react";
import kpopLogo from "./assets/kpop_logo.jpg";

export default function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const isValidUrl = (url: string) => {
        try {
          new URL(url);
          return true;
        } catch {
          return false;
        }
      };

  const runCrawler = async () => {

    const response = await fetch("http://localhost:5000/crawl", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        input_url: url
      })
    });

    const data = await response.json();

    if (Array.isArray(data)) {
      setResults(data);
    } else {
      setResults([data]);
    }
    setShowResults(true);
    setIsLoading(false);
    console.log(data);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900">
      
      {/* Header - Using arbitrary py-[4.5rem] for perfect 18-equivalent padding */}
      <header className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-6 py-[4.5rem] text-center">
          <div className="flex flex-col items-center justify-center gap-4 mb-4">
            <div className="w-24 h-24 overflow-hidden rounded-full border-2 border-slate-100 shadow-sm">
              <img src={kpopLogo} alt="Logo" className="w-full h-full object-cover" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight">Web Crawler</h1>
          </div>
          <p className="text-gray-500 text-sm max-w-md mx-auto leading-relaxed">
            Paste a K-pop singer's Wikipedia page or click Random to start exploring.
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        
        {/* Input Section - Replaced shadcn components with raw Tailwind */}
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="url"
              placeholder="Enter URL to crawl..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 h-11 px-4 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
            <button
              onClick={() => {
                setShowResults(false);
                if (!isValidUrl(url)) {
                  alert("Please enter a valid URL");
                  return;
                }
                setIsLoading(true);
                runCrawler();
              }}
              className="h-11 px-6 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-all active:scale-95"
            >
              {isLoading ? "Crawling..." : "Start Crawl"}
            </button>
          </div>
        </div>


        {/* Results List - Integrated CrawlResult directly */}
        {showResults && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-slate-800">Results</h2>
            
            <div className="space-y-3">
              {results.map((result, index) => {
                const displayOrder = [
                  "stage name",
                  "full name",
                  "gender",
                  "birth year",
                  "age",
                  "nationality",
                  "occupations",
                  "group name",
                  "genre",
                ];

                return (
                  <div
                    key={`${result["stage name"] || 'error'}-${index}`}
                    className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 transition-colors group"
                  >
                    {/* Check if result.error_goofed exists */}
                    {result.error_goofed ? (
                      <div className="py-4 text-center">
                        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-50 text-red-500 mb-3">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        </div>
                        <h3 className="text-red-800 font-bold mb-1">Crawl Goofed</h3>
                        <p className="text-red-600 text-sm">{result.message}</p>
                      </div>
                    ) : (
                      <>
                        {/* Top Section: Header with Stage Name */}
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                              {result["stage name"] || "Unknown Artist"}
                            </h3>
                            <p className="text-sm text-blue-500 font-medium">
                              {result["full name"]}
                            </p>
                          </div>
                          <span className="text-[10px] font-bold px-2 py-1 bg-slate-100 text-slate-500 rounded uppercase tracking-wider">
                            Artist Profile
                          </span>
                        </div>

                        {/* Bottom Section: Grid for all 9 values in order */}
                        <div className="mt-4 pt-4 border-t border-slate-50 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                          {displayOrder.map((key) => (
                            <div key={key} className="flex flex-col">
                              <span className="text-slate-400 text-[10px] font-bold uppercase tracking-tight">
                                {key}
                              </span>
                              <span className="font-medium text-slate-700 truncate">
                                {String(result[key] || "N/A")}
                              </span>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
        <footer className="mt-8 pt-8 border-t border-slate-200 text-center">
          <p className="text-slate-500 text-sm">
            View the source code on{" "}
            <a 
              href="https://github.com/UnmightySmallCommander/ToC_WebCrawler_Proj" 
              target="_blank" 
              className="text-blue-600 hover:underline font-medium"
            >
              GitHub
            </a>
          </p>
        </footer>
      </main>
    </div>
  );
}