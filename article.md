Temporal Cliques Admit Linear Spanners
Júlia Baligács∗
University of Oxford
Abstract
A temporal graph is a graph in which every edge carries a non-empty set of time labels,
and it is temporally connected if for every two vertices u and v, there exists a u-v-path with
non-decreasing time labels. A spanner is a subset of its edges preserving temporal connectivity.
Unlike static graphs, temporally connected graphs need not admit sparse spanners; nonetheless,
minimizing spanner size is a central and widely studied problem. A particularly intriguing
question is whether temporal cliques admit spanners of linear size. Despite considerable effort
over the past years, the best known upper bound remained O(n log n). We finally resolve this
question, proving that every temporal clique on n vertices admits a spanner of size 7n. Moreover,
such a spanner can be computed in polynomial time.
1 Introduction
A temporal graph is a graph G = (V, E, λ) in which each edge e ∈ E carries a non-empty set of
time labels λ(e) ⊆ R. A temporal path is a path (v1, . . . , vk) whose edges admit non-decreasing
time labels, that is, there exist li ∈ λ({vi
, vi+1}) with l1 ≤ · · · ≤ lk−1, in which case vk is said to
be temporally reachable from v1. (While some works also consider the variant where labels need
to be strictly increasing, we follow the classical non-decreasing convention.) Then G is temporally
connected if u is temporally reachable from v for every u, v ∈ V .
Temporal graphs model a wide range of real-world phenomena. For example, in an informationdissemination setting, vertices represent agents and a time label on an edge records when its two
endpoints communicate. A temporal u-v-path then certifies that agent v can acquire information
originating at u. Beyond communication protocols, temporal graphs naturally encode transportation networks, the spread of infectious diseases, and dynamically evolving networks more generally.
Over the past decades, temporal graphs have also emerged as compelling theoretical objects and
have attracted considerable attention (see surveys [Mic16, CFQS12]). A central theme is the search
for temporal analogues of classical graph-theoretic results, particularly concerning connectivity.
Such analogues, however, frequently fail to hold outright or turn out to be significantly harder to
establish [AMSZ18, MMN+23, CHMZ21, ZFMN20].
Temporal reachability serves as a prime example of the latter. Unlike in static graphs, temporal
reachability is neither symmetric nor transitive, making connectivity a far more subtle notion.
Furthermore, properties of the underlying static graph offer essentially no guarantee of temporal
connectivity: whenever {u, v} ∈/ E, one can assign label 2 to all edges incident to u and label 1 to
∗Email: jbaligacs@gmail.com. Funded by the European Union (ERC, CCOO, 101165139). Views and opinions
expressed are however those of the author only and do not necessarily reflect those of the European Union or the
European Research Council. Neither the European Union nor the granting authority can be held responsible for
them.
1
arXiv:2606.05156v1 [cs.DM] 3 Jun 2026
all edges incident to v, so that no temporal path from u to v exists. Consequently, the only static
graphs guaranteed to be temporally connected under any labeling are cliques.
A temporal spanner of G is a subset of edges E′ ⊆ E such that (V, E′
, λ|E′) is temporally
connected. In the static setting, every connected graph on n = |V | vertices admits a spanner
of size n − 1, namely a spanning tree, computable in polynomial time. In the temporal setting,
the situation is far more complex. Kempe, Kleinberg, and Kumar [KKK00] asked whether every
temporally connected graph admits a temporal spanner of size O(n), and immediately answered
it negatively by constructing graphs in which every temporal spanner has size Ω(n log n). This
was later strengthened by Axiotis and Fotakis [AF16], who constructed graphs requiring spanners
of size Ω(n
2
). From a computational perspective, finding a temporal spanner of minimum size
is APX-hard [AF16]. In light of these results, a natural direction is to identify graph classes
admitting sparse spanners. A particularly compelling candidate is the class of temporal cliques:
as argued above, cliques are the only graphs guaranteeing temporal connectivity regardless of the
labeling, making them a canonical setting in which to study temporal spanners.
Question 1 (Casteigts, Peters, Schoeters, 2019). Does every temporal clique admit a spanner of
size O(n)?
Since it was first posed as an open problem in 2019 (conference version of [CPS21]), Question 1
has been approached from many directions. Akrida, Gąsieniec, Mertzios, and Spirakis [AGMS17]
gave the first improvement over the trivial bound, a spanner of size n
2

− ⌊n/4⌋ (still Θ(n
2
)),
and showed that if each edge receives a single label chosen uniformly at random from an interval,
then a spanner of size O(n log n) exists almost surely. The most significant improvement is due to
Casteigts, Peters, and Schoeters [CPS21], who proved that every temporal clique admits a spanner
of size O(n log n). More recently, powerful new techniques [ABF+24, CCC25] pushed the linear
regime within reach, but only for restricted subclasses such as the so-called edge-pivot cliques. The
problem has also been studied under additional constraints: bounding the length of the reachability
paths [BDG+22], requiring the spanner to satisfy a robustness criterion [BDG+24], or building it
from selfish agents located at the vertices [BCF+23, BCF+25], as well as for general temporal
graphs [KKK00, AF16] and random temporal graphs [CRRZ24]. Despite this sustained effort,
the O(n log n) bound remained the state of the art prior to our work.
Our results. We answer Question 1 in the affirmative. Every temporal clique admits a spanner
of linear size.
Theorem 2. Every temporal clique on n vertices admits a temporal spanner of size 7n.
This is asymptotically optimal, since every temporal spanner trivially needs to contain a spanning tree, i.e., at least n − 1 edges, and in fact at least 2n − 4 edges by a classical result in gossip
theory [Bum81].
It is noteworthy that, despite the problem having resisted multiple independent attempts over
several years, our proof of a linear bound is surprisingly short and self-contained: while it draws on
ideas from prior work, it does not invoke any external result as a black box. On its own it yields
a spanner of size 14n. The factor-two improvement to the 7n of Theorem 2 is a minor refinement,
obtained by invoking a result of [CCC25], and is the only part of our work that relies on an external
result.
To prove Theorem 2, we pass to the bipartite setting. As observed in [ABF+24], Question 1
is equivalent to its analogue for bi-cliques, which are often more convenient to work with. We
make this equivalence precise in Section 2 and work with bi-cliques throughout. A temporal biclique is a triple G = (S, T, λ) where S and T are disjoint sets of sources and targets, the edge
2
set is E := {{s, t} : s ∈ S, t ∈ T}, and λ assigns each edge a non-empty finite set of time labels.
A spanner is a subset of its edges through which every source reaches every target by a temporal
path; paths from targets to sources are not required.
Theorem 3. Every temporal bi-clique (S, T, λ) admits a temporal spanner of size
10 min(|S|, |T|) + 2(|S| + |T|).
We further show that all spanners above can be computed in polynomial time.
Additional related work. Whereas we sparsify a given temporal graph, a related line of work
asks how to construct the time labels in the first place. The usual goal is to make a static graph
temporally connected with as few labels as possible [KMMS22], sometimes under additional constraints [MMS19]. Motivated by epidemic control, the opposite objective has also been studied: reducing the number of vertices a single source can reach. This can be done by deleting
edges [EMMZ21], reordering their activation times [EMS21], or delaying them [MRZ21].
Temporal connectivity has also been studied on temporal versions of random graphs. A common model assigns each edge of an Erdős–Rényi graph G(n, p) a time label chosen uniformly at
random from [0, 1]. Here, sharp thresholds are known for various reachability properties [CRRZ24],
including the emergence of a giant temporally connected component [BCC+26]. Further properties
have been studied in other models, such as the temporal diameter [BKL24] and the size of the
largest temporal clique [MNRS24, ADL25].
Outline and overview of techniques. In Section 2, we collect and summarize the ideas from
prior work that we build on. Using these, we prove that Theorem 3 implies that temporal cliques
contain spanners of linear size, and that we may assume that temporal bi-cliques satisfy an additional structural property known as extremally matched.
A generally useful technique throughout the paper is to find a set of edges solving the reachabilities of a large subgraph and then proceed with the unsolved part. Formally, for two vertices s
and t, a set of edges E′
covers (s, t) if a temporal s-t-path exists using only edges of E′
. In Section 3,
we introduce a natural set of edges called a simple star, consisting of a star and a matching, which
already covers half of all pairs (s, t) ∈ S × T. We also identify a technique for appending further
paths to a simple star, covering additional pairs at a cost of adding only O(n) additional edges.
In Section 3.1, we present two results that, while not needed for the main proof, motivate the
key ideas. We show that if Ω(n) paths can be appended to a simple star, the main result follows
relatively easily. This is, however, not the case in general: a classical construction from [ABF+24],
the shifted matching graph, serves as a counterexample. Interestingly, the converse also holds: we
prove that if no paths can be appended to a simple star, then the graph is isomorphic to a shifted
matching graph — and shifted matching graphs are known to admit linear spanners. In summary,
both extreme cases, where Ω(n) paths are appendable or none are, admit linear spanners. It remains
to handle the intermediate cases. The main difficulty here lies in finding the correct notion, one
that captures both extreme cases simultaneously.
Our main technical contribution is in Section 4. We introduce the carefully constructed extended
stars, which capture the reachabilities of a simple star together with a subset of its appendable
paths. We prove that either there exist two extended stars, one centered at a source and one at
a target (analogously to the spanner structure of a shifted matching graph), that together cover
a sufficiently large subgraph, or there exists a simple star to which Ω(n) paths can be appended.
Intuitively, the first condition holds when the graph is “close” to a shifted matching graph, and
3
the second when it is “far” from one. This allows us to complete our proof that temporal cliques
contain spanners of linear size.
Finally, in Section 5, we briefly show that the constant factor found in our construction can
be easily halved by invoking a result from [CCC25]. In Section 6, we provide the missing proofs
from Section 3.1 that were not required for our main results, but only to settle the intuition. In
Section 7, we recap the proof observing that the steps can be carried out in polynomial time, and
we conclude.
2 Preliminaries
2.1 Notation and conventions
We collect a few simple observations that fix the setting and notation used throughout. We write
a temporal clique as G = (V, λ), omitting the edge set, which is always V
2

. First, observe that it
suffices to prove Theorems 2 and 3 for temporal cliques and bi-cliques, respectively, in which every
edge carries exactly one time label: when an edge has multiple labels, delete all but one; then any
spanner of the modified graph is also a spanner of the original. We therefore assume λ(e) ∈ R for
all edges e throughout. Moreover, since temporality of a path depends only on the relative ordering
of its edge labels, we may assume without loss of generality that λ(e) ∈ N; more generally, for any
set L ⊆ R of size at least the number of edges |E|, we may assume λ(E) ⊆ L whenever convenient.
We may further assume that no two edges incident to the same vertex share a label: ties can
be broken arbitrarily, and any spanner of the modified temporal graph is also a spanner of the
original. Under this assumption, each vertex v induces a total ordering on its neighbors, and we
write posv
(u) = i if {u, v} is the (i + 1)-th smallest edge incident to v (so posv
is 0-indexed). We
caution that posv
(u) = posu
(v) does not hold in general. In this notation, a path (v1, . . . , vk) is
temporal if and only if posvi
(vi−1) < posvi
(vi+1) for every i ∈ {2, . . . , k−1}. Many of our arguments
hinge on the neighbors of a vertex that occupy the smallest and largest positions in its induced
ordering. For a vertex v, we define Nmin(v) as the unique vertex w with posv
(w) = 0, and Nmax(v)
as the unique vertex w maximizing posv
(w).
To certify that vk is temporally reachable from v1 in a spanner, we sometimes exhibit a temporal
walk rather than a temporal path, that is, a sequence W = (v1, . . . , vk) of vertices that may repeat,
including consecutively. We call W temporal if the sequence (u1, . . . , uk
′) obtained by collapsing
each maximal run of identical consecutive vertices into a single occurrence satisfies posui
(ui−1) ≤
posui
(ui+1) for every i ∈ {2, . . . , k′−1}. It is immediate that a temporal walk from v1 to vk contains
a temporal v1-vk-path, so it serves as a valid certificate. We use walks because they let us avoid
case distinctions when a vertex or edge may repeat.
2.2 Temporal cliques and bi-cliques
It was observed in [ABF+24] that the question of whether temporal cliques admit sparse spanners
is in fact equivalent to the analogous question for bi-cliques. To see the implication from cliques
to bi-cliques, let G = (S, T, λ) be a temporal bi-clique with edge labels in [1, L]. We extend G to a
temporal clique by assigning label L + 1 to all edges between two sources, and label 0 to all edges
between two targets (cf. Figure 1, left). Observe that any temporal path from a source to a target
cannot traverse any of the newly added edges. Hence, every temporal spanner of the constructed
clique contains a temporal spanner of G.
For the reverse implication, the authors of [ABF+24] showed how to associate to any temporal
clique a temporal bi-clique whose spanners translate to spanners of the original graph. We employ
4
L + 1 0
∈ [1, L]
S T
1
2 3
u w
v
1
1
2
3
0
u 0
s
vs
ws
ut
vt
wt
Figure 1: On the left, the resulting clique contains a spanner of the underlying bi-clique. On the
right, we are given a temporal clique and the corresponding constructed bi-clique (Lemma 4).
this construction to prove that Theorem 3 implies our main result that temporal cliques admit
spanners of linear size.
Lemma 4. Theorem 3 implies that every temporal clique on n vertices admits a spanner of size 14n.
Proof. Given a temporal clique G = (V, λ) on n vertices with strictly positive edge labels, we
construct a temporal bi-clique G′ = (S, T, λ′
) as follows (cf. Figure 1, right). For every v ∈ V ,
introduce a copy vS ∈ S and a copy vT ∈ T. Set λ
′
({vS, vT }) := 0 for all v and λ
′
({vS, uT }) :=
λ({v, u}) for all v ̸= u.
By Theorem 3, G′ admits a temporal spanner E′ of size 10 min(|S|, |T|) + 2(|S| + |T|) = 14n.
Define E∗ ⊆ V
(2) to be its projection, that is, E∗
:= 
{u, v} : {uS, vT } ∈ E′
, u ̸= v
	
. Then |E∗
| ≤
|E′
| ≤ 14n, and it remains to show that E∗
is a temporal spanner of G. Indeed, for every u, v ∈ V ,
there exists a temporal uS-vT -path P
′
in E′
. Project P
′ vertex by vertex, mapping xS and xT
both to x. Edges of the form {xS, xT } become consecutive repetitions and are collapsed (this can
occur only in a prefix of P
′
, since all edge labels of G are strictly positive). Every remaining edge
corresponds to an edge of E∗
, and the edge labels are preserved; hence the projection is a temporal
path in G.
For the remainder of the paper, we therefore focus on temporal bi-cliques. In some scenarios,
they can be easier to work with because they separate the roles of sources and targets. In a clique,
every vertex plays both roles simultaneously.
2.3 Dismountability and extremally matched bi-cliques
In [CPS21], Casteigts, Peters, and Schoeters introduced the concept of dismountability, which was
adapted to bi-cliques in [ABF+24] and revisited in [CCC25]. It is a simple yet powerful tool based
on the following idea (cf. Figure 2, left): Let s ∈ S, t := Nmin(s), and suppose there exists s
′ ∈ S
with post
(s
′
) < post
(s). Then the concatenation of the path (s
′
, t, s) with any temporal path
from s yields a temporal walk. Therefore, if a set of edges E′
covers (s, T) (i.e., covers (s, v)
for every v ∈ T), then E′ ∪ {{s, t}, {s
′
, t}} also covers (s
′
, T). This means that we can delete s
′
from the graph, find a spanner of the remaining graph, and then reintroduce s
′
together with the
edges {s, t} and {s
′
, t}. Since we add only a constant number of edges (two) per deleted source,
this is compatible with the goal of finding linear-sized spanners. In this case, we say that s
′
is
dismountable1
via (s, t).
Note that, if no dismountable sources exist, then for every s ∈ S we have Nmin(Nmin(s)) = s. In
particular, no two sources share the same smallest neighbor, and hence |S| ≤ |T|. The same concept
1The exact definitions of dismountable and extremally matched vary slightly throughout the literature. The
definitions given here are tailored to our purposes.
5
s
′
s
t = Nmin(s)
t
′
t
s = Nmax(t)
Figure 2: On the left, s
′
is dismountable via (s, t). On the right, t
′
is dismountable via (s, t).
applies to targets (cf. Figure 2, right): given t, t′ ∈ T with s := Nmax(t) and poss
(t
′
) > poss
(t),
one can extend any temporal walk ending in t by appending the path (t, s, t′
), allowing us to
delete t
′
, find a spanner of the remaining graph, and reintroduce t
′
together with the edges {s, t}
and {s, t′}. We then say that t
′
is dismountable via (s, t). Analogously, this yields a graph in which,
for every t ∈ T we have Nmax(Nmax(t)) = t, and in particular |T| ≤ |S|.
It follows that, if there are neither dismountable sources nor dismountable targets, the bi-clique
satisfies the following properties, and we call it extremally matched.
• Emin := {{s, Nmin(s)} : s ∈ S} = {{t, Nmin(t)} : t ∈ T} is a perfect matching.
• Emax := {{s, Nmax(s)} : s ∈ S} = {{t, Nmax(t)} : t ∈ T} is a perfect matching.
In particular, extremally matched bi-cliques satisfy |S| = |T|. We summarize these findings in the
following result. Here, given S
′ ⊆ S, T′ ⊆ T, we denote by G[S
′
, T′
] := (S
′
, T′
, λ|{{s,t} : s∈S′
, t∈T′}
)
the induced temporal subgraph.
Lemma 5 (Dismountability). Given a temporal bi-clique G = (S, T, λ), there exist S
′ ⊆ S, T
′ ⊆ T,
and a set E′ of at most 2(|S| + |T| − |S
′
| − |T
′
|) edges such that G[S
′
, T′
] is extremally matched
and, if E∗
is a temporal spanner of G[S
′
, T′
], then E∗ ∪ E′
is a temporal spanner of G.
Proof. Consider the algorithm that initializes S
′
:= S, T
′
:= T, E′
:= ∅ and repeatedly adjusts these
sets as follows. Throughout, dismountability refers to dismountability in the current graph G[S
′
, T′
].
• If s
′ ∈ S
′
is dismountable via (s, t), remove s
′
from S
′ and add {s, t} and {s
′
, t} to E′
.
• If t
′ ∈ T
′
is dismountable via (s, t), remove t
′
from T
′ and add {s, t} and {s, t′} to E′
.
The algorithm terminates once no dismountable vertices remain, and the resulting S
′
, T
′
, E′
satisfy
the claimed properties by construction.
This allows us to restrict our attention to extremally matched bi-cliques. More precisely, we
establish next that it suffices to prove the following.
Theorem 6. Every extremally matched temporal bi-clique (S, T, λ) with n := |S| = |T| contains a
temporal spanner of size 14n.
Proof that Theorem 6 implies Theorem 3. Given a temporal bi-clique (S, T, λ), by Lemma 5 there
exist S
′ ⊆ S and T
′ ⊆ T such that G[S
′
, T′
] is extremally matched, and a set E′ of at most
2(|S| + |T| − |S
′
| − |T
′
|) edges such that any temporal spanner of G[S
′
, T′
] can be extended to a
temporal spanner of G by adding the edges in E′
. By Theorem 6, G[S
′
, T′
] admits a temporal
spanner of size 14|S
′
|. Adding the edges in E′ yields a temporal spanner of G of size
14|S
′
| + 2(|S| + |T| − |S
′
| − |T
′
|)
|S
′
|=|T
′
|
= 10|S
′
| + 2(|S| + |T|) ≤ 10 min(|S|, |T|) + 2(|S| + |T|).
In the next two sections, we focus on proving Theorem 6, which, as shown in this section, implies
our main results Theorem 3 and that every temporal clique contains a spanner of linear size.
6
s
∗ = s0
si
sk
sn−1
t0
tj
tk+1
tn−1
min
k-cut
S
′
T
′
Figure 3: A 1-hop-k-cut-crossing source si (Definition 8).
3 Cuts in stars
Throughout this section, let G = (S, T, λ) be an extremally matched temporal bi-clique and assume
as usual that no two incident edges have the same label such that poss
(t) and post
(s) are welldefined for every s ∈ S, t ∈ T. Many of the statements in this and the next section come in two
analogous forms, one from the perspective of S and one from that of T. We label such pairs of
statements (a) and (b), and use (i), (ii) for parts that are not analogous. First, we introduce a
canonical way to label the vertices of G that we use throughout this and the next section.
Definition 7.
(a) For s
∗ ∈ S, the s
∗
-ordered labeling (cf. Figure 4, left) is the vertex labeling T = {t0, . . . , tn−1}
and S = {s0, . . . , sn−1} where the ti are ordered such that poss
∗ (ti) < poss
∗ (ti+1) for all
i ≤ n − 2 and si = Nmin(ti) for all i ≤ n − 1.
(b) For t
∗ ∈ T, the t
∗
-ordered labeling (cf. Figure 4, right) is the vertex labeling T = {t0, . . . , tn−1}
and S = {s0, . . . , sn−1} where the si are ordered such that post
∗ (si) > post
∗ (si+1) for all
i ≤ n − 2 and ti = Nmax(si) for all i ≤ n − 1.
Note that, since the bi-clique is extremally matched, we have in the s
∗
-ordered labeling that
s0 = Nmin(t0) = Nmin(Nmin(s
∗
)) = s
∗
. Next, we define a simple set of edges already covering a
large set of vertices.
Definition 8. Let s
∗ ∈ S and consider the s
∗
-ordered labeling.
(i) The simple star from s
∗
, denoted Star(s
∗
) consists of Emin and all edges incident to s
∗
.
(ii) Let k ∈ {0, . . . , n − 2}. We say that a source si
is m-hop-k-cut-crossing for s
∗
(cf. Figure 3)
if i > k and there exists j ≤ k and a temporal path of length at most m + 1 that begins in si
and ends with the edge {tj , s∗}.
The motivation for the definition above is as follows (cf. Figure 3): First, observe that, for
every j ≤ i, Star(s
∗
) covers the pair (sj , ti) via the temporal walk (sj , tj , s∗
, ti). In particular, given
some k ∈ {0, . . . , n−2}, we can set S
′
:= {s0, . . . , sk}, T
′
:= {tk, . . . , tn−1}, and obtain that Star(s
∗
)
covers (S
′
, T′
), that is, it covers (s, t) for every s ∈ S
′
, t ∈ T
′
.
7
Further, observe that, if a source si
is m-hop-k-cut-crossing via the path P, then Star(s
∗
)∪P also
covers (si
, T′
) via the temporal walks given by P ◦(s
∗
, t) for any t ∈ T
′
(cf. Figure 3), where W1 ◦W2
denotes the concatenation of the walks W1, W2. In other words, si being m-hop-k-cut-crossing
means that we can add si to S
′ by additionally adding m edges to Star(s
∗
) (those m edges are the
edges of P, where the last edge of P is already contained in Star(s
∗
)).
We remark that the definition could be easily extended to incorporate more cases, such as
targets crossing the cut, and the analogous case where the star center is a target. But since our
proof does not need that generality, we state only the one-sided version here for brevity.
The following observation summarizes the above discussion.
Observation 9. Let s
∗ ∈ S, m ∈ N, k ∈ {0, . . . , n − 2}, and consider the s
∗
-ordered labeling. Let Scross denote the set of sources that are m-hop-k-cut-crossing, T
′
:= {tk, . . . , tn−1},
and S
′
:= {s0, . . . , sk}∪Scross. Then there exists a set of |Scross|·m edges E′
such that E′ ∪Star(s
∗
)
covers (S
′
, T′
).
3.1 Intuition for proof of Theorem 6
In this subsection, we explain the intuition behind our proof of Theorem 6. The two results in
this subsection are not needed for the proof, but serve to motivate the proof structure used in
the following section. We state them here only giving the main ideas, deferring the full proofs to
Section 6. A reader interested only in a direct proof of Theorem 6 may skip to Section 4.
The next lemma shows that Theorem 6 follows if a linear number of edges covers a sufficiently
large subgraph.
Lemma 10. Suppose there exist constants C ≥ 1, δ ∈ (0, 1] such that, for every extremally matched
temporal bi-clique G = (S, T, λ) of size n := |S|, there exist S
′ ⊆ S, T
′ ⊆ T and a set E′ of at
most Cn edges satisfying
(i) E′
covers (S
′
, T′
),
(ii) |S
′
| + |T
′
| ≥ (1 + δ)n.
Then every temporal bi-clique contains a spanner of size O(n).
Proof sketch. It remains to cover (S \ S
′
, T) and (S, T \ T
′
). By dismountability (Lemma 5),
each reduces to an extremally matched instance of size at most |S \ S
′
|, respectively |T \ T
′
|, at
the cost of linearly many additional edges. The total size of the remaining instances is therefore
|S \ S
′
| + |T \ T
′
| = 2n − |S
′
| − |T
′
| ≤ (1 − δ)n. With this, a straightforward recursion yields a
spanner of size O(n), where the constant factor hidden in the O-notation depends on C and δ.
An immediate consequence of Observation 9 is the following: if there exists a constant m ∈ N,
such that every extremally matched temporal bi-clique (S, T, λ) admits some s
∗ ∈ S and k ∈
{0, . . . , n − 2} with Ω(n) many m-hop-k-cut-crossing sources, then the assumptions of Lemma 10
are satisfied, and Theorem 6 follows. One might hope to prove this in general, but this fails: we
prove that the classical shifted matching graphs provide a counterexample. The shifted matching graph of size n is defined by (see Figure 6) S := {s0, . . . , sn−1}, T := {t0, . . . , tn−1}, and
λ({si
, tj}) := j − i mod n. Shifted matching graphs were introduced in [ABF+24] alongside a notion called edge pivotability, closely related to our definition of crossing cuts in stars. There, the
authors showed that edge-pivotable temporal bi-cliques admit linear spanners, while the shifted
matching graphs witness that not every temporal bi-clique is edge-pivotable. It is therefore unsurprising that they also fail to have Ω(n) crossing sources.
8
We prove something stronger, however: having no 1-hop-k-cut-crossing sources for any s
∗
and k characterizes the shifted matching graph up to isomorphism. Here, two temporal bi-cliques
(S1, T1, λ1) and (S2, T2, λ2) are isomorphic if there exist bijections ΨS : S1 → S2 and ΨT : T1 → T2
such that poss
(t) = posΨS(s)
(ΨT (t)) and post
(s) = posΨT (t)
(ΨS(s)) for all s ∈ S1, t ∈ T1.
Proposition 11. Let G = (S, T, λ) be an extremally matched temporal bi-clique with n := |S|.
Then G is isomorphic to the shifted matching graph on n vertices if and only if, for every s
∗ ∈ S
and every k ∈ {0, . . . , n − 2}, there is no 1-hop-k-cut-crossing source.
However, as noted in [ABF+24], the shifted matching graph admits a linear spanner (see Figure 6, right): let E′
consist of Emin, Emax, all edges incident to s0, and all edges incident to t0. For
i ≤ j, the pair (si
, tj ) is covered by the temporal walk (si
, ti
, s0, tj ); for i > j, by (si
, t0, sj+1, tj ).
To summarize, if a temporal bi-clique has a simple star and a k-cut with Ω(n) crossing sources,
Observation 9 together with Lemma 10 yields a linear spanner. If no k-cut has any crossing sources
for any star, the graph is isomorphic to a shifted matching graph, which also admits a linear
spanner. It remains to handle the intermediate cases. To this end, we introduce in the next section
the notion of extended stars. These are simple stars augmented by a linear number of edges that
capture many cut-crossing paths. We then show that either some simple star has many cut-crossing
sources, or there exist two extended stars, one centered at a source and one at a target, similarly
to the spanner structure of the shifted matching graph, that together cover a sufficiently large
subgraph.
4 Extended stars
This section contains our main technical contribution. We introduce a carefully constructed structure of O(n) edges called an extended star and prove that either two such structures together cover
a sufficiently large subset of vertices, or some simple star has sufficiently many 3-hop-k-cut-crossing
sources. This then allows us to conclude that temporal cliques admit spanners of linear size.
Throughout this section, let G = (S, T, λ) be an extremally matched temporal bi-clique of
size n := |S| = |T|, and assume that no two incident edges share a label, such that poss
(t) and
post
(s) are well-defined for every s ∈ S, t ∈ T. We begin by defining extended stars.
Definition 12. Let s
∗ ∈ S and t
∗ ∈ T. For x ∈ {s
∗
, t∗}, the extended star from x, denoted Ext(x),
consists of Emin, Emax, all edges incident to x, and the following additional edges.
(a) If x = s
∗
, consider the labeling induced by s
∗ and, for each s ∈ S \ {s
∗}, define its extend
index (cf. Figure 4, left) as
ind(s) := max
l : postl
(s) > postl
(s
∗
)
	
whenever this set is nonempty. If ind(s) is defined, add the edge {s, tind(s)} to Ext(s
∗
).
(b) If x = t
∗
, consider the labeling induced by t
∗ and, for each t ∈ T \ {t
∗}, define its extend
index (cf. Figure 4, right) as
ind(t) := max
l : possl
(t) < possl
(t
∗
)
	
whenever this set is nonempty. If ind(t) is defined, add the edge {sind(t)
, t} to Ext(t
∗
).
The following lemma identifies a large class of source-target pairs covered by extended stars,
and conveys the main intuition behind their definition.
9
s
∗ = s0
s1
s2
sn−1
t0 = Nmin(s
∗
)
t1
t2
tn−1 = Nmax(s
∗
)
extend index
of s2
min
Nmax(t
∗
) = s0
s1
s2
Nmin(t
∗
) = sn−1
t0 = t
∗
t1
t2
tn−1
extend index
of t2
max
Figure 4: The left subfigure illustrates the labeling induced by s
∗
(Definition 7 (a)). The dashed
edges denote the minimum label matching Emin. The extend index of s2 (Definition 12 (a)) is the
index of the bottommost target satisfying the ordering indicated by the red arrow.
The right subfigure illustrates the labeling induced by t
∗
(Definition 7 (b)). The dashed edges
denote the maximum label matching Emax. The extend index of t2 (Definition 12 (b)) is the index
of the bottommost source satisfying the ordering indicated by the red arrow.
Lemma 13.
(a) Let s
∗ ∈ S, and consider the labeling induced by s
∗
. Let t ∈ T and assume that the extend
index of Nmax(t) is defined and equals i. Then Ext(s
∗
) covers (sj , t) for all j ≤ i.
(b) Let t
∗ ∈ T, and consider the labeling induced by t
∗
. Let s ∈ S and assume that the extend
index of Nmin(s) is defined and equals i. Then Ext(t
∗
) covers (s, tj ) for all j ≤ i.
Proof. For part (a), observe that Nmax(t) having extend index i implies, by definition, that the
path (s
∗
, ti
, Nmax(t)) is temporal. Given j ≤ i, we obtain that the walk
(sj , tj , s∗
, ti
, Nmax(t), t)
is temporal (cf. Figure 4, left), where we used that Nmin(tj ) = sj , and that the bi-clique is extremally matched, so the edge {Nmax(t), t} is maximal at Nmax(t). Moreover, the walk is contained
in Ext(s
∗
), so that Ext(s
∗
) covers (sj , t).
Part (b) follows analogously from the fact that the walk
(s, Nmin(s), si
, t∗
, sj , tj )
is temporal for every j ≤ i (cf. Figure 4, right).
Conversely, if an extended star does not cover a pair, we can deduce the following about the
ordering of certain edges.
Lemma 14. Let s, s∗ ∈ S and t, t∗ ∈ T.
(a) If Ext(s
∗
) does not cover (s, t), then posNmin(s)
(Nmax(t)) ≤ posNmin(s)
(s
∗
).
10
min
max
s
∗
Nmax(t)
s Nmin(s)
t
∗
t
by Lemma 14 (b)
by Lemma 14 (a)
Figure 5: If Ext(s
∗
) ∪ Ext(t
∗
) does not cover (s, t), then the edges are ordered as indicated by the
arrows.
(b) If Ext(t
∗
) does not cover (s, t), then posNmax(t)
(t
∗
) ≤ posNmax(t)
(Nmin(s)).
Proof. For part (a), consider the labeling induced by s
∗ and let j be chosen such that s = sj .
If Nmax(t) = s
∗
, the desired inequality holds with equality, so we can assume Nmax(t) ̸= s
∗
. (One
can even observe that Nmax(t) = s
∗
is a contradiction to (s, t) not being covered.) If Nmax(t)
has an extend index that is greater or equal to j, then by Lemma 13 (a), Ext(s
∗
) covers the
pair (sj , t) = (s, t), which is a contradiction. Therefore, Nmax(t) has either no extend index or it is
strictly smaller than j. By Definition 12 (a) (with Nmax(t) ̸= s
∗
), this means that
postl
(Nmax(t)) ≤ postl
(s
∗
) for every l ≥ j.
In particular, this holds for l = j, i.e., when tl = tj = Nmin(sj ) = Nmin(s).
For part (b), consider the labeling induced by t
∗ and let j be such that t = tj . Analogously
to part (a), the case Nmin(s) = t
∗
is trivial, so we can assume Nmin(s) ̸= t
∗
. By Lemma 13 (b),
if Nmin(s) has an extend index greater or equal to j, then Ext(t
∗
) covers (s, tj ) = (s, t). Therefore, Nmin(s) has either no extend index or it is smaller than j. Analogously to the proof of part (a),
this implies that possj
(Nmin(s)) ≥ possj
(t
∗
). This completes the proof as sj = Nmax(t).
Putting the two parts of this lemma together, we immediately obtain the following (cf. Figure 5).
Corollary 15. Let s, s∗ ∈ S and t, t∗ ∈ T. If Ext(s
∗
) ∪ Ext(t
∗
) does not cover (s, t), then the walk
(Nmin(t
∗
), t∗
, Nmax(t), Nmin(s), s∗
)
is temporal.
This corollary connects the coverage of extended stars to cut-crossings in simple stars.
Lemma 16. Let s
∗ ∈ S and consider the s
∗
-ordered labeling. Let k ∈ {0, . . . , n − 2}. Then, for
every i > k, one of the following holds:
(i) si is 3-hop-k-cut-crossing.
(ii) Ext(s
∗
) ∪ Ext(ti) covers (sj , T) for every j ≤ k.
Proof. Assume that condition (ii) is not fulfilled, i.e., there exists j ≤ k and t ∈ T such that (sj , t) is
not covered by Ext(s
∗
)∪Ext(ti). Then, by Corollary 15, the walk (si
, ti
, Nmax(t), tj , s∗
) is temporal.
This means that si
is 3-hop-k-cut-crossing (cf. Figure 5, Definition 8).
11
We summarize the findings of this section in the following result, which constitutes our main
technical contribution.
Lemma 17. Fix s
∗ ∈ S, consider the s
∗
-ordered labeling, and set k := ⌊n/2⌋. Let S
′
:= {s0, . . . , sk}
and T
′
:= {tk, . . . , tn−1}. Then there exists a set E∗ of at most 6n edges containing Emin ∪ Emax
that covers either
(i) (S, T′
), or
(ii) (S
′
, T).
Proof. First, assume that every source si with i > k is 3-hop-k-cut-crossing, i.e., the set of 3-hop-kcut-crossing sources is Scross = {sk+1, . . . , sn−1}. By Observation 9, there exists a set E′ of at most
3|Scross| ≤ 3n edges such that E′ ∪ Star(s
∗
) covers (S
′ ∪ Scross, T′
) = (S, T′
). Recall that Star(s
∗
)
contains Emin and | Star(s
∗
)| = 2n − 1. So we can set E∗
:= Star(s
∗
) ∪ E′ ∪ Emax to obtain a set
of at most 6n edges fulfilling condition (i).
Now assume there exists i > k such that si
is not 3-hop-k-cut-crossing. Then by Lemma 16, the
set E∗
:= Ext(s
∗
)∪Ext(ti) covers (S
′
, T). Recall from Definition 12 that Ext(s
∗
)∪Ext(ti) consists
of Emin, Emax, all edges incident to s
∗
, all edges incident to ti
, at most one additional edge per
source (from Ext(s
∗
)), and at most one additional edge per target (from Ext(ti)). Each of these
six groups contains at most n edges, so |E∗
| ≤ 6n, and condition (ii) holds.
We now have all the ingredients to prove Theorem 6. We restate it here in a slightly stronger
form that will allow us to improve the bound on the constant factors for cliques in Section 5.
Theorem 18. Every extremally matched temporal bi-clique (S, T, λ) with n := |S| = |T| contains
a temporal spanner of size 14n. Moreover, this spanner also covers (S ∪ T, S ∪ T).
Proof. Let f(n) denote the maximum size of a lightest spanner of an extremally matched temporal
bi-clique of size n, that is,
f(n) := max{min{|E
′
| : E
′
is a spanner of G} : G = (S, T, λ) is extremally matched with |S| = n}.
Let Gn = (S, T, λ) be an extremally matched temporal bi-clique realizing this maximum. Fix s
∗ ∈ S,
consider the s
∗
-ordered labeling, and let S
′
, T′ be as in Lemma 17. By Lemma 17, there exists a
set E∗ of at most 6n edges covering either (S, T ′
) or (S
′
, T). In the first case, it remains to find a
spanner of (S, T \ T
′
), and in the second a spanner of (S \ S
′
, T). In both cases, call this remaining
subgraph G′
.
Note that |S\S
′
| = |{s⌊n/2⌋+1, . . . , sn−1}| ≤ ⌊n/2⌋, and similarly |T \T
′
| = |{t0, . . . , t⌊n/2⌋−1}| =
⌊n/2⌋. Hence, in both cases, G′
is a bi-clique with at most ⌊3n/2⌋ vertices in total, with the
smaller side having size at most ⌊n/2⌋ and the larger side having size n. Applying dismountability,
i.e., Lemma 5 to G′
, we obtain S
′′ ⊆ S and T
′′ ⊆ T such that G[S
′′, T′′] is extremally matched
with |S
′′| = |T
′′| ≤ ⌊n/2⌋, and a set of edges E′′ such that adding E′′ to any spanner of G[S
′′, T′′]
yields a spanner of G′
, where
|E
′′| ≤ 2 · (⌊3n/2⌋ − |S
′′| − |T
′′|)
|S
′′|=|T
′′|
≤ 3n − 4|S
′′|.
To summarize, we have selected the edges E∗∪E′′ and it only remains to find a spanner of G[S
′′, T′′]
to obtain a spanner of Gn. Setting xn := |S
′′| ≤ ⌊n/2⌋, we have
f(n) ≤ |E
∗
| + |E
′′| + f(|S
′′|) ≤ 6n + 3n − 4xn + f(xn) = 9n − 4xn + f(xn).
12
We now prove by strong induction that f(n) ≤ 14n. The base case f(1) = 1 is immediate (and we
set f(0) := 0 for the case where xn = 0, i.e., the recursion ends). For the induction step, we have
f(n) ≤ 9n − 4xn + f(xn)
ind. hyp.
≤ 9n + (14 − 4)xn
xn≤n/2
≤ 9n + 10 ·
n
2
≤ 14n.
Hence spanners of the claimed size exist. Last, the final edge set contains Emin ∪ Emax as it is
contained in the edge set added in the first recursion level chosen according to Lemma 17. This
ensures that the spanner does in fact preserve all temporal reachabilities: any target t reaches the
same set of vertices as Nmin(t), since prefixing any temporal walk beginning in Nmin(t) with the
edge {t, Nmin(t)} yields a valid temporal walk (where we have used that G is extremally matched).
Symmetrically, any source s is reachable from the same set of vertices that reach Nmax(s), since
appending {s, Nmax(s)} to any temporal walk ending at Nmax(s) again yields a temporal walk.
Recall from Section 2 that Theorem 6 implies Theorem 3 and that every temporal clique contains
a spanner of size 14n.
5 A simple improvement on the constant factor for cliques
While the focus of our work lies in proving the optimal asymptotics of spanners of temporal cliques,
we illustrate here briefly how a result from the literature can be invoked to halve the constant factor
for cliques from 14n to 7n.
In [CCC25], the concept of dismountability for cliques was refined as follows. Given a temporal
clique G = (V, λ), we say that a vertex v is {1, 2}-hop dismountable if there exist vertices u, w such
that (v, Nmin(u), u) is a temporal walk and (w, Nmax(w), v) is a temporal walk. If this is the case,
one can remove v from the graph, find a spanner of the remaining graph and then reintroduce v
together with the at most 4 edges of the two walks. Analogously to the proof of Lemma 5, we
obtain the following by repeatedly deleting dismountable vertices.
Observation 19. Let G = (V, λ) be a temporal clique. Then there exists V
′ ⊆ V and a set E′ of
at most 4(|V | − |V
′
|) edges such that no vertex of G[V
′
] is {1, 2}-hop dismountable and, if E∗
is a
temporal spanner of G[V
′
], then E∗ ∪ E′
is a temporal spanner of G.
We make use of the following known result for which we do not provide a proof here.
Theorem 20 (Carnevale, Casteigts, Corsini [CCC25, Corollary 4.1]). Let G = (V, λ) be a temporal
clique that has no {1, 2}-hop dismountable vertices. Let V
− := {Nmin(v) : v ∈ V } and V
+ :=
{Nmax(v) : v ∈ V }. Then V
− and V
+ have the same size and form a partition of V , and the
temporal bi-clique G′
:= (V
−, V +, λ) is extremally matched.
This allows us to halve the factor proven in Lemma 4 and conclude our main result in its final
form. We begin by restating it.
Theorem 2. Every temporal clique on n vertices admits a temporal spanner of size 7n.
Proof. Let G = (V, λ) be a temporal clique on n vertices. Then by Observation 19, there exists V
′ ⊆ V of size n
′
:= |V
′
|, and a set E′ of size at most 4(n − n
′
) such that G[V
′
] has no
{1, 2}-hop dismountable vertices, and unioning a spanner of G[V
′
] with E′ yields a spanner of G.
Then by Theorem 20, the sets V
− := {Nmin(v) : v ∈ V
′} and V
+ := {Nmax(v) : v ∈ V
′} (where Nmin
and Nmax are taken in G[V
′
]) have each size n
′/2, partition V
′
, and the bi-clique G′
:= (V
−, V +, λ)
is extremally matched. By Theorem 18, G′
contains a spanner E∗ of size 14n
′/2 = 7n
′
that also
spans G[V
′
]. Together, we obtain a spanner of size
7n
′ + 4(n − n
′
) = 4n + 3n
′ ≤ 7n.
13
6 Recursion in bi-cliques and shifted matching graphs
In this subsection, we provide the missing proofs from Section 3.1. We begin by restating the
lemma that allows recursion in bi-cliques when a sufficiently large subgraph is already covered. Its
proof is analogous to the argument that Lemma 17 implies Theorem 6 at the end of the previous
section and in fact generalizes it, where we are somewhat less careful about minimizing constant
factors.
Lemma 10. Suppose there exist constants C ≥ 1, δ ∈ (0, 1] such that, for every extremally matched
temporal bi-clique G = (S, T, λ) of size n := |S|, there exist S
′ ⊆ S, T
′ ⊆ T and a set E′ of at
most Cn edges satisfying
(i) E′
covers (S
′
, T′
),
(ii) |S
′
| + |T
′
| ≥ (1 + δ)n.
Then every temporal bi-clique contains a spanner of size O(n).
Proof. Let f(n) denote the maximum lightest-spanner size over all extremally matched temporal
bi-cliques of size n, i.e.,
f(n) := max
min{|E
′
| : E
′
is a spanner of G} : G = (S, T, λ) is extremally matched with |S| = n
	
,
and let G = (S, T, λ) be an extremally matched bi-clique of size n realizing this maximum. By
assumption, there exist S
′ and T
′ as described, so it remains to cover (S \ S
′
, T) and (S, T \ T
′
).
Before proceeding recursively, we apply dismountability (Lemma 5). Applied to G[S \ S
′
, T],
Lemma 5 yields subsets S
′′ ⊆ S \ S
′ and T
′′ ⊆ T such that G[S
′′, T′′] is extremally matched,
together with an edge set E′′ of size safely upper bounded by 2(|S| + |T|) = 4n such that any
spanner of G[S
′′, T′′] together with E′′ forms a spanner of G[S \ S
′
, T]. Since S
′′ ⊆ S \ S
′
, we
have |S
′′| ≤ n − |S
′
|. An analogous application of Lemma 5 to G[S, T \ T
′
] reduces covering that
subgraph to an extremally matched bi-clique of size at most n − |T
′
|, at an additional cost of at
most 4n edges.
To summarize, there exists a set of edges consisting of the Cn edges from Lemma 10, and
another at most 4n + 4n = 8n edges from applying dismountability, such that the problem reduces
to finding spanners of two smaller bi-cliques, one of size an := n−|S
′
| and one of size bn := n−|T
′
|,
which satisfy an + bn ≤ (1 − δ)n. Therefore, we have
f(n) ≤ (C + 8)n + f(an) + f(bn).
We prove by strong induction that f(n) ≤
C+8
δ
n for all n. The base case f(1) = 1 ≤
C+8
δ
is
immediate as C ≥ 1, δ ∈ (0, 1] (and we set f(0) := 0 for the case where an or bn is 0, i.e., the
recursion ends). For the induction step, we have
f(n) ≤ (C + 8) n + f(an) + f(bn)
ind. hyp.
≤ (C + 8) n +
C + 8
δ
(an + bn)
≤ (C + 8) n +
C + 8
δ
(1 − δ) n =
C + 8
δ
n.
Next, we establish the relation between the shifted matching graph and the existence of 1-hopk-cut-crossing sources as stated in Section 3.1. We begin by restating the assertion.
Proposition 11. Let G = (S, T, λ) be an extremally matched temporal bi-clique with n := |S|.
Then G is isomorphic to the shifted matching graph on n vertices if and only if, for every s
∗ ∈ S
and every k ∈ {0, . . . , n − 2}, there is no 1-hop-k-cut-crossing source.
14
0
1
2
0
1
2
n − 1
n − 2
0
1
n − 1
n − 2
0
0
s
∗ = s0
s1
s2
sn−1
t0
t1
t2
tn−1
s0
s1
s2
sn−1
t0
t1
t2
tn−1
Figure 6: On the left, a subset of edges of the shifted matching graph is illustrated. On the right,
a spanner of the shifted matching graph is depicted. The red edges {si
, ti} denote the 0-labeled
edges. The blue edges {si
, ti − 1} denote the edges of label n − 1.
Proof. We first show that the shifted matching graph admits no 1-hop-k-cut-crossing sources.
By symmetry, for any s
∗ ∈ S, the s
∗
-ordered labeling of the shifted matching graph satisfies
again λ({si
, tj}) = j − i mod n (cf. Figure 6). For every i > j, we have
postj
(s0) = j
i≤n−1
< j + (n − i) = n − (i − j) = j − i mod n = postj
(si).
Observe that this means precisely that there are no 1-hop-k-cut-crossing sources for s0 and any k
(cf. Figure 3). As s0 was chosen arbitrary, the statement follows for every s0 ∈ S.
For the converse, let G = (S, T, λ) be an extremally matched temporal bi-clique with no 1-hopk-cut-crossing sources. Fix s0 ∈ S and consider the s0-ordered labeling. We show that postj
(si) =
possi
(tj ) = j − i mod n for all i, j, which implies that G is isomorphic to the shifted matching
graph.
The absence of 1-hop-k-cut-crossing sources means precisely (cf. Figure 3) that
postj
(si) > postj
(s0) for every 0 ≤ j < i ≤ n − 1. (1)
We derive several consequences.
First, (1) implies for each j that, in the ordering of S induced by tj , at least n − 1 − j vertices
appear after s0, and hence postj
(s0) ≤ n − 1 − (n − j − 1) = j = poss0
(tj ). Since s0 and tj were
arbitrary, we obtain post
(s) ≤ poss
(t) for all s and t. As P
s,t poss
(t) = P
s,t post
(s) = Pn−1
i=0
Pn−1
j=0 j,
no pair can achieve a strict inequality, so
poss
(t) = post
(s) for all s ∈ S, t ∈ T. (2)
Our findings so far imply the following: For every j ∈ {0, . . . , n − 1}, in the ordering of S induced by tj , we have by (2) that s0 is in j-th position and by (1) that {sj+1, . . . , sn−1} occupy
positions j + 1, . . . , n − 1. Therefore, {s0, . . . , sj} fill positions {0, . . . , j}. By definition, we also
have postj
(sj ) = 0. To summarize, we have
postj
(sj ) = 0
postj
(si) ∈ {1, . . . , j} for i ∈ {0, . . . , j − 1} (3)
postj
(si) ∈ {j + 1, . . . , n − 1} for i ∈ {j + 1, . . . , n − 1}
15
In particular, we have
Nmax(tj ) ∈ {sj+1, . . . , sn−1} for every j ∈ {0, . . . , n − 2}
Applying this at j = n − 2 gives Nmax(tn−2) = sn−1, and since Nmax : T → S is a bijection,
downward induction together with Nmax(tn−1) = s0 yields
Nmax(tj ) = sj+1 mod n for all j. (4)
Next, observe that (1) with s := s0, i = n − 1 and arbitrary t ̸= Nmax(s) (i.e., t = tj for some
j ∈ {0, . . . , n − 2}) reads as
post
(Nmin(Nmax(s))) = post
(sn−1)
(1)
> post
(s0) = post
(s) (5)
Since s0 was fixed arbitrarily, this means that this holds for every s and t ̸= Nmax(s). In our fixed
labeling, applying this on s = si together with the fact that Nmin(Nmax(si)) = si−1 mod n by (4),
this implies that
postj
(si−1 mod n) > postj
(si) for every j ̸= i − 1. (6)
To conclude, observe that (3) together with (6) imply that postj
(si) = j − i mod n as desired.
Together with (2), this completes the proof.
7 Concluding remarks
In this work, we settled the optimal asymptotic size of a lightest spanner of a temporal clique to
be Θ(n), improving on the previous known bound of O(n log n) [CPS21].
Let us recap the proof of Theorem 6 from an algorithmic perspective. Fix an arbitrary s
∗ ∈ S
and set k := ⌊n/2⌋. By Lemma 16, either every source si with i > k is 3-hop-k-cut-crossing, or
there exists a non-crossing source si such that Ext(s
∗
) ∪ Ext(ti) covers a large subgraph. Checking
whether a source is 3-hop-k-cut-crossing, and finding the corresponding path if so, can be done in
polynomial time, as can computing Ext(v) for any vertex v. Hence, determining which of the two
conditions holds and computing the edge set E∗
in Lemma 17 can be carried out in polynomial
time.
In the proof that Lemma 17 implies Theorem 6, we apply dismountability and then recurse
to a depth of at most log n, each step taking polynomial time. Last, the steps in the proof that
Theorem 20 implies Theorem 2 are also polynomial, so we obtain the following.
Observation 21.
(i) For every temporal bi-clique (S, T, λ), a spanner of size 10 min(|S|, |T|) + 2(|S| + |T|) can be
computed in polynomial time.
(ii) For every temporal clique on n vertices, a spanner of size 7n can be computed in polynomial
time.
With the asymptotics now settled, the natural next question is to determine the correct constants. Our aim in this work was to establish a linear bound, and we make no claim that our bound
of 7n is anywhere near optimal. We believe that optimizing it further lies beyond the scope of this
work, but we regard it as an interesting direction for future research. The best known lower bound
is 2n − 4 [Bum81]. Moreover, the authors of [CPS21] report that, despite an extensive computer
search, they found no instance failing to admit a spanner with 2n − 3 edges, and they pose the
following open problem.
16
Question 22. Does every temporal clique admit a spanner of size 2n − 3?
Recent research [BDG+22] has focused not only on minimizing the size of a temporal spanner,
but also its stretch, that is, the maximum length of a temporal reachability path in the spanner.
We remark that, in Lemma 17, the set E∗
in fact covers the claimed subgraphs in such a way
that each reachability path has length at most 5, so one might hope that our techniques carry
over to this setting. This is not the case, however. The main obstacle is our heavy reliance on
dismountability (Lemma 5): we sometimes remove a vertex, find a spanner of the remaining graph,
and then reintroduce the vertex, which can add 2 to the stretch of the spanner. This paradigm is
therefore incompatible with bounding the stretch. In particular, Lemma 17 assumes the bi-clique to
be extremally matched, and this assumption is without loss of generality only when we are allowed
to use dismountability. While [BDG+22] shows that no sparse spanners of stretch 2 exist, it is
an intriguing question whether the same holds for stretch 3 or more. We pose the following two
versions of this question, both of which remain open.
Question 23. Does every temporal clique admit a spanner of size O(n) and stretch O(1)?
Question 24. Does every temporal clique admit a spanner of size O(n) and stretch 3?
Acknowledgements. I am grateful to Davide Bilò for suggesting the related question of temporal
spanners with bounded stretch at the AlgUW workshop in Będlewo (September 2025), which first
drew my attention to the problem resolved in the present paper. I thank him, along with Václav
Blažej, Maël Dumas, and Anna Zych-Pawlewicz, for the fruitful discussions that followed.
References
[ABF+24] Sebastian Angrick, Ben Bals, Tobias Friedrich, Hans Gawendowicz, Niko Hastrich,
Nicolas Klodt, Pascal Lenzner, Jonas Schmidt, George Skretas, and Armin Wells. How
to reduce temporal cliques to find sparse spanners. In Proceedings of the 32nd European
Symposium on Algorithms (ESA), pages 11:1–11:15, 2024.
[ADL25] Caelan Atamanchuk, Luc Devroye, and Gábor Lugosi. On the size of temporal cliques
in subcritical random temporal graphs. Combinatorics, Probability and Computing,
34(5):671–679, 2025.
[AF16] Kyriakos Axiotis and Dimitris Fotakis. On the size and the approximability of minimum
temporally connected subgraphs. In Proceedings of the 43rd International Colloquium
on Automata, Languages, and Programming (ICALP), LIPIcs, pages 149:1–149:14,
2016.
[AGMS17] Eleni C. Akrida, Leszek Gąsieniec, George B. Mertzios, and Paul G. Spirakis. The
complexity of optimal design of temporally connected graphs. Theory of Computing
Systems, 61(3):907–944, 2017.
[AMSZ18] Eleni C. Akrida, George B. Mertzios, Paul G. Spirakis, and Viktor Zamaraev. Temporal
vertex cover with a sliding time window. In Proceedings of the 45th International Colloquium on Automata, Languages, and Programming (ICALP), volume 107 of LIPIcs,
pages 148:1–148:14, 2018.
17
[BCC+26] Ruben Becker, Arnaud Casteigts, Pierluigi Crescenzi, Bojana Kodric, Michael Raskin,
Malte Renken, and Viktor Zamaraev. Giant components in random temporal graphs.
SIAM Journal on Discrete Mathematics, 40(2):449–485, 2026.
[BCF+23] Davide Bilò, Sarel Cohen, Tobias Friedrich, Hans Gawendowicz, Nicolas Klodt, Pascal
Lenzner, and George Skretas. Temporal network creation games. In Proceedings of the
32nd International Joint Conference on Artificial Intelligence (IJCAI), pages 2511–
2519, 2023.
[BCF+25] Davide Bilò, Sarel Cohen, Tobias Friedrich, Hans Gawendowicz, Nicolas Klodt, Pascal Lenzner, and George Skretas. Temporal network creation games: The impact of
non-locality and terminals. In Proceedings of the 24th International Conference on
Autonomous Agents and Multiagent Systems (AAMAS), pages 334–342, 2025.
[BDG+22] Davide Bilò, Gianlorenzo D’Angelo, Luciano Gualà, Stefano Leucci, and Mirko Rossi.
Sparse temporal spanners with low stretch. In Proceedings of the 30th European Symposium on Algorithms (ESA), volume 244 of LIPIcs, pages 19:1–19:16, 2022.
[BDG+24] Davide Bilò, Gianlorenzo D’Angelo, Luciano Gualà, Stefano Leucci, and Mirko Rossi.
Blackout-tolerant temporal spanners. Journal of Computer and System Sciences,
141:103495, 2024.
[BKL24] Nicolas Broutin, Nina Kamčev, and Gábor Lugosi. Increasing paths in random temporal graphs. The Annals of Applied Probability, 34(6):5498–5521, 2024.
[Bum81] Richard T. Bumby. A problem with telephones. SIAM Journal on Algebraic Discrete
Methods, 2(1):13–18, 1981.
[CCC25] Daniele Carnevale, Arnaud Casteigts, and Timothée Corsini. Dismountability in temporal cliques revisited. In Proceedings of the 4th Symposium on Algorithmic Foundations of Dynamic Networks (SAND), LIPIcs, pages 6:1–6:18, 2025.
[CFQS12] Arnaud Casteigts, Paola Flocchini, Walter Quattrociocchi, and Nicola Santoro. Timevarying graphs and dynamic networks. International Journal of Parallel, Emergent
and Distributed Systems, 27(5):387–408, 2012.
[CHMZ21] Arnaud Casteigts, Anne-Sophie Himmel, Hendrik Molter, and Philipp Zschoche. Finding temporal paths under waiting time constraints. Algorithmica, 83(9):2754–2802,
2021.
[CPS21] Arnaud Casteigts, Joseph G. Peters, and Jason Schoeters. Temporal cliques admit
sparse spanners. Journal of Computer and System Sciences, 121:1–17, 2021.
[CRRZ24] Arnaud Casteigts, Michael Raskin, Malte Renken, and Viktor Zamaraev. Sharp thresholds in random simple temporal graphs. SIAM Journal on Computing, 53(2):346–388,
2024.
[EMMZ21] Jessica A. Enright, Kitty Meeks, George B. Mertzios, and Viktor Zamaraev. Deleting
edges to restrict the size of an epidemic in temporal networks. Journal of Computer
and System Sciences, 119:60–77, 2021.
18
[EMS21] Jessica A. Enright, Kitty Meeks, and Fiona Skerman. Assigning times to minimise
reachability in temporal graphs. Journal of Computer and System Sciences, 115:169–
186, 2021.
[KKK00] David Kempe, Jon M. Kleinberg, and Amit Kumar. Connectivity and inference problems for temporal networks. In Proceedings of the 32nd Annual ACM Symposium on
Theory of Computing (STOC), pages 504–513, 2000.
[KMMS22] Nina Klobas, George B. Mertzios, Hendrik Molter, and Paul G. Spirakis. The complexity of computing optimum labelings for temporal connectivity. In Proceedings of
the 47th International Symposium on Mathematical Foundations of Computer Science
(MFCS), volume 241 of LIPIcs, pages 62:1–62:15, 2022.
[Mic16] Othon Michail. An introduction to temporal graphs: An algorithmic perspective. Internet Mathematics, 12(4):239–280, 2016.
[MMN+23] George B. Mertzios, Hendrik Molter, Rolf Niedermeier, Viktor Zamaraev, and Philipp
Zschoche. Computing maximum matchings in temporal graphs. Journal of Computer
and System Sciences, 137:1–19, 2023.
[MMS19] George B. Mertzios, Othon Michail, and Paul G. Spirakis. Temporal network optimization subject to connectivity constraints. Algorithmica, 81(4):1416–1449, 2019.
[MNRS24] George B. Mertzios, Sotiris E. Nikoletseas, Christoforos Raptopoulos, and Paul G.
Spirakis. The threshold of existence of δ-temporal cliques in random simple temporal
graphs. In Proceedings of the 20th International Symposium on Algorithmics of Wireless
Networks (ALGOWIN), volume 15026 of Lecture Notes in Computer Science, 2024.
[MRZ21] Hendrik Molter, Malte Renken, and Philipp Zschoche. Temporal reachability minimization: Delaying vs. deleting. In Proceedings of the 46th International Symposium
on Mathematical Foundations of Computer Science (MFCS), volume 202 of LIPIcs,
pages 76:1–76:15, 2021.
[ZFMN20] Philipp Zschoche, Till Fluschnik, Hendrik Molter, and Rolf Niedermeier. The complexity of finding small separators in temporal graphs. Journal of Computer and System
Sciences, 107:72–92, 2020.
19