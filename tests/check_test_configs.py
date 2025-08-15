import subprocess
import os
import yaml
from filecmp import cmp
import sys

CHECK = True

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'check':
        CHECK = True

    configs = [e for e in os.listdir("./") if e.endswith("yaml") or e.endswith("yml")]
    print(f"Config files detected: {', '.join(configs)}")

    for cfg in configs:
        subprocess.run(f'python ../main_sl.py {cfg}')

    hasMismatches = False
    if CHECK:
        dirCont = os.listdir('./expect/')
        print("Analyzing newer versions of files from ./expect/ ...")
        # print(dirCont)
        for cfg in configs:
            print(f"Comparing output for {cfg}")
            with open(cfg, 'r') as f:
                configDict = yaml.load(f, Loader=yaml.loader.SafeLoader)
            mask = configDict['output']['mask']
            for f in dirCont:
                if f.startswith(mask):
                    rst = cmp(os.path.join('./expect', f), os.path.join('./out', f))
                    if rst:
                        print(f"./out/{f} and ./expect/{f} are the same")
                    else:
                        print(f"./out/{f} is different from ./expect/{f}!")
                        hasMismatches = True
    exit(hasMismatches)




