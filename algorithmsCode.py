import pandas as pd


class WorkflowNet:
    def __init__(self, places, transitions, flow_relations):
        self.places = places
        self.transitions = transitions
        self.flow_relations = flow_relations

    def pre_set(self, t):
        return set(p for p in self.places if (p, t) in self.flow_relations)

    def post_set(self, t):
        return set(p for p in self.places if (t, p) in self.flow_relations)

    def pre_set_p(self, p):
        return set(t for t in self.transitions if (t, p) in self.flow_relations)

    def post_set_p(self, p):
        return set(t for t in self.transitions if (p, t) in self.flow_relations)

    def pre_task(self, t):
        p_pre = set(p for p in self.places if (p, t) in self.flow_relations)
        task = set()
        for p in p_pre:
            task.update(list(t for t in self.transitions if (t, p) in self.flow_relations))
        return task


def computeNCP(wn, T, x, y):
    Q = []
    S = set()

    for z in wn.pre_task(x):
        Q.append(z)
        while Q:
            q = Q.pop(0)
            if q in wn.pre_task(y):
                S.add(q)
    return S.intersection(T)


def computeNCP_P(wn, P, x, y):
    Q = []
    S = set()

    for z in wn.pre_set(x):
        Q.append(z)
        while Q:
            q = Q.pop(0)
            if q in wn.pre_set(y):
                S.add(q)
    return S.intersection(P)

def compute_TER(WFN):
    P = WFN.places
    T = WFN.transitions
    TERM = pd.DataFrame(data="∞", index=[x for x in T if x != "t"], columns=[x for x in T if x != "t"])
    for p in P:
        if p == "i" or p == "o":
            continue
        for x in WFN.pre_set_p(p):
            for y in WFN.post_set_p(p):
                if x == "t" or y == "t":
                    continue
                TERM.loc[x, y] = "->"
    for z in T:
        for x in T:
            for y in T:
                if x == "t" or y == "t" or z == "t":
                    continue
                if (TERM.loc[x, z] == "->" or TERM.loc[x, z] == "=>") and (
                        TERM.loc[z, y] == "->" or TERM.loc[z, y] == "=>") and TERM.loc[x, y] != "->":
                    TERM.loc[x, y] = "=>"
    for x in T:
        for y in T:
            for z in T:
                if computeNCP(WFN, T, x, y) == z and x != z and y != z:
                    TERM.loc[z, y] = "->"
                    TERM.loc[x, x] = "->"
    print(TERM)
    # return TERM


def determine_task_type(wfn, tau):
    # Get the input and output places of the task
    tau_type = {}
    P = wfn.places
    for ta in tau:
        P1 = wfn.pre_set(ta)
        P2 = wfn.post_set(ta)
        # Determine the type based on the input and output places
        if len(wfn.pre_set(ta)) == 1 and len(wfn.post_set(ta)) > 1:
            tau_type[ta] = "AND-SPLIT"
        elif len(wfn.post_set(ta)) == 1 and len(wfn.pre_set(ta)) > 1:
            tau_type[ta] = "AND-JOIN"
        elif computeNCP_P(wn, P, P1, P2) == P1:
            tau_type[ta] = "SKIP"
        elif computeNCP_P(wn, P, P1, P2) == P2:
            tau_type[ta] = "REDO"
        else:
            tau_type[ta] = "SWITCH"

    print(tau_type)
    return tau_type


wn = WorkflowNet(["i", "p1", "p2", "p3", "p4", "p5", "o"], ["A", "B", "C", "D", "E", "F", "t"],
                 [("i", "A"), ("A", "p1"), ("p1", "B"), ("p1", "C"), ("p1", "D"), ("p2", "t"), ("B", 'p2'), ("C", "p3"),
                  ("p3", "E"), ("E", "p4"), ("t", "p4"), ("D", 'p4'), ('p4', 'F'), ('F', 'o')])

compute_TER(wn)

wn2 = WorkflowNet(["i", "p1", "p2", "p3", "p4", "p5", "p6", 'p7', 'p8', 'p9', 'p10', 'p12', "o"],
                  ["A", "B", "C", "D", "E", "F", 'G', 'H', 'I', "t1", 't2', 't3', 't4', 't5', 't6', 't7'],
                  [("i", "t1"), ("t1", "p1"), ('t1', 'p6'), ("p1", "t2"), ("p1", "A"), ("t2", "p2"), ("A", "p2"),
                   ("p2", "B"),
                   ("p2", "C"), ("B", "p4"), ("C", "p3"), ("p4", "t3"), ("t3", "p3"), ("p3", "E"), ("p4", "D"),
                   ("E", "p5"), ("D", "t4"), ("p5", "t4"), ("p6", "H"), ("H", "p11"), ("p11", "I"),
                   ("I", "p12"), ("p6", "t5"), ("t5", "p7"), ("t5", "p8"), ("p7", "F"), ("p8", "G"), ("p8", "t6"),
                   ("F", "p9"), ("G", "p10"), ("p10", "t6"), ("p9", "t7"), ("p10", "t7"), ("t7", "p12"),
                   ("t4", "o"), ("p12", "o")])

tau = ["t1", 't2', 't3', 't4', 't5', 't6', 't7']
determine_task_type(wn2, tau)
