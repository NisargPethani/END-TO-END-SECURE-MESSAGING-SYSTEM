# End to End Secure Messaging System
This is an end to end messaging system like whatsapp where users can send messages/files to other users or to members of a group. Messages are end to end encrypted using the triple - DES encryption and key exchange is done using Diffie Hellman key exchange algorithm. Also load balancing algorithm is used to distribute the load among different servers. System is fault tolerant, which is achieved using load balancer. It takes care of the situation when some of the servers are down.

### Getting Started 
* Run the load balancer.
```
python3 LoadBalancer.py
```
* Any number of server can be started using the following command.
```
python3 server.py <ip_address:port>
```
* Any number of peer can be started using the following command.
```
python3 peer.py <ip_address:port>
```
### Commands
* To Sign Up
```
SIGNUP <username> <password>
```
* To Sign In
```
SIGNIN <username> <password>
```
* List available groups along with the number of participants.
```
LIST
```
* To join a group.
```
JOIN <group_name>
```
* To create a new group
```
CREATE <group_name>
```
* To send messages to user/users
```
SEND <user_name1,user_name2> <MSG/FILE> <message/file_path>
```
* To send a message to group/groups.
```
SEND <group_name1,group_name2,group_name3> <MSG/FILE> <message/file_path>
```
* To send a message to users and group.
```
SEND <user_name1,group_name1,user_name2,group_name2> <MSG/FILE> <message/file_path>
```
