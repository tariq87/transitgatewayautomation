# transit gateway automation
----------------------------
<p>This tool will create a transit gateway with default settings</p>
<p>Will also create transit gateway with custom settings</p>
<p>Will create security domains</p>
<p>Will attach VPC to security domains</p>
<p>Will let you create segmented routing using security domains</p>
----------------------------
```python:
<p>How to create transit gateway</p>
python3 gateway.py --transitgateway <transitGatewayName> --region <RegionName>
<p>How to create a Security Domain</p>
python3 gateway.py --secdo <securityDomainName> --transitgateway <transitGatewayName> --region <RegionName>
