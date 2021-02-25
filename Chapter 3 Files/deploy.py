#docker pull docker.elastic.co/elasticsearch/elasticsearch:7.11.1-amd64
#docker pull docker.elastic.co/kibana/kibana:7.11.1
#docker pull docker.elastic.co/logstash/logstash:7.11.1-amd64

import os
import re
import shutil
import socket
import subprocess
import time

def install():
    if not os.path.isfile("docker-compose-stack.yml"):
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
    install.S_IP = str(input("enter IP address for LME \n"))
    install.S_Name = str(input("enter the DNS name for LME \n"))
    regex = ("^((?!-)[A-Za-z0-9-]" + "{1,63}(?<!-)\\.)" + "+[A-Za-z]{2,6}")
    Pattern = re.compile(regex)
    while not re.fullmatch(Pattern, install.S_Name):
        try:
            print("that server name isn't a valid dns name, please enter a name like \"test.local\"")
            install.S_Name = str(input("enter a valid DNS name for LME \n"))
        except KeyboardInterrupt:
            exit()
    print("Testing...\n")

    IP_Fin = False
    Sname_Fin = False

    while not IP_Fin:
        try:
            socket.gethostbyaddr(install.S_IP)
        except KeyboardInterrupt:
            exit()
        except:
            print("that IP didn't respond, please enter a valid IP address")
            install.S_IP = str(input("enter a valid IP address for LME \n"))
        else:
            IP_Fin = True

    while not Sname_Fin:
        try:
            socket.gethostbyname(install.S_Name)
        except KeyboardInterrupt:
            exit()
        except:
            print("that server name didn't respond, please enter a valid name")
            install.S_Name = str(input("enter a valid DNS name for LME \n"))
        else:
            Sname_Fin = True
    
    print("Success! Configuring LME with IP address \"" + install.S_IP + "\" and server name \"" + install.S_Name + "\"\n")
    
    generate_certs()
    configure()
    up()

def generate_certs():

    #manually generate certificate for Kibana
    try:
        parent_dir = os.getcwd()
        directory = "certs"
        path = os.path.join(parent_dir, directory)
        if os.path.isdir("certs"):
            print("\n ...about to remove certs folder, ctrl-c if you're not sure... \n")
            time.sleep(3)
            shutil.rmtree(path)
        os.mkdir(path, 0o755)
    except KeyboardInterrupt:
        exit()
    except OSError as error:
        print(error)
        exit()
    #create CA private key
    subprocess.check_call(r'"openssl" genrsa -out certs/root.key 4096', stderr=subprocess.STDOUT, shell=True)
    #create a csr
    subprocess.check_call(r'"openssl" req -new -key certs/root.key -out certs/root.csr -sha256 -subj "/C=GB/ST=UK/L=London/O=Docker/CN=Elastic"', stderr=subprocess.STDOUT, shell=True)
    
    with open('root.cnf', 'w') as file:
        file.write("[root_ca]\n"
        "basicConstraints = critical,CA:TRUE,pathlen:1 \n"
        "keyUsage = critical, nonRepudiation, cRLSign, keyCertSign \n"
        "subjectKeyIdentifier=hash")

    #sign the root cert
    subprocess.check_call(r'"openssl" x509 -req  -days 3650  -in certs/root.csr -signkey certs/root.key -sha256 -out certs/root.crt -extfile root.cnf -extensions root_ca', stderr=subprocess.STDOUT, shell=True)
    #create server certificate
    subprocess.check_call(r'"openssl" genrsa -out certs/kibana.key 4096', stderr=subprocess.STDOUT, shell=True)
    #create a csr
    subprocess.check_call(r'"openssl" req -new -key certs/kibana.key -out certs/kibana.csr -sha256 -subj "/C=GB/ST=UK/L=London/O=Docker/CN=LME"', stderr=subprocess.STDOUT, shell=True)
    
    with open('kibana.cnf', 'w') as file:
        file.write("[server]\n"
        "authorityKeyIdentifier=keyid,issuer \n"
        "basicConstraints = critical,CA:FALSE \n"
        "extendedKeyUsage=serverAuth \n"
        "keyUsage = critical, digitalSignature, keyEncipherment \n"
        "subjectAltName = DNS:"+ install.S_Name +", IP:" + install.S_IP + ", DNS:kibana\n"
        "subjectKeyIdentifier=hash")

    subprocess.check_call(r'"openssl" x509 -req -days 750 -in certs/kibana.csr -sha256 -CA certs/root.crt -CAkey certs/root.key -CAcreateserial -out certs/kibana.crt -extfile kibana.cnf -extensions server', stderr=subprocess.STDOUT, shell=True)

    with open('internal.cnf', 'w') as file:
        file.write("[server]\n"
        "authorityKeyIdentifier=keyid,issuer \n"
        "basicConstraints = critical,CA:FALSE \n"
        "extendedKeyUsage=serverAuth \n"
        "keyUsage = critical, digitalSignature, keyEncipherment \n"
        "subjectAltName = DNS:localhost, IP:127.0.0.1, DNS:es01, DNS:es02, DNS:es03, DNS:logstash \n"
        "subjectKeyIdentifier=hash")
   
    #create internal private key
    subprocess.check_call(r'"openssl" genrsa -out certs/internal.key 4096', stderr=subprocess.STDOUT, shell=True)
    #create a csr
    subprocess.check_call(r'"openssl" req -new -key certs/internal.key -out certs/internal.csr -sha256 -subj "/C=GB/ST=UK/L=London/O=Docker/CN=ELK"', stderr=subprocess.STDOUT, shell=True)
    #create internal certificate
    subprocess.check_call(r'"openssl" x509 -req -days 750 -in certs/internal.csr -sha256 -CA certs/root.crt -CAkey certs/root.key -CAcreateserial -out certs/internal.crt -extfile internal.cnf -extensions server', stderr=subprocess.STDOUT, shell=True)

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

def configure():
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

def up():
    print("creating certs volume...")
    subprocess.check_call(r'"docker" run -d --rm --name gen_certs -v lme_certs:/certs docker.elastic.co/elasticsearch/elasticsearch:7.11.1 tail -f /dev/null', stderr=subprocess.STDOUT, shell=True)
    subprocess.check_call(r'"docker" cp certs/. gen_certs:/certs/', stderr=subprocess.STDOUT, shell=True)
    subprocess.check_call(r'"docker" stop gen_certs', stderr=subprocess.STDOUT, shell=True)
    print("Bringing up environment now...")
    subprocess.check_call(r'"docker-compose" -f docker-compose-stack-live.yml up -d', stderr=subprocess.STDOUT, shell=True)

install()
print("\n An deireadh! \n")
exit()