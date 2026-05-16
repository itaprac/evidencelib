from evidencelib import Frame


frame = Frame.dst(["Alive", "Dead"])
Alive, Dead = frame.symbols()

mass = frame.mass({
    Alive: 0.2,
    Dead: 0.5,
    Alive | Dead: 0.3,
})

print("Bel(Alive):", mass.belief(Alive))
print("Pl(Alive):", mass.plausibility(Alive))
print("BetP:", mass.pignistic())

