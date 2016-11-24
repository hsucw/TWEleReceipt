import random
import json

rand_num_list = random.sample(range(1, 10000), 9999)
guess_list = [str(n).zfill(4) for n in rand_num_list]

with open("guess_list.json","w") as f:
    f.write(json.dumps(guess_list))
