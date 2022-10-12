# transit gateway automation
----------------------------

<p>This tool require to authenticate boto3 with your aws using either aws cli credentials or environment variables</p>
<p>You need to pip install boto3, redis as well</p>
<p>This tool will create a transit gateway with default settings</p>
<p>Will also create transit gateway with custom settings</p>
<p>Will create security domains</p>
<p>Security domains are nothing but custom route tables</p>
<p>Will attach VPC to security domains</p>
<p>Will let you create segmented routing using security domains</p>
<p>So any 2 or more vpc's in the same security domain will be able to talk to eachother</p>
<p>Suppose you have 3 vpc's A,B,C all attached to a single transit gateway, by default they all will be able to talk to eachother, but if you want that vpc C should not be talking to vpc A and B,then we create 2 security domains, say secdomain1 and secdomain2, we put vpc A and B in secdomain1 and vpc C in secdomain2. Now you have segmented routing where A and B are able to talk to eachother because they are in the same security domain but cannot talk to vpc C because of different security domain</p>

---------------------------------------------------------------------


<p>How to create transit gateway - new - new</p>

```python3 gateway.py --name <transitGatewayName> --region <RegionName>```

<br></br>
<p>How to create a Security Domain</p>

```python3 gateway.py --secdo <security_Domain_Name> --transitgateway <transit_Gateway_Name> --region <Region_Name>```
<br></br>

<p>How to attach VPC to transit gateway</p>

```python3 gateway.py --vpcname <vpc_name> --transitgateway <transit_Gateway_Name> --region <Region_Name>```
<br></br>
<p>How to attach VPC to a security domain</p>

```python3 gateway.py --vpcname <vpc_name> --secdo <security_domain_name> --transitgateway <transit_Gateway_Name> --region <Region_Name>```
<br></br>

<p>How to Connect two security domains</p>

```python3 gateway.py --connect <SecurityDomain1> <SecurityDomain2> --region <Region_Name>```
<br></br>

<p>How to Disconnect two security domains</p>

```python3 gateway.py --disconnect <SecurityDomain1> <SecurityDomain2> --region <Region_Name>```
<br></br>

<p>How to delete transit gateway</p>

```python3 gateway.py --delete <transit_Gateway_Name> --region <Region_Name>```
<br></br>

<p>How to create transit gateway - new - new peering attachment for inter-region communication</p>

```python3 gateway.py --peer <transit_Gateway_Name1> <transit_Gateway_Name2> --region <Region_Name> --peer-region <Region_Name>```
<br></br>

<p>How to two security domains across the region</p>

```python3 gateway.py --connect <SecurityDomain1> <SecurityDomain2> --region <Region_Name> --peer-region <Region_Name> --peer-attachment-name <Peering_Attachment_Name>```


