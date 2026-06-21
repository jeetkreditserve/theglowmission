export function JsonLd({ data }: { data: Record<string, unknown> | Array<Record<string, unknown>> }) {
  const graph = Array.isArray(data) ? data : [data];
  const payload =
    graph.length === 1 && graph[0]["@context"]
      ? graph[0]
      : {
          "@context": "https://schema.org",
          "@graph": graph
        };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(payload).replace(/</g, "\\u003c") }} />;
}
