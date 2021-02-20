import shutil

def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fG" % (G)
        else:
            return "%.2fM" % (M)
    else:
        return "%.2fkb" % (kb)

usage = shutil.disk_usage("/")
free_space = formatSize(usage[2])
print(free_space)
fs = free_space.strip("G")
#seventyfive = float(fs)*0.75
#days = seventyfive / 7.5
# 75% of the available diskspace, divided by 7.5G per day allowance = free_space /10
#print('%.1f'%seventyfive + "G")
days = float(fs) / 10
print('%.0f'%days + " Days")