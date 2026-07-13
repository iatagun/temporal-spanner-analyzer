from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional

# The four association measures a corpus can be gated on (see
# graph_builder.compute_association_measures); shared by every request/
# response model that carries a measure choice or a threshold against it.
AssociationMeasure = Literal["npmi", "log_likelihood", "dice", "t_score"]


class EdgeSchema(BaseModel):
    u: str
    v: str
    label: float
    # All four association measures for this pair, computed once at
    # upload time -- not just the one `association_measure` gated the
    # edge on. Lets the UI show "NPMI 0.42 / G^2 18.3 / Dice 0.31 / t 4.1"
    # side by side instead of locking a corpus linguist into one number.
    scores: Dict[str, float] = {}


class GraphSchema(BaseModel):
    vertices: List[str]
    edges: List[EdgeSchema]


class SpannerRequest(BaseModel):
    graph: GraphSchema
    min_clique_size: int = Field(3, ge=2, le=50)
    max_cliques: int = Field(0, ge=0, le=100_000)


class CliqueQualitySchema(BaseModel):
    size: int
    members: List[str]
    spanner_edges: int
    verified: Optional[bool]


class MetricSchema(BaseModel):
    uploaded_edges: int
    full_clique_edges: int
    spanner_edges: int
    bound_7n: int
    ratio_per_n: float
    savings_pct: float
    verified: Optional[bool]
    stretch_factor: Optional[float] = None
    cliques_processed: int = 0
    stopwords_filtered: int = 0
    clique_qualities: List[CliqueQualitySchema] = []
    truncated: bool = False


class SpannerResponse(BaseModel):
    original: GraphSchema
    spanner: GraphSchema
    metrics: MetricSchema
    cliques: list[list[str]] = []


class CsvRow(BaseModel):
    date: str
    words: List[str]


class RawDocumentSchema(BaseModel):
    """One corpus row/sentence as (resolved date label, content words,
    original raw text) -- preserved past upload so /api/trends can
    recompute association scores per time window instead of only slicing
    the corpus-global edge set, and so the frontend can show KWIC/
    concordance context for a word or pair without a second request."""
    label: float
    words: List[str]
    text: str = ""


class UploadResponse(BaseModel):
    graph: GraphSchema
    rows_parsed: int
    time_range: List[str]
    stopwords_filtered: int = 0
    # NOTE: kept as `pmi_threshold` (not renamed to a generic `threshold`)
    # for backward compatibility -- its meaning is now "the gate value for
    # whichever `association_measure` was selected", not always an NPMI
    # score. NPMI's [-1,1] scale no longer bounds it (log-likelihood/
    # t-score are unbounded), see AssociationMeasure/Field bounds below.
    pmi_threshold: float = 0.0
    association_measure: AssociationMeasure = "npmi"
    raw_documents: List[RawDocumentSchema] = []


class CliqueSnapshot(BaseModel):
    window: int
    window_start: float
    window_end: float
    members: List[str]
    size: int


class CliqueTimeline(BaseModel):
    id: str
    label: str
    birth: float
    death: Optional[float] = None
    snapshots: List[CliqueSnapshot]
    max_size: int


class TrendRequest(BaseModel):
    graph: GraphSchema
    windows: int = Field(10, ge=1, le=200)
    # When present, trend computation recomputes association scores
    # independently within each time window instead of slicing the single
    # corpus-global edge set -- see trend_analyzer.compute_trends.
    # pmi_threshold/association_measure must match what the corpus was
    # uploaded with for "significant" to mean the same thing locally as
    # it did globally.
    raw_documents: List[RawDocumentSchema] = []
    # Widened from NPMI's [-1,1] band: log-likelihood/t-score are
    # unbounded, so a fixed range can't fit every measure.
    pmi_threshold: float = Field(0.15, ge=-1000.0, le=1000.0)
    association_measure: AssociationMeasure = "npmi"


class TrendResponse(BaseModel):
    timelines: List[CliqueTimeline]
    time_range: List[float]
    window_edges: List[int]
    truncated: bool = False


class CompareRequest(BaseModel):
    graph1: GraphSchema
    graph2: GraphSchema
    label1: str = "A"
    label2: str = "B"


class CompareMetricSchema(BaseModel):
    vertex_union: int
    vertex_intersection: int
    vertex_overlap_pct: float
    edge_union: int
    edge_intersection: int
    edge_overlap_pct: float
    savings_compare: str
    clique_count_1: int = 0
    clique_count_2: int = 0
    clique_jaccard: float = 0.0
    cliques_processed_1: int = 0
    cliques_processed_2: int = 0
    truncated: bool = False


class CompareResponse(BaseModel):
    spanner1: SpannerResponse
    spanner2: SpannerResponse
    comparison: CompareMetricSchema
