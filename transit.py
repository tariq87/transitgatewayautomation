import boto3
import redis
import random
import helper
from redis import ConnectionError

try:
    cache = redis.Redis(host="localhost", db=1)
except redis.exceptions.ConnectionError as ce:
    print(ce)
    
class Gateway():
    
    def __init__(self, region):
        try:
            self.session = boto3.Session()
            self.region = region
            #self.cache = redis.Redis(host="localhost", db=1)
            self.client = self.session.client('ec2', region_name=self.region)
            #print(f"Created Sessions With AWS in Region {self.region}")
        except Exception as e:
            print(e)
        

    
    def create_security_domain(self, name, gatewayid):
        try:  
            res = self.client.create_transit_gateway_route_table(
                    TransitGatewayId=gatewayid,
                    TagSpecifications=[
                       {
                            'ResourceType': 'transit-gateway-route-table',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': name 
                                },
                            ]
                         },
                ]
            )
            _tgrtid = res['TransitGatewayRouteTable']['TransitGatewayRouteTableId']
            _tgrtname = res['TransitGatewayRouteTable']['Tags'][0]['Value']
            cache.set(_tgrtname,_tgrtid)
            return res
        except Exception as e:
            print(e)

    
    def get_transit_gateway_routetable_status(self,routetableid):
        try:
            res = self.client.describe_transit_gateway_route_tables(
                    TransitGatewayRouteTableIds=[routetableid] )  
            return res     
        except Exception as e:
            print(e)
            
    
    def get_transit_gateway_status(self, gatewayid):
        try:
            res = self.client.describe_transit_gateways(
                    TransitGatewayIds=[gatewayid]
            )
            return res
        except Exception as e:
            print(e)

    
    def create_gateway(self, name):
        try:
            res = self.client.create_transit_gateway(
                Description = 'Testing transit gateway automation',
                Options = {
                    'AmazonSideAsn': random.randint(64512,65534),
                    'AutoAcceptSharedAttachments': 'enable',
                    'DefaultRouteTableAssociation': 'enable',
                    'DefaultRouteTablePropagation': 'enable',
                    'VpnEcmpSupport': 'enable',
                    'DnsSupport': 'enable',
                    'MulticastSupport': 'enable',
                },
                TagSpecifications=[
                {   

                    'ResourceType': 'transit-gateway',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name +"-"+ str(random.randint(5555,9999))
                        },
                        ]
                    },
                ],
            )
            _tgwid = res['TransitGateway']['TransitGatewayId']
            _tgwname = res['TransitGateway']['Tags'][0]['Value']
            cache.set(_tgwname,_tgwid)
            return res
            
        except Exception as e:
            print(e)


    def create_attachments(self,gatewayid,vpcid,subnetid,name):
        try:
            res = self.client.create_transit_gateway_vpc_attachment(
                TransitGatewayId=gatewayid,
                VpcId=vpcid,
                SubnetIds=[s for s in subnetid],
                TagSpecifications=[
                    {
                        'ResourceType': 'transit-gateway-attachment',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': name+str(random.randint(1,99))

                            },
                        ]
                    },

                ],
                
            )
            _attachment = res['TransitGatewayVpcAttachment']['Tags'][0]['Value']
            _attachmentId = res['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
            cache.set(_attachment,_attachmentId)
            return res
            
        except Exception as e:
            print(e)
    
    def get_vpc_attachment_status(self, attachmentId):
        try:
            res = self.client.describe_transit_gateway_vpc_attachments(
                TransitGatewayAttachmentIds=[attachmentId],
            )
            return res
        except Exception as e:
            print(e)
        

    def disassociate_vpc_from_default(self):
        pass

    def associate_vpc_to_secdomain(self):
        pass

    def create_propagation(self):
        pass
    