def insertSolutions(solutionsFile, outputFile, statsinfoFile):
    with open(outputFile, 'r') as file:
        solves = file.readlines()
    with open(solutionsFile, 'r') as file:
        solutions = file.readlines()
    solvesdata=[]
    for solve in solves:
        solve = solve.split('\t')
        solve[7] = solve[7].replace('\n','')
        solvesdata.append(solve)
    solvesdata[0].append("Optimal solution")
    solvesdata[0].append("Optimal length")
    sid = 0
    stats = []
    for solve in solvesdata:
        if solve[0] == "4x4" and solve[7] != "Not found in replays":
            sol = solutions[sid].replace('\n', '')
            solve.append(sol)
            solve.append(str(len(sol)))
            sid += 1
            stats.append([solve[4], solve[5], solve[9]])
    with open(outputFile, 'w') as file:
        for solve in solvesdata:
            file.write('\t'.join(solve) + '\n')
    with open(statsinfoFile, "w") as file:
        for stat in stats:
            file.write('\t'.join(stat) + '\n')
