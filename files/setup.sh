#firefox --version
#tshark -v

#dpkg-query -L firefox		
#pip show selenium									#Version 2.53.6
#dpkg -s firefox | grep 'Version'		#Version 49.0-2
#cat /etc/issue 										#Debian GNU/Linux 8

echo "[1] set firefox config"
mv /opt/monroe/autoconfig.js /opt/firefox/defaults/pref
mv /opt/monroe/mozilla.cfg  /opt/firefox


echo "[2] add yomo and adblock_plus to firefox"
mv /opt/monroe/yomo-42.florian.wamser@informatik.uni-wuerzburg.de.xpi /opt/firefox/browser/extensions 
mv /opt/monroe/{d10d0bf8-f5b5-c8b4-a8b2-2b9879e08c5d}.xpi /opt/firefox/browser/extensions


#echo "[2,5] get metadata"
#python /opt/monroe/measurements.py >> /monroe/results/metadata.txt &
#sleep 30s


echo "[3] select network interface"
#pefered interfaces
PREFINTERFACES=(op1 op2 op0)

#save network infos
echo "-save network infos"
sleep 10s
route -e >> /monroe/results/rt_tables.txt 
ifconfig >> /monroe/results/ifconfig.txt 
ip route >> /monroe/results/ipRoute.txt 

#delete default gateways
echo "-delelte default gateways"
route del default 2> /dev/null || X=1
route del default 2> /dev/null || X=1
route del default 2> /dev/null || X=1
route del default 2> /dev/null || X=1
route del default 2> /dev/null || X=1

#get list of available network interfaces
TEST_IP="81.169.145.159"
NUMOFSTARS=28
AVINTERF=[]
INTERFCOUNT=0
EXIST=0
ACTIVE=0
#eth0
PING=$(traceroute -i eth0 $TEST_IP) || EXIST=1
echo "$PING" >> /monroe/results/ping_eth0.txt
route del default 2> /dev/null || X=1
if [ $EXIST -eq 0 ]; then
	echo "-eth0 interface"
	ACTIVE=$( echo "$PING" | grep "*" | wc -l)
	echo "stars: $ACTIVE"
	if [ $ACTIVE -lt $NUMOFSTARS ]; then
		echo "--eth0 is active"
		AVINTERF["$INTERFCOUNT"]="eth0"
		INTERFCOUNT=$((INTERFCOUNT+1))
	fi
fi
EXIST=0
ACTIVE=0
#op0
PING=$(traceroute -i op0 $TEST_IP) || EXIST=1
echo "$PING" >> /monroe/results/ping_op0.txt
route del default 2> /dev/null || X=1
if [ $EXIST -eq 0 ]; then
	echo "-op0 interface"
	ACTIVE=$(echo "$PING" | grep "*" | wc -l)
	if [ $ACTIVE -lt $NUMOFSTARS ]; then
		echo "--op0 is active"
		AVINTERF["$INTERFCOUNT"]="op0"
		INTERFCOUNT=$((INTERFCOUNT+1))
	fi
fi
EXIST=0
ACTIVE=0
#op1
PING=$(traceroute -i op1 $TEST_IP) || EXIST=1
echo "$PING" >> /monroe/results/ping_op1.txt
route del default 2> /dev/null || X=1
if [ $EXIST -eq 0 ]; then
	echo "-op1 interface"
	ACTIVE=$(echo "$PING" | grep "*" | wc -l)
	if [ $ACTIVE -lt $NUMOFSTARS ]; then
		echo "--op1 is active"
		AVINTERF["$INTERFCOUNT"]="op1"
		INTERFCOUNT=$((INTERFCOUNT+1))
	fi
fi
EXIST=0
ACTIVE=0
#op2
PING=$(traceroute -i op2 $TEST_IP) || EXIST=1
echo "$PING" >> /monroe/results/ping_op2.txt
route del default 2> /dev/null || X=1
if [ $EXIST -eq 0 ]; then
	echo "-op2 interface"
	ACTIVE=$(echo "$PING" | grep "*" | wc -l)
	if [ $ACTIVE -lt $NUMOFSTARS ]; then
		echo "--op2 is active"
		AVINTERF["$INTERFCOUNT"]="op2"
		INTERFCOUNT=$((INTERFCOUNT+1))
	fi
fi
EXIST=0
ACTIVE=0
echo "-number of available interfaces: $INTERFCOUNT"

#get prefered interface
INTERF=""
for i in $(seq 0 ${#PREFINTERFACES[@]}) "${PREFINTERFACES[@]}"
do
	if [[ "${AVINTERF[@]}" =~ "${PREFINTERFACES[i]}" ]]; then
    INTERF="${PREFINTERFACES[i]}"
		break
	fi
done
echo "-prefered interface: $INTERF"

#set prefered interface as default
echo "prefered interface: $INTERF" >> /monroe/results/setRoute_pref.txt
route add default dev "$INTERF" >> /monroe/results/setRoute_pref.txt 2> /monroe/results/setRoute__pref_error.txt
traceroute $TEST_IP >> /monroe/results/ping_route_pref.txt
curl -s http://whatismijnip.nl |cut -d " " -f 5 >> /monroe/results/curl_pref.txt


echo "[5] start collecting network traffic infos"
sleep 10s
tshark -n -i $INTERF -E separator=, -T fields -e frame.time_epoch -e tcp.len -e frame.len -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.analysis.ack_rtt -e tcp.analysis.lost_segment -e tcp.analysis.out_of_order -e tcp.analysis.fast_retransmission -e tcp.analysis.duplicate_ack -e dns -Y "tcp or dns"  >> /monroe/results/tshark.txt 2> /monroe/results/tshark_error.txt &
# -e dns.resp.primaryname


echo "[6] do measurements"
python /opt/monroe/measurements.py

echo "[6] finished"
