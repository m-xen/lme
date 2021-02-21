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
import time

def install():
    if os.path.isfile("docker-compose-stack.yml"):
        print("OK")
    else:
        print("Can't find docker-compose-stack.yml please change directory to Chapter 3 Files and rerun this script")
        exit()

    #move configs
    if os.path.isfile("docker-compose-stack-live.yml"):
        try:
            if os.path.isfile("docker-compose-stack-live.yml.bak"):
                try:
                    os.remove("docker-compose-stack-live.yml.bak")
                except OSError as error:
                    print(error)
                    exit()
            os.rename("docker-compose-stack-live.yml","docker-compose-stack-live.yml.bak")
        except OSError as error:
            print(error)
            exit()
    shutil.copy("docker-compose-stack.yml","docker-compose-stack-live.yml")


    #get the IP and Server DNS name
    IP_Fin = False
    while not IP_Fin:
        try:
            S_IP = str(input("enter IP address for LME \n"))
            socket.gethostbyaddr(S_IP)
        except KeyboardInterrupt:
            exit()
        except:
            print("that IP didn't respond, please enter a valid IP address")
        else:
            print(S_IP + " connection tested\n")
            IP_Fin = True

    Sname_Fin = False
    while not Sname_Fin:
        try:
            S_Name = input("enter the DNS name of LME \n")
            socket.gethostbyname(S_Name)
        except KeyboardInterrupt:
            exit()
        except:
            print("that server name didn't respond, please enter a valid name")
        else:
            print(S_Name + " connection tested\n")
            Sname_Fin = True

    SelfS = input("This script will use self signed certificates for communication and encryption, Do you want to continue with self signed certificates? Y or N")

    if SelfS in ["Y","y","Yes","yes","YES"]:
        generate_certs()
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

def generate_certs():
    
    try:
        print("\n ...about to remove certs folder, ctrl-c if you're not sure... \n")
        time.sleep(3)
        parent_dir = os.getcwd()
        directory = "certs"
        path = os.path.join(parent_dir, directory)
        shutil.rmtree(path)
        os.mkdir(path, 0o666)
        exit()
    except KeyboardInterrupt:
        exit()
    except OSError as error:
        print(error)
        exit()

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
