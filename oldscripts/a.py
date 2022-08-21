from tabulate import tabulate

with open('mixing_rat.txt', 'r+') as f:
    lines = f.readlines()
    final_vec = [[3, 9, 15, 21, 27]]
    vec = []
    m_sum = 0
    for i, line in enumerate(lines):
        if i % 30 == 0:
            m_sum /= 30
            if i != 0:
                vec.append(m_sum)
                if i % 150 == 0:
                    final_vec.append(vec)
                    vec = []
            m_sum = float(line)
        else:
            m_sum += float(line) 
    
    vec.append(m_sum/30)
    final_vec.append(vec)
    final_vec = [ [ round(x, 2) for x in l ] for l in final_vec ] 

    f.write("final array: " + str(final_vec) + "\n")
    print(tabulate(final_vec, tablefmt='fancy_grid'))
