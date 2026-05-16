from evidencelib import Frame


frame = Frame.dsmt(["t1", "t2", "t3"])
t1, t2, t3 = frame.symbols()

m1 = frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
m2 = frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})

combined = m1.dsmc(m2)

for proposition, value in combined.items():
    print(f"{proposition}: {value:.6f}")
