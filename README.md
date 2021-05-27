# transit gateway automation
----------------------------
<p>This tool will create a transit gateway with default settings</p>
<p>Will also create transit gateway with custom settings</p>
<p>Will create security domains</p>
<p>Will attach VPC to security domains</p>
<p>Will let you create segmented routing using security domains</p>

---------------------------------------------------------------------


<p>How to create transit gateway</p>

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

