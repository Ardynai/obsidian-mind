import { HonestNull, Empty } from "../components/States";

export function CitationList({ data }: { data: Record<string, unknown> }) {
  const report = (data.report || data) as Record<string, unknown>;
  const nested = (report.research || {}) as Record<string, unknown>;
  const honest = Boolean(data.honest_null || report.honest_null || nested.honest_null);
  const honestText = String(
    data.honest_null_text ||
      (report.result as { summary?: string } | undefined)?.summary ||
      "",
  );
  if (honest) return <HonestNull text={honestText} />;

  const retrieved = (report.retrieved || nested.retrieved || []) as Array<Record<string, unknown>>;
  const byId = Object.fromEntries(retrieved.map((item) => [String(item.id), item]));
  const claims = (report.claims || nested.claims || []) as Array<Record<string, unknown>>;
  const grade =
    (report.result as { evidence_grade?: string } | undefined)?.evidence_grade ||
    (nested.result as { evidence_grade?: string } | undefined)?.evidence_grade;
  if (!claims.length && !grade) {
    return <Empty title="No bound claims" body="Nothing in the local corpus attached a passage to this query." />;
  }
  return (
    <>
      {grade ? (
        <p>
          <span className="pill">Grade: {String(grade)}</span>
        </p>
      ) : null}
      {claims.map((claim, index) => (
        <article className="finding" key={index}>
          <p>{String(claim.text || "")}</p>
          <ul>
            {((claim.passage_ids as string[]) || []).map((id) => {
              const passage = byId[id];
              if (!passage) return <li key={id}>Missing citation {id}</li>;
              return (
                <li key={id}>
                  <strong>{String(passage.title || id)}</strong>
                  {passage.url ? (
                    <p className="muted">Source URL (not fetched): {String(passage.url)}</p>
                  ) : null}
                  <p>{String(passage.text || "")}</p>
                </li>
              );
            })}
          </ul>
        </article>
      ))}
    </>
  );
}
