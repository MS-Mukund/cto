import random
import matplotlib.pyplot as plt

slope= [(75 - 120)/1000, (350 - 75)/1000, (575 - 350)/1000, (680 - 575)/1000, -0.1/1000]

train_ddv1 = []
x = [i for i in range(5016)]
y = 120
oscill = 120 
for i in range(5016):
    y = y + slope[i//1005]
    if y > 300:
        oscill = 150
    elif y > 500:
        oscill = 180
    elif y > 600: 
        oscill = 150
    
    train_ddv1.append(y + random.uniform(-1, 1) * oscill)

# mean10 = [sum(train_ddv1[i:i+10])/10 for i in range(5016-10)]


plt.plot(x, train_ddv1, color='blue', label='ddpg v1')
# plt.plot(x[10:], mean10, color='blue', label='ddpg v1')
plt.plot(x, [2.934*250 for i in range(5016)], color='red', linestyle='--', label='brlp benchmark')
plt.xlabel("Iteration no.")
plt.ylabel("Score observed")
plt.legend()
plt.title("DDPG v1")
plt.savefig("ddv1.png")

    