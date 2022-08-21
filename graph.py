# from matplotlib.lines import _LineStyle
import matplotlib.pyplot as plt

f0 = open('obs_comp_kstep.txt', 'r')             # Memorisation (change name)
f10 = open('obs_comp_explexpl.txt', 'r')        # Explore-Exploit

num_obs = [2, 6, 10, 14, 18]
final_vec0 = []
vec0 = []

i = 0
mt_0, mt_10 = 0, 0
sum0, sum10 = 0, 0
for l0, l10 in zip(f0.readlines(), f10.readlines()):
    if i % 30 == 0:
        sum0 /= 30
        sum10 /= 30
        rem0, rem10 = int(sum0) % 5, int(sum10) % 5
        sum0 /= num_obs[rem0]
        sum10 /= num_obs[rem10]

        mt_0 += sum0
        mt_10 += sum10

        sum0 = float(l0)
        sum10 = float(l10)

        if i != 0 and i % 150 == 0:
            ans = ( (mt_0 - mt_10) / mt_10 ) * 100
            vec0.append(ans)

            if i % 750 == 0:
                final_vec0.append(vec0)
                vec0 = []
    else:
        sum0 += float(l0)
        sum10 += float(l10)
        
    i += 1

mt_0 += sum0
mt_10 += sum10
ans = ( (mt_0 - mt_10) / mt_10 ) * 100
vec0.append(ans)
final_vec0.append(vec0)

# for vec0, speed in zip(final_vec0, [0.5, 0.8, 1.0, 1.2]):
    # plt.plot([3, 9, 15, 21, 27], vec0, _LineStyle='dashed', label='Speed {}'.format(speed))
num_targs = [3, 9, 15, 21, 27]
plt.plot(num_targs, final_vec0[0], linestyle='solid', marker='o', color='b', label='Speed 0.5')
plt.plot(num_targs, final_vec0[1], linestyle='dashed', marker='D', color='g', label='Speed 0.8')
plt.plot(num_targs, final_vec0[2], linestyle='dotted', marker='^', color='black', label='Speed 1.0')
plt.plot(num_targs, final_vec0[3], linestyle='dashdot', marker='s', color='r', label='Speed 1.2')

plt.legend()
plt.title('k-step vs Explore Exploit')    # change title
plt.xlabel('Number of targets')
plt.ylabel('Average percentage')

# plt.show()
plt.savefig('kstep_vs_explexpl.png') # change filename
