installdocker
initdockerswarm
populatecerts
generatepasswords
customlogstashconf
populatelogstashconfig
configuredocker
deploylme
setpasswords
configelasticsearch
zipfiles

function install(){
echo -e "\e[32m[x]\e[0m Installing prerequisites"
#install net-tools to allow backwards compatibility
sudo apt-get install net-tools -y -q
#move configs
cp docker-compose-stack.yml docker-compose-stack-live.yml

#find the IP winlogbeat will use to communicate with the logstash box (on elk)

#get interface name of default route
DEFAULT_IF="$(route | grep '^default' | grep -o '[^ ]*$')"

#get ip of the interface
EXT_IP="$(/sbin/ifconfig $DEFAULT_IF| awk -F ' *|:' '/inet /{print $3}')"

read -e -p "Enter the IP of this linux server: " -i "$EXT_IP" logstaship

read -e -p "Enter the DNS name of this linux server, This needs to be resolvable from the Windows Event Collector: " logstashcn
echo "[x] Configuring winlogbeat config and certificates to use $logstaship as the IP and $logstashcn as the DNS"

#enable auto updates if ubuntu
auto_os_updates

read -e -p "This script will use self signed certificates for communication and encryption, Do you want to continue with self signed certificates? ([y]es/[n]o): " -i "y" selfsignedyn

if [ "$selfsignedyn" == "y" ]; then
#make certs
generatecerts





elif [ "$selfsignedyn" == "n" ]; then

echo "Please make sure you have the following certificates named correctly"
echo "./certs/root-ca.crt"
echo "./certs/elasticsearch.key"
echo "./certs/elasticsearch.crt"
echo "./certs/logstash.crt"
echo "./certs/logstash.key"

echo "[x] checking for root-ca.crt"
if [ ! -f ./certs/root-ca.crt ]; then
    echo "File not found!"
    exit
fi
echo "[x] checking for elasticsearch.key"
if [ ! -f ./certs/elasticsearch.key ]; then
    echo -e "\e[31m[X]\e[0m File not found!"
    exit
fi
echo "[x] checking for elasticsearch.crt"
if [ ! -f ./certs/elasticsearch.crt ]; then
    echo -e "\e[31m[X]\e[0m File not found!"
    exit
fi
echo "[x] checking for logstash.crt"
if [ ! -f ./certs/logstash.crt ]; then
    echo -e "\e[31m[X]\e[0m File not found!"
    exit
fi
echo "[x] checking for logstash.key"
if [ ! -f ./certs/logstash.key ]; then
    echo -e "\e[31m[X]\e[0m File not found!"
    exit
fi


else
echo "Not a valid option"
fi

installdocker
initdockerswarm
populatecerts
generatepasswords
customlogstashconf
populatelogstashconfig
configuredocker
deploylme
setpasswords
configelasticsearch
zipfiles

read -e -p "Do you want to automatically update LME ([y]es/[n]o): " -i "y" autoupdate_enabled

if [ "$autoupdate_enabled" == "y" ]; then
echo -e "\e[32m[x]\e[0m Enabling LME Automatic Update"
#cron lme update
auto_lme_update
fi

read -e -p "Do you want to automatically update Dashboards ([y]es/[n]o): " -i "y" dashboardupdate_enabled

if [ "$dashboardupdate_enabled" == "y" ]; then
echo -e "\e[32m[x]\e[0m Enabling Dashboard Automatic Update"
#cron dash update
dashboard_update
fi

#ILM
data_retention

#pipelines
pipelines

echo "##################################################################################"
echo "## KIBANA/Elasticsearch Credentials are (these will not be accesible again!!!!) ##"
echo "##"
echo "## Web Interface login:"
echo "## elastic:$elastic_user_pass"
echo "##"
echo "## System Credentials"
echo "## kibana_system_pass:$kibana_system_pass"
echo "## logstash_system:$logstash_system_pass"
echo "## logstash_writer:$logstash_writer"
echo "## update_user:$update_user_pass"
echo "##################################################################################"
}