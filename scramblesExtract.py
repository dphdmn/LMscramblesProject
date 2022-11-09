def extractScrambles(inputFile, scramblesFile):
    with open(inputFile, 'r') as file:
        solves = file.readlines()
    scrambles = []
    for solve in solves:
        solve = solve.split('\t')
        if solve[0] == "4x4" and solve[7] != "Not found in replays\n":
            scrambles.append(solve[7])
    with open(scramblesFile, 'w') as file:
        file.write(''.join(scrambles))
