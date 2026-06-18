import { useQuery } from "@tanstack/react-query";
import { useSearchParams, Link } from "react-router-dom";
import api from "../../lib/api";
import { Card, CardContent } from "../../components/ui/card";

export default function SearchResults() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";

  const { data: results, isLoading } = useQuery({
    queryKey: ["search", query],
    queryFn: () => api.get(`/system/search?q=${query}`).then((res) => res.data),
    enabled: !!query,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Search Results for "{query}"</h1>
      {isLoading ? (
        <p>Searching...</p>
      ) : results?.length ? (
        <div className="space-y-4">
          {results.map((result, idx) => (
            <Link key={idx} to={result.link} className="block">
              <Card className="hover:bg-muted/50 transition-colors">
                <CardContent className="p-4 flex flex-col">
                  <span className="text-sm text-muted-foreground uppercase">{result.type}</span>
                  <span className="font-medium text-lg">{result.title}</span>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <p>No results found.</p>
      )}
    </div>
  );
}
