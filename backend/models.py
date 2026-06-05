from pydantic import BaseModel
from typing import List, Optional


class EdgeSchema(BaseModel):
    u: str
    v: str
    label: float


class GraphSchema(BaseModel):
    vertices: List[str]
    edges: List[EdgeSchema]


class SpannerRequest(BaseModel):
    graph: GraphSchema


class CliqueQualitySchema(BaseModel):
    size: int
    members: List[str]
    spanner_edges: int
    verified: bool


class MetricSchema(BaseModel):
    uploaded_edges: int
    full_clique_edges: int
    spanner_edges: int
    bound_7n: int
    ratio_per_n: float
    savings_pct: float
    verified: bool
    stretch_factor: Optional[float] = None
    cliques_processed: int = 0
    pmi_threshold: float = 0.0
    stopwords_filtered: int = 0
    clique_qualities: List[CliqueQualitySchema] = []


class SpannerResponse(BaseModel):
    original: GraphSchema
    spanner: GraphSchema
    metrics: MetricSchema


class CsvRow(BaseModel):
    date: str
    words: List[str]


class UploadResponse(BaseModel):
    session_id: str
    graph: GraphSchema
    rows_parsed: int
    time_range: List[str]
    stopwords_filtered: int = 0


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
    windows: int = 10


class TrendResponse(BaseModel):
    timelines: List[CliqueTimeline]
    time_range: List[float]
    window_edges: List[int]


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


class CompareResponse(BaseModel):
    spanner1: SpannerResponse
    spanner2: SpannerResponse
    comparison: CompareMetricSchema
