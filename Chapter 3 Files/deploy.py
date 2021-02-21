# installdocker
# initdockerswarm
# populatecerts
# generatepasswords
# customlogstashconf
# populatelogstashconfig
# configuredocker
# deploylme
# setpasswords
# configelasticsearch
# zipfiles

import os
import shutil
import socket

def install():
    if os.path.isfile("docker-compose-stack.yml"):
        print("OK")
    else:
        print("please change directory to Chapter 3 Files and rerun")
        exit()

    #move configs
    if os.path.isfile("docker-compose-stack-live.yml"):
        os.rename("docker-compose-stack-live.yml","docker-compose-stack-live.yml.bak")
    else:
        shutil.copy("docker-compose-stack.yml","docker-compose-stack-live.yml")


    #find the IP and Server DNS name
    IP_Fin = False
    while not IP_Fin:
        try:
            S_IP = str(input("enter IP address for LME \n"))
            result = socket.gethostbyaddr(S_IP)
        except:
            print("that IP didn't respond, please enter a valid IP address")
        else:
            print(S_IP + " connection tested\n")
            IP_Fin = True


    S_Name = input("enter the DNS name of LME")

    SelfS = input("This script will use self signed certificates for communication and encryption, Do you want to continue with self signed certificates? Y or N")

    if SelfS in ["Y","y","Yes","yes","YES"]:
        print("OK")
    else:
        Certs = input("Please create certificates and put them in the /certs folder. The press Y to continue or N to quit the install")
        if Certs in ["Y","y","Yes","yes","YES"]:
            if os.path.isdir("Certs"):
                print("OK")
            else:
                exit()
        else:
            exit()
    data_retention()

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

def data_retention():
    usage = shutil.disk_usage("/")
    #needs choice of path
    # Ubuntu: /var/lib/docker/
    # Fedora: /var/lib/docker/
    # Debian: /var/lib/docker/
    # Windows: C:\ProgramData\DockerDesktop
    # MacOS: ~/Library/Containers/com.docker.docker/Data/vms/0/
    free_space = formatSize(usage[2])
    print(free_space)
    fs = free_space.strip("G")
    #seventyfive = float(fs)*0.75
    #days = seventyfive / 7.5
    # 75% of the available diskspace, divided by 7.5G per day allowance = free_space /10
    #print('%.1f'%seventyfive + "G")
    days = float(fs) / 10
    print('%.0f'%days + " Days")

install()
